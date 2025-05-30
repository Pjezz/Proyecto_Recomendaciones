document.addEventListener('DOMContentLoaded', () => {
  const images = document.querySelectorAll('.carrusel-imagenes img');
  let currentIndex = 0;
  const intervalTime = 4000; // 4 segundos

  // Función para cambiar de imagen con efecto fade
  function nextImage() {
    // Oculta la imagen actual
    images[currentIndex].classList.remove('active');
    
    // Avanza al siguiente índice (vuelve a 0 si llega al final)
    currentIndex = (currentIndex + 1) % images.length;
    
    // Muestra la nueva imagen
    images[currentIndex].classList.add('active');
  }

  // Inicia el carrusel automático si hay imágenes
  let carruselInterval;
  if (images.length > 0) {
    carruselInterval = setInterval(nextImage, intervalTime);
  }

  // Opcional: Pausar al interactuar con el formulario
  const loginForm = document.querySelector('.login-container');
  if (loginForm) {
    loginForm.addEventListener('mouseenter', () => {
      clearInterval(carruselInterval);
    });

    loginForm.addEventListener('mouseleave', () => {
      if (images.length > 0) {
        carruselInterval = setInterval(nextImage, intervalTime);
      }
    });
  }

  // Lógica del login
  const loginButton = document.getElementById('login-button');
  if (loginButton) {
    loginButton.addEventListener('click', async (e) => {
      e.preventDefault();
      
      const username = document.getElementById('username').value;
      const password = document.getElementById('password').value;
      const errorMessage = document.getElementById('error-message');

      // Limpiar mensaje de error anterior
      errorMessage.style.display = 'none';

      if (username && password) {
        try {
          const response = await fetch('/login', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
              username: username, 
              password: password 
            })
          });
          
          const data = await response.json();
          
          if (data.success) {
            window.location.href = data.redirect;
          } else {
            errorMessage.textContent = data.message || 'Error en el login';
            errorMessage.style.display = 'block';
          }
        } catch (error) {
          console.error('Error:', error);
          errorMessage.textContent = 'Error de conexión';
          errorMessage.style.display = 'block';
        }
      } else {
        errorMessage.textContent = 'Por favor, ingresa usuario y contraseña';
        errorMessage.style.display = 'block';
      }
    });
  }
});