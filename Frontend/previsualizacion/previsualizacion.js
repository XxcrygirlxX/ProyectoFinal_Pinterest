const urlParams = new URLSearchParams(window.location.search);
const pinId = urlParams.get('id');
const API_BASE = "http://18.225.168.210:8000/api/v1/pins";
const usuarioAutenticado = localStorage.getItem("usuario_autenticado") === "true";

document.addEventListener("DOMContentLoaded", () => {
    if (!pinId) { window.location.href = "../index.html"; return; }
    cargarDetalles();
    cargarComentarios();
    initializeCajaComentarios();
    configurarBotonReporte();
});

async function cargarDetalles() {
    try {
        const res = await fetch(`${API_BASE}/${pinId}`);
        if (!res.ok) throw new Error();
        const pin = await res.json();

        const badge = document.getElementById("pin-category-tag");
        if(badge) badge.innerHTML = `<i class="fa-solid fa-server" aria-hidden="true"></i> ${pin.categoria.toUpperCase()}`;

        document.getElementById("pin-title").textContent = pin.titulo;
        document.getElementById("pin-author").textContent = `@${pin.username_autor || 'System_User'}`;
        document.getElementById("pin-description").textContent = pin.descripcion || "Sin descripción.";
        
        const imgElement = document.getElementById("pin-image");
        imgElement.src = pin.source;
        imgElement.alt = `Fotografía titulada: ${pin.titulo}`;
    } catch (e) { window.location.href = "../index.html"; }
}

async function cargarComentarios() {
    const lista = document.getElementById("comments-list");
    if (!lista) return;
    lista.innerHTML = "";
    try {
        const res = await fetch(`${API_BASE}/${pinId}/comments`);
        const comentarios = await res.json();

        if (comentarios.length === 0) {
            lista.innerHTML = `<p style="color: var(--text-muted); font-size: 0.85rem; text-align: center; padding: 1rem;">No se registran comentarios aún.</p>`;
            return;
        }

        comentarios.forEach(c => {
            const item = document.createElement("div");
            item.className = "comment-item";
            item.innerHTML = `<strong>@${c.username_autor}</strong><p>${c.texto}</p>`;
            lista.appendChild(item);
        });
        lista.scrollTop = lista.scrollHeight;
    } catch (e) { console.error(e); }
}

function initializeCajaComentarios() {
    const contenedor = document.getElementById("comment-box-wrapper");
    if (!contenedor) return;
    if (usuarioAutenticado) {
        contenedor.innerHTML = `
            <form class="comment-form" id="comment-form">
                <input type="text" id="comment-text" required placeholder="Escribir una aportación..." aria-label="Campo para redactar un comentario">
                <button type="submit" class="btn-comment-submit" aria-label="Enviar datos al endpoint de comentarios">Enviar</button>
            </form>
        `;
        document.getElementById("comment-form").addEventListener("submit", publicarComentario);
    } else {
        contenedor.innerHTML = `<p style="font-size: 0.85rem; color: var(--pink-dark); text-align: center; padding: 0.5rem;">Autenticación requerida para habilitar comentarios.</p>`;
    }
}

async function publicarComentario(e) {
    e.preventDefault();
    const input = document.getElementById("comment-text");
    const texto = input.value.trim();

    const formData = new FormData();
    formData.append("texto", texto);
    formData.append("usuario_id", localStorage.getItem("usuario_id") || "1");
    formData.append("username_autor", localStorage.getItem("username") || "Fyntasy_User");

    try {
        const res = await fetch(`${API_BASE}/${pinId}/comments`, { method: "POST", body: formData });
        const data = await res.json();
        if (res.ok) {
            input.value = "";
            cargarComentarios();
        } else {
            alert(`Excepción del validador: ${data.detail}`);
        }
    } catch (err) { console.error(err); }
}

function configurarBotonReporte() {
    const btnReportar = document.getElementById("btn-reportar-detalle");
    if (!btnReportar) return;

    btnReportar.addEventListener("click", async () => {
        const usuarioId = localStorage.getItem("usuario_id");
        if (!usuarioId) {
            alert("Autenticación requerida para realizar reportes.");
            return;
        }
        if (!confirm("¿Confirmar registro de reporte técnico sobre este pin?")) return;

        const formData = new FormData();
        formData.append("usuario_id", usuarioId);

        try {
            const response = await fetch(`${API_BASE}/${pinId}/report`, { method: "POST", body: formData });
            const data = await response.json();
            alert(data.message);
            if (response.ok && data.message.includes("retirado")) {
                window.location.href = "../index.html";
            }
        } catch (e) {
            console.error("Error al procesar el reporte:", e);
            alert("Fallo de red en el servicio de reportes.");
        }
    });
}