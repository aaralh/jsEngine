import sys
from Scanner import Scanner

class JavaScript():

    had_error = False

    def __init__(self):
        print("this is the JS engine")

    @staticmethod
    def report(line: int, where: str, message: str) -> None:
        print(f"[line {line}] Error{where}: {message}")

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
        for token in tokens:
            print(token)

    @staticmethod
    def run_file(path: str) -> None:
        file = JavaScript.read_file(path)
        JavaScript.run(file)
        if JavaScript.had_error:
            sys.exit(65)

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
