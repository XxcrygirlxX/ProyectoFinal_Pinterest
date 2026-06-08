const API_URL = "http://127.0.0.1:8000/pins";

document.addEventListener('DOMContentLoaded', () => {
    const pinGrid = document.getElementById('pinGrid');
    const btnNavCrear = document.getElementById('btnNavCrear');
    const modalCrearPin = document.getElementById('modalCrearPin');
    const formCrearPin = document.getElementById('formCrearPin');
    
    verificarEstadoSesion();

    async function cargarPines() {
        try {
            const response = await fetch(API_URL);
            if (!response.ok) throw new Error("Error de comunicación con el backend");
            const pines = await response.json();
            renderPins(pines);
        } catch (error) {
            console.error(error);
            pinGrid.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; color: #767676; padding: 40px;">
                    <i class="fa-solid fa-server" style="font-size: 30px; margin-bottom: 10px;"></i>
                    <p>La API de Pinterest está fuera de línea.</p>
                </div>`;
        }
    }

    function renderPins(listaDePins) {
        pinGrid.innerHTML = ''; 
        
        if (listaDePins.length === 0) {
            pinGrid.innerHTML = `<p style="grid-column: 1/-1; text-align: center; color: #767676;">No hay pines disponibles aprobados por moderación.</p>`;
            return;
        }

        listaDePins.forEach(pin => {
            const pinCard = document.createElement('div');
            pinCard.classList.add('pin-card');
            
            pinCard.innerHTML = `
                <img src="http://127.0.0.1:8000${pin.source}" alt="${pin.titulo}" loading="lazy">
                <div class="pin-overlay">
                    <button class="btn-save">Guardar</button>
                    <div class="overlay-bottom">
                        <button class="btn-icon-action btn-share" title="Compartir">
                            <i class="fa-solid fa-arrow-up-right-from-square"></i>
                        </button>
                        <button class="btn-icon-action btn-report" title="Reportar Imagen" data-id="${pin.id}">
                            <i class="fa-solid fa-flag"></i>
                        </button>
                    </div>
                </div>
            `;

            pinCard.addEventListener('click', (e) => {
                if (e.target.closest('.btn-save') || e.target.closest('.btn-icon-action')) {
                    return; 
                }
                window.location.href = `./previsualizacion/previsualizacion.html?img=${encodeURIComponent('http://127.0.0.1:8000'+pin.source)}&title=${encodeURIComponent(pin.titulo)}&id=${pin.id}`;
            });

            const reportBtn = pinCard.querySelector('.btn-report');
            reportBtn.addEventListener('click', async (e) => {
                e.stopPropagation(); 
                const pinId = reportBtn.getAttribute('data-id');
                await ejecutarReporte(pinId);
            });

            pinGrid.appendChild(pinCard);
        });
    }

    async function ejecutarReporte(pinId) {
        if (!confirm("¿Deseas reportar este pin para que sea revisado por los moderadores?")) return;
        
        try {
            const response = await fetch(`${API_URL}/${pinId}/reportar`, {
                method: 'PATCH'
            });
            if (response.ok) {
                alert("Imagen ocultada del feed. Enviada a moderación exitosamente.");
                cargarPines();
            } else {
                alert("Error al intentar procesar el reporte.");
            }
        } catch (error) {
            console.error("Error en la petición PATCH:", error);
        }
    }

    function verificarEstadoSesion() {
        const usuarioLogueado = localStorage.getItem('usuario');
        const rolUsuario = localStorage.getItem('rol');

        if (usuarioLogueado) {
            const btnLogin = document.querySelector('.nav-auth-btn.btn-login');
            const btnRegister = document.querySelector('.nav-auth-btn.btn-register');
            const profileIcon = document.querySelector('.nav-profile-icon');

            if (btnLogin) btnLogin.style.display = 'none';
            if (btnRegister) btnRegister.style.display = 'none';
            if (profileIcon) {
                profileIcon.style.display = 'flex';
                profileIcon.innerHTML = `<span style="font-weight:bold; font-size: 14px; color: white;">${usuarioLogueado.charAt(0).toUpperCase()}</span>`;
                profileIcon.setAttribute('title', `Conectado como: ${usuarioLogueado} (${rolUsuario})`);
            }
        }
    }

    // LÓGICA COMPLETA DEL MODAL DE CREACIÓN DE PINES
    if (btnNavCrear) {
        btnNavCrear.addEventListener('click', () => {
            const usuarioId = localStorage.getItem('usuario_id');
            if (!usuarioId) {
                alert("Debes iniciar sesión con tus credenciales locales, Google o Active Directory para poder crear un Pin.");
                window.location.href = "./login/login.html";
                return;
            }
            modalCrearPin.style.display = 'flex';
        });
    }

    if (formCrearPin) {
        formCrearPin.addEventListener('submit', async (e) => {
            e.preventDefault();

            const titulo = document.getElementById('pinTitulo').value;
            const archivo = document.getElementById('pinArchivo').files[0];

            if (!archivo) {
                alert("Por favor, selecciona una imagen.");
                return;
            }

            // Se estructuran los datos binarios físicos en un FormData multipart
            const formData = new FormData();
            formData.append('titulo', titulo);
            formData.append('file', archivo);

            try {
                // Petición directa al endpoint asíncrono de subida física
                const response = await fetch(`${API_URL}/upload`, {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    alert("¡Pin creado con éxito! Ha superado las políticas visuales de la IA y de vocabulario.");
                    formCrearPin.reset();
                    modalCrearPin.style.display = 'none';
                    cargarPines(); // Recarga síncronamente el feed principal
                } else {
                    const errorData = await response.json();
                    // Captura los errores explícitos de Moderacion_IA (NSFW) o el JSON de palabras prohibidas
                    alert(`Error de moderación: ${errorData.detail || 'Archivo rechazado por políticas de laboratorio.'}`);
                }
            } catch (error) {
                console.error("Error al subir el pin:", error);
                alert("No se pudo conectar con el servidor local de Pinterest.");
            }
        });
    }

    cargarPines();
});