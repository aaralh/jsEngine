import unittest
import Expr
from Parser import Parser
from Token import Token, TokenType

class TestParser(unittest.TestCase):

    def test_parser_primary(self):
        tokens = [Token(TokenType.FALSE, "false", None, 1)]
        parser = Parser(tokens)
        expr = parser.primary()
        self.assertIsInstance(expr, Expr.Literal)
        self.assertEqual(expr.value, False)

    def test_parser_match(self):
        tokens = [Token(TokenType.VAR, "var", None, 1)]
        parser = Parser(tokens)
        self.assertTrue(parser.match(TokenType.VAR))

    def test_parser_check(self):
        tokens = [Token(TokenType.VAR, "var", None, 1)]
        parser = Parser(tokens)
        self.assertTrue(parser.check(TokenType.VAR))

    def test_parser_is_at_end(self):
        tokens = [Token(TokenType.EOF, "", None, 1)]
        parser = Parser(tokens)
        self.assertTrue(parser.is_at_end())

    def test_parser_peek(self):
        tokens = [Token(TokenType.VAR, "var", None, 1)]
        parser = Parser(tokens)
        self.assertEqual(parser.peek().type, TokenType.VAR)

    def test_parser_advance(self):
        tokens = [Token(TokenType.VAR, "var", None, 1)]
        parser = Parser(tokens)
        self.assertEqual(parser.advance().type, TokenType.VAR)

    def test_parser_previous(self):
        tokens = [Token(TokenType.VAR, "var", None, 1)]
        parser = Parser(tokens)
        self.assertEqual(parser.previous().type, TokenType.VAR)

    def test_parser_expression(self):
        tokens = [Token(TokenType.NUMBER, "1", 1, 1), Token(TokenType.PLUS, "+", None, 1), Token(TokenType.NUMBER, "2", 2, 1)]
        parser = Parser(tokens)
        expr = parser.expression()
        self.assertIsInstance(expr, Expr.Binary)
        self.assertIsInstance(expr.left, Expr.Literal)
        self.assertIsInstance(expr.right, Expr.Literal)
        self.assertEqual(expr.operator.type, TokenType.PLUS)
        self.assertEqual(expr.left.value, 1)
        self.assertEqual(expr.right.value, 2)

    def test_parser_unary(self):
        tokens = [Token(TokenType.MINUS, "-", None, 1), Token(TokenType.NUMBER, "1", 1, 1)]
        parser = Parser(tokens)
        expr = parser.unary()
        self.assertIsInstance(expr, Expr.Unary)
        self.assertIsInstance(expr.right, Expr.Literal)
        self.assertEqual(expr.operator.type, TokenType.MINUS)
        self.assertEqual(expr.right.value, 1)

    def test_parser_multiplication(self):
        tokens = [Token(TokenType.NUMBER, "2", 2, 1), Token(TokenType.STAR, "*", None, 1), Token(TokenType.NUMBER, "3", 3, 1)]
        parser = Parser(tokens)
        expr = parser.factor()
        self.assertIsInstance(expr, Expr.Binary)
        self.assertIsInstance(expr.left, Expr.Literal)
        self.assertIsInstance(expr.right, Expr.Literal)
        self.assertEqual(expr.operator.type, TokenType.STAR)
        self.assertEqual(expr.left.value, 2)
        self.assertEqual(expr.right.value, 3)

    def test_parser_addition(self):
        tokens = [Token(TokenType.NUMBER, "2", 2, 1), Token(TokenType.PLUS, "+", None, 1), Token(TokenType.NUMBER, "3", 3, 1)]
        parser = Parser(tokens)
        expr = parser.term()
        self.assertIsInstance(expr, Expr.Binary)
        self.assertIsInstance(expr.left, Expr.Literal)
        self.assertIsInstance(expr.right, Expr.Literal)
        self.assertEqual(expr.operator.type, TokenType.PLUS)
        self.assertEqual(expr.left.value, 2)
        self.assertEqual(expr.right.value, 3)

    def test_parser_comparison(self):
        tokens = [Token(TokenType.NUMBER, "2", 2, 1), Token(TokenType.GREATER, ">", None, 1), Token(TokenType.NUMBER, "3", 3, 1)]
        parser = Parser(tokens)
        expr = parser.comparison()
        self.assertIsInstance(expr, Expr.Binary)
        self.assertIsInstance(expr.left, Expr.Literal)
        self.assertIsInstance(expr.right, Expr.Literal)
        self.assertEqual(expr.operator.type, TokenType.GREATER)
        self.assertEqual(expr.left.value, 2)
        self.assertEqual(expr.right.value, 3)