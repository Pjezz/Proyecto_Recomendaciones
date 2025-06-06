document.addEventListener('DOMContentLoaded', () => {
  // Variables para almacenar las selecciones
  let profileData = {
    displayName: '',
    gender: '',
    ageRange: ''
  };

  // Referencias a elementos
  const displayNameInput = document.getElementById('display-name');
  const genderButtons = document.querySelectorAll('.gender-btn');
  const ageButtons = document.querySelectorAll('.age-btn');
  const continueBtn = document.getElementById('continue-btn');
  const form = document.getElementById('profile-form');

  // Configurar eventos
  setupInputEvents();
  setupFormSubmission();
  loadUserName();

  function setupInputEvents() {
    // Input de nombre
    displayNameInput.addEventListener('input', function() {
      profileData.displayName = this.value.trim();
      validateForm();
    });

    // Botones de género
    genderButtons.forEach(btn => {
      btn.addEventListener('click', function() {
        // Deseleccionar otros
        genderButtons.forEach(b => b.classList.remove('selected'));
        
        // Seleccionar actual
        this.classList.add('selected');
        profileData.gender = this.dataset.gender;
        
        validateForm();
      });
    });

    // Botones de edad
    ageButtons.forEach(btn => {
      btn.addEventListener('click', function() {
        // Deseleccionar otros
        ageButtons.forEach(b => b.classList.remove('selected'));
        
        // Seleccionar actual
        this.classList.add('selected');
        profileData.ageRange = this.dataset.age;
        
        validateForm();
      });
    });
  }

  function validateForm() {
    const isValid = profileData.displayName.length > 0 && 
                   profileData.gender !== '' && 
                   profileData.ageRange !== '';
    
    continueBtn.disabled = !isValid;
    
    if (isValid) {
      continueBtn.textContent = 'Continuar con las recomendaciones';
    } else {
      const missing = [];
      if (!profileData.displayName) missing.push('nombre');
      if (!profileData.gender) missing.push('género');
      if (!profileData.ageRange) missing.push('edad');
      
      continueBtn.textContent = `Selecciona: ${missing.join(', ')}`;
    }
  }

  function setupFormSubmission() {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      if (continueBtn.disabled) return;
      
      try {
        // Mostrar loading
        continueBtn.disabled = true;
        continueBtn.textContent = 'Guardando perfil...';
        
        const response = await fetch('/api/save-profile', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(profileData)
        });
        
        if (response.ok) {
          const result = await response.json();
          console.log('Perfil guardado:', result);
          
          // Actualizar nombre en la navbar si está visible
          updateNavbarUserName(profileData.displayName);
          
          // Redireccionar a brands
          window.location.href = '/brands';
        } else {
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
      } catch (error) {
        console.error('Error al guardar perfil:', error);
        alert('Error al guardar el perfil. Por favor, intenta de nuevo.');
        
        // Restaurar botón
        continueBtn.disabled = false;
        validateForm();
      }
    });
  }

  function loadUserName() {
    // Intentar obtener el nombre del usuario desde la sesión
    fetch('/api/user-info')
      .then(response => response.json())
      .then(data => {
        if (data.username) {
          updateNavbarUserName(data.username);
        }
      })
      .catch(error => {
        console.log('No se pudo obtener info del usuario (normal en primer setup)');
      });
  }

  function updateNavbarUserName(name) {
    const userNameElement = document.getElementById('user-name');
    if (userNameElement) {
      userNameElement.textContent = name;
    }
  }

  // Hacer funciones disponibles globalmente para la navbar
  window.profileSetupData = profileData;
});

// Funciones para los modales (llamadas desde navbar.js)
function openProfileModal() {
  const modal = document.getElementById('profile-modal');
  const modalBody = document.getElementById('profile-modal-body');
  
  // Obtener datos del perfil actual
  fetch('/api/user-profile')
    .then(response => response.json())
    .then(data => {
      modalBody.innerHTML = generateProfileModalContent(data);
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
    })
    .catch(error => {
      console.error('Error cargando perfil:', error);
      modalBody.innerHTML = `
        <div class="error-message">
          <p>Error al cargar el perfil. Por favor, intenta de nuevo.</p>
        </div>
      `;
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
    });
}

function closeProfileModal() {
  const modal = document.getElementById('profile-modal');
  modal.classList.remove('active');
  document.body.style.overflow = 'auto';
}

function openFavoritesModal() {
  const modal = document.getElementById('favorites-modal');
  const modalBody = document.getElementById('favorites-modal-body');
  
  // Obtener favoritos del usuario
  fetch('/api/user-favorites')
    .then(response => response.json())
    .then(data => {
      modalBody.innerHTML = generateFavoritesModalContent(data);
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
    })
    .catch(error => {
      console.error('Error cargando favoritos:', error);
      modalBody.innerHTML = `
        <div class="error-message">
          <p>Error al cargar favoritos. Por favor, intenta de nuevo.</p>
        </div>
      `;
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
    });
}

function closeFavoritesModal() {
  const modal = document.getElementById('favorites-modal');
  modal.classList.remove('active');
  document.body.style.overflow = 'auto';
}

function generateProfileModalContent(userData) {
  return `
    <div class="profile-info">
      <div class="profile-field">
        <label>Nombre:</label>
        <span>${userData.displayName || 'No especificado'}</span>
      </div>
      <div class="profile-field">
        <label>Email:</label>
        <span>${userData.email || 'No especificado'}</span>
      </div>
      <div class="profile-field">
        <label>Género:</label>
        <span>${userData.gender || 'No especificado'}</span>
      </div>
      <div class="profile-field">
        <label>Edad:</label>
        <span>${userData.ageRange || 'No especificado'}</span>
      </div>
    </div>
    <div class="profile-actions">
      <button onclick="editProfile()" class="btn-primary">Editar Perfil</button>
    </div>
  `;
}

function generateFavoritesModalContent(favoritesData) {
  if (!favoritesData.favorites || favoritesData.favorites.length === 0) {
    return `
      <div class="no-favorites">
        <p>Aún no tienes favoritos.</p>
        <p>¡Completa el proceso de recomendaciones para guardar tus autos preferidos!</p>
      </div>
    `;
  }

  return `
    <div class="favorites-grid">
      ${favoritesData.favorites.map(car => `
        <div class="favorite-item">
          <h4>${car.name}</h4>
          <p>${car.brand} - ${car.year}</p>
          <p class="price">$${car.price.toLocaleString()}</p>
          <button onclick="removeFavorite('${car.id}')" class="btn-remove">Eliminar</button>
        </div>
      `).join('')}
    </div>
  `;
}

function editProfile() {
  alert('Función de editar perfil próximamente...');
  closeProfileModal();
}

function removeFavorite(carId) {
  if (confirm('¿Eliminar este auto de favoritos?')) {
    fetch('/api/remove-favorite', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ carId: carId })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        openFavoritesModal(); // Recargar modal
      }
    })
    .catch(error => {
      console.error('Error eliminando favorito:', error);
      alert('Error al eliminar favorito');
    });
  }
}

// Cerrar modales con Escape
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    closeProfileModal();
    closeFavoritesModal();
  }
});

// Cerrar modales haciendo clic fuera
document.addEventListener('click', function(e) {
  if (e.target && e.target.classList.contains('modal-overlay')) {
    closeProfileModal();
    closeFavoritesModal();
  }
});