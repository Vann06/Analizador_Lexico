from token import Token
from token_type import TokenType
from tabla_simbolos import SymbolTable

# palabras reservadas para que el lexer las reconozca 
KEYWORDS = {
    "package","import","public","class","static","final","private","String","double","int","void",
    "return","if","else","new","this"
}
# separadores
DELIMITERS = set("{}()[];,.")
# operadores
OPERATORS = set("=+-*/<>!")
OPERATORS_2 = {"<=", ">=", "==", "!=", "&&", "||", "++", "--"}


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

    def scan_number(self):
        """
        Lee un literal numérico (INT o FLOAT).
        Regla simple:
        - dígitos obligatorios
        - si hay '.' solo cuenta como float si viene otro dígito después
        """
        line0, col0 = self.line, self.col
        lex = ""

        # parte entera
        while self.peek().isdigit():
            lex += self.advance()

        # parte decimal (float)
        if self.peek() == "." and self.peek(1).isdigit():
            lex += self.advance()  # consume '.'
            while self.peek().isdigit():
                lex += self.advance()
            return Token(TokenType.FLOAT_LIT, lex, line0, col0, attr=f"float={lex}")

        return Token(TokenType.INT_LIT, lex, line0, col0, attr=f"int={lex}")
    def scan_string(self):
        """
        Lee un STRING literal entre comillas dobles " ... "
        Si llega fin de línea o EOF sin cerrar, devuelve ERROR.
        """
        line0, col0 = self.line, self.col
        lex = ""

        # consumir comilla inicial
        lex += self.advance()  # "

        while True:
            ch = self.peek()

            if ch == "\0" or ch == "\n":
                # string sin cerrar
                return Token(TokenType.ERROR, lex, line0, col0, attr="unterminated_string")

            if ch == '"':
                lex += self.advance()  # consumir comilla final
                break

            # soporta escapes simples \" o \\ (opcional, pero útil)
            if ch == "\\" and self.peek(1) != "\0":
                lex += self.advance()
                lex += self.advance()
            else:
                lex += self.advance()

        return Token(TokenType.STRING_LIT, lex, line0, col0, attr=f"string={lex}")
    def scan_comment(self):
        """
        Maneja comentarios:
        - // hasta fin de línea
        - /* ... */ bloque
        """
        line0, col0 = self.line, self.col

        # Line comment //
        if self.peek() == "/" and self.peek(1) == "/":
            lex = self.advance() + self.advance()  # consume //
            while self.peek() not in ("\n", "\0"):
                lex += self.advance()
            return Token(TokenType.COMMENT, lex, line0, col0)

        # Block comment /* */
        if self.peek() == "/" and self.peek(1) == "*":
            lex = self.advance() + self.advance()  # consume /*
            while True:
                if self.peek() == "\0":
                    return Token(TokenType.ERROR, lex, line0, col0, attr="unterminated_comment")
                if self.peek() == "*" and self.peek(1) == "/":
                    lex += self.advance() + self.advance()  # consume */
                    break
                lex += self.advance()
            return Token(TokenType.COMMENT, lex, line0, col0)

        # Si no era comentario, error (no debería llamarse aquí)
        bad = self.advance()
        return Token(TokenType.ERROR, bad, line0, col0, attr="invalid_comment_start")

    def scan_symbol(self):
        """
        Manejo de delimitadores y operadores.
        IMPORTANTE: primero intenta operadores de 2 caracteres (<=, >=, ==, !=, etc.)
        """
        line0, col0 = self.line, self.col

        two = self.peek() + self.peek(1)
        if two in OPERATORS_2:
            self.advance()
            self.advance()
            return Token(TokenType.OPERATOR, two, line0, col0)

        ch = self.peek()

        if ch in DELIMITERS:
            return Token(TokenType.DELIMITER, self.advance(), line0, col0)

        if ch in OPERATORS:
            return Token(TokenType.OPERATOR, self.advance(), line0, col0)

        bad = self.advance()
        return Token(TokenType.ERROR, bad, line0, col0, attr="invalid_char")

    def tokenize(self):
        """
        Loop principal del lexer
        repite hasta el fin del archivo EOF
        salta whitespaces
        decide el tipo de token a escanear
        agrega el token a la lista
        """
        tokens = []
        while True:
            self.skip_whitespace()
            # verificación de fin de archivo EOF
            if self.peek() == "\0":
                tokens.append(Token(TokenType.EOF, "", self.line, self.col))
                break
            # que scaner utilizar 
            ch = self.peek()

            # comentarios
            if ch == "/" and self.peek(1) in ("/", "*"):
                self.scan_comment()
                continue

            # identificador o palabra reservada
            if ch.isalpha() or ch in ("_", "$"):
                tokens.append(self.scan_identifier_or_keyword())
            elif ch.isdigit():
                tokens.append(self.scan_number())
            elif ch == '"':
                tokens.append(self.scan_string())
            
            else:
                tokens.append(self.scan_symbol())

        return tokens
