document.addEventListener('DOMContentLoaded', () => {
    const profileName = document.getElementById('profileName');
    const profileBio = document.getElementById('profileBio');
    const userAvatar = document.getElementById('userAvatar');
    
    const editModal = document.getElementById('editModal');
    const btnOpenEdit = document.getElementById('btnOpenEdit');
    const btnCancelEdit = document.getElementById('btnCancelEdit');
    const editProfileForm = document.getElementById('editProfileForm');
    
    const inputName = document.getElementById('inputName');
    const inputBio = document.getElementById('inputBio');
    
    const userGrid = document.getElementById('userGrid');

    const uploadedPhotos = [
        { id: 101, title: 'Mi espacio de trabajo', url: 'https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=500&auto=format&fit=crop&q=60' },
        { id: 102, title: 'Fotografía Urbana', url: 'https://images.unsplash.com/photo-1514565131-fce0801e5785?w=500&auto=format&fit=crop&q=60' },
        { id: 103, title: 'Librerías y Enfoque', url: 'https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?w=500&auto=format&fit=crop&q=60' },
        { id: 104, title: 'Explorando la Montaña', url: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=500&auto=format&fit=crop&q=60' },
        { id: 105, title: 'Código de noche', url: 'https://images.unsplash.com/photo-1607799279861-4dd421887fb3?w=500&auto=format&fit=crop&q=60' },
        { id: 106, title: 'Minimalist Architecture', url: 'https://images.unsplash.com/photo-1513694203232-719a280e022f?w=500&auto=format&fit=crop&q=60' }
    ];

    function renderUserGrid() {
        userGrid.innerHTML = '';
        uploadedPhotos.forEach(photo => {
            const card = document.createElement('div');
            card.classList.add('pub-card');
            
            card.innerHTML = `
                <img src="${photo.url}" alt="${photo.title}" loading="lazy">
            `;
            
            card.addEventListener('click', () => {
                const imgUrl = encodeURIComponent(photo.url);
                const title = encodeURIComponent(photo.title);
                window.location.href = `../previsualizacion/previsualizacion.html?img=${imgUrl}&title=${title}`;
            });

            userGrid.appendChild(card);
        });
    }

    btnOpenEdit.addEventListener('click', () => {
        inputName.value = profileName.textContent;
        inputBio.value = profileBio.textContent;
        
        editModal.classList.add('open');
    });

    function closeModal() {
        editModal.classList.remove('open');
    }

    btnCancelEdit.addEventListener('click', closeModal);

    editModal.addEventListener('click', (e) => {
        if (e.target === editModal) closeModal();
    });

    editProfileForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        profileName.textContent = inputName.value.trim();
        profileBio.textContent = inputBio.value.trim();
        
        if (inputName.value.length > 0) {
            userAvatar.textContent = inputName.value.charAt(0).toUpperCase();
        }

        console.log('Perfil actualizado con éxito:', {
            nuevoNombre: inputName.value,
            nuevaBio: inputBio.value
        });
        
        closeModal();
    });

    renderUserGrid();
});