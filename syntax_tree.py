from dataclasses import dataclass
from typing import Set, Optional

@dataclass
class Node:
    nullable: Optional[bool] = None
    firstpos: Optional[Set[int]] = None
    lastpos: Optional[Set[int]] = None

@dataclass
class Leaf(Node):
    symbol: str = ''
    position: int = -1 # posicion unica para cada hoja

@dataclass
class Concat(Node):
    left: Node = None
    right: Node = None

@dataclass
class Union(Node):
    left: Node = None
    right: Node = None

@dataclass
class Star(Node):
    child: Node = None
