from token_type import TokenType  

class Token:
    def __init__(self, token_type: str, lexeme: str, line: int, column: int, attr=None):
        self.type = token_type
        self.lexeme = lexeme
        self.line = line
        self.column = column
        self.attr = attr

    def __repr__(self):
        base = f"{self.line}:{self.column} {self.type:10} {self.lexeme!r}"
        return base + (f" {self.attr}" if self.attr is not None else "")
