const IP_SERVIDOR = "127.0.0.1";
const urlParams = new URLSearchParams(window.location.search);
const pinId = urlParams.get('id');
const API_BASE = `http://${IP_SERVIDOR}:8000/api/v1/pins`;
const usuarioAutenticado = localStorage.getItem("usuario_autenticado") === "true";

let urlDeLaImagenAws = "";

document.addEventListener("DOMContentLoaded", () => {
    if (!pinId) { window.location.href = "../index.html"; return; }
    cargarDetalles();
    cargarComentarios();
    inicializarCajaComentarios();
    configurarControlesSociales();
});

async function cargarDetalles() {
    try {
        const res = await fetch(`${API_BASE}/${pinId}`);
        if (!res.ok) throw new Error();
        const pin = await res.json();

        urlDeLaImagenAws = pin.source;

        const badge = document.getElementById("pin-category-tag");
        if(badge) badge.innerHTML = `<i class="fa-solid fa-sparkles"></i> ${pin.categoria.toUpperCase()}`;

        document.getElementById("pin-title").textContent = pin.titulo;
        document.getElementById("pin-author").textContent = `@${pin.username_autor || 'Fyntasy_Girl'}`;
        document.getElementById("pin-description").textContent = pin.descripcion || "Sin descripción.";
        document.getElementById("pin-image").src = pin.source;
    } catch (e) { 
        window.location.href = "../index.html"; 
    }
}

async function cargarComentarios() {
    const lista = document.getElementById("comments-list");
    if (!lista) return;
    lista.innerHTML = "";
    try {
        const res = await fetch(`${API_BASE}/${pinId}/comments`);
        const comentarios = await res.json();

        if (comentarios.length === 0) {
            lista.innerHTML = `<p style="color: var(--text-muted); font-size: 0.85rem; text-align: center; padding: 1rem;">Sé el primero en dejar un comentario.</p>`;
            return;
        }

        comentarios.forEach(c => {
            const item = document.createElement("div");
            item.className = "comment-item";
            item.innerHTML = `<strong>@${c.username_autor}</strong><p>${c.texto}</p>`;
            lista.appendChild(item);
        });
        lista.scrollTop = lista.scrollHeight;
    } catch (e) { 
        console.error(e); 
    }
}

function inicializarCajaComentarios() {
    const contenedor = document.getElementById("comment-box-wrapper");
    if (!contenedor) return;
    if (usuarioAutenticado) {
        contenedor.innerHTML = `
            <form class="comment-form" id="comment-form">
                <input type="text" id="comment-text" required placeholder="Añade un comentario tierno...">
                <button type="submit" class="btn-comment-submit">Enviar</button>
            </form>
        `;
        document.getElementById("comment-form").addEventListener("submit", publicarComentario);
    } else {
        contenedor.innerHTML = `<p style="font-size: 0.85rem; color: var(--pink-dark); text-align: center; padding: 0.5rem;">Debes iniciar sesión para comentar.</p>`;
    }
}

async function publicarComentario(e) {
    e.preventDefault();
    const input = document.getElementById("comment-text");
    const texto = input.value.trim();

    const formData = new FormData();
    formData.append("texto", texto);
    formData.append("usuario_id", localStorage.getItem("usuario_id") || "1");
    formData.append("username_autor", localStorage.getItem("username") || "Fyntasy_Girl");

    try {
        const res = await fetch(`${API_BASE}/${pinId}/comments`, { method: "POST", body: formData });
        const data = await res.json();
        if (res.ok) {
            input.value = "";
            cargarComentarios();
        } else {
            alert(`Filtro: ${data.detail}`);
        }
    } catch (err) { console.error(err); }
}

function configurarControlesSociales() {
    const btnReportar = document.getElementById("btn-reportar-detalle");
    const btnCopiar = document.getElementById("btn-copiar-enlace");

    if (btnCopiar) {
        btnCopiar.addEventListener("click", () => {
            if (!urlDeLaImagenAws) return;
            navigator.clipboard.writeText(urlDeLaImagenAws);
            alert("¡Link directo de AWS S3 copiado al portapapeles!");
        });
    }

    if (btnReportar) {
        btnReportar.addEventListener("click", async () => {
            const usuarioId = localStorage.getItem("usuario_id");
            if (!usuarioId) { alert("Inicia sesión para reportar."); return; }
            if (!confirm("¿Reportar esta idea? Al acumular 3 reportes se borrará de forma definitiva.")) return;

            const formData = new FormData();
            formData.append("usuario_id", usuarioId);

            try {
                const res = await fetch(`${API_BASE}/${pinId}/report`, { method: "POST", body: formData });
                const data = await res.json();
                alert(data.message || data.detail);
                
                let reportados = JSON.parse(localStorage.getItem("fyntasy_mis_reportes") || "[]");
                if(!reportados.includes(Number(pinId))) {
                    reportados.push(Number(pinId));
                    localStorage.setItem("fyntasy_mis_reportes", JSON.stringify(reportados));
                }
                
                window.location.href = "../index.html"; 
            } catch (e) { console.error(e); }
        });
    }
}