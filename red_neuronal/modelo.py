import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import matplotlib.pyplot as plt
import os

class ResiduosRNA:
    def __init__(self, input_dim=12):
        self.input_dim = input_dim
        self.model = None
        self.history = None
    
    def build_model(self):
        """Construye la arquitectura de la RNA"""
        model = keras.Sequential([
            # Capa de entrada (12 neuronas)
            layers.Input(shape=(self.input_dim,)),
            
            # Capa oculta 1: 12 → 4 (agrupación de factores)
            layers.Dense(4, activation='relu', name='capa_agrupacion'),
            
            # Capa oculta 2: 4 → 3 (procesamiento profundo)
            layers.Dense(3, activation='relu', name='capa_profunda'),
            
            # Capa de salida: 3 → 1 (IIGR)
            layers.Dense(1, activation='linear', name='capa_salida')
        ])
        
        # Compilar el modelo
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae', 'mse']
        )
        
        self.model = model
        print("✅ Modelo RNA construido exitosamente")
        self.model.summary()
        return model
    
    def train(self, X_train, y_train, X_val, y_val, epochs=100, batch_size=32):
        """Entrena la RNA"""
        print(f"\n🚀 Iniciando entrenamiento por {epochs} épocas...")
        
        # Callbacks
        early_stop = keras.callbacks.EarlyStopping(
            monitor='val_loss', patience=10, restore_best_weights=True
        )
        
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            verbose=1,
            callbacks=[early_stop]
        )
        
        print("✅ Entrenamiento completado")
        return self.history
    
    def predict(self, X):
        """Predice residuos normalizados (0-1)"""
        return self.model.predict(X)
    
    def get_iigr(self, X):
        """Retorna el IIGR en porcentaje (0-100)"""
        predictions = self.predict(X)
        return predictions.flatten() * 100
    
    def evaluate(self, X_test, y_test):
        """Evalúa el modelo con datos de prueba"""
        loss, mae, mse = self.model.evaluate(X_test, y_test, verbose=0)
        print(f"\n📊 Evaluación en datos de prueba:")
        print(f"   Loss (MSE): {loss:.4f}")
        print(f"   MAE: {mae:.4f}")
        print(f"   RMSE: {np.sqrt(mse):.4f}")
        return {'loss': loss, 'mae': mae, 'rmse': np.sqrt(mse)}
    
    def save_model(self, filename='resultados/modelo.keras'):
        """Guarda el modelo entrenado"""
        os.makedirs('resultados', exist_ok=True)
        self.model.save(filename)
        print(f"✅ Modelo guardado en {filename}")
    
    def load_model(self, filename='resultados/modelo.keras'):
        """Carga un modelo guardado"""
        self.model = keras.models.load_model(filename)
        print(f"✅ Modelo cargado desde {filename}")
        return self.model
    
    def plot_history(self):
        """Grafica el historial de entrenamiento"""
        if self.history is None:
            print("⚠️ No hay historial de entrenamiento")
            return
        
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        
        # Loss
        axes[0].plot(self.history.history['loss'], label='Entrenamiento')
        axes[0].plot(self.history.history['val_loss'], label='Validación')
        axes[0].set_title('Pérdida (MSE) durante el entrenamiento')
        axes[0].set_xlabel('Época')
        axes[0].set_ylabel('Loss')
        axes[0].legend()
        axes[0].grid(True)
        
        # MAE
        axes[1].plot(self.history.history['mae'], label='Entrenamiento')
        axes[1].plot(self.history.history['val_mae'], label='Validación')
        axes[1].set_title('Error Absoluto Medio (MAE)')
        axes[1].set_xlabel('Época')
        axes[1].set_ylabel('MAE')
        axes[1].legend()
        axes[1].grid(True)
        
        plt.tight_layout()
        os.makedirs('resultados', exist_ok=True)
        plt.savefig('resultados/historial_entrenamiento.png', dpi=150)
        plt.show()
        print("✅ Gráfica guardada en resultados/historial_entrenamiento.png")


if __name__ == "__main__":
    print("=" * 60)
    print("RED NEURONAL ARTIFICIAL - PREDICCIÓN DE RESIDUOS")
    print("=" * 60)
    
    # Importar preprocesador
    import sys
    sys.path.append('datos')
    from preprocesamiento import PreprocesadorDatos
    
    # Cargar y preprocesar datos
    preprocesador = PreprocesadorDatos()
    df = preprocesador.cargar_datos()
    X, y = preprocesador.preprocesar(df)
    X_train, X_val, X_test, y_train, y_val, y_test = preprocesador.dividir_datos(X, y)
    
    # Convertir a numpy arrays (importante)
    X_train = np.array(X_train)
    X_val = np.array(X_val)
    X_test = np.array(X_test)
    y_train = np.array(y_train)
    y_val = np.array(y_val)
    y_test = np.array(y_test)
    
    # Crear y entrenar RNA
    rna = ResiduosRNA(input_dim=12)
    rna.build_model()
    
    # Entrenar
    rna.train(X_train, y_train, X_val, y_val, epochs=100)
    
    # Evaluar
    rna.evaluate(X_test, y_test)
    
    # Graficar
    rna.plot_history()
    
    # Guardar modelo
    rna.save_model()
    
    # Ejemplo de predicción (CORREGIDO)
    print("\n" + "=" * 60)
    print("EJEMPLO DE PREDICCIÓN")
    print("=" * 60)
    
    # Tomar 5 ejemplos de prueba
    muestras = X_test[:5]
    residuos_reales = y_test[:5] * 300  # Desnormalizar
    residuos_predichos = rna.predict(muestras).flatten() * 300
    
    for i in range(5):
        print(f"  Muestra {i+1}: Real={residuos_reales[i]:.1f} kg → Predicho={residuos_predichos[i]:.1f} kg")
        print(f"           Error: {abs(residuos_reales[i] - residuos_predichos[i]):.1f} kg")
    
    print("\n✅ RNA entrenada y guardada exitosamente!")