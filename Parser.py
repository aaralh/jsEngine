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

        return self.call()

    def finish_call(self, callee: Expr.Expr) -> Expr.Expr:
        arguments: List[Expr.Expr] = []

        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.expression())
            while self.match(TokenType.COMMA):
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguments.")
                arguments.append(self.expression())

        paren: Token = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")

        return Expr.Call(callee, paren, arguments)

    def call(self) -> Expr.Expr:
        expr: Expr.Expr = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            else:
                break

        return expr

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

    def return_statement(self) -> Stmt.Stmt:
        keyword: Token = self.previous()
        value: Optional[Expr.Expr] = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return Stmt.Return(keyword, value)

    def expression_statement(self) -> Stmt.Stmt:
        expr: Expr.Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Stmt.Expression(expr)

    def function(self, kind: str) -> Stmt.Stmt:
        name: Token = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters: List[Token] = []

        if not self.check(TokenType.RIGHT_PAREN):
            parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))
            while self.match(TokenType.COMMA):
                if len(parameters) >= 255:
                    self.error(self.peek(), "Can't have more than 255 parameters.")
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))

        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body: List[Stmt.Stmt] = self.block()
        return Stmt.Function(name, parameters, body)

    def assignment(self) -> Expr.Expr:
        expr: Expr.Expr = self.or_expr()

        if self.match(TokenType.EQUAL):
            equals: Token = self.previous()
            value: Expr.Expr = self.assignment()

            if isinstance(expr, Expr.Variable):
                name: Token = expr.name
                return Expr.Assign(name, value)

            self.error(equals, "Invalid assignment target.")

        return expr

    def or_expr(self) -> Expr.Expr:
        expr: Expr.Expr = self.and_expr()

        while self.match(TokenType.OR):
            operator: Token = self.previous()
            right: Expr.Expr = self.and_expr()
            expr = Expr.Logical(expr, operator, right)

        return expr

    def and_expr(self) -> Expr.Expr:
        expr: Expr.Expr = self.equality()

        while self.match(TokenType.AND):
            operator: Token = self.previous()
            right: Expr.Expr = self.equality()
            expr = Expr.Logical(expr, operator, right)

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
        if self.match(TokenType.FOR):
            return self.for_statement()

        if self.match(TokenType.IF):
            return self.if_statement()

        if self.match(TokenType.PRINT):
            return self.print_statement()

        if self.match(TokenType.RETURN):
            return self.return_statement()

        if self.match(TokenType.WHILE):
            return self.while_statement()

        if self.match(TokenType.LEFT_BRACE):
            return Stmt.Block(self.block())

        return self.expression_statement()

    def for_statement(self) -> Stmt.Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        if self.match(TokenType.SEMICOLON):
            initializer: Optional[Stmt.Stmt] = None
        elif self.match(TokenType.VAR):
            initializer: Stmt.Stmt = self.var_declaration()
        else:
            initializer: Stmt.Stmt = self.expression_statement()

        condition: Optional[Expr.Expr] = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment: Optional[Expr.Expr] = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        body: Stmt.Stmt = self.statement()

        if increment is not None:
            body = Stmt.Block([body, Stmt.Expression(increment)])

        if condition is None:
            condition = Expr.Literal(True)
        body = Stmt.While(condition, body)

        if initializer is not None:
            body = Stmt.Block([initializer, body])

        return body

    def if_statement(self) -> Stmt.Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition: Expr.Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        then_branch: Stmt.Stmt = self.statement()
        else_branch: Optional[Stmt.Stmt] = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()

        return Stmt.If(condition, then_branch, else_branch)

    def var_declaration(self) -> Stmt.Stmt:
        name: Token = self.consume(TokenType.IDENTIFIER, "Expect variable name.")

        initializer: Optional[Expr.Expr] = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Stmt.Var(name, initializer)

    def while_statement(self) -> Stmt.Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition: Expr.Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body: Stmt.Stmt = self.statement()

        return Stmt.While(condition, body)

    def declaration(self) -> Optional[Stmt.Stmt]:
        try:
            if self.match(TokenType.FUNCTION):
                return self.function("function")
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

            if self.peek().type in [TokenType.CLASS, TokenType.FUNCTION, TokenType.VAR, TokenType.FOR, TokenType.IF, TokenType.WHILE, TokenType.PRINT, TokenType.RETURN]:
                return

            self.advance()

    def parse(self) -> List[Stmt.Stmt]:
        statements: List[Stmt.Stmt] = []

        while not self.is_at_end():
            statement = self.declaration()
            if statement is None: continue
            statements.append(statement)

        return statements
