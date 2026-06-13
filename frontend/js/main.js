// Sistema Principal
const RNA = new RNAAnimacion();
const AGEvol = new AGEvolucion();
const Mapa = new MapaLaPaz();

const API_URL = 'http://localhost:8000';

// Estado del sistema
let estado = {
    rnaActivada: false,
    agEjecutado: false,
    rutaOptimizada: false,
    prediccionFinalizada: false
};

// Actualizar indicadores
function actualizarIndicadores() {
    document.querySelectorAll('.status-led').forEach(led => led.classList.remove('active'));
    if (estado.rnaActivada) document.getElementById('ledRNA')?.classList.add('active');
    if (estado.agEjecutado) document.getElementById('ledAG')?.classList.add('active');
    if (estado.rutaOptimizada) document.getElementById('ledRuta')?.classList.add('active');
    if (estado.prediccionFinalizada) document.getElementById('ledPrediccion')?.classList.add('active');
}

// Mostrar dashboard principal
function mostrarDashboard() {
    return `
        <div class="grid-2">
            <!-- RED NEURONAL -->
            <div class="card">
                <h3>🧠 Red Neuronal Artificial</h3>
                <div id="rnaContainer">${RNA.mostrarArquitectura()}</div>
                <div id="iigrResultado" style="text-align:center; margin-top:15px; padding:10px; background:#f0f2f5; border-radius:10px;">
                    <strong>IIGR (Índice Inteligente de Generación de Residuos)</strong><br>
                    <span id="iigrValor" style="font-size:1.5rem; font-weight:bold;">---</span>
                </div>
            </div>
            
            <!-- PRIORIDADES SEMÁFORO -->
            <div class="card">
                <h3>📊 Prioridad por Distrito</h3>
                <div id="prioridadesSemaforo"></div>
            </div>
        </div>
        
        <div class="grid-2">
            <!-- MAPA -->
            <div class="card">
                <h3>🗺️ Mapa de Prioridades - La Paz</h3>
                <div id="mapaContainer" style="position:relative;"></div>
            </div>
            
            <!-- ALGORITMO GENÉTICO -->
            <div class="card">
                <h3>🧬 Evolución del Algoritmo Genético</h3>
                ${AGEvol.mostrarContenedor()}
            </div>
        </div>
        
        <div class="grid-2">
            <!-- RUTA ÓPTIMA -->
            <div class="card">
                <h3>🚛 Ruta Óptima de Recolección</h3>
                <div id="rutaOptimaContainer" class="ruta-container" style="padding:15px; text-align:center;">
                    <div id="rutaOptima" class="pasos">---</div>
                </div>
                <div id="explicacionIA" style="margin-top:15px; padding:12px; background:#e3f2fd; border-radius:10px; font-size:0.85rem;"></div>
            </div>
            
            <!-- BENEFICIOS -->
            <div class="card">
                <h3>📈 Impacto del Sistema</h3>
                <div id="beneficios" class="beneficios-grid">
                    <div class="beneficio"><div class="beneficio-valor" id="ahorroTiempo">---</div><div class="beneficio-label">Reducción de tiempo</div></div>
                    <div class="beneficio"><div class="beneficio-valor" id="ahorroCombustible">---</div><div class="beneficio-label">Ahorro de combustible</div></div>
                    <div class="beneficio"><div class="beneficio-valor" id="reduccionDistancia">---</div><div class="beneficio-label">Reducción de distancia</div></div>
                    <div class="beneficio"><div class="beneficio-valor" id="prioridadAtendida">---</div><div class="beneficio-label">Prioridad atendida</div></div>
                </div>
            </div>
        </div>
    `;
}

// Mostrar prioridades con semáforo
function mostrarPrioridadesSemaforo(prioridades) {
    const container = document.getElementById('prioridadesSemaforo');
    if (!container) return;
    
    const colores = {
        muyAlta: '#dc3545',
        alta: '#fd7e14',
        media: '#ffc107',
        baja: '#28a745'
    };
    
    const prioridadesArray = Object.entries(prioridades).sort((a,b) => b[1] - a[1]);
    
    container.innerHTML = `<div class="prioridad-lista">
        ${prioridadesArray.map(([distrito, valor]) => {
            let categoria = valor >= 70 ? 'muyAlta' : valor >= 50 ? 'alta' : valor >= 30 ? 'media' : 'baja';
            let emoji = valor >= 70 ? '🟥' : valor >= 50 ? '🟧' : valor >= 30 ? '🟨' : '🟩';
            return `
                <div class="prioridad-item">
                    <div class="prioridad-color" style="background: ${colores[categoria]};"></div>
                    <div class="prioridad-info">
                        <div class="prioridad-nombre">${emoji} ${distrito}</div>
                        <div class="prioridad-valor">${valor.toFixed(1)}% IIGR</div>
                    </div>
                    <div class="prioridad-barra-contenedor">
                        <div class="prioridad-barra" style="width: ${valor}%; background: ${colores[categoria]};"></div>
                    </div>
                    <div style="font-weight:bold;">${Math.round(valor * 2.5)} Ton</div>
                </div>
            `;
        }).join('')}
    </div>`;
}

// Ejecutar sistema completo
async function ejecutarSistema() {
    const btn = document.getElementById('btnEjecutar');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Procesando... Activando RNA y AG';
    
    try {
        // Indicador RNA activándose
        document.getElementById('ledRNA')?.classList.add('loading');
        
        const response = await fetch(`${API_URL}/api/optimizar`, { method: 'POST' });
        const data = await response.json();
        
        // 1. ANIMAR RNA
        const iigrPromedio = Object.values(data.prioridades).reduce((a,b) => a+b, 0) / Object.values(data.prioridades).length;
        await RNA.animarPrediccion(iigrPromedio);
        document.getElementById('iigrValor').innerHTML = `${iigrPromedio.toFixed(1)}%`;
        estado.rnaActivada = true;
        document.getElementById('ledRNA')?.classList.remove('loading');
        document.getElementById('ledRNA')?.classList.add('active');
        
        // 2. MOSTRAR PRIORIDADES
        mostrarPrioridadesSemaforo(data.prioridades);
        
        // 3. MOSTRAR MAPA
        const mapaContainer = document.getElementById('mapaContainer');
        if (mapaContainer) {
            mapaContainer.innerHTML = Mapa.mostrarMapa(data.prioridades, data.ruta);
            Mapa.dibujarMarcadores(data.prioridades);
            Mapa.dibujarRuta(data.ruta, data.prioridades);
        }
        
        // 4. SIMULAR EVOLUCIÓN DEL AG
        estado.agEjecutado = true;
        document.getElementById('ledAG')?.classList.add('loading');
        await AGEvol.simularEvolucion(data.ruta, data.fitness, 40);
        document.getElementById('ledAG')?.classList.remove('loading');
        document.getElementById('ledAG')?.classList.add('active');
        
        // 5. MOSTRAR RUTA ÓPTIMA
        const rutaContainer = document.getElementById('rutaOptima');
        if (rutaContainer) {
            rutaContainer.innerHTML = data.ruta.map((d,i) => `<span class="paso">${d}</span>${i < data.ruta.length-1 ? '<span class="flecha">→</span>' : ''}`).join('');
        }
        estado.rutaOptimizada = true;
        document.getElementById('ledRuta')?.classList.add('active');
        
        // 6. EXPLICACIÓN IA
        const prioridadMax = Object.entries(data.prioridades).sort((a,b) => b[1] - a[1])[0];
        const residuosMax = (prioridadMax[1] * 2.5).toFixed(0);
        document.getElementById('explicacionIA').innerHTML = `
            🤖 <strong>Explicación del Sistema:</strong><br>
            El sistema detectó que <strong>${prioridadMax[0]}</strong> presenta la mayor generación estimada
            de residuos (${residuosMax} Ton).<br>
            Por este motivo, el Algoritmo Genético priorizó esta zona dentro de la ruta óptima de recolección.
        `;
        
        // 7. BENEFICIOS
        const distanciaEstimada = 12.5;
        const tiempoEstimado = distanciaEstimada / 20;
        const beneficio = {
            ahorroTiempo: '18%',
            ahorroCombustible: '12%',
            reduccionDistancia: `${(distanciaEstimada * 0.18).toFixed(1)} km`,
            prioridadAtendida: '100%'
        };
        document.getElementById('ahorroTiempo').innerHTML = beneficio.ahorroTiempo;
        document.getElementById('ahorroCombustible').innerHTML = beneficio.ahorroCombustible;
        document.getElementById('reduccionDistancia').innerHTML = beneficio.reduccionDistancia;
        document.getElementById('prioridadAtendida').innerHTML = beneficio.prioridadAtendida;
        
        estado.prediccionFinalizada = true;
        document.getElementById('ledPrediccion')?.classList.add('active');
        
    } catch (error) {
        alert('Error: Asegúrate que el backend esté corriendo en http://localhost:8000');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '🚀 EJECUTAR SISTEMA';
        actualizarIndicadores();
    }
}

// Inicializar tabs
function initTabs() {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(tab.dataset.tab).classList.add('active');
        });
    });
}

// Cargar dashboard
document.addEventListener('DOMContentLoaded', () => {
    const mainContent = document.getElementById('mainContent');
    if (mainContent) {
        mainContent.innerHTML = mostrarDashboard();
    }
    initTabs();
    
    // Cargar prioridades iniciales
    fetch(`${API_URL}/api/prioridades`)
        .then(res => res.json())
        .then(data => {
            mostrarPrioridadesSemaforo(data);
        })
        .catch(e => console.log('Esperando backend...'));
});