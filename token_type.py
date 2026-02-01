
# uso de strings por simplicidad y mas facil de depurar 
class TokenType:
    # Palabras reservadas y nombres
    IDENTIFIER = 'IDENTIFIER'
    KEYWORD = 'KEYWORD'

    # Literales
    INT_LIT = 'INT_LIT'
    FLOAT_LIT = 'FLOAT_LIT'
    STRING_LIT = 'STRING_LIT'

    # Símbolos
    OPERATOR = 'OPERATOR'
    DELIMITER = 'DELIMITER'

    # Otros
    EOF = 'EOF'
    COMMENT = 'COMMENT'
    ERROR = 'ERROR'