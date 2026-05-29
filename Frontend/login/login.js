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
