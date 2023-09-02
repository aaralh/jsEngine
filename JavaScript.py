import sys
from Scanner import Scanner
from Token import Token, TokenType
from typing import cast, overload
from AstPrinter import AstPrinter
from Interpreter import Interpreter
from Parser import Parser
from RuntimeErrorException import RuntimeErrorException
from Expr import Expr

class JavaScript():

    had_error = False
    had_runtime_error = False
    interpreter = Interpreter()

    def __init__(self):
        print("this is the JS engine")

    @staticmethod
    def report(line: int, where: str, message: str) -> None:
        print(f"[line {line}] Error{where}: {message}")

    @staticmethod
    def error_with_token(token: Token, message: str) -> None:
        if token.type == TokenType.EOF:
            JavaScript.report(token.line, " at end", message)
        else:
            JavaScript.report(token.line, f" at '{token.lexeme}'", message)

    def runtime_error(self, error: RuntimeErrorException) -> None:
        print(f"{error.message}\n[line {error.token.line}]")
        JavaScript.had_runtime_error = True

    @staticmethod
    def error(line: int, message: str) -> None:
        JavaScript.report(line, "", message)
        JavaScript.had_error = True

    @staticmethod
    def read_file(path: str) -> str:
        with open(path, "r") as f:
            return f.read()

    @staticmethod
    def run(source: str) -> None:
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        parser = Parser(tokens)
        expression = parser.parse()

        if JavaScript.had_error :
            return

        expression = cast(Expr, expression)
        JavaScript.interpreter.interpret(expression)

    @staticmethod
    def run_file(path: str) -> None:
        file = JavaScript.read_file(path)
        JavaScript.run(file)
        if JavaScript.had_error:
            sys.exit(65)
        if JavaScript.had_runtime_error:
            sys.exit(70)

    @staticmethod
    def run_prompt() -> None:
        while True:
            line = input("> ")
            if line == "exit()":
                break
            JavaScript.run(line)
            JavaScript.had_error = False


if __name__ == "__main__":
    args = sys.argv
    if len(args) > 2:
        sys.exit(64)
    elif len(args) == 2:
        JavaScript.run_file(args[1])
    else:
        JavaScript.run_prompt()
