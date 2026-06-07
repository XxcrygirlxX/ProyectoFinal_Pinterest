document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('registerForm');
    const emailInput = document.getElementById('regEmail');
    const passwordInput = document.getElementById('regPassword');
    const birthdateInput = document.getElementById('regBirthdate');

    // ==========================================
    // 1. CONFIGURACIÓN E INTEGRACIÓN DE GOOGLE SIGN-IN
    // ==========================================
    google.accounts.id.initialize({
        client_id: "62688628748-80so2m75d6mtoeortm12mt1pf4stdup6.apps.googleusercontent.com", 
        callback: handleGoogleRegisterResponse
    });

    google.accounts.id.renderButton(
        document.getElementById("googleRegisterButton"),
        { 
            theme: "outline", 
            size: "large", 
            type: "standard",
            shape: "pill",      
            text: "signup_with", // Muestra el texto "Continuar con Google" de manera oficial
            logo_alignment: "left",
            width: 384 
        }
    );

    // Procesa el token enviado por Google y despacha el correo desde el Backend
    function handleGoogleRegisterResponse(response) {
        console.log("JWT de Registro con Google obtenido:", response.credential);

        fetch('http://127.0.0.1:8000/api/v1/auth/google-login-register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ credential: response.credential })
        })
        .then(res => {
            if (res.ok) return res.json();
            throw new Error('Error al procesar la autenticación de Google en el servidor.');
        })
        .then(data => {
            alert(`¡Ingreso con Google exitoso! Bienvenido ${data.datos_sesion.nombre_usuario}`);
            
            // Guardar datos en localStorage para persistencia de la sesión
            localStorage.setItem('usuario', data.datos_sesion.nombre_usuario);
            localStorage.setItem('rol', data.datos_sesion.rol_en_app);
            localStorage.setItem('permisos', JSON.stringify(data.datos_sesion.permisos_pinterest));
            
            window.location.href = "../index.html";
        })
        .catch(error => {
            alert(error.message);
        });
    }

    // ==========================================
    // 2. REGISTRO LOCAL DE USUARIOS (FASTAPI + SQLITE)
    // ==========================================
    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            e.preventDefault(); // Evita recargas inesperadas en el envío clásico
            
            // Aquí puedes llamar a tu lógica existente de validación de edad o campos
            let isValid = true; 
            limpiarErrores();

            // Validación básica de ejemplo antes de despachar al fetch
            if (!emailInput.value.includes('@')) {
                showError('regEmailError', 'Por favor ingresa un correo válido.');
                isValid = false;
            }

            if (passwordInput.value.length < 4) {
                showError('regPasswordError', 'La contraseña debe tener al menos 4 caracteres.');
                isValid = false;
            }

            if (isValid) {
                const nuevoUsuario = {
                    email: emailInput.value,
                    password: passwordInput.value
                };

                // Enviar datos al endpoint de registro nativo de tu base de datos local
                fetch('http://127.0.0.1:8000/api/v1/auth/register', { 
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(nuevoUsuario)
                })
                .then(response => {
                    if (response.ok) {
                        return response.json();
                    }
                    throw new Error('El correo ya se encuentra registrado o los datos son inválidos.');
                })
                .then(data => {
                    alert('¡Registro completado con éxito!');
                    window.location.href = "../login/login.html"; 
                })
                .catch(error => {
                    showError('regEmailError', error.message);
                });
            }
        });
    }

    // Funciones auxiliares para el manejo visual de errores estéticos
    function showError(elementId, message) {
        const errorSpan = document.getElementById(elementId);
        if (errorSpan) {
            errorSpan.textContent = message;
            errorSpan.style.display = 'block';
        }
    }

    function limpiarErrores() {
        const errores = document.querySelectorAll('.error-message');
        errores.forEach(err => err.textContent = '');
    }
});