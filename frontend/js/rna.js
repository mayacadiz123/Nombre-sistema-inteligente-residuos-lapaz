// Animación de la Red Neuronal
class RNAAnimacion {
    constructor() {
        this.activando = false;
    }
    
    mostrarArquitectura() {
        return `
            <div class="rna-animation">
                <div class="rna-layers">
                    <div class="layer">
                        <div class="neurons" id="neuronas-entrada"></div>
                        <div class="layer-title">Variables de Entrada (12)</div>
                    </div>
                    <div style="color:white; font-size:24px;">→</div>
                    <div class="layer">
                        <div class="neurons" id="neuronas-oculta1"></div>
                        <div class="layer-title">Capa Oculta 1 (4)</div>
                    </div>
                    <div style="color:white; font-size:24px;">→</div>
                    <div class="layer">
                        <div class="neurons" id="neuronas-oculta2"></div>
                        <div class="layer-title">Capa Oculta 2 (3)</div>
                    </div>
                    <div style="color:white; font-size:24px;">→</div>
                    <div class="layer">
                        <div class="neurons" id="neuronas-salida"></div>
                        <div class="layer-title">Salida (IIGR)</div>
                    </div>
                </div>
            </div>
        `;
    }
    
    async animarPrediccion(iigr) {
        const neuronasEntrada = document.getElementById('neuronas-entrada');
        const neuronasOculta1 = document.getElementById('neuronas-oculta1');
        const neuronasOculta2 = document.getElementById('neuronas-oculta2');
        const neuronasSalida = document.getElementById('neuronas-salida');
        
        // Crear neuronas
        neuronasEntrada.innerHTML = Array(12).fill().map(() => '<div class="neuron"></div>').join('');
        neuronasOculta1.innerHTML = Array(4).fill().map(() => '<div class="neuron"></div>').join('');
        neuronasOculta2.innerHTML = Array(3).fill().map(() => '<div class="neuron"></div>').join('');
        neuronasSalida.innerHTML = '<div class="neuron neuron-output">IIGR</div>';
        
        const neuronas = document.querySelectorAll('.neuron');
        
        // Animación: se encienden secuencialmente
        for (let i = 0; i < neuronas.length; i++) {
            if (i < 12) { // Capa de entrada
                await this.sleep(80);
                neuronas[i].classList.add('active');
            } else if (i < 16) { // Capa oculta 1
                await this.sleep(60);
                neuronas[i].classList.add('active');
            } else if (i < 19) { // Capa oculta 2
                await this.sleep(50);
                neuronas[i].classList.add('active');
            }
        }
        
        // Mostrar resultado
        await this.sleep(200);
        const salida = document.querySelector('.neuron-output');
        salida.innerHTML = `${Math.round(iigr)}%`;
        salida.classList.add('active');
        
        return iigr;
    }
    
    sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }
}