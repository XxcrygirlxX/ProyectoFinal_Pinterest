import { pins } from './data.js';

document.addEventListener('DOMContentLoaded', () => {
    const pinGrid = document.getElementById('pinGrid');

    function renderPins(listaDePins) {
        pinGrid.innerHTML = ''; 
        
        listaDePins.forEach(pin => {
            const pinCard = document.createElement('div');
            pinCard.classList.add('pin-card');
            
            pinCard.innerHTML = `
                <img src="${pin.source}" alt="${pin.titulo}" loading="lazy">
                <div class="pin-overlay">
                    <button class="btn-save">Guardar</button>
                    <div class="overlay-bottom">
                        <button class="btn-icon-action" title="Compartir"><i class="fa-solid fa-share-nodes"></i></button>
                    </div>
                </div>
            `;
            pinCard.addEventListener('click', () => {
                const url = `./previsualizacion/previsualizacion.html?img=${encodeURIComponent(pin.source)}&title=${encodeURIComponent(pin.titulo)}`;
                window.location.href = url;
            });
            
            pinGrid.appendChild(pinCard);
        });
    }
    renderPins(pins);
});