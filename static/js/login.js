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

  // Inicia el carrusel automático
  let carruselInterval = setInterval(nextImage, intervalTime);

  // Opcional: Pausar al interactuar con el formulario
  const loginForm = document.querySelector('.login-container');
  loginForm.addEventListener('mouseenter', () => {
    clearInterval(carruselInterval);
  });

  loginForm.addEventListener('mouseleave', () => {
    carruselInterval = setInterval(nextImage, intervalTime);
  });

  // Lógica del login (se mantiene igual)
  document.getElementById('login-button').addEventListener('click', (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (username && password) {
    localStorage.setItem("isLoggedIn", "true");
    window.location.href = "brands.html"; // ← Asegúrate de que coincida el nombre del archivo.
}
  });
});