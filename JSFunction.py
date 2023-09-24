from JSCallable import JSCallable
import Stmt
from Environment import Environment
from Return import Return
from copy import deepcopy

class JSFunction(JSCallable):
    decalaration: Stmt.Function
    closure: Environment

    def __init__(self, declaration: Stmt.Function, closure: Environment):
        self.declaration = declaration
        self.closure = deepcopy(closure)

    def call(self, interpreter, arguments):
        environment = Environment(self.closure)
        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as returnValue:
            return returnValue.value

        return None

    def arity(self):
        return len(self.declaration.params)

    def __str__(self):
        return "function " + self.declaration.name.lexeme + f"({self.declaration.params}) {self.declaration.body}"
