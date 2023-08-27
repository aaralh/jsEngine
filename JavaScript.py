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
        JavaScript.has_errpr = True

    def read_file(self, path: str) -> str:
        with open(path, "r") as f:
            return f.read()

    def run(self, source: str) -> None:
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        for token in tokens:
            print(token)

    def run_file(self, path: str) -> None:
        file = self.read_file(path)
        self.run(file)
        if self.had_error:
            sys.exit(65)

    def run_prompt(self) -> None:
        while True:
            line = input("> ")
            if line == "exit()":
                break
            self.run(line)
            self.had_error = False


if __name__ == "__main__":
    args = sys.argv
    js_engine = JavaScript()
    if len(args) > 1:
        sys.exit(64)
    elif len(args) == 1:
        js_engine.run_file(args[0])
    else:
        js_engine.run_prompt()
