from syntax_tree import Leaf, Concat, Star, Union
from typing import Set, Dict

def nullable(node) -> bool:
    if isinstance(node, Leaf):
        return False
    if isinstance(node, Concat):
        return nullable(node.left) and nullable(node.right)
    if isinstance(node, Union):
        return nullable(node.left) or nullable(node.right)
    if isinstance(node, Star):
        return True
    raise TypeError("Nodo desconocido")


def firstpos(node) -> Set[int]:
    if isinstance(node, Leaf):
        return {node.position}

    if isinstance(node, Union):
        return firstpos(node.left) | firstpos(node.right)

    if isinstance(node, Concat):
        if nullable(node.left):
            return firstpos(node.left) | firstpos(node.right)
        return firstpos(node.left)

    if isinstance(node, Star):
        return firstpos(node.child)

    raise TypeError("Nodo desconocido")


def lastpos(node) -> Set[int]:
    if isinstance(node, Leaf):
        return {node.position}

    if isinstance(node, Union):
        return lastpos(node.left) | lastpos(node.right)

    if isinstance(node, Concat):
        if nullable(node.right):
            return lastpos(node.left) | lastpos(node.right)
        return lastpos(node.right)

    if isinstance(node, Star):
        return lastpos(node.child)

    raise TypeError("Nodo desconocido")


def compute_followpos(node, followpos_dict: Dict[int, Set[int]]):
    """
    Llena followpos_dict aplicando reglas:
    - Concat(A·B): para i en lastpos(A), followpos(i) += firstpos(B)
    - Star(A*): para i en lastpos(A), followpos(i) += firstpos(A)
    Recorre TODO el árbol (recursivo).
    """
    if isinstance(node, Concat):
        for i in lastpos(node.left):
            followpos_dict[i] |= firstpos(node.right)

        # IMPORTANTÍSIMO: seguir recorriendo
        compute_followpos(node.left, followpos_dict)
        compute_followpos(node.right, followpos_dict)
        return

    if isinstance(node, Star):
        for i in lastpos(node.child):
            followpos_dict[i] |= firstpos(node.child)

        compute_followpos(node.child, followpos_dict)
        return

    if isinstance(node, Union):
        compute_followpos(node.left, followpos_dict)
        compute_followpos(node.right, followpos_dict)
        return

    if isinstance(node, Leaf):
        return

    raise TypeError("Nodo desconocido")
