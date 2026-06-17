const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("log-email").value.trim();
    const password = document.getElementById("log-password").value;

    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem("usuario_autenticado", "true");
            localStorage.setItem("usuario_id", data.usuario_id);
            localStorage.setItem("username", data.user.username);

            alert(`Autenticación exitosa. Identificador: @${data.user.username}`);
            window.location.href = "../index.html"; 
        } else {
            alert(`Fallo de autenticación: ${data.detail || "Credenciales inválidas."}`);
        }
    } catch (error) {
        console.error("Error en login tradicional:", error);
        alert("No se pudo establecer conexión con el servicio de autenticación.");
    }
});

async function handleGoogleCredentialResponse(response) {
    if (!response || !response.credential) {
        console.error("No se recibió una credencial válida desde la ventana de Google.");
        return;
    }

    console.log("[OAUTH] Token JWT legítimo obtenido desde los servidores de Google.");

    try {
        const res = await fetch(`${API_BASE_URL}/auth/google`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ token: String(response.credential) })
        });

        const data = await res.json();

        if (res.ok) {
            localStorage.setItem("usuario_autenticado", "true");
            localStorage.setItem("usuario_id", data.usuario_id);
            localStorage.setItem("username", data.user.username);
            
            alert(`Autenticación con Google exitosa. Usuario activo: @${data.user.username}`);
            window.location.href = "../index.html"; 
        } else {
            alert(`Falla de validación en el servidor: ${data.detail}`);
        }
    } catch (error) {
        console.error("Error en el pipeline de verificación:", error);
        alert("Error de red al intentar validar la firma digital con los servidores de Google.");
    }
}

window.handleGoogleCredentialResponse = handleGoogleCredentialResponse;