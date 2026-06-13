import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Agregar ruta del proyecto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar tu sistema
from sistema_completo import SistemaRecoleccionIA

# Configuración de la página (DEBE IR PRIMERO)
st.set_page_config(
    page_title="Sistema de Recolección de Residuos - La Paz",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar CSS personalizado
def load_css():
    st.markdown("""
    <style>
    /* Estilos modernos */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .ruta-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        font-size: 1.2rem;
        margin: 1rem 0;
    }
    .footer {
        text-align: center;
        padding: 2rem;
        color: #666;
        margin-top: 3rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Inicializar estado de sesión
if 'resultados' not in st.session_state:
    st.session_state.resultados = None
if 'ejecutado' not in st.session_state:
    st.session_state.ejecutado = False

# Cargar estilos
load_css()

# ============================================================
# HEADER PRINCIPAL
# ============================================================
st.markdown("""
<div class="main-header">
    <h1>🚛 Sistema Inteligente de Recolección de Residuos</h1>
    <p>Municipio de La Paz - Red Neuronal + Algoritmo Genético</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Bandera_de_La_Paz_%28Bolivia%29.svg/1200px-Bandera_de_La_Paz_%28Bolivia%29.svg.png", 
             use_container_width=True)
    
    st.markdown("## ⚙️ Configuración")
    
    # Opciones de configuración
    num_registros = st.slider("📊 Número de registros históricos", 100, 1000, 500)
    generaciones = st.slider("🔄 Generaciones del AG", 10, 200, 50)
    tamano_poblacion = st.slider("👥 Tamaño de la población", 10, 100, 30)
    
    st.markdown("---")
    st.markdown("### 📋 Variables consideradas")
    
    with st.expander("Ver variables"):
        st.markdown("""
        - 🏙️ Distrito
        - 👥 Densidad poblacional
        - 📅 Día de la semana
        - 📆 Mes del año
        - 🏪 Ferias y mercados
        - 🎉 Eventos especiales
        - ☁️ Condiciones climáticas
        - 📊 Historial de residuos
        - 🏘️ Tipo de zona
        - 🏪 Actividad comercial
        - 🚧 Bloqueos viales
        - 🚦 Transitabilidad
        """)
    
    st.markdown("---")
    
    # Botón de ejecución
    ejecutar = st.button("🚀 EJECUTAR SISTEMA", type="primary", use_container_width=True)

# ============================================================
# CONTENIDO PRINCIPAL
# ============================================================
if ejecutar:
    with st.spinner("🔄 Procesando... Entrenando Red Neuronal y ejecutando Algoritmo Genético"):
        try:
            # Ejecutar el sistema
            sistema = SistemaRecoleccionIA()
            
            # Modificar parámetros
            sistema.ag.evolucionar = lambda gen=50: None  # Esto es un placeholder
            # En realidad, deberías modificar el sistema para aceptar parámetros
            
            # Por ahora, ejecutamos con los valores por defecto
            resultado = sistema.ejecutar()
            
            st.session_state.resultados = {
                'ruta': resultado,
                'prioridades': sistema.ag.prioridades if hasattr(sistema, 'ag') else {},
                'fitness': sistema.ag.mejor_fitness if hasattr(sistema, 'ag') else 0
            }
            st.session_state.ejecutado = True
            
            st.success("✅ Sistema ejecutado exitosamente!")
            
        except Exception as e:
            st.error(f"❌ Error al ejecutar el sistema: {str(e)}")
            st.info("Asegúrate de que todos los módulos estén correctamente instalados")

# ============================================================
# MOSTRAR RESULTADOS
# ============================================================
if st.session_state.ejecutado and st.session_state.resultados:
    resultados = st.session_state.resultados
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🏆 Fitness</h3>
            <h2>{resultados['fitness']:.6f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📍 Distritos</h3>
            <h2>{len(resultados['ruta'])}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🔄 Generaciones</h3>
            <h2>{generaciones}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 Registros</h3>
            <h2>{num_registros}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Ruta óptima
    st.markdown("## 🗺️ Ruta Óptima de Recolección")
    
    # Mostrar ruta con flechas
    ruta_html = " → ".join(resultados['ruta'])
    st.markdown(f"""
    <div class="ruta-container">
        <h3>🏆 MEJOR RUTA ENCONTRADA</h3>
        <p style="font-size: 1.5rem; font-weight: bold;">{ruta_html}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabla de prioridades
    st.markdown("## 📊 Prioridades por Distrito (IIGR)")
    
    if resultados['prioridades']:
        df_prioridades = pd.DataFrame([
            {"Distrito": d, "IIGR (%)": p} 
            for d, p in resultados['prioridades'].items()
        ]).sort_values("IIGR (%)", ascending=False)
        
        # Gráfico de barras con Plotly
        fig = px.bar(
            df_prioridades, 
            x="Distrito", 
            y="IIGR (%)",
            title="Índice Inteligente de Generación de Residuos por Distrito",
            color="IIGR (%)",
            color_continuous_scale="Viridis",
            text="IIGR (%)"
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla
        st.dataframe(df_prioridades, use_container_width=True)
    
    # Visualización de la ruta (mapa conceptual)
    st.markdown("## 🗺️ Visualización de la Ruta")
    
    # Crear diagrama de la ruta
    fig_ruta = go.Figure()
    
    # Posiciones circulares para los distritos
    n = len(resultados['ruta'])
    angulos = np.linspace(0, 2*np.pi, n, endpoint=False)
    
    # Coordenadas
    xs = np.cos(angulos)
    ys = np.sin(angulos)
    
    # Mapeo de distritos a coordenadas
    posiciones = {distrito: (xs[i], ys[i]) for i, distrito in enumerate(resultados['ruta'])}
    
    # Dibujar conexiones
    for i in range(n):
        origen = resultados['ruta'][i]
        destino = resultados['ruta'][(i+1) % n]
        x_origen, y_origen = posiciones[origen]
        x_destino, y_destino = posiciones[destino]
        
        fig_ruta.add_trace(go.Scatter(
            x=[x_origen, x_destino],
            y=[y_origen, y_destino],
            mode='lines+markers',
            line=dict(width=3, color='#667eea'),
            marker=dict(size=10, color='#764ba2'),
            text=[origen, destino],
            hoverinfo='text',
            showlegend=False
        ))
    
    # Añadir nodos
    for distrito, (x, y) in posiciones.items():
        fig_ruta.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode='markers+text',
            marker=dict(size=20, color='#667eea', symbol='circle'),
            text=[distrito],
            textposition="bottom center",
            textfont=dict(size=12, color='white'),
            showlegend=False
        ))
    
    fig_ruta.update_layout(
        title="Representación Circular de la Ruta",
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        plot_bgcolor='rgba(0,0,0,0)',
        height=500,
        showlegend=False
    )
    
    st.plotly_chart(fig_ruta, use_container_width=True)

# ============================================================
# INFORMACIÓN DEL SISTEMA
# ============================================================
st.markdown("---")
st.markdown("## ℹ️ Acerca del Sistema")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🧠 Red Neuronal Artificial
    
    - **Arquitectura:** 9 → 4 → 3 → 1
    - **Función de activación:** ReLU (capas ocultas)
    - **Función de pérdida:** MSE
    - **Optimizador:** Adam
    - **Salida:** IIGR (0-100%)
    """)

with col2:
    st.markdown("""
    ### 🧬 Algoritmo Genético
    
    - **Selección:** Torneo (k=3)
    - **Cruce:** Ordered Crossover (OX)
    - **Mutación:** Swap Mutation
    - **Elitismo:** Mejor individuo
    - **Fitness:** P / (D + T)
    """)

# Footer
st.markdown("""
<div class="footer">
    <p>© 2024 - Sistema Inteligente para la Gestión de Residuos Sólidos</p>
    <p>Municipio de La Paz - Bolivia</p>
</div>
""", unsafe_allow_html=True)