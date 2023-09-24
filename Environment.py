from Token import Token
from typing import Any, Dict, Optional
from RuntimeErrorException import RuntimeErrorException


class Environment:

    def __init__(self, enclosing: Optional["Environment"] = None) -> None:
        self.enclosing = enclosing
        self.values: Dict[str, Any] = {}

    def define(self, name: str, value: Any) -> None:
        self.values[name] = value

    def get(self, name: Token) -> Any:
        if name.lexeme in self.values.keys():
            return self.values[name.lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise RuntimeErrorException(name, f"Undefined variable '{name.lexeme}'.")

    def ancestor(self, distance: int) -> "Environment":
        environment: "Environment" = self
        for i in range(distance):
            environment = environment.enclosing
        return environment

    def get_at(self, distance: int, name: str) -> Any:
        return self.ancestor(distance).values[name]

    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self.values.keys():
            self.values[name.lexeme] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return

        raise RuntimeErrorException(name, f"Undefined variable '{name.lexeme}'.")

    def assign_at(self, distance: int, name: Token, value: Any) -> None:
        self.ancestor(distance).values[name.lexeme] = value
