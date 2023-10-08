from JSCallable import JSCallable
import Stmt
from Environment import Environment
from Return import Return
from copy import deepcopy

class JSFunction(JSCallable):
    decalaration: Stmt.Function
    closure: Environment
    is_initializer: bool

    def __init__(self, declaration: Stmt.Function, closure: Environment, is_initializer: bool):
        self.declaration = declaration
        self.closure = deepcopy(closure)
        self.is_initializer = is_initializer

    def bind(self, js_instance):
        environment = Environment(self.closure)
        environment.define("this", js_instance)
        return JSFunction(self.declaration, environment, self.is_initializer)

    def call(self, interpreter, arguments):
        environment = Environment(self.closure)
        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as returnValue:
            if self.is_initializer:
                return self.closure.get_at(0, "this")

            return returnValue.value

        if self.is_initializer:
            return self.closure.get_at(0, "this")

        return None

    def arity(self):
        return len(self.declaration.params)

    def __str__(self):
        return "function " + self.declaration.name.lexeme + f"({self.declaration.params}) {self.declaration.body}"
