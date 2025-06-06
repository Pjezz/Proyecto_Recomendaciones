// navbar.js - Sistema de navegación común para todas las páginas
document.addEventListener('DOMContentLoaded', () => {
  initializeNavbar();
  loadThemePreference();
});

function initializeNavbar() {
  const userMenuBtn = document.getElementById('user-menu-btn');
  const userDropdown = document.getElementById('user-dropdown');
  
  if (userMenuBtn && userDropdown) {
    // Toggle dropdown al hacer clic
    userMenuBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleUserDropdown();
    });
    
    // Cerrar dropdown al hacer clic fuera
    document.addEventListener('click', (e) => {
      if (!userMenuBtn.contains(e.target) && !userDropdown.contains(e.target)) {
        closeUserDropdown();
      }
    });
    
    // Cerrar dropdown con Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        closeUserDropdown();
      }
    });
  }
  
  // Cargar información del usuario
  loadUserInfo();
}

function toggleUserDropdown() {
  const userMenu = document.querySelector('.user-menu');
  const userDropdown = document.getElementById('user-dropdown');
  
  if (userMenu && userDropdown) {
    const isActive = userDropdown.classList.contains('active');
    
    if (isActive) {
      closeUserDropdown();
    } else {
      openUserDropdown();
    }
  }
}

function openUserDropdown() {
  const userMenu = document.querySelector('.user-menu');
  const userDropdown = document.getElementById('user-dropdown');
  
  if (userMenu && userDropdown) {
    userMenu.classList.add('active');
    userDropdown.classList.add('active');
  }
}

function closeUserDropdown() {
  const userMenu = document.querySelector('.user-menu');
  const userDropdown = document.getElementById('user-dropdown');
  
  if (userMenu && userDropdown) {
    userMenu.classList.remove('active');
    userDropdown.classList.remove('active');
  }
}

async function loadUserInfo() {
  try {
    const response = await fetch('/api/user-info');
    if (response.ok) {
      const userData = await response.json();
      updateNavbarUserName(userData.displayName || userData.username || 'Usuario');
    }
  } catch (error) {
    console.log('No se pudo cargar información del usuario');
  }
}

function updateNavbarUserName(name) {
  const userNameElement = document.getElementById('user-name');
  if (userNameElement) {
    userNameElement.textContent = name;
  }
}

// Funciones del menú de usuario
function openProfileModal() {
  const modal = document.getElementById('profile-modal');
  const modalBody = document.getElementById('profile-modal-body');
  
  if (!modal || !modalBody) {
    alert('Modal de perfil no disponible en esta página');
    return;
  }
  
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
  
  closeUserDropdown();
}

function openFavoritesModal() {
  const modal = document.getElementById('favorites-modal');
  const modalBody = document.getElementById('favorites-modal-body');
  
  if (!modal || !modalBody) {
    // Si no hay modal en la página actual, redirigir a una página que lo tenga
    window.location.href = '/profile?tab=favorites';
    return;
  }
  
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
  
  closeUserDropdown();
}

function toggleTheme() {
  const currentTheme = document.body.classList.contains('dark-theme') ? 'dark' : 'light';
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  
  // Aplicar tema
  if (newTheme === 'dark') {
    document.body.classList.add('dark-theme');
  } else {
    document.body.classList.remove('dark-theme');
  }
  
  // Guardar preferencia
  localStorage.setItem('theme-preference', newTheme);
  
  // Guardar en el servidor
  fetch('/api/save-theme', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ theme: newTheme })
  }).catch(error => {
    console.log('No se pudo guardar tema en servidor');
  });
  
  // Actualizar texto del botón
  updateThemeButtonText(newTheme);
  
  closeUserDropdown();
}

function updateThemeButtonText(theme) {
  const themeButton = document.querySelector('[onclick="toggleTheme()"]');
  if (themeButton) {
    themeButton.innerHTML = theme === 'dark' ? '☀️ Tema Claro' : '🌙 Tema Oscuro';
  }
}

function loadThemePreference() {
  // Cargar desde localStorage
  const savedTheme = localStorage.getItem('theme-preference');
  
  if (savedTheme === 'dark') {
    document.body.classList.add('dark-theme');
    updateThemeButtonText('dark');
  } else {
    updateThemeButtonText('light');
  }
  
  // También intentar cargar desde servidor
  fetch('/api/user-theme')
    .then(response => response.json())
    .then(data => {
      if (data.theme && data.theme !== savedTheme) {
        localStorage.setItem('theme-preference', data.theme);
        if (data.theme === 'dark') {
          document.body.classList.add('dark-theme');
        } else {
          document.body.classList.remove('dark-theme');
        }
        updateThemeButtonText(data.theme);
      }
    })
    .catch(error => {
      console.log('No se pudo cargar tema del servidor');
    });
}

function confirmLogout() {
  return confirm('¿Estás seguro de que quieres cerrar sesión? Se perderán las selecciones no guardadas.');
}

// Funciones para generar contenido de modales
function generateProfileModalContent(userData) {
  return `
    <div class="profile-info">
      <div class="profile-field">
        <label><strong>Nombre:</strong></label>
        <span>${userData.displayName || 'No especificado'}</span>
      </div>
      <div class="profile-field">
        <label><strong>Email:</strong></label>
        <span>${userData.email || 'No especificado'}</span>
      </div>
      <div class="profile-field">
        <label><strong>Género:</strong></label>
        <span>${getGenderLabel(userData.gender)}</span>
      </div>
      <div class="profile-field">
        <label><strong>Edad:</strong></label>
        <span>${userData.ageRange || 'No especificado'}</span>
      </div>
      <div class="profile-field">
        <label><strong>Miembro desde:</strong></label>
        <span>${formatDate(userData.createdAt)}</span>
      </div>
    </div>
    <div class="profile-actions">
      <button onclick="editProfile()" class="btn-primary">✏️ Editar Perfil</button>
      <button onclick="downloadData()" class="btn-secondary">📥 Descargar Datos</button>
    </div>
  `;
}

function generateFavoritesModalContent(favoritesData) {
  if (!favoritesData.favorites || favoritesData.favorites.length === 0) {
    return `
      <div class="no-favorites">
        <div class="empty-state">
          <div class="empty-icon">❤️</div>
          <h3>Aún no tienes favoritos</h3>
          <p>¡Completa el proceso de recomendaciones para guardar tus autos preferidos!</p>
          <button onclick="startRecommendations()" class="btn-primary">Buscar Autos</button>
        </div>
      </div>
    `;
  }

  return `
    <div class="favorites-header">
      <p><strong>${favoritesData.favorites.length}</strong> autos guardados</p>
    </div>
    <div class="favorites-grid">
      ${favoritesData.favorites.map(car => `
        <div class="favorite-item">
          <div class="favorite-car-info">
            <h4>${car.name}</h4>
            <p class="car-details">${car.brand} • ${car.year}</p>
            <p class="car-price">$${car.price.toLocaleString()}</p>
            <div class="car-specs">
              <span class="spec">${car.fuel}</span>
              <span class="spec">${car.transmission}</span>
              <span class="spec">${car.type}</span>
            </div>
          </div>
          <div class="favorite-actions">
            <button onclick="viewCarDetails('${car.id}')" class="btn-view">👁️ Ver</button>
            <button onclick="removeFavorite('${car.id}')" class="btn-remove">🗑️ Eliminar</button>
          </div>
        </div>
      `).join('')}
    </div>
    <div class="favorites-actions">
      <button onclick="clearAllFavorites()" class="btn-danger">Limpiar Todo</button>
      <button onclick="exportFavorites()" class="btn-secondary">📤 Exportar</button>
    </div>
  `;
}

// Funciones auxiliares
function getGenderLabel(gender) {
  const labels = {
    'masculino': '👨 Masculino',
    'femenino': '👩 Femenino',
    'otro': '🧑 Otro'
  };
  return labels[gender] || 'No especificado';
}

function formatDate(dateString) {
  if (!dateString) return 'No disponible';
  const date = new Date(dateString);
  return date.toLocaleDateString('es-GT', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });
}

// Funciones de acción para los modales
function editProfile() {
  alert('Redirigiendo a edición de perfil...');
  window.location.href = '/profile/edit';
}

function downloadData() {
  fetch('/api/user-data-export')
    .then(response => response.blob())
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'mis-datos.json';
      a.click();
      window.URL.revokeObjectURL(url);
    })
    .catch(error => {
      console.error('Error descargando datos:', error);
      alert('Error al descargar datos');
    });
}

function startRecommendations() {
  window.location.href = '/brands';
}

function viewCarDetails(carId) {
  // Implementar vista de detalles del auto
  alert(`Ver detalles del auto ${carId}`);
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

function clearAllFavorites() {
  if (confirm('¿Eliminar TODOS los favoritos? Esta acción no se puede deshacer.')) {
    fetch('/api/clear-favorites', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        openFavoritesModal(); // Recargar modal
      }
    })
    .catch(error => {
      console.error('Error limpiando favoritos:', error);
      alert('Error al limpiar favoritos');
    });
  }
}

function exportFavorites() {
  fetch('/api/export-favorites')
    .then(response => response.blob())
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'mis-favoritos.json';
      a.click();
      window.URL.revokeObjectURL(url);
    })
    .catch(error => {
      console.error('Error exportando favoritos:', error);
      alert('Error al exportar favoritos');
    });
}

function closeProfileModal() {
  const modal = document.getElementById('profile-modal');
  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
  }
}

function closeFavoritesModal() {
  const modal = document.getElementById('favorites-modal');
  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
  }
}

// Hacer funciones disponibles globalmente
window.openProfileModal = openProfileModal;
window.openFavoritesModal = openFavoritesModal;
window.toggleTheme = toggleTheme;
window.confirmLogout = confirmLogout;
window.closeProfileModal = closeProfileModal;
window.closeFavoritesModal = closeFavoritesModal;