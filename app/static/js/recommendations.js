console.log('🚀 Recommendations JS iniciando...');

// Estado global
let userFavorites = [];
let filteredCars = [];
let similarTastesCars = [];
let demographicCars = [];
let currentFilters = {};

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    console.log('📱 DOM cargado, iniciando aplicación...');
    initializeApp();
});

async function initializeApp() {
    try {
        console.log('🔄 Inicializando aplicación...');
        
        // Cargar componentes básicos
        await loadUserInfo();
        loadFiltersApplied();
        await loadUserFavorites();
        
        // Cargar recomendaciones
        await loadRecommendations();
        
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

// Mostrar filtros aplicados y guardar en estado
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
    
    // Guardar en estado global para usar en análisis de recomendaciones
    currentFilters = filters;
    
    console.log('📋 Filtros obtenidos desde sessionStorage:', filters);
    
    // Verificar si hay datos
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
        return `$${parseInt(min).toLocaleString()} - $${parseInt(max).toLocaleString()}`;
    }
    
    return budget;
}

// Cargar recomendaciones
async function loadRecommendations() {
    console.log('🎯 Iniciando carga de recomendaciones...');
    
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
        
        // Procesar recomendaciones
        processRecommendations(data);
        hideLoading();
        
        console.log('✅ Recomendaciones cargadas exitosamente');
        
    } catch (error) {
        console.error('❌ Error cargando recomendaciones:', error);
        hideLoading();
        showError(error.message);
    }
}

// Procesar y separar recomendaciones con lógica corregida y límite por marca
function processRecommendations(cars) {
    console.log('🔄 Procesando recomendaciones...', cars.length, 'autos recibidos');
    console.log('📊 Filtros del usuario:', currentFilters);
    
    // PASO 1: Filtrar coincidencias EXACTAS
    let exactMatches = cars.filter(car => {
        const matches = matchesAllFilters(car, currentFilters);
        console.log(`${car.name}: ¿Coincide exactamente? ${matches}`);
        return matches;
    });
    
    // Limitar a 4 autos por marca en filtrados
    exactMatches = limitCarsByBrand(exactMatches, 4);
    
    // PASO 2: Recomendaciones por gustos similares
    let similarTastes = cars.filter(car => {
        if (exactMatches.some(exact => exact.id === car.id)) return false; // No duplicar exactos
        return matchesSimilarTastes(car, currentFilters);
    });
    
    // Limitar a 4 autos por marca en gustos similares
    similarTastes = limitCarsByBrand(similarTastes, 4);
    
    // PASO 3: Recomendaciones demográficas
    let demographicRecs = cars.filter(car => {
        if (exactMatches.some(exact => exact.id === car.id)) return false; // No duplicar exactos
        if (similarTastes.some(similar => similar.id === car.id)) return false; // No duplicar similares
        return hasDemographicBonus(car);
    });
    
    // Limitar a 4 autos por marca en demográficas
    demographicRecs = limitCarsByBrand(demographicRecs, 4);
    
    console.log('📊 Resultados separados (con límite por marca):');
    console.log('  🔍 Coincidencias exactas:', exactMatches.length);
    console.log('  🎯 Gustos similares:', similarTastes.length);
    console.log('  👤 Demográficas:', demographicRecs.length);
    
    // Mostrar distribución por marca
    console.log('📈 Distribución por marca en filtrados:');
    const filteredByBrand = groupByBrand(exactMatches);
    Object.entries(filteredByBrand).forEach(([brand, cars]) => {
        console.log(`  ${brand}: ${cars.length} autos`);
    });
    
    console.log('📈 Distribución por marca en gustos similares:');
    const similarByBrand = groupByBrand(similarTastes);
    Object.entries(similarByBrand).forEach(([brand, cars]) => {
        console.log(`  ${brand}: ${cars.length} autos`);
    });
    
    // Guardar en variables globales
    filteredCars = exactMatches;
    similarTastesCars = similarTastes;
    demographicCars = demographicRecs;
    
    // Mostrar en orden correcto
    displayFilteredResults(exactMatches);
    displaySimilarTastesRecommendations(similarTastes);
    displayDemographicRecommendations(demographicRecs);
}

// Función para limitar autos por marca
function limitCarsByBrand(cars, maxPerBrand = 4) {
    console.log(`🔢 Limitando a ${maxPerBrand} autos por marca de ${cars.length} autos totales`);
    
    // Agrupar por marca
    const carsByBrand = groupByBrand(cars);
    
    // Limitar cada marca y combinar
    const limitedCars = [];
    
    Object.entries(carsByBrand).forEach(([brand, brandCars]) => {
        // Ordenar por puntuación descendente y tomar los mejores
        const sortedBrandCars = brandCars
            .sort((a, b) => (b.similarity_score || 0) - (a.similarity_score || 0))
            .slice(0, maxPerBrand);
        
        console.log(`  ${brand}: ${brandCars.length} → ${sortedBrandCars.length} autos`);
        limitedCars.push(...sortedBrandCars);
    });
    
    // Ordenar el resultado final por puntuación
    const finalResult = limitedCars.sort((a, b) => (b.similarity_score || 0) - (a.similarity_score || 0));
    
    console.log(`✅ Resultado final: ${cars.length} → ${finalResult.length} autos (máximo ${maxPerBrand} por marca)`);
    
    return finalResult;
}

// Función para agrupar autos por marca
function groupByBrand(cars) {
    const grouped = {};
    
    cars.forEach(car => {
        const brand = car.brand || 'Sin marca';
        if (!grouped[brand]) {
            grouped[brand] = [];
        }
        grouped[brand].push(car);
    });
    
    return grouped;
}

// Verificar si un auto coincide EXACTAMENTE con TODOS los filtros
function matchesAllFilters(car, filters) {
    console.log(`Verificando ${car.name}:`);
    
    // Verificar marca - DEBE estar en la lista seleccionada
    if (filters.brands.length > 0) {
        const brandMatch = filters.brands.includes(car.brand);
        console.log(`  Marca ${car.brand} en ${JSON.stringify(filters.brands)}: ${brandMatch}`);
        if (!brandMatch) return false;
    }
    
    // Verificar combustible
    if (filters.fuel.length > 0) {
        const fuelMatch = filters.fuel.includes(car.fuel);
        console.log(`  Combustible ${car.fuel} en ${JSON.stringify(filters.fuel)}: ${fuelMatch}`);
        if (!fuelMatch) return false;
    }
    
    // Verificar tipo
    if (filters.types.length > 0) {
        const typeMatch = filters.types.includes(car.type);
        console.log(`  Tipo ${car.type} en ${JSON.stringify(filters.types)}: ${typeMatch}`);
        if (!typeMatch) return false;
    }
    
    // Verificar transmisión
    if (filters.transmission.length > 0) {
        const transMatch = filters.transmission.includes(car.transmission);
        console.log(`  Transmisión ${car.transmission} en ${JSON.stringify(filters.transmission)}: ${transMatch}`);
        if (!transMatch) return false;
    }
    
    // Verificar presupuesto
    if (filters.budget && filters.budget.includes('-')) {
        const [min, max] = filters.budget.split('-').map(x => parseInt(x));
        const budgetMatch = car.price >= min && car.price <= max;
        console.log(`  Precio $${car.price} entre $${min}-$${max}: ${budgetMatch}`);
        if (!budgetMatch) return false;
    }
    
    console.log(`  ✅ ${car.name} cumple TODOS los filtros`);
    return true;
}

// Verificar si un auto es recomendación por gustos similares
function matchesSimilarTastes(car, filters) {
    if (filters.brands.length === 0) return false;
    
    // Definir marcas similares por origen/características
    const brandSimilarities = {
        // Marcas alemanas de lujo
        'BMW': ['Audi', 'Mercedes-Benz', 'Lexus', 'Genesis'],
        'Mercedes-Benz': ['BMW', 'Audi', 'Lexus', 'Genesis'],
        'Audi': ['BMW', 'Mercedes-Benz', 'Lexus', 'Genesis'],
        
        // Marcas japonesas confiables
        'Toyota': ['Honda', 'Mazda', 'Nissan', 'Subaru'],
        'Honda': ['Toyota', 'Mazda', 'Nissan', 'Subaru'],
        'Mazda': ['Honda', 'Toyota', 'Subaru', 'Nissan'],
        'Subaru': ['Mazda', 'Honda', 'Toyota', 'Nissan'],
        'Nissan': ['Toyota', 'Honda', 'Mazda', 'Subaru'],
        
        // Marcas coreanas de valor
        'Hyundai': ['Kia', 'Honda', 'Toyota', 'Nissan'],
        'Kia': ['Hyundai', 'Honda', 'Toyota', 'Mazda'],
        
        // Marcas americanas
        'Ford': ['Chevrolet', 'Jeep'],
        'Chevrolet': ['Ford', 'Jeep'],
        
        // Marcas de lujo
        'Lexus': ['BMW', 'Mercedes-Benz', 'Audi', 'Genesis'],
        'Genesis': ['BMW', 'Mercedes-Benz', 'Audi', 'Lexus']
    };
    
    // Verificar si la marca del auto es similar a alguna marca seleccionada
    for (const selectedBrand of filters.brands) {
        const similarBrands = brandSimilarities[selectedBrand] || [];
        if (similarBrands.includes(car.brand)) {
            console.log(`${car.name}: Marca ${car.brand} es similar a ${selectedBrand}`);
            return true;
        }
    }
    
    return false;
}

// Verificar si un auto tiene bonificación demográfica
function hasDemographicBonus(car) {
    return car.demographic_bonus && car.demographic_bonus > 0;
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
    container.innerHTML = cars.map(car => createCarCard(car, 'filtered', 'Coincidencia exacta con todos tus filtros')).join('');
    section.style.display = 'block';
    
    console.log('✅ Coincidencias exactas mostradas:', cars.length);
}

// Mostrar recomendaciones por gustos similares
function displaySimilarTastesRecommendations(cars) {
    const section = document.getElementById('similar-tastes-section');
    const container = document.getElementById('similar-cars');
    const countElement = document.getElementById('similar-count');
    
    if (!section || !container || !countElement) {
        console.error('❌ Elementos de gustos similares no encontrados');
        return;
    }
    
    if (cars.length === 0) {
        section.style.display = 'none';
        return;
    }
    
    countElement.textContent = cars.length;
    container.innerHTML = cars.map(car => {
        const reason = getSimilarTasteReason(car, currentFilters);
        return createCarCard(car, 'similar', reason);
    }).join('');
    section.style.display = 'block';
    
    console.log('✅ Recomendaciones por gustos similares mostradas:', cars.length);
}

// Mostrar recomendaciones demográficas
function displayDemographicRecommendations(cars) {
    const section = document.getElementById('demographic-section');
    const container = document.getElementById('demographic-cars');
    const countElement = document.getElementById('demographic-count');
    
    if (!section || !container || !countElement) {
        console.error('❌ Elementos demográficos no encontrados');
        return;
    }
    
    if (cars.length === 0) {
        section.style.display = 'none';
        return;
    }
    
    countElement.textContent = cars.length;
    container.innerHTML = cars.map(car => {
        const reason = getDemographicReason(car);
        return createCarCard(car, 'demographic', reason);
    }).join('');
    section.style.display = 'block';
    
    console.log('✅ Recomendaciones demográficas mostradas:', cars.length);
}

// Obtener razón específica para gustos similares
function getSimilarTasteReason(car, filters) {
    const brandOrigins = {
        'BMW': 'alemana de lujo', 'Mercedes-Benz': 'alemana de lujo', 'Audi': 'alemana de lujo',
        'Toyota': 'japonesa confiable', 'Honda': 'japonesa confiable', 'Mazda': 'japonesa confiable', 'Subaru': 'japonesa confiable',
        'Hyundai': 'coreana de valor', 'Kia': 'coreana de valor',
        'Lexus': 'lujo japonés', 'Genesis': 'lujo coreano'
    };
    
    const carOrigin = brandOrigins[car.brand] || 'similar';
    return `Marca ${carOrigin} similar a tus selecciones`;
}

// Obtener razón específica para demografía
function getDemographicReason(car) {
    if (car.demographic_bonus) {
        return `Recomendado para tu perfil (+${car.demographic_bonus} puntos demográficos)`;
    }
    return 'Recomendado para tu perfil demográfico';
}

// Crear tarjeta de auto con razón de recomendación
function createCarCard(car, type, reason) {
    const isFavorite = userFavorites.some(fav => fav.id === car.id);
    const scoreLabel = type === 'filtered' ? 'Coincidencia' : 'Recomendación';
    
    return `
        <div class="car-card" onclick="showCarDetails('${car.id}', '${type}')">
            <div class="score-badge">${scoreLabel}: ${Math.round(car.similarity_score)}%</div>
            <div class="car-image">🚗</div>
            <div class="car-content">
                <div class="car-header">
                    <div class="car-name">${car.name || 'Auto sin nombre'}</div>
                    <div class="car-price">$${(car.price || 0).toLocaleString()}</div>
                </div>
                
                <!-- Razón de recomendación -->
                <div class="recommendation-reason">
                    <span class="reason-label">💡 ${reason}</span>
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
    
    // Buscar el auto en todas las listas
    const allCars = [...filteredCars, ...similarTastesCars, ...demographicCars];
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
    
    detailsContainer.innerHTML = `
        <div class="modal-car-header">
            <h2>${car.name}</h2>
            <div class="modal-price">$${car.price.toLocaleString()}</div>
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
            
            ${car.recommendation_reason ? `
            <div class="recommendation-info">
                <h3>💡 Razón de Recomendación</h3>
                <p>${car.recommendation_reason}</p>
            </div>
            ` : ''}
            
            ${car.demographic_bonus ? `
            <div class="demographic-info">
                <h3>👤 Personalización Aplicada</h3>
                <p>Este auto recibió +${car.demographic_bonus} puntos adicionales basándose en tu perfil demográfico.</p>
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
        const allCars = [...filteredCars, ...similarTastesCars, ...demographicCars];
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
    if (similarTastesCars.length > 0) {
        displaySimilarTastesRecommendations(similarTastesCars);
    }
    if (demographicCars.length > 0) {
        displayDemographicRecommendations(demographicCars);
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
    const demographic = document.getElementById('demographic-section');
    
    if (loading) loading.style.display = 'block';
    if (error) error.style.display = 'none';
    if (filtered) filtered.style.display = 'none';
    if (similar) similar.style.display = 'none';
    if (demographic) demographic.style.display = 'none';
    
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
    loadRecommendations();
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

// Función de debug para probar sessionStorage
function debugSessionStorage() {
    console.log('🔍 DEBUG SESSIONSTORAGE:');
    console.log('All sessionStorage items:');
    for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        const value = sessionStorage.getItem(key);
        console.log(`  ${key}: ${value}`);
    }
    
    console.log('\nSpecific filters:');
    console.log('  brands:', sessionStorage.getItem('selected_brands'));
    console.log('  budget:', sessionStorage.getItem('selected_budget'));
    console.log('  fuel:', sessionStorage.getItem('selected_fuel'));
    console.log('  types:', sessionStorage.getItem('selected_types'));
    console.log('  transmission:', sessionStorage.getItem('selected_transmission'));
}

// Ejecutar debug después de 2 segundos para diagnosticar problemas
setTimeout(debugSessionStorage, 2000);

// Hacer funciones disponibles globalmente
window.showCarDetails = showCarDetails;
window.toggleFavorite = toggleFavorite;
window.closeModal = closeModal;
window.retryRecommendations = retryRecommendations;
window.goBack = goBack;
window.updateModalFavoriteButton = updateModalFavoriteButton;
window.debugSessionStorage = debugSessionStorage;

console.log('✅ recommendations.js cargado completamente');