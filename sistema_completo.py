import pandas as pd
import numpy as np
import random
import copy
import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split

# ============================================================
# 1. GENERADOR DE DATOS
# ============================================================
class GeneradorDatos:
    def __init__(self):
        self.distritos = ['Centro', 'Max Paredes', 'Cotahuma', 'Sur', 'Periférica',
                          'Miraflores', 'Sopocachi', 'San Pedro', 'Villa Fátima', 'Zona Sur']
        self.dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        self.tipos_zona = ['Residencial', 'Comercial', 'Mixto', 'Industrial']
        self.climas = ['Soleado', 'Nublado', 'Lluvia', 'Tormenta']
        
        self.densidad = {d: 12000 - i*500 for i, d in enumerate(self.distritos)}
        self.actividad = {d: 95 - i*5 for i, d in enumerate(self.distritos)}
    
    def generar_datos(self, num_registros=500):
        data = []
        for i in range(num_registros):
            distrito = random.choice(self.distritos)
            dia = random.choice(self.dias_semana)
            mes = random.randint(1, 12)
            feria = 1 if random.random() < 0.15 else 0
            evento = 1 if random.random() < 0.08 else 0
            clima = random.choice(self.climas)
            tipo_zona = random.choice(self.tipos_zona)
            bloqueos = 1 if random.random() < 0.05 else 0
            transitabilidad = 1 if random.random() < 0.85 else 0
            
            # Calcular residuos
            base = 80
            if distrito == 'Centro': base = 120
            elif distrito == 'Max Paredes': base = 110
            elif distrito == 'Cotahuma': base = 90
            else: base = 70
            
            residuos = base
            if feria: residuos *= 1.4
            if evento: residuos *= 1.3
            if bloqueos: residuos *= 1.2
            if transitabilidad == 0: residuos *= 1.1
            if dia in ['Sábado', 'Domingo']: residuos *= 0.85
            if mes in [12, 1]: residuos *= 1.2
            
            residuos *= random.uniform(0.85, 1.15)
            residuos = max(30, round(residuos, 1))
            
            data.append([distrito, dia, mes, feria, evento, clima, tipo_zona, bloqueos, transitabilidad, residuos])
        
        return pd.DataFrame(data, columns=['distrito', 'dia_semana', 'mes', 'feria', 'evento', 'clima', 'tipo_zona', 'bloqueos', 'transitabilidad', 'residuos'])


# ============================================================
# 2. RED NEURONAL
# ============================================================
class RedNeuronal:
    def __init__(self):
        self.model = None
        self.scaler = MinMaxScaler()
        self.encoders = {}
    
    def preprocesar_entrenamiento(self, df):
        """Para datos de entrenamiento (TIENEN la columna 'residuos')"""
        df_proc = df.copy()
        
        # Normalizar mes
        df_proc['mes'] = self.scaler.fit_transform(df_proc[['mes']])
        
        # Codificar categóricas
        cat_cols = ['distrito', 'dia_semana', 'clima', 'tipo_zona']
        for col in cat_cols:
            self.encoders[col] = LabelEncoder()
            df_proc[col] = self.encoders[col].fit_transform(df_proc[col])
        
        # Variables binarias
        bin_cols = ['feria', 'evento', 'bloqueos', 'transitabilidad']
        for col in bin_cols:
            df_proc[col] = df_proc[col].astype(int)
        
        # Características (X)
        X = df_proc[['distrito', 'dia_semana', 'mes', 'feria', 'evento', 
                     'clima', 'tipo_zona', 'bloqueos', 'transitabilidad']].values
        
        # Etiquetas (y) - NORMALIZADAS a 0-1
        y = df_proc['residuos'].values / 300
        
        return X, y
    
    def preprocesar_prediccion(self, df):
        """Para datos de predicción (NO tienen la columna 'residuos')"""
        df_proc = df.copy()
        
        # Normalizar mes (usando el scaler ya entrenado)
        df_proc['mes'] = self.scaler.transform(df_proc[['mes']])
        
        # Codificar categóricas (usando los encoders ya entrenados)
        cat_cols = ['distrito', 'dia_semana', 'clima', 'tipo_zona']
        for col in cat_cols:
            df_proc[col] = self.encoders[col].transform(df_proc[col])
        
        # Variables binarias
        bin_cols = ['feria', 'evento', 'bloqueos', 'transitabilidad']
        for col in bin_cols:
            df_proc[col] = df_proc[col].astype(int)
        
        # Características (X)
        X = df_proc[['distrito', 'dia_semana', 'mes', 'feria', 'evento', 
                     'clima', 'tipo_zona', 'bloqueos', 'transitabilidad']].values
        
        return X
    
    def construir(self, input_dim=9):
        self.model = keras.Sequential([
            keras.layers.Input(shape=(input_dim,)),
            keras.layers.Dense(4, activation='relu', name='capa_agrupacion'),
            keras.layers.Dense(3, activation='relu', name='capa_profunda'),
            keras.layers.Dense(1, activation='linear', name='capa_salida')
        ])
        self.model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001), 
                          loss='mse', 
                          metrics=['mae'])
        print("✅ Red Neuronal construida")
        print(self.model.summary())
        return self.model
    
    def entrenar(self, X_train, y_train, X_val, y_val, epochs=50):
        early_stop = keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
        
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=32,
            verbose=0,
            callbacks=[early_stop]
        )
        print("✅ Entrenamiento completado")
        return self.history
    
    def predecir_iigr(self, X):
        """Predice el IIGR en porcentaje (0-100)"""
        pred = self.model.predict(X, verbose=0)
        return pred.flatten() * 100


# ============================================================
# 3. ALGORITMO GENÉTICO
# ============================================================
class AlgoritmoGenetico:
    def __init__(self, distritos, prioridades, distancias, tiempos):
        self.distritos = distritos
        self.prioridades = prioridades
        self.distancias = distancias
        self.tiempos = tiempos
        self.mejor_ruta = None
        self.mejor_fitness = 0
    
    def fitness(self, ruta):
        P = sum(self.prioridades.get(d, 0) for d in ruta) / len(ruta) / 100
        D = sum(self.distancias.get((ruta[i], ruta[i+1]), self.distancias.get((ruta[i+1], ruta[i]), 1)) 
                for i in range(len(ruta)-1))
        T = sum(self.tiempos.get((ruta[i], ruta[i+1]), self.tiempos.get((ruta[i+1], ruta[i]), 0.5)) 
                for i in range(len(ruta)-1))
        return P / (D + T) if (D + T) > 0 else 0
    
    def inicializar(self, tamano=30):
        self.poblacion = []
        for _ in range(tamano):
            ruta = self.distritos.copy()
            random.shuffle(ruta)
            fit = self.fitness(ruta)
            self.poblacion.append((ruta, fit))
        self.poblacion.sort(key=lambda x: x[1], reverse=True)
        self.mejor_ruta, self.mejor_fitness = self.poblacion[0]
    
    def seleccionar_padres(self):
        # Torneo
        seleccionados = random.sample(self.poblacion, 3)
        return max(seleccionados, key=lambda x: x[1])[0]
    
    def cruzar(self, padre1, padre2):
        # Ordered crossover
        n = len(padre1)
        p1, p2 = random.randint(0, n-1), random.randint(0, n-1)
        if p1 > p2: p1, p2 = p2, p1
        
        hijo = [None] * n
        for i in range(p1, p2+1):
            hijo[i] = padre1[i]
        
        pos = 0
        for gen in padre2:
            if gen not in hijo:
                while hijo[pos] is not None:
                    pos += 1
                hijo[pos] = gen
        return hijo
    
    def mutar(self, ruta, prob=0.1):
        if random.random() > prob:
            return ruta
        i, j = random.sample(range(len(ruta)), 2)
        ruta[i], ruta[j] = ruta[j], ruta[i]
        return ruta
    
    def evolucionar(self, generaciones=50):
        print("\n🚀 Evolución del Algoritmo Genético...")
        for gen in range(generaciones):
            nueva_poblacion = []
            nueva_poblacion.append(self.poblacion[0])  # Elitismo
            
            while len(nueva_poblacion) < len(self.poblacion):
                padre1 = self.seleccionar_padres()
                padre2 = self.seleccionar_padres()
                hijo = self.cruzar(padre1, padre2)
                hijo = self.mutar(hijo)
                fit = self.fitness(hijo)
                nueva_poblacion.append((hijo, fit))
            
            nueva_poblacion.sort(key=lambda x: x[1], reverse=True)
            self.poblacion = nueva_poblacion
            self.mejor_ruta, self.mejor_fitness = self.poblacion[0]
            
            if (gen + 1) % 10 == 0:
                print(f"   Generación {gen+1}: Fitness = {self.mejor_fitness:.6f}")
        
        print(f"✅ Mejor fitness: {self.mejor_fitness:.6f}")
        return self.mejor_ruta


# ============================================================
# 4. SISTEMA COMPLETO
# ============================================================
class SistemaRecoleccionIA:
    def __init__(self):
        self.rna = None
        self.ag = None
        self.distritos = ['Centro', 'Max Paredes', 'Cotahuma', 'Sur', 'Periférica']
        
        # Matrices de distancias y tiempos
        self.distancias = {
            ('Centro', 'Max Paredes'): 2.5, ('Centro', 'Cotahuma'): 3.0,
            ('Centro', 'Sur'): 4.0, ('Centro', 'Periférica'): 6.0,
            ('Max Paredes', 'Cotahuma'): 2.0, ('Max Paredes', 'Sur'): 3.5,
            ('Max Paredes', 'Periférica'): 5.0, ('Cotahuma', 'Sur'): 2.5,
            ('Cotahuma', 'Periférica'): 4.5, ('Sur', 'Periférica'): 3.0,
        }
        self.tiempos = {k: v / 20 for k, v in self.distancias.items()}
    
    def ejecutar(self):
        print("=" * 60)
        print("SISTEMA INTELIGENTE DE RECOLECCIÓN DE RESIDUOS")
        print("Municipio de La Paz")
        print("=" * 60)
        
        # PASO 1: Generar datos
        print("\n📊 Paso 1: Generando datos históricos...")
        generador = GeneradorDatos()
        df = generador.generar_datos(500)
        print(f"   ✅ Generados {len(df)} registros")
        
        # PASO 2: Preprocesar y entrenar RNA
        print("\n🧠 Paso 2: Entrenando Red Neuronal...")
        self.rna = RedNeuronal()
        
        # Preprocesar para entrenamiento
        X, y = self.rna.preprocesar_entrenamiento(df)
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Construir y entrenar
        self.rna.construir(input_dim=X.shape[1])
        self.rna.entrenar(X_train, y_train, X_test, y_test, epochs=50)
        
        # PASO 3: Predecir prioridades con la RNA
        print("\n📈 Paso 3: Calculando prioridades por distrito...")
        prioridades = {}
        
        for distrito in self.distritos:
            df_pred = pd.DataFrame([{
                'distrito': distrito, 
                'dia_semana': 'Lunes', 
                'mes': 6,
                'feria': 0, 
                'evento': 0, 
                'clima': 'Soleado',
                'tipo_zona': 'Mixto', 
                'bloqueos': 0, 
                'transitabilidad': 1
            }])
            X_pred = self.rna.preprocesar_prediccion(df_pred)
            iigr = self.rna.predecir_iigr(X_pred)[0]
            prioridades[distrito] = round(iigr, 1)
            print(f"   {distrito}: {prioridades[distrito]:.1f}%")
        
        # PASO 4: Optimizar rutas con AG
        print("\n🚛 Paso 4: Optimizando rutas de recolección...")
        self.ag = AlgoritmoGenetico(self.distritos, prioridades, self.distancias, self.tiempos)
        self.ag.inicializar(tamano=30)
        mejor_ruta = self.ag.evolucionar(generaciones=50)
        
        # RESULTADO FINAL
        print("\n" + "=" * 60)
        print("RESULTADO FINAL")
        print("=" * 60)
        print(f"\n📋 Ruta óptima recomendada:")
        print(f"   {' → '.join(mejor_ruta)}")
        print(f"\n📊 Fitness de la ruta: {self.ag.mejor_fitness:.6f}")
        print(f"\n💡 Prioridades utilizadas (IIGR):")
        for d, p in prioridades.items():
            print(f"   {d}: {p}%")
        
        return mejor_ruta


# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================
if __name__ == "__main__":
    sistema = SistemaRecoleccionIA()
    ruta_final = sistema.ejecutar()
    
    print("\n" + "=" * 60)
    print("✅ SISTEMA COMPLETADO EXITOSAMENTE")
    print("=" * 60)