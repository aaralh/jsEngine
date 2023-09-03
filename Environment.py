from Token import Token
from typing import Any, Dict
from RuntimeErrorException import RuntimeErrorException


class Environment:
    values: Dict[str, Any] = {}

    def define(self, name: str, value: Any) -> None:
        self.values[name] = value

    def get(self, name: Token) -> Any:
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        raise RuntimeErrorException(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        raise RuntimeErrorException(name, f"Undefined variable '{name.lexeme}'.")
