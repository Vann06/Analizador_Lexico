"""Dibujo de AFD (original y minimizado) usando Graphviz.

Aquí no calculo nada nuevo, solo recibo:
  - Un DFA normal (de dfa_build.DFA), o
  - Un MinimizedDFA (de dfa_minimize.MinimizedDFA),

"""

from graphviz import Digraph

from dfa_build import DFA
from dfa_minimize import MinimizedDFA


def render_dfa(dfa: DFA, out_base: str = "dfa_identifier") -> None:
    """Dibuja el AFD construido por construcción directa.

    - Cada estado se muestra como el conjunto de posiciones que lo forman.
    - Usa círculo doble para estados de aceptación.
    """

    dot = Digraph(format="png")
    dot.attr(rankdir="LR", nodesep="0.3", ranksep="0.4")
    dot.attr("node", shape="circle", fontname="Helvetica", fontsize="10")

    # Nodo fantasma para la flecha de inicio
    dot.node("__start__", label="", shape="none")

    # Creo un nombre corto para cada estado (S0, S1, ...)
    state_names = {}
    for idx, state in enumerate(sorted(dfa.states, key=lambda s: sorted(s))):
        name = f"S{idx}"
        state_names[state] = name
        label = f"{name}\n{sorted(state)}"
        shape = "doublecircle" if state in dfa.accepts else "circle"
        dot.node(name, label=label, shape=shape)

    # Flecha de inicio
    dot.edge("__start__", state_names[dfa.start])

    # Transiciones
    for (state, symbol), dest in dfa.transitions.items():
        src_name = state_names[state]
        dest_name = state_names.get(dest)
        if dest_name is None:
            # Si dest no está en el diccionario, es probablemente el estado vacío
            # que no agregamos explícitamente.
            continue
        dot.edge(src_name, dest_name, label=symbol)

    dot.render(out_base, cleanup=True)
    print(f"Se generaron los archivos: {out_base}.dot y {out_base}.png")


def render_minimized_dfa(min_dfa: MinimizedDFA, out_base: str = "dfa_identifier_min") -> None:
    """Dibuja el AFD minimizado.

    Cada nuevo estado es un bloque de estados originales.
    En la etiqueta muestro los estados-originales que incluye.
    """

    dot = Digraph(format="png")
    dot.attr(rankdir="LR", nodesep="0.3", ranksep="0.4")
    dot.attr("node", shape="circle", fontname="Helvetica", fontsize="10")

    dot.node("__start__", label="", shape="none")

    block_names = {}
    for idx, block in enumerate(sorted(min_dfa.new_states, key=lambda b: len(b))):
        name = f"Q{idx}"
        block_names[block] = name
        # En la etiqueta muestro los conjuntos de posiciones de cada estado original
        inner = [sorted(s) for s in block]
        label = f"{name}\n{inner}"
        shape = "doublecircle" if block in min_dfa.accepts else "circle"
        dot.node(name, label=label, shape=shape)

    dot.edge("__start__", block_names[min_dfa.start])

    for (block, symbol), dest_block in min_dfa.transitions.items():
        src_name = block_names[block]
        dest_name = block_names[dest_block]
        dot.edge(src_name, dest_name, label=symbol)

    dot.render(out_base, cleanup=True)
    print(f"Se generaron los archivos: {out_base}.dot y {out_base}.png")


if __name__ == "__main__":
    # Prueba rápida para generar ambas imágenes desde aquí.
    from build_regex import build_java_identifier_tree_expanded
    from dfa_build import build_dfa_from_tree
    from dfa_minimize import minimize_dfa

    root = build_java_identifier_tree_expanded()
    dfa = build_dfa_from_tree(root)

    print("\n[Dibujo del AFD original]")
    render_dfa(dfa, "dfa_identifier")

    print("\n[Dibujo del AFD minimizado]")
    min_dfa = minimize_dfa(dfa)
    render_minimized_dfa(min_dfa, "dfa_identifier_min")
