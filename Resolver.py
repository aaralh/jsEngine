import Stmt
import Expr
from typing import List
from Token import Token
from RuntimeErrorException import RuntimeErrorException
from enum import Enum, auto


class FunctionType(Enum):
    NONE = auto()
    FUNCTION = auto()
    METHOD = auto()
    CONSTRUCTOR = auto()

class ClassType(Enum):
    NONE = auto()
    CLASS = auto()
    SUBCLASS = auto()


class Resolver(Stmt.Visitor, Expr.Visitor):

    current_class = ClassType.NONE

    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.scopes = []
        self.current_function = FunctionType.NONE

    def resolve(self, statements: List[Stmt.Stmt]):
        for statement in statements:
            self.resolve_stmt(statement)

    def resolve_stmt(self, statement: Stmt.Stmt):
        statement.accept(self)

    def resolve_expr(self, expression: Expr.Expr):
        expression.accept(self)

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name: Token):
        if len(self.scopes) == 0:
            return

        scope = self.scopes[-1]
        if name.lexeme in scope:
            raise RuntimeErrorException(name, "Variable with this name already declared in this scope.")

        scope[name.lexeme] = False

    def define(self, name: Token):
        if len(self.scopes) == 0:
            return

        self.scopes[-1][name.lexeme] = True

    def resolve_local(self, expr: Expr.Expr, name: Token):
        for i in range(len(self.scopes) - 1, -1, -1):
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return

    def resolve_function(self, function: Stmt.Function, function_type: FunctionType):
        enclosing_function = self.current_function
        self.current_function = function_type

        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)

        self.resolve(function.body)
        self.end_scope()

        self.current_function = enclosing_function

    def visit_block_stmt(self, stmt):
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()

    def visit_class_stmt(self, stmt):
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS

        self.declare(stmt.name)
        self.define(stmt.name)

        if stmt.superclass is not None:
            self.current_class = ClassType.SUBCLASS
            if stmt.name.lexeme == stmt.superclass.name.lexeme:
                raise RuntimeErrorException(stmt.superclass.name, "A class cannot inherit from itself.")

            self.resolve([stmt.superclass])

        if stmt.superclass is not None:
            self.begin_scope()
            self.scopes[-1]["super"] = True

        self.begin_scope()
        self.scopes[-1]["this"] = True

        for method in stmt.methods:
            declaration = FunctionType.METHOD
            if method.name.lexeme == "constructor":
                declaration = FunctionType.CONSTRUCTOR
            self.resolve_function(method, declaration)

        self.end_scope()

        if stmt.superclass is not None:
            self.end_scope()

        self.current_class = enclosing_class

    def visit_var_stmt(self, stmt):
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve_expr(stmt.initializer)
        self.define(stmt.name)

    def visit_variable_expr(self, expr):
        if len(self.scopes) != 0:
            if self.scopes[-1].get(expr.name.lexeme) == False:
                raise RuntimeErrorException(expr.name, "Cannot read local variable in its own initializer.")
        self.resolve_local(expr, expr.name)

    def visit_assign_expr(self, expr):
        self.resolve_expr(expr.value)
        self.resolve_local(expr, expr.name)

    def visit_function_stmt(self, stmt):
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt, FunctionType.FUNCTION)

    def visit_expression_stmt(self, stmt):
        self.resolve_expr(stmt.expression)

    def visit_if_stmt(self, stmt):
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.then_branch)
        if stmt.else_branch is not None:
            self.resolve_stmt(stmt.else_branch)

    def visit_print_stmt(self, stmt):
        self.resolve_expr(stmt.expression)

    def visit_return_stmt(self, stmt):
        if self.current_function == FunctionType.NONE:
            raise RuntimeErrorException(stmt.keyword, "Cannot return from top-level code.")

        if stmt.value is not None:
            if self.current_function == FunctionType.CONSTRUCTOR:
                # TODO: Return always instance of class.
                raise RuntimeErrorException(stmt.keyword, "Cannot return a value from a constructor.")
            self.resolve_expr(stmt.value)

    def visit_while_stmt(self, stmt):
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.body)

    def visit_binary_expr(self, expr):
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def visit_call_expr(self, expr):
        self.resolve_expr(expr.callee)
        for argument in expr.arguments:
            self.resolve_expr(argument)

    def visit_get_expr(self, expr):
        self.resolve_expr(expr.object)

    def visit_grouping_expr(self, expr):
        self.resolve_expr(expr.expression)

    def visit_literal_expr(self, expr):
        pass

    def visit_logical_expr(self, expr):
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def visit_set_expr(self, expr):
        self.resolve_expr(expr.value)
        self.resolve_expr(expr.object)

    def visit_super_expr(self, expr):
        if self.current_class == ClassType.NONE:
            raise RuntimeErrorException(expr.keyword, "Cannot use 'super' outside of a class.")
        elif self.current_class != ClassType.SUBCLASS:
            raise RuntimeErrorException(expr.keyword, "Cannot use 'super' in a class with no superclass.")
        self.resolve_local(expr, expr.keyword)

    def visit_this_expr(self, expr):
        if self.current_class== ClassType.NONE:
            raise RuntimeErrorException(expr.keyword, "Cannot use 'this' outside of a class.")
        self.resolve_local(expr, expr.keyword)

    def visit_unary_expr(self, expr):
        self.resolve_expr(expr.right)

