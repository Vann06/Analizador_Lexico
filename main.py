
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
regex completo para java
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

Para generar un AFD a partir de las expresiones regulares para 
identificadores, voy a utilizar un enfoque dividido en clases
L = [A-Za-z_]
A = [A-Za-z0-9_]
entonces simplificado queda como: L A*
y para su construccion correcta queda como L A* # 


"""