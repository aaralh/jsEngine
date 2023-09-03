from typing import List, Optional
from Token import Token, TokenType
import Expr
import Stmt

class Parser:

    class ParseError(Exception):
        pass

    tokens: List[Token] = []
    index: int = 0

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens

    def previous(self) -> Token:
        return self.tokens[self.index - 1]

    def advance(self) -> Token:
        if not self.is_at_end():
            self.index += 1

        return self.previous()

    def peek(self) -> Token:
        return self.tokens[self.index]

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def check(self, type: TokenType) -> bool:
        if self.is_at_end():
            return False

        return self.peek().type == type

    def match(self, *types: TokenType) -> bool:
        for type in types:
            if self.check(type):
                self.advance()
                return True

        return False

    def primary(self) -> Expr.Expr:
        if self.match(TokenType.FALSE):
            return Expr.Literal(False)
        if self.match(TokenType.TRUE):
            return Expr.Literal(True)
        if self.match(TokenType.NULL):
            return Expr.Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Expr.Literal(self.previous().literal)

        if (self.match(TokenType.IDENTIFIER)):
            return Expr.Variable(self.previous())

        if self.match(TokenType.LEFT_PAREN):
            expr: Expr.Expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Expr.Grouping(expr)

        raise self.error(self.peek(), "Expect expression.")

    def unary(self) -> Expr.Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator: Token = self.previous()
            right: Expr.Expr = self.unary()
            return Expr.Unary(operator, right)

        return self.primary()

    def factor(self) -> Expr.Expr:
        expr: Expr.Expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator: Token = self.previous()
            right: Expr.Expr = self.unary()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def term(self) -> Expr.Expr:
        expr: Expr.Expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator: Token = self.previous()
            right: Expr.Expr = self.factor()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def comparison(self) -> Expr.Expr:
        expr: Expr.Expr = self.term()

        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator: Token = self.previous()
            right: Expr.Expr = self.term()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def equality(self) -> Expr.Expr:
        expr: Expr.Expr = self.comparison()

        while self.match(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            operator: Token = self.previous()
            right: Expr.Expr = self.comparison()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def print_statement(self) -> Stmt.Stmt:
        value: Expr.Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Stmt.Print(value)

    def expression_statement(self) -> Stmt.Stmt:
        expr: Expr.Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Stmt.Expression(expr)

    def assignment(self) -> Expr.Expr:
        expr: Expr.Expr = self.equality()

        if self.match(TokenType.EQUAL):
            equals: Token = self.previous()
            value: Expr.Expr = self.assignment()

            if isinstance(expr, Expr.Variable):
                name: Token = expr.name
                return Expr.Assign(name, value)

            self.error(equals, "Invalid assignment target.")

        return expr

    def expression(self) -> Expr.Expr:
        return self.assignment()

    def block(self) -> List[Stmt.Stmt]:
        statements: List[Stmt.Stmt] = []

        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statement: Optional[Stmt.Stmt] = self.declaration()
            if statement is not None:
                statements.append(statement)

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def statement(self) -> Stmt.Stmt:
        if self.match(TokenType.PRINT):
            return self.print_statement()

        if self.match(TokenType.LEFT_BRACE):
            return Stmt.Block(self.block())

        return self.expression_statement()

    def var_declaration(self) -> Stmt.Stmt:
        name: Token = self.consume(TokenType.IDENTIFIER, "Expect variable name.")

        initializer: Optional[Expr.Expr] = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Stmt.Var(name, initializer)

    def declaration(self) -> Optional[Stmt.Stmt]:
        try:
            if self.match(TokenType.VAR):
                return self.var_declaration()

            return self.statement()
        except Parser.ParseError:
            self.synchronize()
            return None

    def error(self, token: Token, message: str) -> ParseError:
        from JavaScript import JavaScript
        JavaScript.error_with_token(token, message)
        return Parser.ParseError()

    def consume(self, type: TokenType, message: str) -> Token:
        if self.check(type):
            return self.advance()

        raise self.error(self.peek(), message)

    def synchronize(self) -> None:
        self.advance()

        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return

            if self.peek().type in [TokenType.CLASS, TokenType.FUN, TokenType.VAR, TokenType.FOR, TokenType.IF, TokenType.WHILE, TokenType.PRINT, TokenType.RETURN]:
                return

            self.advance()

    def parse(self) -> List[Stmt.Stmt]:
        statements: List[Stmt.Stmt] = []

        while not self.is_at_end():
            statement = self.declaration()
            if statement is None: continue
            statements.append(statement)

        return statements
