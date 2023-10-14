from Scanner import Scanner
from Token import Token, TokenType
import unittest

class TestScanner(unittest.TestCase):
    def test_scanner(self):
        scanner = Scanner('var x = 5;')
        scanner.scan_tokens()
        assert len(scanner.tokens) == 6
        assert scanner.tokens[0].type == TokenType.VAR
        assert scanner.tokens[1].type == TokenType.IDENTIFIER
        assert scanner.tokens[2].type == TokenType.EQUAL
        assert scanner.tokens[3].type == TokenType.NUMBER
        assert scanner.tokens[4].type == TokenType.SEMICOLON
        assert scanner.tokens[5].type == TokenType.EOF

    def test_scanner_is_at_end(self):
        scanner = Scanner('')
        assert scanner.is_at_end() == True

    def test_scanner_advance(self):
        scanner = Scanner('var x = 5;')
        assert scanner.advance() == 'v'

    def test_scanner_add_token(self):
        scanner = Scanner('var x = 5;')
        scanner.add_token(TokenType.VAR)
        assert len(scanner.tokens) == 1
        assert scanner.tokens[0].type == TokenType.VAR

    def test_scanner_match(self):
        scanner = Scanner('var x = 5;')
        assert scanner.match('v') == True

    def test_scanner_peek(self):
        scanner = Scanner('var x = 5;')
        assert scanner.peek() == 'v'

    def test_scanner_report(self):
        scanner = Scanner('var x = 5;')
        assert scanner.report(1, "", "test") == None

    def test_scanner_error(self):
        scanner = Scanner('var x = 5;')
        assert scanner.error(1, "test") == None

    def test_scanner_error_token(self):
        scanner = Scanner('var x = 5;')
        assert scanner.error_token("test") == None

    def test_scanner_string(self):
        scanner = Scanner('"test"')
        scanner.string()
        assert scanner.line == 1