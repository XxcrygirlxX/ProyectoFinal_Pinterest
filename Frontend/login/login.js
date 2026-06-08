// ========================================================
// 1. CALLBACK GLOBAL DE GOOGLE SIGN-IN (Fuera del DOMContentLoaded)
// ========================================================
window.handleGoogleLoginResponse = function (response) {
  console.log("JWT de Login con Google obtenido:", response.credential);

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

      localStorage.setItem('usuario_id', data.usuario_id);
      localStorage.setItem('usuario', data.datos_sesion.nombre_usuario);
      localStorage.setItem('rol', data.datos_sesion.rol_en_app);
      localStorage.setItem('permisos', JSON.stringify(data.datos_sesion.permisos_pinterest));

      window.location.href = "../index.html";
    })
    .catch(error => {
      alert(error.message);
    });
};

// ========================================================
// 2. INICIO DE SESIÓN CENTRALIZADO ACTIVE DIRECTORY (UIDE.A)
// ========================================================
document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('loginForm');

  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault(); 

      const usernameInput = document.getElementById('loginUser').value;
      const passwordInput = document.getElementById('loginPassword').value;

      // SOLUCIÓN AL ERROR 422: URLSearchParams fuerza el formato x-www-form-urlencoded
      const formData = new URLSearchParams();
      formData.append('username', usernameInput);
      formData.append('password', passwordInput);

      try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/auth/login-uide', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          body: formData
        });

        if (response.ok) {
          const data = await response.json();

          // Guardar de forma estricta los datos devueltos por la BD centralizada
          localStorage.setItem('usuario_id', data.usuario_id); 
          localStorage.setItem('usuario', data.datos_sesion.nombre_usuario);
          localStorage.setItem('rol', data.datos_sesion.rol_en_app);
          localStorage.setItem('permisos', JSON.stringify(data.datos_sesion.permisos_pinterest));

          alert(`¡Autenticación exitosa! Bienvenido, ${data.datos_sesion.nombre_usuario}.`);
          window.location.href = "../index.html";
        } else {
          const errData = await response.json();
          alert(`Error de autenticación: ${errData.detail || 'Credenciales incorrectas en DC01'}`);
        }
      } catch (error) {
        console.error("Error en la conexión con el servidor AD:", error);
        alert("No se pudo establecer comunicación con el controlador de dominio DC01.");
      }
    });
  }
});