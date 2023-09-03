from Token import Token
from typing import Any, Dict, Optional
from RuntimeErrorException import RuntimeErrorException


class Environment:
    values: Dict[str, Any] = {}
    enclosing: Optional["Environment"] = None

    def __init__(self, enclosing: Optional["Environment"] = None) -> None:
        self.enclosing = enclosing

    def define(self, name: str, value: Any) -> None:
        self.values[name] = value

    def get(self, name: Token) -> Any:
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise RuntimeErrorException(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return

        raise RuntimeErrorException(name, f"Undefined variable '{name.lexeme}'.")
