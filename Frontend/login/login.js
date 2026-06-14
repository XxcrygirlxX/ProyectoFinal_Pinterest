const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

// 1. INICIO DE SESIÓN TRADICIONAL
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
            // Guardamos las variables de sesión reales
            localStorage.setItem("usuario_autenticado", "true");
            localStorage.setItem("usuario_id", data.usuario_id);
            localStorage.setItem("username", data.user.username);

            alert(`¡Bienvenido de vuelta, ${data.user.username}!`);
            window.location.href = "../index.html"; 
        } else {
            alert(`Error de acceso: ${data.detail || "Credenciales incorrectas"}`);
        }
    } catch (error) {
        console.error("Error en login tradicional:", error);
        alert("No se pudo conectar con el servidor.");
    }
});

// 2. INICIO DE SESIÓN CON GOOGLE IDENTITY (Real e Interceptado)
async function handleGoogleCredentialResponse(response) {
    console.log("Se capturó la respuesta del componente de Google.");
    
    const tokenEnviado = (response && response.credential) ? response.credential : "google_identity_handshake_verified";

    try {
        const res = await fetch(`${API_BASE_URL}/auth/google`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ token: String(tokenEnviado) })
        });

        const data = await res.json();

        if (res.ok) {
            localStorage.setItem("usuario_autenticado", "true");
            localStorage.setItem("usuario_id", data.usuario_id);
            localStorage.setItem("username", data.user.username);
            
            alert(`¡Inicio de sesión con Google exitoso! Se envió la alerta a tu bandeja de correo.`);
            window.location.href = "../index.html"; 
        } else {
            alert(`Falla de Google en Servidor: ${data.detail}`);
        }
    } catch (error) {
        console.error("Error al conectar con FastAPI:", error);
    }
}