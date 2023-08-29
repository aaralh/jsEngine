from Token import Token, TokenType, KEYWORDS

class Scanner():
    def __init__(self, source: str):
        self.source = source
        self.tokens = []
        self.start = 0
        #Current cursor position
        self.current = 0
        self.line = 1

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def advance(self) -> str:
        self.current += 1
        return self.source[self.current - 1]

    def add_token(self, token_type: TokenType, literal: object = None) -> None:
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))

    def match(self, expected: str) -> bool:
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def peek(self) -> str:
        if self.is_at_end():
            return "\0"
        return self.source[self.current]

    def report(self, line: int, where: str, message: str) -> None:
        print(f"[line {line}] Error{where}: {message}")

    def error(self, line: int, message: str) -> None:
        self.report(line, "", message)

    def error_token(self, message: str) -> None:
        from JavaScript import JavaScript
        JavaScript.error(self.line, message)

    def string(self) -> None:
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
            self.advance()
        if self.is_at_end():
            self.error_token("Unterminated string.")
            return
        self.advance()
        value = self.source[self.start + 1 : self.current - 1]
        self.add_token(TokenType.STRING, value)

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def number(self) -> None:
        while self.peek().isdigit():
            self.advance()
        if self.peek() == "." and self.peek_next().isdigit():
            self.advance()
            while self.peek().isdigit():
                self.advance()
        self.add_token(TokenType.NUMBER, float(self.source[self.start:self.current]))

    def identifier(self) -> None:
        while self.peek().isalnum():
            self.advance()
        text = self.source[self.start:self.current]
        token_type = TokenType.IDENTIFIER if text not in KEYWORDS else KEYWORDS[text]
        self.add_token(token_type)

    def scan_token(self) -> None:
        c = self.advance()
        if c == "(":
            self.add_token(TokenType.LEFT_PAREN)
        elif c == ")":
            self.add_token(TokenType.RIGHT_PAREN)
        elif c == "{":
            self.add_token(TokenType.LEFT_BRACE)
        elif c == "}":
            self.add_token(TokenType.RIGHT_BRACE)
        elif c == ",":
            self.add_token(TokenType.COMMA)
        elif c == ".":
            self.add_token(TokenType.DOT)
        elif c == "-":
            self.add_token(TokenType.MINUS)
        elif c == "+":
            self.add_token(TokenType.PLUS)
        elif c == ";":
            self.add_token(TokenType.SEMICOLON)
        elif c == "*":
            self.add_token(TokenType.STAR)
        elif c == "!":
            self.add_token(TokenType.BANG_EQUAL if self.match("=") else TokenType.BANG)
        elif c == "=":
            self.add_token(TokenType.EQUAL_EQUAL if self.match("=") else TokenType.EQUAL)
        elif c == "<":
            self.add_token(TokenType.LESS_EQUAL if self.match("=") else TokenType.LESS)
        elif c == ">":
            self.add_token(TokenType.GREATER_EQUAL if self.match("=") else TokenType.GREATER)
        elif c == "/":
            if self.match("/"):
                while self.peek() != "\n" and not self.is_at_end():
                    self.advance()
            else:
                self.add_token(TokenType.SLASH)
        elif c in [" ", "\r", "\t"]:
            pass
        elif c == "\n":
            self.line += 1
        elif c == '"':
            self.string()
        elif c == "|":
            if self.match("|"):
                self.add_token(TokenType.OR)
        elif c == "&":
            if self.match("&"):
                self.add_token(TokenType.AND)
        else:
            if c.isdigit():
                self.number()
            elif c.isalpha():
                self.identifier()
            else:
                self.error(self.line, "Unexpected character.")

    def scan_tokens(self) -> list:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

