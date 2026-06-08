const API_URL = "http://127.0.0.1:8000";

document.addEventListener('DOMContentLoaded', () => {
    const usuarioId = localStorage.getItem('usuario_id');
    const profileName = document.getElementById('profileName');
    const profileBio = document.getElementById('profileBio');
    const userGrid = document.getElementById('userGrid');
    const editProfileForm = document.getElementById('editProfileForm');

    if (!usuarioId) {
        alert("Debes iniciar sesión para ver tu perfil");
        window.location.href = '../login/login.html';
        return;
    }

    // 1. Cargar los pines creados por el usuario
    async function cargarPinesCreados() {
        try {
            const response = await fetch(`${API_URL}/perfil/${usuarioId}/pines-creados`);
            const pines = await response.json();
            renderUserGrid(pines);
        } catch (error) {
            console.error("Error al cargar pines", error);
        }
    }

    // 2. Renderizar los pines en la grilla
    function renderUserGrid(pines) {
        userGrid.innerHTML = '';
        if (pines.length === 0) {
            userGrid.innerHTML = "<p>Aún no tienes pines.</p>";
            return;
        }

        pines.forEach(pin => {
            const card = document.createElement('div');
            card.classList.add('pub-card');
            // Cargar imagen servida desde el backend
            card.innerHTML = `<img src="http://127.0.0.1:8000${pin.source}" alt="${pin.titulo}" loading="lazy">`;
            
            card.addEventListener('click', () => {
                window.location.href = `../previsualizacion/previsualizacion.html?img=${encodeURIComponent('http://127.0.0.1:8000'+pin.source)}&title=${encodeURIComponent(pin.titulo)}&id=${pin.id}`;
            });
            userGrid.appendChild(card);
        });
    }

    // 3. Guardar cambios del perfil en la Base de Datos
    editProfileForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const inputName = document.getElementById('inputName').value;
        const inputBio = document.getElementById('inputBio').value;

        try {
            const response = await fetch(`${API_URL}/perfil/${usuarioId}?nombre=${inputName}&biografia=${inputBio}`, {
                method: 'PUT'
            });
            if (response.ok) {
                profileName.textContent = inputName;
                profileBio.textContent = inputBio;
                document.getElementById('editModal').classList.remove('open');
                alert("Perfil actualizado");
            }
        } catch (error) {
            console.error("Error al actualizar", error);
        }
    });

    cargarPinesCreados();
});

// Abrir el modal
document.querySelectorAll('.nav-btn')[1].addEventListener('click', () => {
    document.getElementById('modalCrearPin').style.display = 'flex';
});

// Enviar el archivo al backend
document.getElementById('formCrearPin').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const titulo = document.getElementById('pinTitulo').value;
    const archivo = document.getElementById('pinArchivo').files[0];
    
    // IMPORTANTE: Para enviar archivos no se usa JSON, se usa FormData
    const formData = new FormData();
    formData.append('titulo', titulo);
    formData.append('file', archivo);

    try {
        const res = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        if (res.ok) {
            alert("Pin creado exitosamente (Aprobado por IA)");
            document.getElementById('modalCrearPin').style.display = 'none';
            cargarPines(); // Recargar el feed
        } else {
            const error = await res.json();
            alert(`Error: ${error.detail}`); // Aquí saltará si es NSFW o Mala Palabra
        }
    } catch (err) {
        console.error(err);
    }
});