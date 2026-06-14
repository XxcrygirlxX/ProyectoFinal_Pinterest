const usuarioId = localStorage.getItem("usuario_id");
const usernameLogueado = localStorage.getItem("username");

document.addEventListener("DOMContentLoaded", () => {
    if (!localStorage.getItem("usuario_autenticado") === "true" || !usuarioId) {
        window.location.href = "../login/login.html";
        return;
    }
    
    document.getElementById("profile-username").textContent = `@${usernameLogueado}`;
    cargarMisPines();
});

async function cargarMisPines() {
    const grid = document.getElementById("user-pin-grid");
    grid.innerHTML = "";

    try {
        const res = await fetch(`http://127.0.0.1:8000/api/v1/pins/user/${usuarioId}`);
        const pines = await res.json();

        document.getElementById("pin-count").textContent = pines.length;

        if (pines.length === 0) {
            grid.innerHTML = `<p style="color: var(--text-muted); text-align: center; width: 100%;">Aún no has publicado ninguna idea en Fyntasy.</p>`;
            return;
        }

        pines.forEach(pin => {
            const card = document.createElement("div");
            card.className = "pin-card";
            
            const rutaImagen = pin.source.startsWith("http") ? pin.source : `http://127.0.0.1:8000/${pin.source}`;

            card.innerHTML = `
                <img src="${rutaImagen}" alt="${pin.titulo}" style="cursor: pointer;" onclick="location.href='../previsualizacion/previsualizacion.html?id=${pin.id}'">
                <div class="pin-info">
                    <h4>${pin.titulo}</h4>
                    <p>${pin.descripcion || 'Sin descripción.'}</p>
                </div>
            `;
            grid.appendChild(card);
        });
    } catch (e) { console.error("Error cargando galería del perfil", e); }
}