from token import Token
from token_type import TokenType
from tabla_simbolos import SymbolTable

# palabras reservadas para que el lexer las reconozca 
KEYWORDS = {
    "public","class","static","final","private","String","double","int","void",
    "return","if","else","new","this"
}
# separadores
DELIMITERS = set("{}()[];,.")
# operadores
OPERATORS = set("=+-*/<>!")

class Lexer:
    def __init__(self, text: str):
        # texto fuente 
        self.text = text
        self.n = len(text)
        # posición actual en el texto 
        self.i = 0
        #controlar ubicación 
        self.line = 1
        self.col = 1
        # tabla de símbolos
        self.symtab = SymbolTable()

    def peek(self, k=0):
        """
        Obervar el caracter actual SIN consumirlo 
        ver y revisar el actual y el siguiente 
        si se pasa k, mira k posiciones adelante
        """
        j = self.i + k
        return self.text[j] if j < self.n else "\0"

    def advance(self):
        """
        Avanza una posición 
        - Devuelve el caracter consumido 
        - incrementa i 
        - actualiza línea y columna
        """
        ch = self.peek()
        if ch == "\0":
            return ch
        self.i += 1
        # si hay salto, sube linea y reinicia columna
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def skip_whitespace(self):
        """
        Omite espacios en blanco, tabulaciones y saltos de línea
        """
        while self.peek() in (" ", "\t", "\r", "\n"):
            self.advance()

    def scan_identifier_or_keyword(self):
        """
        Lee un identificador o palabra reservada
        - Devuelve un token de tipo IDENTIFIER o KEYWORD
        luego decide si es palabra reservada o identificador
        """
        line0, col0 = self.line, self.col
        lex = ""
        while True:
            ch = self.peek()
            if ch.isalnum() or ch in ("_", "$"):
                lex += self.advance()
            else:
                break

        if lex in KEYWORDS:
            return Token(TokenType.KEYWORD, lex, line0, col0)

        sym_id = self.symtab.get_or_insert(lex, "IDENTIFIER", line0)
        return Token(TokenType.IDENTIFIER, lex, line0, col0, attr=f"symId={sym_id}")

    def scan_symbol(self):
        line0, col0 = self.line, self.col
        ch = self.peek()

        if ch in DELIMITERS:
            return Token(TokenType.DELIMITER, self.advance(), line0, col0)

        if ch in OPERATORS:
            return Token(TokenType.OPERATOR, self.advance(), line0, col0)

        # si no reconocemos el caracter
        bad = self.advance()
        return Token(TokenType.ERROR, bad, line0, col0, attr="invalid_char")

    def tokenize(self):
        tokens = []
        while True:
            self.skip_whitespace()

            if self.peek() == "\0":
                tokens.append(Token(TokenType.EOF, "", self.line, self.col))
                break

            ch = self.peek()
            if ch.isalpha() or ch in ("_", "$"):
                tokens.append(self.scan_identifier_or_keyword())
            else:
                tokens.append(self.scan_symbol())

        return tokens
