from typing import Dict, Any, Optional
from JSFunction import JSFunction
from JSCallable import JSCallable
from Token import Token

class JSInstance:
    _class: "JSClass"
    fields: Dict[str, Any] = {}

    def __init__(self, cls: "JSClass"):
        self._class = cls

    def __str__(self):
        return self._class.name + " instance"

    def get(self, name: Token):
        # TODO: Change to return undefined if not found.
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method = self._class.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)

        raise RuntimeError(f"Undefined property '{name.lexeme}'.")

    def set(self, name: Token, value: Any):
        self.fields[name.lexeme] = value

class JSClass(JSCallable):
    name: str
    methods: Dict[str, JSFunction]

    def __init__(self, name: str, methods: Dict[str, JSFunction]):
        self.name = name
        self.methods = methods

    def __str__(self):
        return self.name

    def call(self, interpreter: Any, arguments: list) -> JSInstance:
        instance = JSInstance(self)
        initializer = self.find_method("constructor")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    def arity(self):
        initializer = self.find_method("constructor")
        if initializer is None:
            return 0
        return initializer.arity()

    def find_method(self, name: str) -> Optional[JSFunction]:
        if name in self.methods:
            return self.methods[name]

        return None

