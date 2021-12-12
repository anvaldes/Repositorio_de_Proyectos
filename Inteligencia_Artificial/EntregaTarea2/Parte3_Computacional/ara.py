from binary_heap import BinaryHeap
from node import Node
import time

class Ara:

    def __init__(self, initial_state, heuristic, weight, maxima_cantidad):
        self.cost_path_found = 10000
        self.weight = weight
        self.expansions = 0
        self.generated = 0
        self.initial_state = initial_state
        self.heuristic = heuristic
        self.suboptimality = 0
        self.max_cantidad = maxima_cantidad
        self.start_time = time.process_time()
        self.open = BinaryHeap()
        self.expansions = 0
        initial_node = Node(self.initial_state)
        initial_node.g = 0
        initial_node.h = self.heuristic(self.initial_state)
        initial_node.key = self.fvalue(0, initial_node.h) # asignamos el valor f
        self.open.insert(initial_node)
        self.generated = {}
        self.generated[self.initial_state] = initial_node
        self.ultimo_nodo_optimo = 0

    def estimate_suboptimality(self):
        lista_costos = []
        for k in self.open:
            lista_costos.append(k.g + k.h)
        minimo = min(lista_costos)
        self.suboptimality  = round(self.cost_path_found/minimo,2)
        return self.suboptimality   # este método debe ser implementado en la parte 1

    def fvalue(self, g, h):
        return g + (self.weight+0.001)*h

    def proxima_iteracion(self):
        self.weight = self.estimate_suboptimality()
        for k in self.open:
            k.key = self.fvalue(k.g, k.h)
        self.open.reorder()

    def search(self):
        # para cada estado alguna vez generado, generated almacena
        # el Node que le corresponde
        while not self.open.is_empty() and self.expansions <= self.max_cantidad:
            n = self.open.extract()   # extrae n de la open
            if n.state.is_goal():
                self.end_time = time.process_time()
                self.cost_path_found = self.fvalue(n.g, n.h)
                self.proxima_iteracion()
                self.ultimo_nodo_optimo = n
                yield self.ultimo_nodo_optimo
            succ = n.state.successors()
            self.expansions += 1
            if self.expansions == self.max_cantidad:
                yield self.ultimo_nodo_optimo
            for child_state, action, cost in succ:
                child_node = self.generated.get(child_state)
                is_new = child_node is None  # es la primera vez que veo a child_state
                path_cost = n.g + cost  # costo del camino encontrado hasta child_state
                if is_new or path_cost < child_node.g:
                    # si vemos el estado child_state por primera vez o lo vemos por
                    # un mejor camino, entonces lo agregamos a open
                    if is_new:  # creamos el nodo de child_state
                        child_node = Node(child_state, n)
                        child_node.h = self.heuristic(child_state)
                        self.generated[child_state] = child_node
                    child_node.action = action
                    child_node.parent = n
                    child_node.g = path_cost
                    child_node.key = self.fvalue(child_node.g, child_node.h) # actualizamos el valor f de child_node
                    if child_node.g + child_node.h < self.cost_path_found:
                        self.open.insert(child_node) # inserta child_node a la open si no esta en la open
        self.end_time = time.process_time()      # en caso contrario, modifica la posicion de child_node en open
        return None

