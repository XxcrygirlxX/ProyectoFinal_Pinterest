document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("loginForm");
  const emailInput = document.getElementById("email");
  const passwordInput = document.getElementById("password");
  const toRegisterLink = document.getElementById("toRegister");

  loginForm.addEventListener("submit", (e) => {
    e.preventDefault();

    resetErrors();

    let isValid = true;

    if (!validateEmail(emailInput.value)) {
      showError(
        "emailError",
        "El correo electrónico que ingresaste no es válido.",
      );
      isValid = false;
    }

    if (passwordInput.value.trim().length < 6) {
      showError(
        "passwordError",
        "La contraseña debe tener al menos 6 caracteres.",
      );
      isValid = false;
    }

    if (isValid) {
      console.log("Datos enviados:", {
        email: emailInput.value,
        password: passwordInput.value,
      });
    }
  });

  toRegisterLink.addEventListener("click", (e) => {
    e.preventDefault();
    console.log("Redirigiendo a la vista de Registro...");
    window.location.href = "../register/register.html";
  });

  function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(String(email).toLowerCase());
  }

  function showError(elementId, message) {
    const errorSpan = document.getElementById(elementId);
    errorSpan.textContent = message;
    errorSpan.style.display = "block";
  }

  function resetErrors() {
    const errorSpans = document.querySelectorAll(".error-message");
    errorSpans.forEach((span) => {
      span.textContent = "";
      span.style.display = "none";
    });
  }
});
window.onload = function () {
    google.accounts.id.initialize({
        client_id: "62688628748-80so2m75d6mtoeortm12mt1pf4stdup6.apps.googleusercontent.com", 
        callback: handleCredentialResponse
    });

    google.accounts.id.renderButton(
        document.getElementById("googleButton"),
        { 
            theme: "outline", 
            size: "large", 
            type: "standard",
            shape: "pill",      
            text: "signin_with", 
            logo_alignment: "left",
            width: 384 
        }
    );
};

function handleCredentialResponse(response) {
    console.log("Encoded JWT ID token: " + response.credential);

    alert("Login con Google exitoso en el cliente");
}
