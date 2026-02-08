"""Construcción directa del AFD para identificadores Java.

En este archivo quiero conectar varias piezas:
  - El árbol de sintaxis 
	(build_java_identifier_tree_expanded de build_regex.py).
  - Las funciones directas: nullable, firstpos, lastpos, followpos
	(de direct_functions.py).
  - La construcción del AFD usando conjuntos de posiciones.

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


def collect_nodes(root: Node) -> List[Node]:
	# Recolecta *todos* los nodos del árbol.

	visitados: Set[int] = set()
	nodos: List[Node] = []

	def _dfs(n: Node) -> None:
		if id(n) in visitados:
			return
		visitados.add(id(n))
		nodos.append(n)

		for attr in ("child", "left", "right"):
			child = getattr(n, attr, None)
			if child is not None:
				_dfs(child)

	_dfs(root)
	return nodos


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

	# ---- TABLA 1: todos los nodos con nullable / firstpos / lastpos ----
	print("\n============== TABLA DE NODOS (FUNCIONES DIRECTAS) ==============")
	print(f"{'Id':>3} | {'Tipo':^8} | {'Pos':^5} | {'Símbolo':^10} | {'nullable':^8} | {'firstpos':^12} | {'lastpos':^12}")
	print("-" * 80)

	nodos = collect_nodes(root)
	for idx, n in enumerate(nodos, start=1):
		# Tipo de nodo
		if isinstance(n, Leaf):
			tipo = "Leaf"
			pos_str = str(n.position)
			sym_str = n.symbol
		else:
			from syntax_tree import Concat, Union, Star
			if isinstance(n, Concat):
				tipo = "Concat"
			elif isinstance(n, Union):
				tipo = "Union"
			elif isinstance(n, Star):
				tipo = "Star"
			else:
				tipo = "Nodo?"
			pos_str = "-"
			sym_str = "-"

		nullable_n = nullable(n)
		first_n = sorted(firstpos(n))
		last_n = sorted(lastpos(n))

		print(f"{idx:3d} | {tipo:^8} | {pos_str:^5} | {sym_str:^10} | {str(nullable_n):^8} | {str(first_n):^12} | {str(last_n):^12}")

	print("\n========== RESUMEN PARA LA RAÍZ DEL ÁRBOL ==========")
	print(f"nullable(root)    = {nullable(root)}")
	print(f"firstpos(root)    = {sorted(firstpos(root))}")
	print(f"lastpos(root)     = {sorted(lastpos(root))}")

	# ---- TABLA 2: solo followpos(i), separada para que se lea mejor ----
	print("\nLeaf\tSymbol\tFollow Pos")
	for pos in sorted(followpos_dict.keys()):
		leaf = leaves[pos]
		follow = sorted(followpos_dict[pos])
		# Imprimo la lista como "54, 55, 56, ..." sin corchetes
		follow_str = ", ".join(str(i) for i in follow)
		print(f"{pos}\t{leaf.symbol}\t{follow_str}")

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

	# ---- TABLA 3: tabla de transición de estados del AFD ----
	print("\nTransitions Table")

	# Orden fijo del alfabeto para las columnas: A-Z, a-z, _, 0-9
	letters_upper = [chr(c) for c in range(ord('A'), ord('Z') + 1)]
	letters_lower = [chr(c) for c in range(ord('a'), ord('z') + 1)]
	digits = [str(d) for d in range(10)]
	ordered_alphabet = [
		*letters_upper,
		*letters_lower,
		'_',
		*digits,
	]

	# Filtro solo los símbolos que realmente están en el alfabeto del DFA
	ordered_alphabet = [a for a in ordered_alphabet if a in alphabet]

	print("States\t" + "\t".join(ordered_alphabet))

	# Asigno nombres S0, S1, ... a los estados, empezando por el inicial
	ordered_states = sorted(states, key=lambda s: (s != start_set, sorted(s)))
	state_names: Dict[FrozenSet[int], str] = {}
	for idx, st in enumerate(ordered_states):
		state_names[st] = f"S{idx}"

	for st in ordered_states:
		name = state_names[st]
		# Marco con * si es estado de aceptación
		name_prefixed = f"*{name}" if st in accepts else name
		row = [f"{name_prefixed} = {sorted(st)}"]
		for a in ordered_alphabet:
			dest = transitions.get((st, a), frozenset())
			row.append(state_names.get(dest, "-"))
		print("\t".join(row))

	return DFA(states=states, alphabet=alphabet, start=start_set,
			   accepts=accepts, transitions=transitions)


def simulate_dfa(dfa: DFA, word: str) -> None:

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
	print("\n=== Simulación con la palabra 'PotionBrewer' ===")
	simulate_dfa(dfa, "PotionBrewer")

