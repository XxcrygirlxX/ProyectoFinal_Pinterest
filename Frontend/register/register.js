document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('registerForm');
    const emailInput = document.getElementById('regEmail');
    const passwordInput = document.getElementById('regPassword');
    const birthdateInput = document.getElementById('regBirthdate');
    const toLoginLink = document.getElementById('toLogin');

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
            text: "signup_with", 
            logo_alignment: "left",
            width: 384 
        }
    );

    function handleGoogleRegisterResponse(response) {
        console.log("JWT de Registro con Google obtenido:", response.credential);

        alert("¡Registro con Google exitoso en el cliente! Cuenta lista para vincular.");
    }

    registerForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        resetErrors();
        let isValid = true;

        if (!validateEmail(emailInput.value)) {
            showError('regEmailError', 'Introduce un correo electrónico válido.');
            isValid = false;
        }

        if (passwordInput.value.trim().length < 6) {
            showError('regPasswordError', 'La contraseña debe tener al menos 6 caracteres.');
            isValid = false;
        }

        if (!birthdateInput.value) {
            showError('regBirthdateError', 'Por favor, ingresa tu fecha de nacimiento.');
            isValid = false;
        } else if (!validateAge(birthdateInput.value)) {
            showError('regBirthdateError', 'Debes tener al menos 13 años para registrarte.');
            isValid = false;
        }

        if (isValid) {
            console.log('Registro exitoso. Datos capturados:', {
                email: emailInput.value,
                password: passwordInput.value,
                birthdate: birthdateInput.value
            });
        }
    });

    toLoginLink.addEventListener('click', (e) => {
        console.log('Navegando hacia la pantalla de inicio de sesión...');
        window.location.href = "../login/login.html";
    });

    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(String(email).toLowerCase());
    }

    function validateAge(birthdateValue) {
        const birthDate = new Date(birthdateValue);
        const today = new Date();
        let age = today.getFullYear() - birthDate.getFullYear();
        const monthDiff = today.getMonth() - birthDate.getMonth();
        
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
            age--;
        }
        return age >= 13;
    }

    function showError(elementId, message) {
        const errorSpan = document.getElementById(elementId);
        errorSpan.textContent = message;
        errorSpan.style.display = 'block';
    }

    function resetErrors() {
        const errorSpans = document.querySelectorAll('.error-message');
        errorSpans.forEach(span => {
            span.textContent = '';
            span.style.display = 'none';
        });
    }
});