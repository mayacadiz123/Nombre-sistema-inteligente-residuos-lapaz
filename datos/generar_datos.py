import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class GeneradorDatosResiduos:
    """
    Generador de datos sintéticos realistas para el Municipio de La Paz
    Simula 12 variables de entrada y la cantidad de residuos generados
    """
    
    def __init__(self):
        # Distritos de La Paz
        self.distritos = [
            'Centro', 'Max Paredes', 'Cotahuma', 'Sur', 'Periférica',
            'Miraflores', 'Sopocachi', 'San Pedro', 'Villa Fátima', 'Zona Sur'
        ]
        
        # Días de la semana
        self.dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        
        # Meses del año
        self.meses = list(range(1, 13))
        
        # Tipos de zona
        self.tipos_zona = ['Residencial', 'Comercial', 'Mixto', 'Industrial']
        
        # Condiciones climáticas
        self.climas = ['Soleado', 'Nublado', 'Lluvia', 'Tormenta']
        
        # Densidad poblacional por distrito (habitantes/km²)
        self.densidad_poblacional = {
            'Centro': 12000, 'Max Paredes': 11000, 'Cotahuma': 9500,
            'Sur': 8000, 'Periférica': 7000, 'Miraflores': 10000,
            'Sopocachi': 10500, 'San Pedro': 9000, 'Villa Fátima': 8500,
            'Zona Sur': 7500
        }
        
        # Nivel de actividad comercial por distrito (0-100)
        self.actividad_comercial = {
            'Centro': 95, 'Max Paredes': 90, 'Cotahuma': 70,
            'Sur': 65, 'Periférica': 60, 'Miraflores': 85,
            'Sopocachi': 80, 'San Pedro': 75, 'Villa Fátima': 50,
            'Zona Sur': 55
        }
    
    def calcular_residuos_base(self, distrito, densidad, dia, mes, tipo_zona, 
                                feria, evento, clima, actividad, historial, 
                                bloqueos, transitabilidad):
        """
        Calcula la cantidad de residuos generados (en kg)
        Basado en las 12 variables de entrada
        """
        # Peso base por distrito
        pesos_base = {
            'Centro': 120, 'Max Paredes': 110, 'Cotahuma': 90,
            'Sur': 80, 'Periférica': 75, 'Miraflores': 100,
            'Sopocachi': 95, 'San Pedro': 85, 'Villa Fátima': 70,
            'Zona Sur': 65
        }
        
        residuos = pesos_base.get(distrito, 80)
        
        # 1. Densidad poblacional (factor: 0.5 a 1.5)
        densidad_norm = densidad / 12000  # 12000 es el máximo
        residuos *= (0.5 + densidad_norm)
        
        # 2. Día de la semana (fines de semana menos residuos comerciales)
        if dia in ['Sábado', 'Domingo']:
            residuos *= 0.85
        elif dia == 'Viernes':
            residuos *= 1.10
        
        # 3. Mes del año (diciembre y enero más residuos)
        if mes in [12, 1]:
            residuos *= 1.20
        elif mes in [7, 8]:  # Vacaciones de invierno
            residuos *= 1.05
        
        # 4. Ferias (incremento significativo)
        if feria == 1:
            residuos *= random.uniform(1.3, 1.6)
        
        # 5. Eventos especiales
        if evento == 1:
            residuos *= random.uniform(1.2, 1.5)
        
        # 6. Clima (lluvia reduce recolección pero no generación)
        if clima == 'Lluvia':
            residuos *= 0.95
        elif clima == 'Tormenta':
            residuos *= 0.90
        
        # 7. Historial de residuos (tendencia)
        residuos = residuos * 0.7 + historial * 0.3
        
        # 8. Tipo de zona
        if tipo_zona == 'Comercial':
            residuos *= 1.3
        elif tipo_zona == 'Mixto':
            residuos *= 1.15
        elif tipo_zona == 'Industrial':
            residuos *= 1.4
        
        # 9. Actividad comercial
        actividad_norm = actividad / 100
        residuos *= (0.7 + actividad_norm * 0.8)
        
        # 10. Bloqueos (aumenta acumulación)
        if bloqueos == 1:
            residuos *= random.uniform(1.2, 1.5)
        
        # 11. Transitabilidad vial (afecta recolección)
        if transitabilidad == 0:  # Mala transitabilidad
            residuos *= random.uniform(1.1, 1.3)
        
        # Añadir ruido aleatorio (factor realista)
        residuos *= random.uniform(0.85, 1.15)
        
        return max(30, round(residuos, 1))  # Mínimo 30 kg
    
    def generar_registro(self, fecha=None, distrito=None):
        """Genera un registro completo de datos"""
        
        if distrito is None:
            distrito = random.choice(self.distritos)
        
        if fecha is None:
            fecha = datetime.now() - timedelta(days=random.randint(0, 365*2))
        
        dia = self.dias_semana[fecha.weekday()]
        mes = fecha.month
        
        densidad = self.densidad_poblacional[distrito]
        tipo_zona = random.choice(self.tipos_zona)
        clima = random.choice(self.climas)
        actividad = self.actividad_comercial[distrito]
        
        # Probabilidades realistas
        feria = 1 if random.random() < 0.15 else 0
        evento = 1 if random.random() < 0.08 else 0
        bloqueos = 1 if random.random() < 0.05 else 0
        transitabilidad = 1 if random.random() < 0.85 else 0  # 85% buena
        
        # Historial (basado en registros anteriores, simulado)
        historial = random.uniform(50, 200)
        
        # Calcular residuos
        residuos = self.calcular_residuos_base(
            distrito, densidad, dia, mes, tipo_zona,
            feria, evento, clima, actividad, historial,
            bloqueos, transitabilidad
        )
        
        return {
            'fecha': fecha.strftime('%Y-%m-%d'),
            'distrito': distrito,
            'densidad_poblacional': densidad,
            'dia_semana': dia,
            'mes': mes,
            'feria': feria,
            'evento_especial': evento,
            'clima': clima,
            'historial_residuos': round(historial, 1),
            'tipo_zona': tipo_zona,
            'actividad_comercial': actividad,
            'bloqueos': bloqueos,
            'transitabilidad_vial': transitabilidad,
            'residuos_generados': residuos  # Variable objetivo Y
        }
    
    def generar_base_datos(self, num_registros=500, start_date=None):
        """Genera la base de datos completa"""
        
        if start_date is None:
            start_date = datetime(2023, 1, 1)
        
        registros = []
        
        for i in range(num_registros):
            fecha = start_date + timedelta(days=i % 730)  # 2 años de datos
            registro = self.generar_registro(fecha=fecha)
            registros.append(registro)
        
        df = pd.DataFrame(registros)
        return df
    
    def guardar_datos(self, df, filename='datos/residuos.csv'):
        """Guarda los datos en un archivo CSV"""
        import os
        os.makedirs('datos', exist_ok=True)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Datos guardados en {filename}")
        print(f"Total de registros: {len(df)}")
        return df


# Ejecutar generación de datos
if __name__ == "__main__":
    print("=" * 60)
    print("GENERADOR DE DATOS DE RESIDUOS - MUNICIPIO DE LA PAZ")
    print("=" * 60)
    
    generador = GeneradorDatosResiduos()
    
    # Generar 500 registros
    df = generador.generar_base_datos(num_registros=500)
    
    # Guardar
    generador.guardar_datos(df)
    
    # Mostrar estadísticas
    print("\n" + "=" * 60)
    print("ESTADÍSTICAS DE LOS DATOS GENERADOS")
    print("=" * 60)
    print(f"\nDistritos: {df['distrito'].nunique()}")
    print(f"Rango de fechas: {df['fecha'].min()} a {df['fecha'].max()}")
    print(f"\nResiduos generados (kg):")
    print(f"  Mínimo: {df['residuos_generados'].min():.1f}")
    print(f"  Máximo: {df['residuos_generados'].max():.1f}")
    print(f"  Promedio: {df['residuos_generados'].mean():.1f}")
    
    print("\nPrimeras 5 filas:")
    print(df.head())
    
    print("\n✅ Base de datos generada exitosamente!")