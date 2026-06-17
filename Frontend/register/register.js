const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

document.getElementById("register-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("reg-username").value.trim();
    const email = document.getElementById("reg-email").value.trim();
    const password = document.getElementById("reg-password").value;
    
    const politicasAceptadas = document.getElementById("reg-politicas").checked;

    if (!politicasAceptadas) {
        alert("Error de validación: Es obligatorio aceptar las políticas de moderación e IA corporativas para proceder.");
        return;
    }

    if (password.length < 6) {
        alert("La longitud mínima de la contraseña debe ser de 6 caracteres.");
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
            alert("Cuenta registrada de forma exitosa.");
            window.location.href = "../login/login.html";
        } else {
            alert(`Fallo en el registro: ${data.detail || "Esquema de datos inválido."}`);
        }
    } catch (error) {
        console.error("Error de conexión:", error);
        alert("Fallo crítico de red: No se pudo contactar al servidor central de Fyntasy.");
    }
});