"""
Este archivo se encarga de tomar un árbol de sintaxis y dibujarlo en una imagen PNG usando Graphviz.

IMPORTANTE antes de correr este archivo:
 1) Instalar Graphviz en Windows 
   
 2) Instalar la librería de Python:
    - pip install graphviz
"""

from graphviz import Digraph

# Ndos que definí en syntax_tree
from syntax_tree import Leaf, Union, Concat, Star, Node

# Importo la función que construye el árbol grande para identificadores Java
from build_regex import build_java_identifier_tree_expanded


def render_graphviz(root: Node, out_base: str = "java_identifier_tree") -> None:

    dot = Digraph(format="png")

    # Unos ajustes visuales para que no se vea tan aplastado
    dot.attr(rankdir="TB", nodesep="0.2", ranksep="0.35")

    dot.attr("node", fontname="Helvetica", fontsize="10")
    dot.attr("edge", color="black")

    contador = {"i": 0}

    def nuevo_id() -> str:
        """Genera un id de nodo interno como n1, n2, n3, ..."""
        contador["i"] += 1
        return f"n{contador['i']}" 

    def recorrer(n: Node) -> str:
        """Recorre el árbol recursivamente y va creando los nodos
        y aristas en el objeto `dot`.

        Devuelvo el id (string) del nodo creado en Graphviz para poder
        conectar los hijos con el padre.
        """
        mi_id = nuevo_id()

        # Caso 1: hoja (Leaf) -> dibujo un rectangulito con el símbolo y la posición
        if isinstance(n, Leaf):
            etiqueta = f"{n.symbol}\\n({n.position})"
            dot.node(mi_id, etiqueta, shape="box", style="rounded")
            return mi_id

        # Caso 2: unión (|) -> nodo circular con el símbolo "|"
        if isinstance(n, Union):
            dot.node(mi_id, "|", shape="circle")
            hijo_izq = recorrer(n.left)
            hijo_der = recorrer(n.right)
            dot.edge(mi_id, hijo_izq)
            dot.edge(mi_id, hijo_der)
            return mi_id

        # Caso 3: concatenación (·) -> nodo circular con un punto medio
        if isinstance(n, Concat):
            dot.node(mi_id, "·", shape="circle")
            hijo_izq = recorrer(n.left)
            hijo_der = recorrer(n.right)
            dot.edge(mi_id, hijo_izq)
            dot.edge(mi_id, hijo_der)
            return mi_id

        # Caso 4: estrella (*) -> nodo circular con "*" y un solo hijo
        if isinstance(n, Star):
            dot.node(mi_id, "*", shape="circle")
            hijo = recorrer(n.child)
            dot.edge(mi_id, hijo)
            return mi_id

        # Por si acaso llega algo raro 
        dot.node(mi_id, "?", shape="circle")
        return mi_id

    recorrer(root)

    dot.render(out_base, cleanup=True)
    print(f"Se generaron los archivos: {out_base}.dot y {out_base}.png")


if __name__ == "__main__":
    arbol = build_java_identifier_tree_expanded()

    render_graphviz(arbol, "java_identifier_tree")
