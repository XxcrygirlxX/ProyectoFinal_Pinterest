const API_URL = "http://127.0.0.1:8000/api/v1/pins";
let usuarioAutenticado = localStorage.getItem("usuario_autenticado") === "true";
let datosPines = []; 
let categoriaActual = "todas"; // Control global de categoría

document.addEventListener("DOMContentLoaded", () => {
    inicializarNavbar();
    cargarFeedPines();
    configurarEventos();
    configurarFiltrosCategorias();
});

function inicializarNavbar() {
    const contenedorAcciones = document.getElementById("auth-actions");
    if (!contenedorAcciones) return;
    contenedorAcciones.innerHTML = "";

    if (usuarioAutenticado) {
        contenedorAcciones.innerHTML = `
            <button class="btn-nav" id="btn-abrir-crear"><i class="fa-solid fa-plus"></i> Crear</button>
            <button class="btn-auth-outline" onclick="location.href='profile/profile.html'"><i class="fa-solid fa-user"></i> Mi Perfil</button>
            
            <button class="btn-nav" id="btn-logout" title="Cerrar Sesión / Cambiar Usuario" style="background-color: #fff0f3; color: #ff4d6d; border: 1px solid #ffe3e8; margin-left: 8px;">
                <i class="fa-solid fa-right-from-bracket"></i> Salir
            </button>
        `;
        document.getElementById("btn-abrir-crear").addEventListener("click", abrirModalCrear);
        document.getElementById("btn-logout").addEventListener("click", () => {
            localStorage.clear();
            usuarioAutenticado = false;
            alert("Sesión cerrada. ¡Vuelve pronto a Fyntasy!");
            location.reload();
        });
    } else {
        contenedorAcciones.innerHTML = `
            <button class="btn-auth-outline" onclick="location.href='login/login.html'">Iniciar Sesión</button>
            <button class="btn-nav" onclick="location.href='register/register.html'">Registrarse</button>
        `;
    }
}

// Carga con soporte dinámico para las 3 categorías en Fyntasy
async function cargarFeedPines() {
    const grid = document.getElementById("pin-grid");
    if (!grid) return;
    grid.innerHTML = `<p style="color: var(--text-gray); text-align: center; width:100%;">Cargando tu inspiración en Fyntasy...</p>`;
    
    // Si hay una categoría seleccionada, la pasamos como parámetro URL query
    let urlDestino = API_URL;
    if (categoriaActual !== "todas") {
        urlDestino += `?categoria=${categoriaActual}`;
    }

    try {
        const res = await fetch(urlDestino);
        datosPines = await res.json();
        renderizarPines(datosPines);
    } catch (error) {
        grid.innerHTML = `<p style="color: var(--pink-dark); text-align: center;">Error al conectar con Fyntasy.</p>`;
    }
}

function renderizarPines(pines) {
    const grid = document.getElementById("pin-grid");
    if (!grid) return;
    grid.innerHTML = "";

    if (pines.length === 0) {
        grid.innerHTML = `<p style="color: var(--text-gray); text-align: center; width: 100%;">Aún no hay pines publicados.</p>`;
        return;
    }

    pines.forEach(pin => {
        if (!pin.reportado && pin.es_publico) {
            const card = document.createElement("div");
            card.className = "pin-card";
            const rutaImagen = pin.source.startsWith("http") ? pin.source : `http://127.0.0.1:8000/${pin.source}`;
            const botonReporte = usuarioAutenticado 
                ? `<button class="btn-report" onclick="ejecutarReporte(${pin.id})"><i class="fa-solid fa-flag"></i></button>`
                : `<button class="btn-report" onclick="alert('Inicia sesión para reportar.')" style="opacity:0.3;"><i class="fa-solid fa-flag"></i></button>`;

            card.innerHTML = `
                <img src="${rutaImagen}" style="cursor: pointer;" onclick="location.href='previsualizacion/previsualizacion.html?id=${pin.id}'">
                <div class="pin-info">
                    <h4 style="cursor: pointer;" onclick="location.href='previsualizacion/previsualizacion.html?id=${pin.id}'">${pin.titulo}</h4>
                    <p>${pin.descripcion || 'Sin descripción.'}</p>
                    <div class="pin-footer">
                        <span style="font-size: 0.8rem; color: var(--pink-dark); font-weight:600;"><i class="fa-solid fa-heart"></i> Fyntasy • <small style="text-transform: capitalize;">${pin.categoria}</small></span>
                        ${botonReporte}
                    </div>
                </div>
            `;
            grid.appendChild(card);
        }
    });
}

// Configuración de los chips de filtrado visual
function configurarFiltrosCategorias() {
    const chips = document.querySelectorAll(".category-chip");
    chips.forEach(chip => {
        chip.addEventListener("click", (e) => {
            chips.forEach(c => c.classList.remove("active"));
            chip.classList.add("active");
            categoriaActual = chip.getAttribute("data-category");
            cargarFeedPines(); // Recarga instantánea filtrada por backend
        });
    });
}

function configurarEventos() {
    const volverInicio = () => {
        document.getElementById("search-input").value = "";
        categoriaActual = "todas";
        const chips = document.querySelectorAll(".category-chip");
        chips.forEach(c => c.classList.remove("active"));
        if(chips[0]) chips[0].classList.add("active");
        cargarFeedPines();
    };
    if (document.getElementById("btn-inicio")) document.getElementById("btn-inicio").addEventListener("click", volverInicio);
    if (document.getElementById("btn-logo")) document.getElementById("btn-logo").addEventListener("click", volverInicio);

    if (document.getElementById("search-input")) {
        document.getElementById("search-input").addEventListener("input", (e) => {
            const busqueda = e.target.value.toLowerCase().trim();
            const filtrados = datosPines.filter(p => p.titulo.toLowerCase().includes(busqueda) || (p.descripcion && p.descripcion.toLowerCase().includes(busqueda)));
            renderizarPines(filtrados);
        });
    }
    if (document.getElementById("close-modal-btn")) document.getElementById("close-modal-btn").addEventListener("click", cerrarModalCrear);
    if (document.getElementById("upload-form")) document.getElementById("upload-form").addEventListener("submit", procesarNuevoPin);
}

function abrirModalCrear() {
    const modal = document.getElementById("upload-modal");
    if (modal) modal.style.display = "flex";
}

function cerrarModalCrear() {
    const modal = document.getElementById("upload-modal");
    if (modal) modal.style.display = "none";
    document.getElementById("upload-form").reset();
}

async function procesarNuevoPin(e) {
    e.preventDefault();
    const titulo = document.getElementById("pin-title").value.trim();
    const descripcion = document.getElementById("pin-description").value.trim();
    const categoria = document.getElementById("pin-category").value; // Captura la categoría elegida
    const archivoInput = document.getElementById("pin-file");
    const usuarioId = localStorage.getItem("usuario_id");

    if (!usuarioId) { alert("Inicia sesión."); return; }

    const formData = new FormData();
    formData.append("titulo", titulo);
    formData.append("descripcion", descripcion);
    formData.append("categoria", categoria);
    formData.append("usuario_id", usuarioId);
    formData.append("file", archivoInput.files[0]);

    try {
        const response = await fetch("http://127.0.0.1:8000/api/v1/pins/upload", { method: "POST", body: formData });
        const data = await response.json();
        if (response.ok) {
            alert("¡Pin aprobado y publicado con éxito en Fyntasy! ✨");
            cerrarModalCrear();
            cargarFeedPines();
        } else {
            // Muestra de forma elegante el mensaje detallado de la IA o de las palabras obscenas
            alert(`Filtro Fyntasy: ${data.detail}`);
        }
    } catch (error) { alert("Error al conectar con el servidor."); }
}

async function ejecutarReporte(id) {
    const usuarioId = localStorage.getItem("usuario_id");
    if (!usuarioId) {
        alert("Debes iniciar sesión para cuidar la comunidad de Fyntasy.");
        return;
    }

    if (!confirm("¿Deseas reportar esta idea? Si un Pin recibe 3 reportes de usuarios distintos, será eliminado permanentemente de la plataforma.")) return;

    const formData = new FormData();
    formData.append("usuario_id", usuarioId);

    try {
        const response = await fetch(`http://127.0.0.1:8000/api/v1/pins/${id}/report`, { 
            method: "POST",
            body: formData 
        });
        const data = await response.json();
        
        if (response.ok) { 
            alert(data.message); // Avisa si va 1/3, 2/3 o si ya se borró
            cargarFeedPines(); 
        } else {
            alert(`Error: ${data.detail}`);
        }
    } catch (e) { console.error(e); }
}