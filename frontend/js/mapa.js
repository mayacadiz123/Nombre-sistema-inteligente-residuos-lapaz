// Mapa de La Paz con marcadores y ruta
class MapaLaPaz {
    constructor() {
        this.distritos = [
            { nombre: 'CENTRO', x: 45, y: 42 },
            { nombre: 'MAX PAREDES', x: 30, y: 30 },
            { nombre: 'COTAHUMA', x: 65, y: 35 },
            { nombre: 'SUR', x: 75, y: 65 },
            { nombre: 'PERIFERICA', x: 20, y: 70 }
        ];
    }
    
    mostrarMapa(prioridades, ruta) {
        return `
            <div style="position: relative; width: 100%;">
                <img src="assets/mapa.png" alt="Mapa de La Paz" style="width: 100%; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); display: block;">
                <div id="marcadoresMapa" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></div>
            </div>
            <div id="rutaSvgContainer" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;"></div>
        `;
    }
    
    dibujarMarcadores(prioridades) {
        const container = document.getElementById('marcadoresMapa');
        if (!container) return;
        
        const marcadores = this.distritos.map(d => {
            const prioridad = prioridades[d.nombre] || prioridades[d.nombre.charAt(0).toUpperCase() + d.nombre.slice(1).toLowerCase()] || 40;
            let color = prioridad >= 70 ? '#dc3545' : prioridad >= 50 ? '#fd7e14' : prioridad >= 30 ? '#ffc107' : '#28a745';
            let size = 40 + (prioridad / 100) * 20;
            
            return `<div style="position: absolute; left: ${d.x}%; top: ${d.y}%; width: ${size}px; height: ${size}px; background: ${color}; border-radius: 50%; display: flex; align-items: center; justify-content: center; transform: translate(-50%, -50%); box-shadow: 0 3px 10px rgba(0,0,0,0.3); border: 2px solid white; font-size: 10px; font-weight: bold; color: white; text-align: center; z-index: 10;" title="${d.nombre}: ${prioridad.toFixed(1)}%">${d.nombre}</div>`;
        }).join('');
        
        container.innerHTML = marcadores;
        return this.distritos;
    }
    
    dibujarRuta(ruta, prioridades) {
        const container = document.getElementById('marcadoresMapa');
        if (!container) return;
        
        // Obtener coordenadas de la ruta
        const coords = [];
        for (let i = 0; i < ruta.length; i++) {
            const nombreRuta = ruta[i].toUpperCase();
            const distrito = this.distritos.find(d => d.nombre === nombreRuta || d.nombre.includes(nombreRuta));
            if (distrito) coords.push(distrito);
        }
        
        // Dibujar líneas SVG
        let lineasSvg = '';
        for (let i = 0; i < coords.length - 1; i++) {
            lineasSvg += `<line x1="${coords[i].x}%" y1="${coords[i].y}%" x2="${coords[i+1].x}%" y2="${coords[i+1].y}%" stroke="#0f3460" stroke-width="4" stroke-dasharray="8,4" style="filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));"/>`;
        }
        
        // Añadir flechas
        for (let i = 0; i < coords.length - 1; i++) {
            const dx = coords[i+1].x - coords[i].x;
            const dy = coords[i+1].y - coords[i].y;
            const angle = Math.atan2(dy, dx) * 180 / Math.PI;
            const midX = (coords[i].x + coords[i+1].x) / 2;
            const midY = (coords[i].y + coords[i+1].y) / 2;
            lineasSvg += `<polygon points="${midX-2},${midY-4} ${midX+2},${midY-4} ${midX},${midY+2}" fill="#0f3460" style="transform: rotate(${angle}deg); transform-origin: ${midX}% ${midY}%;"/>`;
        }
        
        const svg = `<svg style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;">${lineasSvg}</svg>`;
        
        // Agregar al contenedor
        const existingSvg = container.querySelector('svg');
        if (existingSvg) existingSvg.remove();
        container.insertAdjacentHTML('beforeend', svg);
    }
}