import unittest
from Parser import Parser
from Token import Token, TokenType
import Expr
import Stmt

class TestParser(unittest.TestCase):

    def test_parser_previous(self):
        tokens = [Token(TokenType.NUMBER, "1", 1, 1), Token(TokenType.NUMBER, "2", 2, 1), Token(TokenType.NUMBER, "3", 3, 1)]
        parser = Parser(tokens)
        parser.advance()
        self.assertEqual(parser.previous().literal, 1)

    def test_parser_advance(self):
        tokens = [Token(TokenType.NUMBER, "1", 1, 1), Token(TokenType.NUMBER, "2", 2, 1), Token(TokenType.NUMBER, "3", 3, 1)]
        parser = Parser(tokens)
        self.assertEqual(parser.advance().literal, 1)
        self.assertEqual(parser.advance().literal, 2)
        self.assertEqual(parser.advance().literal, 3)

    def test_parser_peek(self):
        tokens = [Token(TokenType.NUMBER, "1", 1, 1), Token(TokenType.NUMBER, "2", 2, 1), Token(TokenType.NUMBER, "3", 3, 1)]
        parser = Parser(tokens)
        self.assertEqual(parser.peek().literal, 1)
        parser.advance()
        self.assertEqual(parser.peek().literal, 2)
        parser.advance()
        self.assertEqual(parser.peek().literal, 3)

    def test_parser_is_at_end(self):
        tokens = [Token(TokenType.NUMBER, "1", 1, 1), Token(TokenType.NUMBER, "2", 2, 1), Token(TokenType.NUMBER, "3", 3, 1), Token(TokenType.SEMICOLON, ";", None, 1), Token(TokenType.EOF, "", None, 1)]
        parser = Parser(tokens)
        self.assertFalse(parser.is_at_end())
        parser.advance()
        self.assertFalse(parser.is_at_end())
        parser.advance()
        self.assertFalse(parser.is_at_end())
        parser.advance()
        self.assertFalse(parser.is_at_end())
        parser.advance()
        self.assertTrue(parser.is_at_end())

    def test_parser_check(self):
        tokens = [Token(TokenType.NUMBER, "1", 1, 1), Token(TokenType.NUMBER, "2", 2, 1), Token(TokenType.NUMBER, "3", 3, 1), Token(TokenType.SEMICOLON, ";", None, 1)]
        parser = Parser(tokens)
        self.assertTrue(parser.check(TokenType.NUMBER))
        parser.advance()
        self.assertTrue(parser.check(TokenType.NUMBER))
        parser.advance()
        self.assertTrue(parser.check(TokenType.NUMBER))
        parser.advance()
        self.assertFalse(parser.check(TokenType.NUMBER))

    def test_parser_match(self):
        tokens = [Token(TokenType.NUMBER, "1", 1, 1), Token(TokenType.NUMBER, "2", 2, 1), Token(TokenType.NUMBER, "3", 3, 1), Token(TokenType.SEMICOLON, ";", None, 1)]
        parser = Parser(tokens)
        self.assertTrue(parser.match(TokenType.NUMBER))
        self.assertTrue(parser.match(TokenType.NUMBER))
        self.assertTrue(parser.match(TokenType.NUMBER))
        self.assertFalse(parser.match(TokenType.NUMBER))

    def test_parser_primary(self):
        tokens = [Token(TokenType.FALSE, "false", None, 1), Token(TokenType.TRUE, "true", None, 1), Token(TokenType.NULL, "null", None, 1), Token(TokenType.NUMBER, "42", 42, 1), Token(TokenType.STRING, "hello", "hello", 1)]
        parser = Parser(tokens)
        self.assertIsInstance(parser.primary(), Expr.Literal)
        self.assertIsInstance(parser.primary(), Expr.Literal)
        self.assertIsInstance(parser.primary(), Expr.Literal)
        self.assertIsInstance(parser.primary(), Expr.Literal)
        self.assertIsInstance(parser.primary(), Expr.Literal)

    def test_parser_assignment(self):
        tokens = [Token(TokenType.IDENTIFIER, "x", None, 1), Token(TokenType.EQUAL, "=", None, 1), Token(TokenType.NUMBER, "42", 42, 1), Token(TokenType.SEMICOLON, ";", None, 1)]
        parser = Parser(tokens)
        stmt = parser.statement()
        print(stmt.__dict__)
        self.assertIsInstance(stmt, Stmt.Expression)
        self.assertIsInstance(stmt.expression, Expr.Assign)
        self.assertEqual(stmt.expression.name.lexeme, "x")
        self.assertIsInstance(stmt.expression.value, Expr.Literal)
        self.assertEqual(stmt.expression.value.value, 42)

    def test_parser_block(self):
        tokens = [Token(TokenType.LEFT_BRACE, "{", None, 1), Token(TokenType.NUMBER, "1", 1, 1), Token(TokenType.SEMICOLON, ";", None, 1), Token(TokenType.NUMBER, "2", 2, 1), Token(TokenType.SEMICOLON, ";", None, 1), Token(TokenType.RIGHT_BRACE, "}", None, 1)]
        parser = Parser(tokens)
        stmt = parser.statement()
        self.assertIsInstance(stmt, Stmt.Block)
        self.assertEqual(len(stmt.statements), 2)
        self.assertIsInstance(stmt.statements[0], Stmt.Expression)
        self.assertIsInstance(stmt.statements[0].expression, Expr.Literal)
        self.assertEqual(stmt.statements[0].expression.value, 1)
        self.assertIsInstance(stmt.statements[1], Stmt.Expression)
        self.assertIsInstance(stmt.statements[1].expression, Expr.Literal)
        self.assertEqual(stmt.statements[1].expression.value, 2)

    def test_parser_if_statement(self):
        tokens = [Token(TokenType.IF, "if", None, 1), Token(TokenType.LEFT_PAREN, "(", None, 1), Token(TokenType.TRUE, "true", True, 1), Token(TokenType.RIGHT_PAREN, ")", None, 1), Token(TokenType.NUMBER, "1", 1, 1), Token(TokenType.SEMICOLON, ";", None, 1), Token(TokenType.ELSE, "else", None, 1), Token(TokenType.NUMBER, "2", 2, 1), Token(TokenType.SEMICOLON, ";", None, 1)]
        parser = Parser(tokens)
        stmt = parser.statement()
        self.assertIsInstance(stmt, Stmt.If)
        self.assertIsInstance(stmt.condition, Expr.Literal)
        self.assertEqual(stmt.condition.value, True)
        self.assertIsInstance(stmt.then_branch, Stmt.Expression)
        self.assertIsInstance(stmt.then_branch.expression, Expr.Literal)
        self.assertEqual(stmt.then_branch.expression.value, 1)
        self.assertIsInstance(stmt.else_branch, Stmt.Expression)
        self.assertIsInstance(stmt.else_branch.expression, Expr.Literal)
        self.assertEqual(stmt.else_branch.expression.value, 2)

    def test_parser_while_statement(self):
        tokens = [Token(TokenType.WHILE, "while", None, 1), Token(TokenType.LEFT_PAREN, "(", None, 1), Token(TokenType.TRUE, "true", True, 1), Token(TokenType.RIGHT_PAREN, ")", None, 1), Token(TokenType.NUMBER, "1", 1, 1), Token(TokenType.SEMICOLON, ";", None, 1)]
        parser = Parser(tokens)
        stmt = parser.statement()
        self.assertIsInstance(stmt, Stmt.While)
        self.assertIsInstance(stmt.condition, Expr.Literal)
        self.assertEqual(stmt.condition.value, True)
        self.assertIsInstance(stmt.body, Stmt.Expression)
        self.assertIsInstance(stmt.body.expression, Expr.Literal)
        self.assertEqual(stmt.body.expression.value, 1)