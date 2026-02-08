"""Construcción directa del AFD para identificadores Java.

En este archivo quiero conectar varias piezas:
  - El árbol de sintaxis EXPANDIDO del regex de identificadores
	(build_java_identifier_tree_expanded de build_regex.py).
  - Las funciones directas: nullable, firstpos, lastpos, followpos
	(de direct_functions.py).
  - La construcción del AFD usando conjuntos de posiciones.

La idea es que todo quede en modo "estoy aprendiendo":
imprimo cosas en consola y veo cómo se va armando todo.
"""

from dataclasses import dataclass
from typing import Dict, Set, List, Tuple, FrozenSet

from syntax_tree import Node, Leaf
from build_regex import build_java_identifier_tree_expanded
from direct_functions import nullable, firstpos, lastpos, compute_followpos


@dataclass
class DFA:
	"""Representa un AFD muy simple.

	- states: conjunto de estados (cada estado es un frozenset de posiciones).
	- alphabet: símbolos de entrada (a..z, A..Z, _, 0..9 en este caso).
	- start: estado inicial.
	- accepts: conjunto de estados de aceptación.
	- transitions: función de transición δ: (estado, símbolo) -> estado.
	"""

	states: Set[FrozenSet[int]]
	alphabet: Set[str]
	start: FrozenSet[int]
	accepts: Set[FrozenSet[int]]
	transitions: Dict[Tuple[FrozenSet[int], str], FrozenSet[int]]


def collect_leaves(node: Node, leaves: Dict[int, Leaf]) -> None:
	"""Llena el diccionario {posición: hoja} recorriendo el árbol.

	Esto me sirve para saber qué símbolo hay en cada posición.
	"""
	if isinstance(node, Leaf):
		leaves[node.position] = node
		return

	# Si no es hoja, asumo que tiene atributos left/right/child
	# según el tipo de nodo. Para no complicar, pruebo cada uno.
	child = getattr(node, "child", None)
	if child is not None:
		collect_leaves(child, leaves)

	left = getattr(node, "left", None)
	right = getattr(node, "right", None)
	if left is not None:
		collect_leaves(left, leaves)
	if right is not None:
		collect_leaves(right, leaves)


def build_dfa_from_tree(root: Node) -> DFA:
	"""Aplica la construcción directa para obtener el AFD.

	Pasos MUY resumidos:
	  1) Calcular followpos para todas las posiciones.
	  2) Usar firstpos(root) como estado inicial.
	  3) Cada estado del AFD es un conjunto de posiciones.
	  4) Transiciones: desde un estado S, con símbolo a,
		 voy al union de followpos(i) de todas las i en S
		 que tengan ese símbolo a.
	"""

	# 1) Recolecto todas las hojas para saber cuántas posiciones hay
	leaves: Dict[int, Leaf] = {}
	collect_leaves(root, leaves)

	# followpos[i] empieza como conjunto vacío
	followpos_dict: Dict[int, Set[int]] = {pos: set() for pos in leaves.keys()}

	# Llamo a la función que ya programé para llenar followpos_dict
	compute_followpos(root, followpos_dict)

	# ---- Impresión de tablas para el reporte ----
	print("\n==== Tabla de hojas (posición -> símbolo) ====")
	for pos in sorted(leaves.keys()):
		leaf = leaves[pos]
		print(f"pos {pos:3d} -> '{leaf.symbol}'")

	print("\n==== Valores globales de nullable / firstpos / lastpos para la raíz ====")
	print(f"nullable(root) = {nullable(root)}")
	print(f"firstpos(root) = {sorted(firstpos(root))}")
	print(f"lastpos(root)  = {sorted(lastpos(root))}")

	print("\n==== Tabla de followpos(i) para cada posición i ====")
	for pos in sorted(followpos_dict.keys()):
		print(f"followpos({pos}) = {sorted(followpos_dict[pos])}")

	# También necesito saber cuál posición es el símbolo # (fin de cadena)
	end_pos = None
	for pos, leaf in leaves.items():
		if leaf.symbol == "#":
			end_pos = pos
			break

	if end_pos is None:
		raise ValueError("No encontré la hoja con el símbolo # en el árbol")

	# El alfabeto son todos los símbolos de hojas excepto '#'
	alphabet: Set[str] = set(
		leaf.symbol for leaf in leaves.values() if leaf.symbol != "#"
	)

	# 2) Estado inicial = firstpos(root)
	start_set = frozenset(firstpos(root))

	# Voy construyendo los estados del AFD con una especie de BFS
	states: Set[FrozenSet[int]] = set()
	states.add(start_set)
	unmarked: List[FrozenSet[int]] = [start_set]
	transitions: Dict[Tuple[FrozenSet[int], str], FrozenSet[int]] = {}

	while unmarked:
		S = unmarked.pop(0)

		# Para cada símbolo del alfabeto veo a qué conjunto de posiciones voy
		for a in alphabet:
			# T será el nuevo estado destino con símbolo a
			T: Set[int] = set()
			for i in S:
				# Si en la posición i la hoja tiene símbolo a, agrego followpos(i)
				if leaves[i].symbol == a:
					T |= followpos_dict[i]

			T_frozen = frozenset(T)
			transitions[(S, a)] = T_frozen

			# Si es un nuevo estado, lo agrego a la lista para seguir procesando
			if T and T_frozen not in states:
				states.add(T_frozen)
				unmarked.append(T_frozen)

	# 3) Estados de aceptación: los que contienen la posición de #
	accepts: Set[FrozenSet[int]] = set()
	for S in states:
		if end_pos in S:
			accepts.add(S)

	return DFA(states=states, alphabet=alphabet, start=start_set,
			   accepts=accepts, transitions=transitions)


def simulate_dfa(dfa: DFA, word: str) -> None:
	"""Simula el AFD sobre una palabra y muestra el recorrido.

	Ojo: aquí estoy asumiendo que cada carácter de `word` es
	un símbolo del alfabeto (letra, dígito o '_').
	"""

	current = dfa.start
	print(f"Estado inicial: {sorted(current)}")

	for ch in word:
		print(f"\nLeyendo símbolo: '{ch}'")

		key = (current, ch)
		if key not in dfa.transitions:
			print("  No hay transición definida, voy a conjunto vacío {} (estado muerto)")
			current = frozenset()
		else:
			next_state = dfa.transitions[key]
			print(f"  De {sorted(current)} con '{ch}' voy a {sorted(next_state)}")
			current = next_state

	# Al final checo si el estado actual es de aceptación
	if current in dfa.accepts:
		print("\nResultado: la palabra ES un identificador válido (estado de aceptación).")
	else:
		print("\nResultado: la palabra NO es un identificador válido (no caí en estado de aceptación).")


if __name__ == "__main__":
	# 1) Construyo el árbol expandido del regex de identificadores Java
	root = build_java_identifier_tree_expanded()

	# 2) Construyo el AFD por construcción directa
	dfa = build_dfa_from_tree(root)

	print("Cantidad de estados del AFD:", len(dfa.states))
	print("Estados de aceptación (con posición de #):", [sorted(s) for s in dfa.accepts])

	# 3) Pruebo el AFD con un identificador que aparece en el código Java
	#    Por ejemplo: "PotionBrewer"
	print("\n=== Simulación con la palabra 'PotionBrewer' ===")
	simulate_dfa(dfa, "PotionBrewer")

	# Aquí ya tengo lo necesario para el reporte:
	# - El árbol sintáctico (PNG lo genero con render_tree.py).
	# - Las posiciones de las hojas (de build_regex/colección de hojas).
	# - followpos (se calculó dentro de build_dfa_from_tree).
	# - El AFD y una simulación paso a paso.

