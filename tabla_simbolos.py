
# si el identifiacdor ya existe, devuelve mismo symID
# si e nuevo, inserta y asgina nuevo symID
class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.next_id = 1

    def get_or_insert(self, name: str, tipo: str = "IDENTIFIER", line: int = None) -> int:
        if name not in self.symbols:
            self.symbols[name] = {"id": self.next_id, "tipo": tipo, "lineas": set()}
            self.next_id += 1
        if line is not None:
            self.symbols[name]["lineas"].add(line)
        return self.symbols[name]["id"]
    
    def items(self):
        """Devuelve los items de la tabla de simbolos como (nombre, symID)"""
        return sorted(self.symbols.items(), key=lambda item: item[1]["id"])
            
    def print_table(self):
        print("\n TABLA DE SIMBOLOS")
        print(f"{'ID':<5} | {'NOMBRE':<20} | {'TIPO':<15} | {'LINEAS'}")
        print("-" * 60)
        for name, data in self.items():
            lineas = ",".join(map(str, sorted(data["lineas"]))) if data["lineas"] else "-"
            print(f"{data['id']:<5} | {name:<20} | {data['tipo']:<15} | {lineas}")