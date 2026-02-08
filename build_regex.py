import string
from typing import List

from syntax_tree import Leaf, Union, Concat, Star, Node


def make_balanced_union(nodes: List[Node]) -> Node:
    """
    Esta función une una lista de nodos usando el operador Union (|).
    Lo hago de forma "balanceada" para que el árbol no quede como
    una cadena súper larga a la derecha, sino más parejito.
    
    La idea es ir tomando de 2 en 2:
      [n1, n2, n3, n4] -> [Union(n1, n2), Union(n3, n4)] -> [Union( Union(n1,n2), Union(n3,n4) )]
    """
    # Copio la lista para no modificar la original por accidente
    nodes = nodes[:]

    # Si solo hay un nodo, ya está, no hay nada que unir
    if not nodes:
        raise ValueError("La lista de nodos para la unión no puede estar vacía")

    while len(nodes) > 1:
        siguiente = []
        # Recorro de 2 en 2
        for i in range(0, len(nodes), 2):
            if i + 1 < len(nodes):
                # Uno el par nodes[i] | nodes[i+1]
                siguiente.append(Union(left=nodes[i], right=nodes[i + 1]))
            else:
                # Si queda un nodo solito al final, pasa
                siguiente.append(nodes[i])
        nodes = siguiente

    return nodes[0]


def build_java_identifier_tree_expanded() -> Node:
    """ 
    Construyo el árbol de sintaxis para el regex de identificadores para Java:

      [A-Za-z_][A-Za-z0-9_]*

    cada hoja tiene una posición única.
    llevo un contador "pos" que voy aumentando cada vez
    que creo una hoja nueva.
    """
    # Este contador lo uso para asignar la posición a cada hoja
    pos = 1

    # Primer carácter: letras (mayúsculas y minúsculas) + "_"
    first_chars = list(string.ascii_uppercase + string.ascii_lowercase + "_")
    first_leaves: List[Leaf] = []

    for c in first_chars:
        # Creo una hoja por cada carácter posible de X
        hoja = Leaf(symbol=c, position=pos)
        first_leaves.append(hoja)
        pos += 1  # actualizo la posición para la siguiente hoja

    # Construyo X como una gran unión balanceada de todas las hojas first_leaves
    X = make_balanced_union(first_leaves)

    # Resto de caracteres: letras + "_" + dígitos 0-9
    rest_chars = list(string.ascii_uppercase + string.ascii_lowercase + "_" + string.digits)
    rest_leaves: List[Leaf] = []

    for c in rest_chars:
        hoja = Leaf(symbol=c, position=pos)
        rest_leaves.append(hoja)
        pos += 1

    # Construyo Y como otra unión balanceada
    Y = make_balanced_union(rest_leaves)

    end = Leaf(symbol="#", position=pos)
    pos += 1  # por si luego quisiera seguir creando hojas

    raiz = Concat(
        left=Concat(left=X, right=Star(child=Y)),
        right=end,
    )

    return raiz


# Pequeña prueba rápida si ejecuto este archivo directamente
if __name__ == "__main__":
    arbol = build_java_identifier_tree_expanded()
    # No hago nada más aquí para no mezclar con Graphviz.
    # El dibujo bonito lo voy a hacer en render_tree.py.
    print("Árbol para identificadores Java (expandido) construido correctamente.")
