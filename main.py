
from lexer import Lexer

with open("PotionBrewer.java", "r", encoding="utf-8") as f:
    code = f.read()

lx = Lexer(code)
tokens = lx.tokenize()

for t in tokens[:30]:  # imprime los primeros 30
    print(t)

lx.symtab.print_table()
