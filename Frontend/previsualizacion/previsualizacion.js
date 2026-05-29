document.addEventListener('DOMContentLoaded', () => {
    const pinImage = document.getElementById('pinImage');
    const pinTitle = document.getElementById('pinTitle');
    const btnBack = document.getElementById('btnBack');
    const btnSave = document.getElementById('btnSave');

    // 1. Obtener los parámetros de la URL actual
    const urlParams = new URLSearchParams(window.location.search);
    const imageUrl = urlParams.get('img');
    const titleText = urlParams.get('title');

    // 2. Inyectar los datos capturados en los nodos del DOM
    if (imageUrl && titleText) {
        pinImage.src = decodeURIComponent(imageUrl);
        pinImage.alt = decodeURIComponent(titleText);
        pinTitle.textContent = decodeURIComponent(titleText);
    } else {
        // Fallback por si entran directo sin dar click a una imagen
        pinTitle.textContent = "Idea sin título";
        pinImage.src = "https://images.unsplash.com/photo-1557683316-973673baf926?w=500"; 
    }

    // Botón Volver al inicio (Sale de previsualizacion y va a la raíz)
    btnBack.addEventListener('click', () => {
        window.location.href = '../index.html';
    });

    // Acción de Guardar integrada
    btnSave.addEventListener('click', () => {
        alert(`¡Guardaste "${pinTitle.textContent}" en tu colección!`);
    });
});