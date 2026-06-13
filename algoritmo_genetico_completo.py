import random
import copy

# ============================================================
# CROMOSOMA
# ============================================================
class Cromosoma:
    def __init__(self, distritos):
        self.distritos = distritos.copy()
        self.ruta = None
        self.fitness = 0
        self._generar_ruta_aleatoria()
    
    def _generar_ruta_aleatoria(self):
        self.ruta = self.distritos.copy()
        random.shuffle(self.ruta)
    
    def __str__(self):
        return " → ".join(self.ruta)
    
    def __repr__(self):
        return f"Cromosoma(ruta={self.ruta}, fitness={self.fitness:.6f})"


# ============================================================
# FITNESS
# ============================================================
class FuncionFitness:
    def __init__(self, prioridades, distancias, tiempos):
        self.prioridades = prioridades
        self.distancias = distancias
        self.tiempos = tiempos
    
    def evaluar(self, ruta):
        # Prioridad promedio (normalizada a 0-1)
        prioridad_total = sum(self.prioridades.get(d, 0) for d in ruta)
        P = (prioridad_total / len(ruta)) / 100.0
        
        # Distancia total
        D = 0
        for i in range(len(ruta) - 1):
            origen, destino = ruta[i], ruta[i + 1]
            dist = self.distancias.get((origen, destino))
            if dist is None:
                dist = self.distancias.get((destino, origen), 1.0)
            D += dist
        
        # Tiempo total
        T = 0
        for i in range(len(ruta) - 1):
            origen, destino = ruta[i], ruta[i + 1]
            tiempo = self.tiempos.get((origen, destino))
            if tiempo is None:
                tiempo = self.tiempos.get((destino, origen), 0.5)
            T += tiempo
        
        if D + T == 0:
            return 0
        return P / (D + T)


# ============================================================
# SELECCIÓN
# ============================================================
class Seleccion:
    @staticmethod
    def torneo(poblacion, fitness_values, k=3):
        if len(poblacion) < k:
            k = len(poblacion)
        indices = random.sample(range(len(poblacion)), k)
        mejor_indice = max(indices, key=lambda i: fitness_values[i])
        return poblacion[mejor_indice]
    
    @staticmethod
    def torneo_para_padres(poblacion, fitness_values, num_padres, k=3):
        padres = []
        for _ in range(num_padres):
            padre = Seleccion.torneo(poblacion, fitness_values, k)
            padres.append(padre)
        return padres


# ============================================================
# CRUCE
# ============================================================
class Cruce:
    @staticmethod
    def ordered_crossover(padre1, padre2):
        if len(padre1) != len(padre2):
            raise ValueError("Los padres deben tener la misma longitud")
        
        n = len(padre1)
        punto1 = random.randint(0, n - 1)
        punto2 = random.randint(punto1 + 1, n)
        
        hijo = [None] * n
        
        for i in range(punto1, punto2):
            hijo[i] = padre1[i]
        
        pos = punto2
        for gen in padre2:
            if gen not in hijo:
                if pos >= n:
                    pos = 0
                hijo[pos] = gen
                pos += 1
        
        return hijo


# ============================================================
# MUTACIÓN
# ============================================================
class Mutacion:
    @staticmethod
    def swap_mutation(ruta, prob_mutacion=0.1):
        if random.random() > prob_mutacion:
            return ruta
        
        ruta_mutada = ruta.copy()
        n = len(ruta_mutada)
        
        if n < 2:
            return ruta_mutada
        
        pos1 = random.randint(0, n - 1)
        pos2 = random.randint(0, n - 1)
        
        while pos1 == pos2:
            pos2 = random.randint(0, n - 1)
        
        ruta_mutada[pos1], ruta_mutada[pos2] = ruta_mutada[pos2], ruta_mutada[pos1]
        
        return ruta_mutada


# ============================================================
# ALGORITMO GENÉTICO PRINCIPAL
# ============================================================
class AlgoritmoGenetico:
    def __init__(self, distritos, prioridades, distancias, tiempos):
        self.distritos = distritos
        self.prioridades = prioridades
        self.distancias = distancias
        self.tiempos = tiempos
        
        self.fitness_func = FuncionFitness(prioridades, distancias, tiempos)
        self.poblacion = []
        self.mejor_solucion = None
        self.mejor_fitness = -1
        self.historial_fitness = []
    
    def inicializar_poblacion(self, tamano=50):
        self.poblacion = []
        for _ in range(tamano):
            c = Cromosoma(self.distritos)
            c.fitness = self.fitness_func.evaluar(c.ruta)
            self.poblacion.append(c)
        self._actualizar_mejor()
        print(f"✅ Población inicial: {len(self.poblacion)} individuos")
    
    def _actualizar_mejor(self):
        for c in self.poblacion:
            if c.fitness > self.mejor_fitness:
                self.mejor_fitness = c.fitness
                self.mejor_solucion = copy.deepcopy(c)
    
    def _evaluar_poblacion(self):
        for c in self.poblacion:
            c.fitness = self.fitness_func.evaluar(c.ruta)
        self._actualizar_mejor()
    
    def _seleccionar_padres(self, num_padres):
        fitness_values = [c.fitness for c in self.poblacion]
        return Seleccion.torneo_para_padres(self.poblacion, fitness_values, num_padres, k=3)
    
    def _mutar(self, cromosoma, prob_mutacion=0.1):
        ruta_mutada = Mutacion.swap_mutation(cromosoma.ruta, prob_mutacion)
        cromosoma.ruta = ruta_mutada
        return cromosoma
    
    def evolucionar(self, n_generaciones=100, tamano_poblacion=50, 
                    prob_cruce=0.8, prob_mutacion=0.1):
        
        print(f"\n🚀 Iniciando Algoritmo Genético")
        print(f"   Generaciones: {n_generaciones}")
        print(f"   Población: {tamano_poblacion}")
        print(f"   Prob. cruce: {prob_cruce}")
        print(f"   Prob. mutación: {prob_mutacion}")
        print("=" * 50)
        
        self.inicializar_poblacion(tamano_poblacion)
        self.historial_fitness.append(self.mejor_fitness)
        
        for generacion in range(n_generaciones):
            nueva_poblacion = []
            
            # Elitismo
            nueva_poblacion.append(copy.deepcopy(self.mejor_solucion))
            
            while len(nueva_poblacion) < tamano_poblacion:
                padres = self._seleccionar_padres(2)
                padre1, padre2 = padres[0], padres[1]
                
                if random.random() < prob_cruce:
                    hijo1_ruta = Cruce.ordered_crossover(padre1.ruta, padre2.ruta)
                    hijo2_ruta = Cruce.ordered_crossover(padre2.ruta, padre1.ruta)
                else:
                    hijo1_ruta = padre1.ruta.copy()
                    hijo2_ruta = padre2.ruta.copy()
                
                hijo1 = Cromosoma(self.distritos)
                hijo1.ruta = hijo1_ruta
                
                hijo2 = Cromosoma(self.distritos)
                hijo2.ruta = hijo2_ruta
                
                hijo1 = self._mutar(hijo1, prob_mutacion)
                hijo2 = self._mutar(hijo2, prob_mutacion)
                
                nueva_poblacion.append(hijo1)
                if len(nueva_poblacion) < tamano_poblacion:
                    nueva_poblacion.append(hijo2)
            
            self.poblacion = nueva_poblacion
            self._evaluar_poblacion()
            self.historial_fitness.append(self.mejor_fitness)
            
            if (generacion + 1) % 20 == 0:
                print(f"   Generación {generacion + 1}: Mejor fitness = {self.mejor_fitness:.6f}")
        
        print("=" * 50)
        print(f"✅ Evolución completada")
        print(f"   Mejor fitness: {self.mejor_fitness:.6f}")
        print(f"   Mejor ruta: {self.mejor_solucion}")
        
        return self.mejor_solucion


# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("ALGORITMO GENÉTICO - OPTIMIZACIÓN DE RUTAS")
    print("=" * 60)
    
    # Datos de ejemplo
    distritos = ['Centro', 'Max Paredes', 'Cotahuma', 'Sur', 'Periférica']
    
    prioridades = {
        'Centro': 85,
        'Max Paredes': 92,
        'Cotahuma': 70,
        'Sur': 55,
        'Periférica': 40
    }
    
    distancias = {
        ('Centro', 'Max Paredes'): 2.5,
        ('Centro', 'Cotahuma'): 3.0,
        ('Centro', 'Sur'): 4.0,
        ('Centro', 'Periférica'): 6.0,
        ('Max Paredes', 'Cotahuma'): 2.0,
        ('Max Paredes', 'Sur'): 3.5,
        ('Max Paredes', 'Periférica'): 5.0,
        ('Cotahuma', 'Sur'): 2.5,
        ('Cotahuma', 'Periférica'): 4.5,
        ('Sur', 'Periférica'): 3.0,
    }
    
    tiempos = {k: v / 20 for k, v in distancias.items()}
    
    # Crear y ejecutar AG
    ag = AlgoritmoGenetico(distritos, prioridades, distancias, tiempos)
    mejor_ruta = ag.evolucionar(n_generaciones=100, tamano_poblacion=30)
    
    print("\n" + "=" * 60)
    print("RESULTADO FINAL")
    print("=" * 60)
    print(f"Ruta óptima: {ag.mejor_solucion}")
    print(f"Fitness: {ag.mejor_fitness:.6f}")