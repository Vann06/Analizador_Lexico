
"""
Elección de lexemas en el código:
Identificadores:
- System
- main
- args
- println
- PotionBrewer
- MUSHROOM_PRICE
    regex: [A-Za-z_]+
    
[A-Za-z_][A-Za-z0-9_]*


Literales numéricos:
- 5.50
- 3
- 0
- 100.0
- 2 
- 4
    regex: [0-9]+\.[0-9]+


Operadores / delimitadores
Operadores: =, +, -, *, <=, -=, ++
Delimitadores: { } ( ) [ ] ; , .
    regex: [=+\-*/<>!]+ | [\{\}\(\)\[\];,\.]

"""