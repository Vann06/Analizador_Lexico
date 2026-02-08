from dataclasses import dataclass
from typing import Set, Optional, Dict


#Definición de los nodos para el árbol de sintaxis.
#Este archivo define la estructura del árbol

@dataclass
class Node:
    # de construcción directa (nullable, firstpos, lastpos).
    nullable: Optional[bool] = None
    firstpos: Optional[Set[int]] = None
    lastpos: Optional[Set[int]] = None
    

@dataclass
class Leaf(Node):
    symbol: str = ''
    position: int = -1  # posicion unica para cada hoja


@dataclass
class Concat(Node):
    # left · right
    left: Node = None
    right: Node = None


@dataclass
class Union(Node):
    # left | right
    left: Node = None
    right: Node = None


@dataclass
class Star(Node):
    # child*  
    child: Node = None


