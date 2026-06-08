document.addEventListener('DOMContentLoaded', () => {
    const pinImage = document.getElementById('pinImage');
    const pinTitle = document.getElementById('pinTitle');
    const btnBack = document.getElementById('btnBack');
    const btnSave = document.getElementById('btnSave');

    const urlParams = new URLSearchParams(window.location.search);
    const imageUrl = urlParams.get('img');
    const titleText = urlParams.get('title');

    if (imageUrl && titleText) {
        pinImage.src = decodeURIComponent(imageUrl);
        pinImage.alt = decodeURIComponent(titleText);
        pinTitle.textContent = decodeURIComponent(titleText);
    } else {
        pinTitle.textContent = "Idea del Laboratorio de Sistemas";
        pinImage.src = "https://images.unsplash.com/photo-1557683316-973673baf926?w=500"; 
    }

    if (btnBack) {
        btnBack.addEventListener('click', () => {
            window.location.href = '../index.html';
        });
    }

    if (btnSave) {
        btnSave.addEventListener('click', () => {
            const usuarioSesion = localStorage.getItem('usuario') || "Invitado";
            alert(`¡Guardado exitoso! Hola ${usuarioSesion}, has añadido "${pinTitle.textContent}" a tu tablero corporativo.`);
        });
    }
});

const API_URL = "http://127.0.0.1:8000/pins";

document.addEventListener('DOMContentLoaded', () => {
    // ... tu código existente para cargar la imagen en la vista ...
    const urlParams = new URLSearchParams(window.location.search);
    const pinId = urlParams.get('id'); // ID del pin que pasamos en el script.js
    const usuarioId = localStorage.getItem('usuario_id'); 

    const btnSave = document.getElementById('btnSave');

    // Funcionalidad de GUARDAR PIN REAL
    if (btnSave) {
        btnSave.addEventListener('click', async () => {
            if (!usuarioId) {
                alert("Debes iniciar sesión para guardar pines");
                return;
            }

            try {
                // Asumimos un tablero_id por defecto (ej. 1) para simplificar
                const response = await fetch(`${API_URL}/${pinId}/guardar?tablero_id=1&usuario_id=${usuarioId}`, {
                    method: 'POST'
                });
                
                if (response.ok) {
                    btnSave.textContent = "Guardado";
                    btnSave.style.backgroundColor = "black";
                    alert("¡Pin guardado en tu tablero exitosamente!");
                }
            } catch (error) {
                console.error("Error al guardar:", error);
            }
        });
    }

    // Extra: Si quieres listar los comentarios reales, puedes llamar al endpoint
    // fetch(`${API_URL}/${pinId}/comentarios`).then(...)
});