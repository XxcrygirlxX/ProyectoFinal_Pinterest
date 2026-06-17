const IP_SERVIDOR = "127.0.0.1";
const API_BASE_URL = `http://${IP_SERVIDOR}:8000/api/v1`;

document.getElementById("register-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("reg-username").value.trim();
    const email = document.getElementById("reg-email").value.trim();
    const password = document.getElementById("reg-password").value;
    
    const politicasAceptadas = document.getElementById("reg-politicas").checked;

    if (!politicasAceptadas) {
        alert("¡Espera! Para formar parte de Fyntasy, debes leer y aceptar obligatoriamente las Políticas de Convivencia y moderación ética de la plataforma.");
        return;
    }

    if (password.length < 6) {
        alert("La contraseña debe tener al menos 6 caracteres.");
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok) {
            alert("¡Tu cuenta en Fyntasy ha sido creada! Se ha enviado el correo electrónico real de bienvenida.");
            window.location.href = "../login/login.html";
        } else {
            alert(`Error en el registro: ${data.detail || "Datos inválidos"}`);
        }
    } catch (error) {
        console.error("Error de red:", error);
        alert("No se pudo conectar con el servidor central de Fyntasy.");
    }
});