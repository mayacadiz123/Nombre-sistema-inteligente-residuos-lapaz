// Algoritmo Genético - Visualización de evolución
class AGEvolucion {
    constructor() {
        this.generaciones = [];
        this.fitnesses = [];
    }
    
    mostrarContenedor() {
        return `
            <div class="evolucion-container" id="evolucionContainer">
                <div style="text-align:center; color:#888; padding:20px;">
                    Esperando ejecución del sistema...
                </div>
            </div>
            <canvas id="graficaFitnessAG" width="400" height="150" style="margin-top:15px;"></canvas>
        `;
    }
    
    async simularEvolucion(rutaFinal, fitnessFinal, generaciones = 50) {
        const container = document.getElementById('evolucionContainer');
        if (!container) return;
        
        container.innerHTML = '';
        const fitnesses = [];
        const rutas = [];
        
        // Generar evolución simulada
        for (let i = 1; i <= generaciones; i++) {
            let fitness = fitnessFinal * (1 - Math.exp(-i / 15));
            fitness = Math.min(fitnessFinal, fitness + (Math.random() * 0.002));
            fitnesses.push(fitness);
            
            // Generar ruta intermedia
            let rutaIntermedia = [...rutaFinal];
            if (i < generaciones * 0.3) {
                rutaIntermedia = this.mezclarArray([...rutaFinal]);
            } else if (i < generaciones * 0.7) {
                rutaIntermedia = this.mezclarParcial([...rutaFinal]);
            }
            
            this.agregarLineaEvolucion(i, fitness, rutaIntermedia);
            await this.sleep(i < 20 ? 50 : 20);
        }
        
        // Línea final
        this.agregarLineaEvolucion(generaciones, fitnessFinal, rutaFinal, true);
        
        // Graficar evolución del fitness
        this.graficarEvolucion(fitnesses);
        
        return fitnesses;
    }
    
    agregarLineaEvolucion(generacion, fitness, ruta, esMejor = false) {
        const container = document.getElementById('evolucionContainer');
        if (!container) return;
        
        const div = document.createElement('div');
        div.className = 'evolucion-linea' + (esMejor ? ' mejor' : '');
        div.innerHTML = `Gen ${generacion}: Fitness = ${fitness.toFixed(6)} | ${ruta.join(' → ')}`;
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
    }
    
    graficarEvolucion(fitnesses) {
        const canvas = document.getElementById('graficaFitnessAG');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        canvas.width = canvas.clientWidth;
        canvas.height = canvas.clientHeight;
        
        const w = canvas.width;
        const h = canvas.height;
        const step = w / fitnesses.length;
        
        ctx.clearRect(0, 0, w, h);
        
        // Dibujar eje
        ctx.beginPath();
        ctx.strokeStyle = '#ccc';
        ctx.moveTo(40, 10);
        ctx.lineTo(40, h - 30);
        ctx.lineTo(w - 20, h - 30);
        ctx.stroke();
        
        // Dibujar línea de fitness
        ctx.beginPath();
        ctx.strokeStyle = '#0f3460';
        ctx.lineWidth = 2;
        
        const maxFitness = Math.max(...fitnesses);
        const minFitness = Math.min(...fitnesses);
        
        for (let i = 0; i < fitnesses.length; i++) {
            const x = 40 + i * step;
            const y = h - 30 - ((fitnesses[i] - minFitness) / (maxFitness - minFitness)) * (h - 50);
            
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.stroke();
        
        // Puntos
        for (let i = 0; i < fitnesses.length; i += 10) {
            const x = 40 + i * step;
            const y = h - 30 - ((fitnesses[i] - minFitness) / (maxFitness - minFitness)) * (h - 50);
            ctx.beginPath();
            ctx.fillStyle = '#0f3460';
            ctx.arc(x, y, 3, 0, 2 * Math.PI);
            ctx.fill();
        }
        
        // Etiquetas
        ctx.fillStyle = '#666';
        ctx.font = '10px Arial';
        ctx.fillText('0', 35, h - 25);
        ctx.fillText(`${fitnesses.length}`, w - 30, h - 25);
        ctx.fillText('Fitness', 10, 30);
    }
    
    mezclarArray(arr) {
        for (let i = arr.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [arr[i], arr[j]] = [arr[j], arr[i]];
        }
        return arr;
    }
    
    mezclarParcial(arr) {
        for (let i = 0; i < 3; i++) {
            const idx = Math.floor(Math.random() * (arr.length - 1)) + 1;
            [arr[idx], arr[idx - 1]] = [arr[idx - 1], arr[idx]];
        }
        return arr;
    }
    
    sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }
}