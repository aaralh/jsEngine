from Scanner import Scanner
from Token import Token, TokenType
import unittest

class TestScanner(unittest.TestCase):
    def test_scan(self):
        scanner = Scanner("var a = 1;")
        tokens = scanner.scan_tokens()
        lexemes = [token.lexeme for token in tokens]
        self.assertEqual(lexemes, [
            Token(TokenType.VAR, "var", None, 1).lexeme,
            Token(TokenType.IDENTIFIER, "a", None, 1).lexeme,
            Token(TokenType.EQUAL, "=", None, 1).lexeme,
            Token(TokenType.NUMBER, "1", 1, 1).lexeme,
            Token(TokenType.SEMICOLON, ";", None, 1).lexeme,
            Token(TokenType.EOF, "", None, 1).lexeme
        ])
