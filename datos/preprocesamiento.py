import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split

class PreprocesadorDatos:
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.encoders = {}
        self.feature_columns = None
    
    def cargar_datos(self, filename='datos/residuos.csv'):
        """Carga la base de datos"""
        df = pd.read_csv(filename)
        print(f"Datos cargados: {len(df)} registros")
        return df
    
    def preprocesar(self, df):
        """Aplica limpieza, normalización y codificación"""
        df_procesado = df.copy()
        
        # Variables numéricas a normalizar
        numeric_cols = ['densidad_poblacional', 'historial_residuos', 
                        'actividad_comercial']
        
        for col in numeric_cols:
            if col in df_procesado.columns:
                df_procesado[col] = self.scaler.fit_transform(df_procesado[[col]].fillna(0))
        
        # Variables categóricas a codificar
        categorical_cols = ['distrito', 'dia_semana', 'tipo_zona', 'clima']
        
        for col in categorical_cols:
            if col in df_procesado.columns:
                self.encoders[col] = LabelEncoder()
                df_procesado[col] = self.encoders[col].fit_transform(df_procesado[col].fillna('Desconocido'))
        
        # Variables binarias (ya están 0/1)
        binary_cols = ['feria', 'evento_especial', 'bloqueos', 'transitabilidad_vial']
        for col in binary_cols:
            if col in df_procesado.columns:
                df_procesado[col] = df_procesado[col].fillna(0).astype(int)
        
        # Variable mes (ya es numérica)
        if 'mes' in df_procesado.columns:
            df_procesado['mes'] = df_procesado['mes'].fillna(1).astype(int)
            # Normalizar mes (1-12 -> 0-1)
            df_procesado['mes'] = (df_procesado['mes'] - 1) / 11
        
        # Seleccionar características para el modelo (12 variables)
        self.feature_columns = [
            'distrito', 'densidad_poblacional', 'dia_semana', 'mes',
            'feria', 'evento_especial', 'clima', 'historial_residuos',
            'tipo_zona', 'actividad_comercial', 'bloqueos', 'transitabilidad_vial'
        ]
        
        # Verificar que todas las columnas existan
        for col in self.feature_columns:
            if col not in df_procesado.columns:
                print(f"⚠️ Advertencia: Columna {col} no encontrada")
                df_procesado[col] = 0
        
        X = df_procesado[self.feature_columns]
        y = df_procesado['residuos_generados'] / 300  # Normalizar (máximo ~300 kg)
        
        return X, y
    
    def dividir_datos(self, X, y, test_size=0.2, val_size=0.1):
        """Divide datos en entrenamiento, validación y prueba"""
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        val_size_adj = val_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_size_adj, random_state=42
        )
        
        print(f"\nDivisión de datos:")
        print(f"  Entrenamiento: {len(X_train)} registros")
        print(f"  Validación: {len(X_val)} registros")
        print(f"  Prueba: {len(X_test)} registros")
        
        return X_train, X_val, X_test, y_train, y_val, y_test


if __name__ == "__main__":
    print("=" * 60)
    print("PREPROCESAMIENTO DE DATOS")
    print("=" * 60)
    
    preprocesador = PreprocesadorDatos()
    
    # Cargar datos
    df = preprocesador.cargar_datos()
    
    # Preprocesar
    X, y = preprocesador.preprocesar(df)
    
    print(f"\nCaracterísticas de entrada (12 variables): {X.columns.tolist()}")
    print(f"Tamaño de X: {X.shape}")
    print(f"Tamaño de y: {y.shape}")
    
    # Dividir
    X_train, X_val, X_test, y_train, y_val, y_test = preprocesador.dividir_datos(X, y)