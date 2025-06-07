console.log('🚀 Recommendations JS iniciando con separación inteligente...');

// Estado global
let userFavorites = [];
let filteredCars = [];
let recommendedCars = [];
let currentFilters = {};

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    console.log('📱 DOM cargado, iniciando aplicación con separación...');
    initializeApp();
});

async function initializeApp() {
    try {
        console.log('🔄 Inicializando aplicación...');
        
        // Cargar componentes básicos
        await loadUserInfo();
        loadFiltersApplied();
        await loadUserFavorites();
        
        // Cargar recomendaciones con separación
        await loadRecommendationsWithSeparation();
        
        console.log('✅ Aplicación inicializada correctamente');
        
    } catch (error) {
        console.error('❌ Error inicializando aplicación:', error);
        showError('Error cargando la aplicación: ' + error.message);
    }
}

// Cargar información del usuario
async function loadUserInfo() {
    try {
        console.log('👤 Cargando información del usuario...');
        const response = await fetch('/api/user-info');
        
        if (response.ok) {
            const user = await response.json();
            const userNameElement = document.getElementById('user-name');
            
            const displayName = user.displayName || user.username || user.email || 'Usuario';
            
            if (userNameElement) userNameElement.textContent = displayName;
            
            console.log('✅ Información de usuario cargada');
        }
    } catch (error) {
        console.error('❌ Error cargando info del usuario:', error);
    }
}

// Mostrar filtros aplicados
function loadFiltersApplied() {
    console.log('🔍 Cargando filtros aplicados...');
    
    const filtersContainer = document.getElementById('filters-summary');
    if (!filtersContainer) {
        console.error('❌ No se encontró el contenedor de filtros');
        return;
    }
    
    // Obtener datos de sessionStorage
    const filters = {
        brands: JSON.parse(sessionStorage.getItem('selected_brands') || '[]'),
        budget: sessionStorage.getItem('selected_budget') || '',
        fuel: JSON.parse(sessionStorage.getItem('selected_fuel') || '[]'),
        types: JSON.parse(sessionStorage.getItem('selected_types') || '[]'),
        transmission: JSON.parse(sessionStorage.getItem('selected_transmission') || '[]')
    };
    
    currentFilters = filters;
    
    console.log('📋 Filtros obtenidos desde sessionStorage:', filters);
    
    const hasAnyData = filters.brands.length > 0 || filters.budget || 
                      filters.fuel.length > 0 || filters.types.length > 0 || 
                      filters.transmission.length > 0;
    
    if (!hasAnyData) {
        console.warn('⚠️ No se encontraron filtros en sessionStorage');
        filtersContainer.innerHTML = `
            <div class="filter-item error-item">
                <span class="filter-label">⚠️ Error</span>
                <div class="filter-value">No se encontraron filtros aplicados</div>
            </div>
        `;
        return;
    }
    
    const filterItems = [
        {
            label: 'Marcas Preferidas',
            value: filters.brands,
            icon: '🏷️'
        },
        {
            label: 'Presupuesto',
            value: formatBudget(filters.budget),
            icon: '💰'
        },
        {
            label: 'Tipo de Combustible',
            value: filters.fuel,
            icon: '⛽'
        },
        {
            label: 'Tipo de Vehículo',
            value: filters.types,
            icon: '🚗'
        },
        {
            label: 'Transmisión',
            value: filters.transmission,
            icon: '⚙️'
        }
    ];
    
    filtersContainer.innerHTML = filterItems.map(item => `
        <div class="filter-item">
            <span class="filter-label">${item.icon} ${item.label}</span>
            <div class="filter-value">
                ${Array.isArray(item.value) && item.value.length > 0
                    ? `<div class="filter-list">${item.value.map(v => `<span class="filter-tag">${v}</span>`).join('')}</div>`
                    : (item.value || 'No especificado')
                }
            </div>
        </div>
    `).join('');
    
    console.log('✅ Filtros mostrados en interfaz');
}

// Formatear presupuesto
function formatBudget(budget) {
    if (!budget) return 'No especificado';
    
    if (budget.includes('-')) {
        const [min, max] = budget.split('-');
        return `${parseInt(min).toLocaleString()} - ${parseInt(max).toLocaleString()}`;
    }
    
    return budget;
}

// Cargar recomendaciones con separación clara
async function loadRecommendationsWithSeparation() {
    console.log('🎯 Iniciando carga de recomendaciones con separación...');
    
    try {
        showLoading();
        
        console.log('📡 Realizando petición a /api/recommendations...');
        const response = await fetch('/api/recommendations');
        
        console.log('📨 Respuesta recibida:', response.status, response.statusText);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Error HTTP:', errorText);
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        
        const data = await response.json();
        console.log('📄 Datos parseados:', data);
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        if (!Array.isArray(data)) {
            throw new Error('Formato de datos inválido: esperaba un array');
        }
        
        // Separar resultados por tipo
        const filtered = data.filter(car => car.match_type === 'filtered');
        const recommended = data.filter(car => car.match_type === 'recommended');
        
        console.log('📊 SEPARACIÓN DE RESULTADOS:');
        console.log(`  🔍 Filtrados exactos: ${filtered.length}`);
        console.log(`  🎯 Recomendaciones inteligentes: ${recommended.length}`);
        
        // Guardar en variables globales
        filteredCars = filtered;
        recommendedCars = recommended;
        
        // Mostrar cada sección por separado
        displayFilteredResults(filtered);
        displayIntelligentRecommendations(recommended);
        
        hideLoading();
        
        console.log('✅ Recomendaciones cargadas y separadas exitosamente');
        
    } catch (error) {
        console.error('❌ Error cargando recomendaciones:', error);
        hideLoading();
        showError(error.message);
    }
}

// Mostrar resultados filtrados (coincidencias exactas)
function displayFilteredResults(cars) {
    const section = document.getElementById('filtered-section');
    const container = document.getElementById('filtered-cars');
    const countElement = document.getElementById('filtered-count');
    
    if (!section || !container || !countElement) {
        console.error('❌ Elementos de filtrados no encontrados');
        return;
    }
    
    if (cars.length === 0) {
        section.style.display = 'none';
        console.log('⚠️ No hay coincidencias exactas');
        return;
    }
    
    countElement.textContent = cars.length;
    container.innerHTML = cars.map(car => createCarCard(car, 'filtered')).join('');
    section.style.display = 'block';
    
    console.log('✅ Resultados filtrados mostrados:', cars.length);
    
    // Mostrar estadísticas de marcas filtradas
    showFilteredStats(cars);
}

// Mostrar recomendaciones inteligentes
function displayIntelligentRecommendations(cars) {
    const section = document.getElementById('similar-tastes-section');
    const container = document.getElementById('similar-cars');
    const countElement = document.getElementById('similar-count');
    
    if (!section || !container || !countElement) {
        console.error('❌ Elementos de recomendaciones no encontrados');
        return;
    }
    
    if (cars.length === 0) {
        section.style.display = 'none';
        console.log('⚠️ No hay recomendaciones inteligentes');
        return;
    }
    
    countElement.textContent = cars.length;
    container.innerHTML = cars.map(car => createCarCard(car, 'recommended')).join('');
    section.style.display = 'block';
    
    console.log('✅ Recomendaciones inteligentes mostradas:', cars.length);
    
    // Mostrar estadísticas de recomendaciones
    showRecommendationStats(cars);
}

// Mostrar estadísticas de filtrados
function showFilteredStats(cars) {
    const brandCounts = {};
    cars.forEach(car => {
        brandCounts[car.brand] = (brandCounts[car.brand] || 0) + 1;
    });
    
    console.log('📊 Distribución de marcas en filtrados:', brandCounts);
    
    // Mostrar en la interfaz si hay un elemento para ello
    const statsElement = document.getElementById('filtered-stats');
    if (statsElement) {
        const brandsList = Object.entries(brandCounts)
            .map(([brand, count]) => `${brand} (${count})`)
            .join(', ');
        
        statsElement.innerHTML = `
            <div class="stats-info">
                <small>📊 Distribución: ${brandsList}</small>
            </div>
        `;
    }
}

// Mostrar estadísticas de recomendaciones
function showRecommendationStats(cars) {
    const brandCounts = {};
    cars.forEach(car => {
        brandCounts[car.brand] = (brandCounts[car.brand] || 0) + 1;
    });
    
    console.log('🎯 Distribución de marcas en recomendaciones:', brandCounts);
    
    // Mostrar patrones detectados
    const patterns = detectPatterns(cars);
    console.log('🔍 Patrones detectados en recomendaciones:', patterns);
    
    const statsElement = document.getElementById('recommendation-stats');
    if (statsElement) {
        const brandsList = Object.entries(brandCounts)
            .map(([brand, count]) => `${brand} (${count})`)
            .join(', ');
        
        statsElement.innerHTML = `
            <div class="stats-info">
                <small>🎯 Marcas sugeridas: ${brandsList}</small>
                ${patterns.length > 0 ? `<small>🔍 Patrones: ${patterns.join(', ')}</small>` : ''}
            </div>
        `;
    }
}

// Detectar patrones en las recomendaciones
function detectPatterns(cars) {
    const patterns = [];
    const brands = cars.map(car => car.brand);
    
    // Detectar si son marcas alemanas
    const germanBrands = ['BMW', 'Mercedes-Benz', 'Audi', 'Volkswagen', 'Porsche'];
    if (brands.some(brand => germanBrands.includes(brand))) {
        patterns.push('Alemanas Premium');
    }
    
    // Detectar si son marcas japonesas
    const japaneseBrands = ['Toyota', 'Honda', 'Mazda', 'Nissan', 'Subaru', 'Lexus'];
    if (brands.some(brand => japaneseBrands.includes(brand))) {
        patterns.push('Japonesas Confiables');
    }
    
    // Detectar si son marcas americanas
    const americanBrands = ['Ford', 'Chevrolet', 'Dodge', 'Cadillac'];
    if (brands.some(brand => americanBrands.includes(brand))) {
        patterns.push('Americanas Potentes');
    }
    
    return patterns;
}

// Crear tarjeta de auto mejorada con razón de recomendación
function createCarCard(car, type) {
    const isFavorite = userFavorites.some(fav => fav.id === car.id);
    const typeClass = type === 'filtered' ? 'exact-match' : 'smart-recommendation';
    const typeIcon = type === 'filtered' ? '🔍' : '🎯';
    const typeLabel = type === 'filtered' ? 'Coincidencia Exacta' : 'Recomendación Inteligente';
    
    return `
        <div class="car-card ${typeClass}" onclick="showCarDetails('${car.id}', '${type}')">
            <div class="match-type-badge ${typeClass}">
                ${typeIcon} ${typeLabel}
            </div>
            <div class="score-badge">${Math.round(car.similarity_score)}%</div>
            <div class="car-image">🚗</div>
            <div class="car-content">
                <div class="car-header">
                    <div class="car-name">${car.name || 'Auto sin nombre'}</div>
                    <div class="car-price">${(car.price || 0).toLocaleString()}</div>
                </div>
                
                <!-- Razón de coincidencia/recomendación -->
                <div class="match-reason ${typeClass}">
                    <span class="reason-icon">${type === 'filtered' ? '✓' : '💡'}</span>
                    <span class="reason-text">${car.match_reason || 'Sin razón especificada'}</span>
                </div>
                
                <div class="car-details">
                    <div class="car-detail">
                        <strong>Marca:</strong> ${car.brand || 'N/A'}
                    </div>
                    <div class="car-detail">
                        <strong>Año:</strong> ${car.year || 'N/A'}
                    </div>
                    <div class="car-detail">
                        <strong>Tipo:</strong> ${car.type || 'N/A'}
                    </div>
                    <div class="car-detail">
                        <strong>Combustible:</strong> ${car.fuel || 'N/A'}
                    </div>
                </div>
                
                ${car.features && car.features.length > 0 ? `
                <div class="car-features">
                    <div class="features-list">
                        ${car.features.slice(0, 4).map(feature => `
                            <span class="feature-tag">${feature}</span>
                        `).join('')}
                        ${car.features.length > 4 ? `
                            <span class="feature-tag">+${car.features.length - 4} más</span>
                        ` : ''}
                    </div>
                </div>
                ` : ''}
                
                <div class="car-actions" onclick="event.stopPropagation()">
                    <button class="action-btn btn-primary" onclick="showCarDetails('${car.id}', '${type}')">
                        👁️ Ver Detalles
                    </button>
                    <button class="action-btn btn-favorite ${isFavorite ? 'active' : ''}" 
                            onclick="toggleFavorite('${car.id}', '${type}')">
                        ${isFavorite ? '❤️ Favorito' : '🤍 Agregar'}
                    </button>
                </div>
            </div>
        </div>
    `;
}

// Mostrar detalles del auto en modal
function showCarDetails(carId, type) {
    console.log('🔍 Mostrando detalles del auto:', carId, type);
    
    // Buscar el auto en las listas correctas
    const allCars = [...filteredCars, ...recommendedCars];
    const car = allCars.find(c => c.id === carId);
    
    if (!car) {
        console.error('❌ Auto no encontrado:', carId);
        alert('Auto no encontrado');
        return;
    }
    
    const modal = document.getElementById('car-modal');
    const detailsContainer = document.getElementById('modal-car-details');
    
    if (!modal || !detailsContainer) {
        console.error('❌ Modal no encontrado');
        alert('Modal no disponible');
        return;
    }
    
    const typeLabel = car.match_type === 'filtered' ? 'Coincidencia Exacta' : 'Recomendación Inteligente';
    const typeIcon = car.match_type === 'filtered' ? '🔍' : '🎯';
    const typeClass = car.match_type === 'filtered' ? 'exact-match' : 'smart-recommendation';
    
    detailsContainer.innerHTML = `
        <div class="modal-car-header">
            <h2>${car.name}</h2>
            <div class="modal-price">${car.price.toLocaleString()}</div>
            <div class="modal-type-badge ${typeClass}">
                ${typeIcon} ${typeLabel}
            </div>
        </div>
        
        <div class="modal-match-reason ${typeClass}">
            <h3>${car.match_type === 'filtered' ? '✓ Razón de Coincidencia' : '💡 Razón de Recomendación'}</h3>
            <p>${car.match_reason}</p>
        </div>
        
        <div class="modal-car-info">
            <div class="info-grid">
                <div class="info-item">
                    <strong>Marca:</strong> ${car.brand}
                </div>
                <div class="info-item">
                    <strong>Modelo:</strong> ${car.model}
                </div>
                <div class="info-item">
                    <strong>Año:</strong> ${car.year}
                </div>
                <div class="info-item">
                    <strong>Tipo:</strong> ${car.type}
                </div>
                <div class="info-item">
                    <strong>Combustible:</strong> ${car.fuel}
                </div>
                <div class="info-item">
                    <strong>Transmisión:</strong> ${car.transmission}
                </div>
                <div class="info-item">
                    <strong>Segmento:</strong> ${car.segment || 'N/A'}
                </div>
                <div class="info-item">
                    <strong>Puntuación:</strong> ${car.similarity_score.toFixed(1)}%
                </div>
            </div>
            
            ${car.features && car.features.length > 0 ? `
            <div class="modal-features">
                <h3>Características:</h3>
                <div class="features-grid">
                    ${car.features.map(feature => `
                        <span class="feature-tag">${feature}</span>
                    `).join('')}
                </div>
            </div>
            ` : ''}
        </div>
        
        <div class="modal-actions">
            <button class="action-btn btn-favorite" onclick="toggleFavorite('${car.id}', '${type}'); updateModalFavoriteButton('${car.id}')">
                ${userFavorites.some(fav => fav.id === car.id) ? '❤️ Quitar de Favoritos' : '🤍 Agregar a Favoritos'}
            </button>
            <button class="action-btn btn-primary" onclick="closeModal()">
                ✅ Cerrar
            </button>
        </div>
    `;
    
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

// Cerrar modal
function closeModal() {
    const modal = document.getElementById('car-modal');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
}

// Alternar favorito
async function toggleFavorite(carId, type) {
    console.log('❤️ Toggle favorito:', carId, type);
    
    try {
        // Buscar el auto en todas las listas
        const allCars = [...filteredCars, ...recommendedCars];
        const car = allCars.find(c => c.id === carId);
        
        if (!car) {
            console.error('❌ Auto no encontrado para favoritos');
            return;
        }
        
        const isFavorite = userFavorites.some(fav => fav.id === carId);
        
        if (isFavorite) {
            // Quitar de favoritos
            const response = await fetch('/api/remove-favorite', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ carId: carId })
            });
            
            if (response.ok) {
                userFavorites = userFavorites.filter(fav => fav.id !== carId);
                showNotification('Quitado de favoritos', 'success');
                console.log('✅ Favorito eliminado');
            } else {
                throw new Error('Error al eliminar favorito');
            }
        } else {
            // Agregar a favoritos
            const response = await fetch('/api/add-favorite', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ car: car })
            });
            
            if (response.ok) {
                userFavorites.push(car);
                showNotification('Agregado a favoritos', 'success');
                console.log('✅ Favorito agregado');
            } else {
                throw new Error('Error al agregar favorito');
            }
        }
        
        // Actualizar UI
        updateFavoriteButtons();
        
    } catch (error) {
        console.error('❌ Error al actualizar favorito:', error);
        showNotification('Error al actualizar favorito', 'error');
    }
}

// Actualizar botones de favoritos
function updateFavoriteButtons() {
    // Recargar las secciones para actualizar los botones
    if (filteredCars.length > 0) {
        displayFilteredResults(filteredCars);
    }
    if (recommendedCars.length > 0) {
        displayIntelligentRecommendations(recommendedCars);
    }
}

// Actualizar botón de favorito en modal
function updateModalFavoriteButton(carId) {
    const isFavorite = userFavorites.some(fav => fav.id === carId);
    const button = document.querySelector('.modal-actions .btn-favorite');
    if (button) {
        button.innerHTML = isFavorite ? '❤️ Quitar de Favoritos' : '🤍 Agregar a Favoritos';
        button.className = `action-btn btn-favorite ${isFavorite ? 'active' : ''}`;
    }
}

// Cargar favoritos del usuario
async function loadUserFavorites() {
    try {
        const response = await fetch('/api/user-favorites');
        if (response.ok) {
            const data = await response.json();
            userFavorites = data.favorites || [];
            console.log('❤️ Favoritos cargados:', userFavorites.length);
        }
    } catch (error) {
        console.error('❌ Error cargando favoritos:', error);
    }
}

// Mostrar/ocultar loading
function showLoading() {
    const loading = document.getElementById('loading');
    const error = document.getElementById('error-message');
    const filtered = document.getElementById('filtered-section');
    const similar = document.getElementById('similar-tastes-section');
    
    if (loading) loading.style.display = 'block';
    if (error) error.style.display = 'none';
    if (filtered) filtered.style.display = 'none';
    if (similar) similar.style.display = 'none';
    
    console.log('⏳ Loading mostrado');
}

function hideLoading() {
    const loading = document.getElementById('loading');
    if (loading) loading.style.display = 'none';
    console.log('✅ Loading ocultado');
}

// Mostrar error
function showError(message) {
    console.error('💥 Mostrando error:', message);
    
    hideLoading();
    
    const errorElement = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    
    if (errorElement && errorText) {
        errorText.textContent = message;
        errorElement.style.display = 'block';
    } else {
        // Fallback: mostrar alerta
        alert('Error: ' + message);
    }
}

// Mostrar notificación
function showNotification(message, type = 'info') {
    console.log('📢 Notificación:', message, type);
    
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">×</button>
    `;
    
    // Agregar estilos si no existen
    if (!document.getElementById('notification-styles')) {
        const styles = document.createElement('style');
        styles.id = 'notification-styles';
        styles.textContent = `
            .notification {
                position: fixed;
                top: 80px;
                right: 20px;
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 15px 20px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                z-index: 2001;
                display: flex;
                align-items: center;
                gap: 10px;
                animation: slideIn 0.3s ease;
                max-width: 300px;
            }
            .notification.success {
                border-left: 4px solid #10b981;
                background: #f0fdf4;
            }
            .notification.error {
                border-left: 4px solid #ef4444;
                background: #fef2f2;
            }
            .notification button {
                background: none;
                border: none;
                cursor: pointer;
                font-size: 18px;
                color: #64748b;
            }
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(styles);
    }
    
    document.body.appendChild(notification);
    
    // Auto-remover después de 3 segundos
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 3000);
}

// Reintentar recomendaciones
function retryRecommendations() {
    console.log('🔄 Reintentando recomendaciones...');
    loadRecommendationsWithSeparation();
}

// Navegación
function goBack() {
    window.history.back();
}

// Cerrar modal al hacer clic fuera
window.onclick = function(event) {
    const modal = document.getElementById('car-modal');
    if (event.target === modal) {
        closeModal();
    }
}

// Hacer funciones disponibles globalmente
window.showCarDetails = showCarDetails;
window.toggleFavorite = toggleFavorite;
window.closeModal = closeModal;
window.retryRecommendations = retryRecommendations;
window.goBack = goBack;
window.updateModalFavoriteButton = updateModalFavoriteButton;

console.log('✅ recommendations.js con separación inteligente cargado completamente');