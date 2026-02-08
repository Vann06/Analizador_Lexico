
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

from build_regex import build_java_identifier_tree_expanded
from render_tree import render_graphviz
from dfa_build import build_dfa_from_tree, simulate_dfa
from dfa_minimize import minimize_dfa
from dfa_graphviz import render_dfa, render_minimized_dfa


def opcion_1_dibujar_arbol() -> None:
    root = build_java_identifier_tree_expanded()
    render_graphviz(root, "java_identifier_tree")
    print("\n[OK] Árbol dibujado en java_identifier_tree.png")


def opcion_2_construir_afd_y_simular() -> None:
    #Construye el AFD por construcción directa y lo prueba.

    root = build_java_identifier_tree_expanded()

    # Dentro de esta función ya se imprimen las tablas de hojas,
    # nullable/firstpos/lastpos y followpos.
    dfa = build_dfa_from_tree(root)

    print("\nCantidad de estados del AFD:", len(dfa.states))
    print("Estados de aceptación (con posición de #):", [sorted(s) for s in dfa.accepts])

    lexema = input("\nEscribe un identificador para simular (ENTER = PotionBrewer): ")
    if not lexema:
        lexema = "PotionBrewer"

    print(f"\n=== Simulación con la palabra '{lexema}' ===")
    simulate_dfa(dfa, lexema)


def opcion_3_minimizar_afd() -> None:
    #Minimiza el AFD usando el algoritmo de partición de estados.

    root = build_java_identifier_tree_expanded()
    dfa = build_dfa_from_tree(root)

    print("\nEstados originales:", len(dfa.states))
    min_dfa = minimize_dfa(dfa)
    print("Estados minimizados:", len(min_dfa.new_states))

    # Además dibujo ambos autómatas en PNG para el reporte
    print("\n[Generando imágenes del AFD original y minimizado...]")
    render_dfa(dfa, "dfa_identifier")
    render_minimized_dfa(min_dfa, "dfa_identifier_min")


def mostrar_menu() -> None:
    print("\n===== Menú Analizador Léxico =====")
    print("1) Dibujar árbol de sintaxis (Graphviz)")
    print("2) Construir AFD, mostrar tablas y simular identificador")
    print("3) Minimizar AFD")
    print("4) Salir")


if __name__ == "__main__":
    while True:
        mostrar_menu()
        opcion = input("\nElige una opción (1-4): ").strip()

        if opcion == "1":
            opcion_1_dibujar_arbol()
        elif opcion == "2":
            opcion_2_construir_afd_y_simular()
        elif opcion == "3":
            opcion_3_minimizar_afd()
        elif opcion == "4":
            print("\nSaliendo...")
            break
        else:
            print("\nOpción no válida, intenta de nuevo.")
