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

    def test_scanner_is_at_end(self):
        scanner = Scanner("")
        self.assertTrue(scanner.is_at_end())

    def test_scanner_advance(self):
        scanner = Scanner("abc")
        self.assertEqual(scanner.advance(), "a")
        self.assertEqual(scanner.advance(), "b")
        self.assertEqual(scanner.advance(), "c")

    def test_scanner_add_token(self):
        scanner = Scanner("")
        scanner.add_token(TokenType.NUMBER, 123)
        self.assertEqual(len(scanner.tokens), 1)
        self.assertEqual(scanner.tokens[0].type, TokenType.NUMBER)
        self.assertEqual(scanner.tokens[0].literal, 123)

    def test_scanner_string(self):
        scanner = Scanner('"test";')
        scanner.scan_token()
        self.assertEqual(len(scanner.tokens), 1)
        self.assertEqual(scanner.tokens[0].type, TokenType.STRING)
        self.assertEqual(scanner.tokens[0].literal, "test")

    def test_scanner_identifier(self):
        scanner = Scanner("abc")
        scanner.identifier()
        self.assertEqual(len(scanner.tokens), 1)
        self.assertEqual(scanner.tokens[0].type, TokenType.IDENTIFIER)
        self.assertEqual(scanner.tokens[0].lexeme, "abc")

    def test_scanner_number(self):
        scanner = Scanner("123")
        scanner.number()
        self.assertEqual(len(scanner.tokens), 1)
        self.assertEqual(scanner.tokens[0].type, TokenType.NUMBER)
        self.assertEqual(scanner.tokens[0].literal, 123)

    def test_scanner_comment(self):
        scanner = Scanner("// This is a comment\nvar x = 5;")
        scanner.scan_tokens()
        self.assertEqual(len(scanner.tokens), 6)
        self.assertEqual(scanner.tokens[0].type, TokenType.VAR)
        self.assertEqual(scanner.tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(scanner.tokens[2].type, TokenType.EQUAL)
        self.assertEqual(scanner.tokens[3].type, TokenType.NUMBER)
        self.assertEqual(scanner.tokens[4].type, TokenType.SEMICOLON)
        self.assertEqual(scanner.tokens[5].type, TokenType.EOF)

    def test_scanner_keywords(self):
        scanner = Scanner("if else true false null")
        scanner.scan_tokens()
        self.assertEqual(len(scanner.tokens), 6)
        self.assertEqual(scanner.tokens[0].type, TokenType.IF)
        self.assertEqual(scanner.tokens[1].type, TokenType.ELSE)
        self.assertEqual(scanner.tokens[2].type, TokenType.TRUE)
        self.assertEqual(scanner.tokens[3].type, TokenType.FALSE)
        self.assertEqual(scanner.tokens[4].type, TokenType.NULL)
        self.assertEqual(scanner.tokens[5].type, TokenType.EOF)

    def test_scanner_punctuation(self):
        scanner = Scanner("(){};,.")
        scanner.scan_tokens()
        self.assertEqual(len(scanner.tokens), 8)
        self.assertEqual(scanner.tokens[0].type, TokenType.LEFT_PAREN)
        self.assertEqual(scanner.tokens[1].type, TokenType.RIGHT_PAREN)
        self.assertEqual(scanner.tokens[2].type, TokenType.LEFT_BRACE)
        self.assertEqual(scanner.tokens[3].type, TokenType.RIGHT_BRACE)
        self.assertEqual(scanner.tokens[4].type, TokenType.SEMICOLON)
        self.assertEqual(scanner.tokens[5].type, TokenType.COMMA)
        self.assertEqual(scanner.tokens[6].type, TokenType.DOT)
        self.assertEqual(scanner.tokens[7].type, TokenType.EOF)

    def test_scanner_operators(self):
        scanner = Scanner("+-*/%")
        scanner.scan_tokens()
        self.assertEqual(len(scanner.tokens), 6)
        self.assertEqual(scanner.tokens[0].type, TokenType.PLUS)
        self.assertEqual(scanner.tokens[1].type, TokenType.MINUS)
        self.assertEqual(scanner.tokens[2].type, TokenType.STAR)
        self.assertEqual(scanner.tokens[3].type, TokenType.SLASH)
        self.assertEqual(scanner.tokens[4].type, TokenType.MODULO)
        self.assertEqual(scanner.tokens[5].type, TokenType.EOF)

    def test_scanner_comparison(self):
        scanner = Scanner("== != > >= < <=")
        scanner.scan_tokens()
        self.assertEqual(len(scanner.tokens), 7)
        self.assertEqual(scanner.tokens[0].type, TokenType.EQUAL_EQUAL)
        self.assertEqual(scanner.tokens[1].type, TokenType.BANG_EQUAL)
        self.assertEqual(scanner.tokens[2].type, TokenType.GREATER)
        self.assertEqual(scanner.tokens[3].type, TokenType.GREATER_EQUAL)
        self.assertEqual(scanner.tokens[4].type, TokenType.LESS)
        self.assertEqual(scanner.tokens[5].type, TokenType.LESS_EQUAL)
        self.assertEqual(scanner.tokens[6].type, TokenType.EOF)

    def test_scanner_empty(self):
        scanner = Scanner("")
        scanner.scan_tokens()
        self.assertEqual(len(scanner.tokens), 1)
        self.assertEqual(scanner.tokens[0].type, TokenType.EOF)

    def test_scanner_whitespace(self):
        scanner = Scanner("  \t\n  ")
        scanner.scan_tokens()
        self.assertEqual(len(scanner.tokens), 1)
        self.assertEqual(scanner.tokens[0].type, TokenType.EOF)

    def test_scanner_identifier_with_keywords(self):
        scanner = Scanner("if abc else")
        scanner.scan_tokens()
        self.assertEqual(len(scanner.tokens), 4)
        self.assertEqual(scanner.tokens[0].type, TokenType.IF)
        self.assertEqual(scanner.tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(scanner.tokens[1].lexeme, "abc")
        self.assertEqual(scanner.tokens[2].type, TokenType.ELSE)
        self.assertEqual(scanner.tokens[3].type, TokenType.EOF)

    def test_scanner_number_with_decimal(self):
        scanner = Scanner("123.45")
        scanner.scan_tokens()
        self.assertEqual(len(scanner.tokens), 2)
        self.assertEqual(scanner.tokens[0].type, TokenType.NUMBER)
        self.assertEqual(scanner.tokens[0].literal, 123.45)
        self.assertEqual(scanner.tokens[1].type, TokenType.EOF)

    @unittest.skip("Not supported yet")
    def test_scanner_number_with_exponent(self):
        scanner = Scanner("1e2")
        scanner.scan_tokens()
        self.assertEqual(len(scanner.tokens), 1)
        self.assertEqual(scanner.tokens[0].type, TokenType.NUMBER)
        self.assertEqual(scanner.tokens[0].literal, 100.0)

    @unittest.skip("Not supported yet")
    def test_scanner_number_with_negative_exponent(self):
        scanner = Scanner("1e-2")
        scanner.scan_tokens()
        self.assertEqual(len(scanner.tokens), 1)
        self.assertEqual(scanner.tokens[0].type, TokenType.NUMBER)
        self.assertEqual(scanner.tokens[0].literal, 0.01)

    @unittest.skip("Not supported yet")
    def test_scanner_number_with_positive_exponent(self):
        scanner = Scanner("1e+2")
        scanner.scan_tokens()
        self.assertEqual(len(scanner.tokens), 1)
        self.assertEqual(scanner.tokens[0].type, TokenType.NUMBER)
        self.assertEqual(scanner.tokens[0].literal, 100.0)

    @unittest.skip("Not supported yet")
    def test_scanner_number_with_hexadecimal(self):
        scanner = Scanner("0x1a")
        scanner.scan_tokens()
        self.assertEqual(len(scanner.tokens), 1)
        self.assertEqual(scanner.tokens[0].type, TokenType.NUMBER)
        self.assertEqual(scanner.tokens[0].literal, 26)

    @unittest.skip("Not supported yet")
    def test_scanner_number_with_octal(self):
        scanner = Scanner("0o10")
        scanner.scan_tokens()
        self.assertEqual(len(scanner.tokens), 1)
        self.assertEqual(scanner.tokens[0].type, TokenType.NUMBER)
        self.assertEqual(scanner.tokens[0].literal, 8)

    @unittest.skip("Not supported yet")
    def test_scanner_number_with_binary(self):
        scanner = Scanner("0b1010")
        scanner.scan_tokens()
        self.assertEqual(len(scanner.tokens), 1)
        self.assertEqual(scanner.tokens[0].type, TokenType.NUMBER)
        self.assertEqual(scanner.tokens[0].literal, 10)

    def test_scanner_multiline_string(self):
        scanner = Scanner('"test\nstring"')
        scanner.scan_tokens()
        self.assertEqual(len(scanner.tokens), 2)
        self.assertEqual(scanner.tokens[0].type, TokenType.STRING)
        self.assertEqual(scanner.tokens[1].type, TokenType.EOF)
        self.assertEqual(scanner.tokens[0].literal, "test\nstring")