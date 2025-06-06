// Variables globales
let debugMode = false;
let userFavorites = new Set();
let currentRecommendations = [];
let currentUser = null;
let isDarkTheme = false;

// Función para formatear precio
function formatPrice(price) {
  if (typeof price === 'number') {
    return `$${price.toLocaleString('es-GT')}`;
  }
  return price || 'Precio no disponible';
}

// Función para crear una tarjeta de auto
function createCarCard(car, index) {
  const card = document.createElement('div');
