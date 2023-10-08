from typing import List, cast, Dict
from Token import Token, TokenType
import Expr
import Stmt
from RuntimeErrorException import RuntimeErrorException
from Environment import Environment
from JSCallable import JSCallable
from JSFunction import JSFunction
from JSClass import JSClass, JSInstance
from Return import Return

class Log(JSFunction):
    def call(self, interpreter, arguments):
        for argument in arguments:
            print(interpreter.stringify(argument))
        return None

    def arity(self):
        return 1

class Interpreter(Expr.Visitor, Stmt.Visitor):
    _globals = Environment()

    def __init__(self):
        self.environment = self._globals
        self.locals: Dict[Expr.Expr, int] = {}
        console = JSClass("Console", None, {}).call(self, [])
        console.set(Token(TokenType.IDENTIFIER, "log", 0, 0),  Log(Stmt.Function(Token(TokenType.IDENTIFIER, "log", None, 1), [], []), self.environment, False))
        self.environment.define("console", console)

    def visit_literal_expr(self, expr: Expr.Literal):
        return expr.value

    def visit_logical_expr(self, expr: Expr.Logical):
        left = self.evaluate(expr.left)
        if expr.operator.type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left
        return self.evaluate(expr.right)

    def visit_set_expr(self, expr: Expr.Set):
        object = self.evaluate(expr.object)
        if not isinstance(object, JSInstance):
            raise RuntimeErrorException(expr.name, "Only instances have fields.")
        value = self.evaluate(expr.value)
        object.set(expr.name, value)
        return value

    def visit_super_expr(self, expr: Expr.Super):
        distance = self.locals[expr]
        superclass = self.environment.get_at(distance, "super")
        obj = self.environment.get_at(distance - 1, "this")
        method = superclass.find_method(expr.method.lexeme)
        if method is None:
            raise RuntimeErrorException(expr.method, f"Undefined property '{expr.method.lexeme}'.")
        return method.bind(obj)

    def visit_this_expr(self, expr: Expr.This):
        return self.look_up_variable(expr.keyword, expr)

    def evaluate(self, expr: Expr.Expr):
        return expr.accept(self)

    def execute(self, stmt: Stmt.Stmt):
        stmt.accept(self)

    def resolve(self, expr: Expr.Expr, depth: int):
        self.locals[expr] = depth

    def execute_block(self, statements: List[Stmt.Stmt], environment: Environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def visit_block_stmt(self, stmt: Stmt.Block):
        self.execute_block(stmt.statements, Environment(self.environment))
        return None

    def visit_class_stmt(self, stmt: Stmt.Class):
        superclass = None
        if stmt.superclass is not None:
            superclass = self.evaluate(stmt.superclass)
            if not isinstance(superclass, JSClass):
                raise RuntimeErrorException(stmt.superclass.name, "Superclass must be a class.")

        self.environment.define(stmt.name.lexeme, None)

        if stmt.superclass is not None:
            self.environment = Environment(self.environment)
            self.environment.define("super", superclass)

        methods = {}
        for method in stmt.methods:
            function = JSFunction(method, self.environment, method.name.lexeme == "constructor")
            methods[method.name.lexeme] = function
        klass = JSClass(stmt.name.lexeme, superclass,  methods)

        if superclass is not None:
            self.environment = self.environment.enclosing

        self.environment.assign(stmt.name, klass)
        return None

    def is_truthy(self, obj):
        if obj is None:
            return False
        if isinstance(obj, bool):
            return obj
        return True

    def check_number_operand(self, operator, operand):
        if isinstance(operand, float):
            return
        raise RuntimeError(operator, "Operand must be a number.")

    def check_number_operand_2(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return
        raise RuntimeErrorException(operator, "Operands must be numbers.")

    def visit_unary_expr(self, expr: Expr.Unary):
        right = self.evaluate(expr.right)
        if expr.operator.type == TokenType.MINUS:
            self.check_number_operand(expr.operator, right)
            return -float(right)
        elif expr.operator.type == TokenType.BANG:
            return not self.is_truthy(right)
        return None

    def is_equal(self, a, b):
        if a is None and b is None:
            return True
        if a is None:
            return False
        return a == b

    def visit_binary_expr(self, expr: Expr.Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        if expr.operator.type == TokenType.MINUS:
            self.check_number_operand_2(expr.operator, left, right)
            return float(left) - float(right)
        elif expr.operator.type == TokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return float(left) + float(right)
            elif isinstance(left, str) and isinstance(right, str):
                return str(left) + str(right)

            raise RuntimeErrorException(expr.operator, "Operands must be two numbers or two strings.")
        elif expr.operator.type == TokenType.SLASH:
            self.check_number_operand_2(expr.operator, left, right)
            return float(left) / float(right)
        elif expr.operator.type == TokenType.STAR:
            self.check_number_operand_2(expr.operator, left, right)
            return float(left) * float(right)
        elif expr.operator.type == TokenType.GREATER:
            self.check_number_operand_2(expr.operator, left, right)
            return float(left) > float(right)
        elif expr.operator.type == TokenType.GREATER_EQUAL:
            self.check_number_operand_2(expr.operator, left, right)
            return float(left) >= float(right)
        elif expr.operator.type == TokenType.LESS:
            self.check_number_operand_2(expr.operator, left, right)
            return float(left) < float(right)
        elif expr.operator.type == TokenType.LESS_EQUAL:
            self.check_number_operand_2(expr.operator, left, right)
            return float(left) <= float(right)
        elif expr.operator.type == TokenType.BANG_EQUAL:
            return not self.is_equal(left, right)
        elif expr.operator.type == TokenType.EQUAL_EQUAL:
            return self.is_equal(left, right)

        return None

    def visit_call_expr(self, expr: Expr.Call):
        callee = self.evaluate(expr.callee)
        arguments = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))
        if not isinstance(callee, JSCallable):
            raise RuntimeErrorException(expr.paren, "Can only call functions and classes.")

        if len(arguments) != callee.arity():
            raise RuntimeErrorException(expr.paren, f"Expected {callee.arity()} arguments but got {len(arguments)}.")
        if isinstance(callee, JSClass) and not expr.has_new_keyword:
            raise RuntimeErrorException(expr.paren, "Cannot call a class like a function. Use 'new' keyword to initialize new instance.")
        return callee.call(self, arguments)

    def visit_get_expr(self, expr: Expr.Get):
        obj = self.evaluate(expr.object)
        if isinstance(obj, JSInstance):
            return obj.get(expr.name)
        raise RuntimeErrorException(expr.name, "Only instances have properties.")

    def visit_print_stmt(self, stmt: Stmt.Print):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))
        return None

    def visit_return_stmt(self, stmt: Stmt.Return):
        value = stmt.value
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        raise Return(value)

    def visit_var_stmt(self, stmt: Stmt.Var):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)
        return None

    def visit_while_stmt(self, stmt: Stmt.While):
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
        return None

    def look_up_variable(self, name: Token, expr: Expr.Expr):
        distance = self.locals.get(expr)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self._globals.get(name)

    def visit_variable_expr(self, expr: Expr.Variable):
        return self.look_up_variable(expr.name, expr)

    def visit_assign_expr(self, expr: Expr.Assign):
        value = self.evaluate(expr.value)
        distance = self.locals.get(expr)
        if distance is not None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self._globals.assign(expr.name, value)
        return value

    def visit_expression_stmt(self, stmt: Stmt.Expression):
        self.evaluate(stmt.expression)
        return None

    def visit_function_stmt(self, stmt: Stmt.Function):
        function = JSFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, function)
        return None

    def visit_if_stmt(self, stmt: Stmt.If):
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)
        return None

    def stringify(self, obj):
        if obj is None:
            return "null"
        if isinstance(obj, float):
            text = str(obj)
            if text.endswith(".0"):
                text = text[:-2]
            return text
        return str(obj)

    def interpret(self, statements: List[Stmt.Stmt]):
        try:
            for statement in statements:
                self.execute(statement)
        except RuntimeErrorException as e:
            from JavaScript import JavaScript
            JavaScript.runtime_error(e)
