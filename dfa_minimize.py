"""Minimización del AFD usando partición de estados.

Aquí no vuelvo a construir el AFD: solo recibo una descripción
del autómata y aplico el algoritmo de particiones para obtener
un AFD equivalente pero (en teoría) con menos estados.

La idea es seguir el esquema clásico:
  1) Partición inicial: F (finales) y N (no finales).
  2) Refinar los bloques según cómo se comportan las transiciones.
  3) Cada bloque final de la partición es un "nuevo" estado.
"""

from dataclasses import dataclass
from typing import Dict, Set, Tuple, FrozenSet, List

from dfa_build import DFA


@dataclass
class MinimizedDFA:
	"""AFD minimizado.

	new_states: bloques de estados originales (cada bloque es un frozenset
				de estados-originales, y cada estado-original es a su vez
				un frozenset de posiciones).
	start: bloque que contiene al estado inicial original.
	accepts: bloques que contienen al menos un estado final original.
	transitions: función de transición sobre bloques.
	alphabet: el mismo alfabeto del AFD original.
	"""

	new_states: Set[FrozenSet[FrozenSet[int]]]
	alphabet: Set[str]
	start: FrozenSet[FrozenSet[int]]
	accepts: Set[FrozenSet[FrozenSet[int]]]
	transitions: Dict[Tuple[FrozenSet[FrozenSet[int]], str], FrozenSet[FrozenSet[int]]]


def minimize_dfa(dfa: DFA) -> MinimizedDFA:
	"""Aplica el algoritmo de partición de estados.

	Nota: aquí cada estado del dfa es un frozenset de posiciones.
	Yo voy a agrupar esos estados en bloques (también frozensets).
	"""

	# Si no hay estados, no hay mucho que hacer
	if not dfa.states:
		raise ValueError("El AFD no tiene estados")

	# Bloque de estados finales y bloque de no finales
	finals = set(dfa.accepts)
	non_finals = set(s for s in dfa.states if s not in finals)

	partition: List[Set[FrozenSet[int]]] = []
	if finals:
		partition.append(finals)
	if non_finals:
		partition.append(non_finals)

	# Función que me dice en qué bloque cae un estado
	def block_of(state: FrozenSet[int]) -> int:
		for idx, block in enumerate(partition):
			if state in block:
				return idx
		# No debería pasar
		return -1

	changed = True
	while changed:
		changed = False
		new_partition: List[Set[FrozenSet[int]]] = []

		for block in partition:
			# Voy a separar este bloque si encuentro estados que se
			# comportan diferente frente a algún símbolo del alfabeto.
			# Uso un diccionario: "firma" -> subconjunto de estados.
			signatures: Dict[Tuple[int, ...], Set[FrozenSet[int]]] = {}

			for state in block:
				# La "firma" de un estado es a qué bloques va con cada símbolo.
				sig_list = []
				for a in sorted(dfa.alphabet):
					dest = dfa.transitions.get((state, a), frozenset())
					sig_list.append(block_of(dest))
				signature = tuple(sig_list)

				if signature not in signatures:
					signatures[signature] = set()
				signatures[signature].add(state)

			# Si solo hay una firma, el bloque se queda igual.
			# Si hay varias, lo partimos en varios subbloques.
			for subset in signatures.values():
				new_partition.append(subset)

			if len(signatures) > 1:
				changed = True

		partition = new_partition

	# Ahora cada conjunto en partition es un nuevo estado del AFD minimizado
	new_states: Set[FrozenSet[FrozenSet[int]]] = set()
	for block in partition:
		new_states.add(frozenset(block))

	# Estado inicial minimizado: bloque que contiene al estado inicial original
	start_block = None
	for block in new_states:
		if dfa.start in block:
			start_block = block
			break

	if start_block is None:
		raise ValueError("No encontré el bloque que contiene al estado inicial")

	# Bloques de aceptación: los que intersectan con el conjunto de finales
	accept_blocks: Set[FrozenSet[FrozenSet[int]]] = set()
	for block in new_states:
		if any(s in dfa.accepts for s in block):
			accept_blocks.add(block)

	# Construyo la nueva función de transición sobre bloques
	new_transitions: Dict[Tuple[FrozenSet[FrozenSet[int]], str], FrozenSet[FrozenSet[int]]] = {}

	# Para cada bloque y cada símbolo veo a qué bloque voy
	for block in new_states:
		# Elijo un representante cualquiera del bloque, porque
		# todos los estados de ese bloque son equivalentes.
		rep = next(iter(block))
		for a in dfa.alphabet:
			dest = dfa.transitions.get((rep, a), frozenset())
			# Busco el bloque al que pertenece dest
			dest_block = None
			for b in new_states:
				if dest in b:
					dest_block = b
					break
			if dest_block is None:
				# Si dest no está en ningún bloque, lo ignoro (sería estado muerto vacío)
				continue
			new_transitions[(block, a)] = dest_block

	return MinimizedDFA(
		new_states=new_states,
		alphabet=set(dfa.alphabet),
		start=start_block,
		accepts=accept_blocks,
		transitions=new_transitions,
	)


if __name__ == "__main__":
	# Pequeña prueba: minimizo el AFD que construyo en dfa_build.
	from dfa_build import build_dfa_from_tree
	from build_regex import build_java_identifier_tree_expanded

	root = build_java_identifier_tree_expanded()
	dfa = build_dfa_from_tree(root)

	print("Estados originales:", len(dfa.states))
	min_dfa = minimize_dfa(dfa)
	print("Estados minimizados:", len(min_dfa.new_states))

	# Aquí, para el reporte, puedo explicar el proceso de partición:
	# - Partición inicial: F y N.
	# - Cómo se van refinando los bloques.
	# Y comparar el número de estados antes y después.

