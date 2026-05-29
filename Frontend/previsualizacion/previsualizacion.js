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

        pinTitle.textContent = "Idea sin título";
        pinImage.src = "https://images.unsplash.com/photo-1557683316-973673baf926?w=500"; 
    }

    btnBack.addEventListener('click', () => {
        window.location.href = '../index.html';
    });

    btnSave.addEventListener('click', () => {
        alert(`¡Guardaste "${pinTitle.textContent}" en tu colección!`);
    });
});