const usuarioId = localStorage.getItem("usuario_id");
const usernameLogueado = localStorage.getItem("username");
const usuarioAutenticado = localStorage.getItem("usuario_autenticado") === "true";

document.addEventListener("DOMContentLoaded", () => {
    console.log("=== COMPROBACIÓN DE PERFIL FYNTASY ===");
    console.log("Usuario Autenticado:", usuarioAutenticado);
    console.log("ID de Usuario:", usuarioId);
    console.log("Username:", usernameLogueado);

    // Corrección de la validación lógica para evitar bloqueos falsos
    if (!usuarioAutenticado || !usuarioId) {
        console.warn("Acceso denegado: Redireccionando al login...");
        window.location.href = "../login/login.html";
        return;
    }
    
    // Asignación segura de textos en el HTML
    const elUsername = document.getElementById("profile-username");
    if (elUsername) {
        elUsername.textContent = `@${usernameLogueado}`;
    }

    // Ejecutar la carga de pines reales del usuario
    cargarMisPines();
});

async function cargarMisPines() {
    const grid = document.getElementById("user-pin-grid");
    const contadorPines = document.getElementById("pin-count");

    if (!grid) {
        console.error("Error: No se encontró el contenedor 'user-pin-grid' en el HTML.");
        return;
    }

    grid.innerHTML = `<p style="color: var(--text-muted); text-align: center; width: 100%; padding: 2rem;">Cargando tus pines creados...</p>`;

    try {
        console.log(`Solicitando pines al backend para el usuario ID: ${usuarioId}`);
        const res = await fetch(`http://127.0.0.1:8000/api/v1/pins/user/${usuarioId}`);
        
        if (!res.ok) {
            throw new Error(`El servidor respondió con estado: ${res.status}`);
        }

        const pines = await res.json();
        console.log("Pines recibidos desde el backend:", pines);

        // Actualizar el contador del perfil en tiempo real
        if (contadorPines) {
            contadorPines.textContent = pines.length;
        }

        grid.innerHTML = ""; // Limpiar mensaje de carga

        if (pines.length === 0) {
            grid.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--text-muted);">
                    <i class="fa-solid fa-folder-open" style="font-size: 2.5rem; color: var(--pink-accent); margin-bottom: 1rem; display: block;"></i>
                    <p style="margin: 0; font-size: 0.95rem;">Aún no has publicado ninguna idea hermosa en Fyntasy.</p>
                </div>
            `;
            return;
        }

        // Renderizar cada una de tus publicaciones en el Masonry del perfil
        pines.forEach(pin => {
            const card = document.createElement("div");
            card.className = "pin-card";
            
            // Validación de rutas de imágenes locales vs externas
            const rutaImagen = pin.source.startsWith("http") 
                ? pin.source 
                : `http://127.0.0.1:8000/${pin.source}`;

            card.innerHTML = `
                <img src="${rutaImagen}" alt="${pin.titulo}" style="cursor: pointer;" onclick="location.href='../previsualizacion/previsualizacion.html?id=${pin.id}'">
                <div class="pin-info">
                    <h4>${pin.titulo}</h4>
                    <p style="font-size: 0.78rem; color: var(--pink-dark); text-transform: uppercase; font-weight: 700; margin-top: 5px;">
                        <i class="fa-solid fa-sparkles"></i> ${pin.categoria}
                    </p>
                </div>
            `;
            grid.appendChild(card);
        });

    } catch (error) {
        console.error("Error crítico al cargar galería del perfil:", error);
        grid.innerHTML = `<p style="color: var(--pink-dark); text-align: center; width: 100%;">No se pudo conectar con el servidor para obtener tus publicaciones.</p>`;
    }
}