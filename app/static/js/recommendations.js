// recommendations.js - Actualizado para recomendaciones inteligentes
document.addEventListener('DOMContentLoaded', () => {
    updateStatus('js-status', '✓ JavaScript cargado');
    loadRecommendations();
});

async function shareCarRecommendation(carId) {
    const carData = getCurrentRecommendations().find(car => car.id === carId);
    
    if (!carData) {
        showToast('❌ Auto no encontrado');
        return;
    }
    
    const shareText = `¡Encontré el auto perfecto! ${carData.name} - ${carData.price.toLocaleString()}\n\nCompatibilidad: ${carData.similarity_score}/100\n${carData.recommendation_reason}`;
    
    if (navigator.share) {
        navigator.share({
            title: `Recomendación: ${carData.name}`,
            text: shareText,
            url: window.location.href
        }).catch(err => console.log('Error compartiendo:', err));
    } else {
        // Fallback: copiar al portapapeles
        navigator.clipboard.writeText(shareText).then(() => {
            showToast('📋 Información copiada al portapapeles');
        }).catch(() => {
            showToast('❌ No se pudo copiar la información');
        });
    }
}

function getCurrentRecommendations() {
    // Obtener recomendaciones actuales del DOM o variable global
    const cards = document.querySelectorAll('.car-card');
    const recommendations = [];
    
    cards.forEach(card => {
        const carId = card.querySelector('.favorite-btn').dataset.carId;
        const name = card.querySelector('.car-name').textContent;
        const brand = card.querySelector('.car-brand').textContent;
        const priceText = card.querySelector('.car-price').textContent;
        const price = parseInt(priceText.replace(/[^0-9]/g, ''));
        const scoreText = card.querySelector('.score-value').textContent;
        const similarity_score = parseFloat(scoreText.split('/')[0]);
        const recommendation_reason = card.querySelector('.recommendation-reason p').textContent;
        const type = card.querySelector('.car-details .detail:nth-child(1) span').textContent;
        const fuel = card.querySelector('.car-details .detail:nth-child(2) span').textContent;
        const transmission = card.querySelector('.car-details .detail:nth-child(3) span').textContent;
        const year = card.querySelector('.car-details .detail:nth-child(4) span').textContent;
        
        const features = [];
        const featureElements = card.querySelectorAll('.car-features li:not(.more-features)');
        featureElements.forEach(el => features.push(el.textContent));
        
        recommendations.push({
            id: carId,
            name,
            brand,
            price,
            similarity_score,
            recommendation_reason,
            type,
            fuel,
            transmission,
            year: parseInt(year),
            features
        });
    });
    
    return recommendations;
}

function showActionButtons() {
    const actionButtons = document.getElementById('action-buttons');
    if (actionButtons) {
        actionButtons.style.display = 'flex';
    }
}

function showNoRecommendations() {
    const container = document.getElementById('recommendations-container');
    if (!container) return;
    
    container.innerHTML = `
        <div class="no-recommendations">
            <h3>🔍 No se encontraron recomendaciones</h3>
            <p>No pudimos encontrar autos que coincidan exactamente con tus criterios.</p>
            <p>Esto puede deberse a:</p>
            <ul>
                <li>Criterios muy específicos que limitan las opciones</li>
                <li>Combinación de preferencias poco común</li>
                <li>Rango de presupuesto muy restringido</li>
            </ul>
            <p><strong>Sugerencias:</strong></p>
            <ul>
                <li>Intenta ampliar tu rango de presupuesto</li>
                <li>Considera marcas adicionales similares a tus preferidas</li>
                <li>Explora diferentes tipos de vehículo</li>
            </ul>
            <button onclick="restartProcess()" class="restart-btn">
                🔄 Comenzar Nueva Búsqueda
            </button>
        </div>
    `;
    container.style.display = 'block';
}

function showLoading(show) {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = show ? 'block' : 'none';
    }
}

function showError(message) {
    const errorContainer = document.getElementById('error-container');
    if (!errorContainer) return;
    
    errorContainer.innerHTML = `
        <div class="error-message">
            <h3>❌ Error al obtener recomendaciones</h3>
            <p><strong>Detalles del error:</strong> ${message}</p>
            
            <h4>🔧 Posibles soluciones:</h4>
            <ul>
                <li>Verifica que hayas completado todos los pasos de selección</li>
                <li>Asegúrate de estar conectado a internet</li>
                <li>Intenta recargar la página</li>
                <li>Si el problema persiste, comienza el proceso nuevamente</li>
            </ul>
            
            <div class="error-actions">
                <button onclick="loadRecommendations()" class="retry-btn">
                    🔁 Reintentar
                </button>
                <button onclick="restartProcess()" class="restart-btn">
                    🔄 Empezar de Nuevo
                </button>
            </div>
        </div>
    `;
    errorContainer.style.display = 'block';
}

function hideError() {
    const errorContainer = document.getElementById('error-container');
    if (errorContainer) {
        errorContainer.style.display = 'none';
    }
}

function updateStatus(elementId, status) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = status;
    }
}

function showToast(message) {
    // Remover toast anterior si existe
    const existingToast = document.querySelector('.toast-notification');
    if (existingToast) {
        existingToast.remove();
    }
    
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #333;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        z-index: 10000;
        font-size: 14px;
        max-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    // Animar entrada
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
    }, 10);
    
    // Animar salida y remover
    setTimeout(() => {
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

// Funciones de acción
function restartProcess() {
    if (confirm('¿Estás seguro de que quieres empezar una nueva búsqueda? Se perderán tus selecciones actuales.')) {
        window.location.href = '/brands';
    }
}

function exportFavorites() {
    fetch('/api/export-favorites')
        .then(response => {
            if (!response.ok) {
                throw new Error('Error exportando favoritos');
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'mis-favoritos.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            showToast('📥 Favoritos exportados exitosamente');
        })
        .catch(error => {
            console.error('Error exportando favoritos:', error);
            showToast('❌ Error al exportar favoritos');
        });
}

// Función para mostrar estadísticas de debug en desarrollo
function showDebugInfo() {
    fetch('/api/debug/session')
        .then(response => response.json())
        .then(data => {
            console.log('🔍 Debug Info:', data);
            
            const debugInfo = document.querySelector('.debug-info');
            if (debugInfo) {
                debugInfo.innerHTML = `
                    <strong>Debug Info:</strong><br>
                    Sesión activa: ${data.session_data?.logged_in ? '✓' : '✗'}<br>
                    Datos completos: ${data.all_present ? '✓' : '✗'}<br>
                    Recommender: ${data.recommender_available ? '✓' : '✗'}<br>
                    Usuarios: ${data.users_count}<br>
                    Perfiles: ${data.profiles_count}
                `;
            }
        })
        .catch(error => {
            console.log('No se pudo obtener info de debug:', error);
        });
}

// Efectos visuales adicionales
function addVisualEnhancements() {
    // Efecto parallax sutil en las tarjetas
    const cards = document.querySelectorAll('.car-card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-8px) scale(1.02)';
            card.style.boxShadow = '0 20px 40px rgba(0,0,0,0.15)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0) scale(1)';
            card.style.boxShadow = '0 6px 12px rgba(0,0,0,0.1)';
        });
    });
    
    // Efecto de typing en las razones de recomendación
    const reasons = document.querySelectorAll('.recommendation-reason p');
    reasons.forEach((reason, index) => {
        const text = reason.textContent;
        reason.textContent = '';
        
        setTimeout(() => {
            let i = 0;
            const typeInterval = setInterval(() => {
                reason.textContent = text.slice(0, i);
                i++;
                if (i > text.length) {
                    clearInterval(typeInterval);
                }
            }, 20);
        }, index * 200);
    });
}

// Inicializar efectos visuales después de cargar recomendaciones
document.addEventListener('recommendationsLoaded', () => {
    addVisualEnhancements();
});

// Ejecutar debug info en desarrollo
if (window.location.hostname === 'localhost') {
    setTimeout(showDebugInfo, 1000);
}

// Event listeners para cerrar modales con Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeCarDetailsModal();
    }
});

// Cerrar modal haciendo clic fuera
document.addEventListener('click', (e) => {
    if (e.target && e.target.classList.contains('modal-overlay')) {
        closeCarDetailsModal();
    }
}); loadRecommendations() {
    try {
        updateStatus('api-status', '⏳ Obteniendo recomendaciones...');
        updateStatus('personalization-status', '⏳ Aplicando personalización...');
        
        showLoading(true);
        hideError();
        
        // Llamar al API de recomendaciones inteligentes
        const response = await fetch('/api/recommendations', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const recommendations = await response.json();
        
        updateStatus('api-status', '✓ Recomendaciones obtenidas');
        updateStatus('personalization-status', '✓ Personalización aplicada');
        
        showLoading(false);
        
        if (recommendations && recommendations.length > 0) {
            displayRecommendations(recommendations);
            showSummary(recommendations);
            showActionButtons();
        } else {
            showNoRecommendations();
        }
        
    } catch (error) {
        console.error('Error cargando recomendaciones:', error);
        updateStatus('api-status', '✗ Error en API');
        updateStatus('personalization-status', '✗ Error en personalización');
        
        showLoading(false);
        showError(error.message);
    }
}

function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendations-container');
    if (!container) {
        console.error('Contenedor de recomendaciones no encontrado');
        return;
    }
    
    // Crear grid de recomendaciones
    const grid = document.createElement('div');
    grid.className = 'recommendations-grid';
    
    recommendations.forEach((car, index) => {
        const carCard = createIntelligentCarCard(car, index);
        grid.appendChild(carCard);
    });
    
    container.innerHTML = '';
    container.appendChild(grid);
    container.style.display = 'block';
    
    // Animar aparición de tarjetas
    setTimeout(() => {
        const cards = grid.querySelectorAll('.car-card');
        cards.forEach((card, index) => {
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }, 100);
}

function createIntelligentCarCard(car, index) {
    const card = document.createElement('div');
    card.className = 'car-card';
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'all 0.5s ease';
    
    // Determinar color del badge de score
    const scoreColor = getScoreColor(car.similarity_score);
    const scoreBadge = car.similarity_score >= 80 ? '🏆' : 
                      car.similarity_score >= 60 ? '⭐' : '👍';
    
    // Badge de bonus demográfico si aplica
    const demographicBonus = car.demographic_bonus ? 
        `<span class="demographic-bonus">+${car.demographic_bonus} Perfil</span>` : '';
    
    card.innerHTML = `
        <div class="car-image">
            ${car.image ? 
                `<img src="${car.image}" alt="${car.name}" loading="lazy">` :
                `<div class="no-image">
                    <div>📷</div>
                    <small>Imagen no disponible</small>
                </div>`
            }
        </div>
        
        <div class="car-info">
            <div class="car-header">
                <h3 class="car-name">${car.name}</h3>
                <span class="car-brand">${car.brand}</span>
            </div>
            
            <div class="car-price">$${car.price.toLocaleString()}</div>
            
            <div class="similarity-score" style="border-color: ${scoreColor}; background: ${scoreColor}15;">
                <div class="score-content">
                    <span class="score-label">${scoreBadge} Compatibilidad</span>
                    <span class="score-value" style="color: ${scoreColor}">
                        ${car.similarity_score}/100
                    </span>
                </div>
                ${demographicBonus}
            </div>
            
            <div class="recommendation-reason">
                <h4><i class="fas fa-lightbulb"></i> ¿Por qué te lo recomendamos?</h4>
                <p>${car.recommendation_reason || 'Buena opción según tus preferencias'}</p>
            </div>
            
            <div class="car-details">
                <div class="detail">
                    <strong>🚗 Tipo:</strong>
                    <span>${car.type}</span>
                </div>
                <div class="detail">
                    <strong>⛽ Combustible:</strong>
                    <span>${car.fuel}</span>
                </div>
                <div class="detail">
                    <strong>⚙️ Transmisión:</strong>
                    <span>${car.transmission}</span>
                </div>
                <div class="detail">
                    <strong>📅 Año:</strong>
                    <span>${car.year}</span>
                </div>
            </div>
            
            ${car.features && car.features.length > 0 ? `
                <div class="car-features">
                    <h4>✨ Características destacadas</h4>
                    <ul>
                        ${car.features.slice(0, 5).map(feature => 
                            `<li>${feature}</li>`
                        ).join('')}
                        ${car.features.length > 5 ? 
                            `<li class="more-features">+${car.features.length - 5} características más</li>` : ''
                        }
                    </ul>
                </div>
            ` : ''}
            
            <div class="car-actions">
                <button class="details-btn" onclick="showCarDetails('${car.id}')">
                    <i class="fas fa-info-circle"></i> Detalles
                </button>
                <button class="favorite-btn" onclick="toggleFavorite('${car.id}', this)" data-car-id="${car.id}">
                    <i class="fas fa-heart"></i> <span>Favorito</span>
                </button>
            </div>
        </div>
    `;
    
    return card;
}

function getScoreColor(score) {
    if (score >= 80) return '#27ae60';      // Verde - Excelente
    if (score >= 60) return '#f39c12';     // Naranja - Bueno  
    if (score >= 40) return '#e67e22';     // Naranja oscuro - Regular
    return '#95a5a6';                      // Gris - Bajo
}

function showSummary(recommendations) {
    const summarySection = document.getElementById('summary-section');
    if (!summarySection) return;
    
    // Calcular estadísticas
    const stats = calculateRecommendationStats(recommendations);
    
    const summaryContent = `
        <div class="summary-stats">
            <div class="stat">
                <span class="stat-number">${recommendations.length}</span>
                <span class="stat-label">Recomendaciones</span>
            </div>
            <div class="stat">
                <span class="stat-number">${stats.avgScore.toFixed(1)}</span>
                <span class="stat-label">Score Promedio</span>
            </div>
            <div class="stat">
                <span class="stat-number">${stats.uniqueBrands}</span>
                <span class="stat-label">Marcas Diferentes</span>
            </div>
            <div class="stat">
                <span class="stat-number">$${stats.avgPrice.toLocaleString()}</span>
                <span class="stat-label">Precio Promedio</span>
            </div>
        </div>
        
        <div class="summary-details">
            <p><strong>🎯 Sistema de Recomendaciones Inteligente:</strong> Estos resultados combinan tus preferencias seleccionadas con análisis de similitudes entre marcas y recomendaciones personalizadas según tu perfil demográfico.</p>
            
            <p><strong>🏆 Mejores opciones:</strong> ${stats.excellentCount} autos con compatibilidad excelente (80+ puntos)</p>
            
            <p><strong>🔍 Marcas incluidas:</strong> ${stats.brandsList}</p>
            
            <p><strong>💡 Tip:</strong> Los autos con mayor puntuación de compatibilidad están optimizados para tu perfil específico, pero también considera opciones con puntuaciones menores que podrían ofrecerte mejor valor.</p>
        </div>
    `;
    
    document.getElementById('summary-content').innerHTML = summaryContent;
    summarySection.style.display = 'block';
}

function calculateRecommendationStats(recommendations) {
    const scores = recommendations.map(car => car.similarity_score || 0);
    const prices = recommendations.map(car => car.price || 0);
    const brands = [...new Set(recommendations.map(car => car.brand))];
    
    return {
        avgScore: scores.reduce((a, b) => a + b, 0) / scores.length,
        avgPrice: prices.reduce((a, b) => a + b, 0) / prices.length,
        uniqueBrands: brands.length,
        brandsList: brands.slice(0, 5).join(', ') + (brands.length > 5 ? '...' : ''),
        excellentCount: recommendations.filter(car => (car.similarity_score || 0) >= 80).length
    };
}

async function toggleFavorite(carId, button) {
    try {
        const span = button.querySelector('span');
        const icon = button.querySelector('i');
        const isCurrentlyFavorite = button.classList.contains('added');
        
        // Cambiar estado visual inmediatamente
        if (isCurrentlyFavorite) {
            button.classList.remove('added');
            button.style.background = '#28a745';
            span.textContent = 'Favorito';
            icon.style.color = 'white';
        } else {
            button.classList.add('added');
            button.style.background = '#dc3545';
            span.textContent = 'Eliminar';
            icon.style.color = 'white';
        }
        
        // Encontrar datos del auto
        const carData = getCurrentRecommendations().find(car => car.id === carId);
        
        if (!carData) {
            throw new Error('Auto no encontrado');
        }
        
        // Enviar al servidor
        if (!isCurrentlyFavorite) {
            // Agregar a favoritos
            const response = await fetch('/api/add-favorite', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ car: carData })
            });
            
            if (!response.ok) {
                throw new Error('Error agregando a favoritos');
            }
            
            showToast(`✅ ${carData.name} agregado a favoritos`);
        } else {
            // Eliminar de favoritos
            const response = await fetch('/api/remove-favorite', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ carId: carId })
            });
            
            if (!response.ok) {
                throw new Error('Error eliminando de favoritos');
            }
            
            showToast(`🗑️ ${carData.name} eliminado de favoritos`);
        }
        
    } catch (error) {
        console.error('Error con favorito:', error);
        
        // Revertir cambio visual
        if (button.classList.contains('added')) {
            button.classList.remove('added');
            button.style.background = '#28a745';
            button.querySelector('span').textContent = 'Favorito';
        } else {
            button.classList.add('added');
            button.style.background = '#dc3545';
            button.querySelector('span').textContent = 'Eliminar';
        }
        
        showToast(`❌ Error: ${error.message}`);
    }
}

function showCarDetails(carId) {
    const carData = getCurrentRecommendations().find(car => car.id === carId);
    
    if (!carData) {
        showToast('❌ Información del auto no encontrada');
        return;
    }
    
    // Crear modal con detalles expandidos
    const modal = document.getElementById('carDetailModal') || createCarDetailModal();
    const modalTitle = document.getElementById('modalCarTitle');
    const modalSubtitle = document.getElementById('modalCarSubtitle');
    const modalBody = document.getElementById('modalBody');
    
    modalTitle.textContent = carData.name;
    modalSubtitle.textContent = `${carData.brand} • $${carData.price.toLocaleString()}`;
    
    modalBody.innerHTML = `
        <div class="detailed-car-info">
            <div class="detail-section">
                <h3>📊 Puntuación de Compatibilidad</h3>
                <div class="score-breakdown">
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${carData.similarity_score || 0}%; background-color: ${getScoreColor(carData.similarity_score || 0)};">
                            ${carData.similarity_score || 0}/100
                        </div>
                    </div>
                    <p class="score-explanation">${carData.recommendation_reason}</p>
                </div>
            </div>
            
            <div class="detail-section">
                <h3>🚗 Especificaciones Técnicas</h3>
                <div class="specs-grid">
                    <div class="spec-item">
                        <span class="spec-label">Tipo de vehículo:</span>
                        <span class="spec-value">${carData.type}</span>
                    </div>
                    <div class="spec-item">
                        <span class="spec-label">Año:</span>
                        <span class="spec-value">${carData.year}</span>
                    </div>
                    <div class="spec-item">
                        <span class="spec-label">Combustible:</span>
                        <span class="spec-value">${carData.fuel}</span>
                    </div>
                    <div class="spec-item">
                        <span class="spec-label">Transmisión:</span>
                        <span class="spec-value">${carData.transmission}</span>
                    </div>
                    ${carData.segmento ? `
                    <div class="spec-item">
                        <span class="spec-label">Segmento:</span>
                        <span class="spec-value">${carData.segmento}</span>
                    </div>
                    ` : ''}
                </div>
            </div>
            
            ${carData.features && carData.features.length > 0 ? `
            <div class="detail-section">
                <h3>✨ Características y Equipamiento</h3>
                <div class="features-list">
                    ${carData.features.map(feature => `
                        <div class="feature-item">
                            <i class="fas fa-check-circle"></i>
                            <span>${feature}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
            ` : ''}
            
            <div class="detail-actions">
                <button class="btn-primary" onclick="toggleFavorite('${carData.id}', this)">
                    <i class="fas fa-heart"></i> Agregar a Favoritos
                </button>
                <button class="btn-secondary" onclick="shareCarRecommendation('${carData.id}')">
                    <i class="fas fa-share"></i> Compartir
                </button>
            </div>
        </div>
    `;
    
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function createCarDetailModal() {
    const modal = document.createElement('div');
    modal.id = 'carDetailModal';
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-container">
            <div class="modal-header">
                <h3 id="modalCarTitle">Detalles del Vehículo</h3>
                <div id="modalCarSubtitle" class="modal-subtitle"></div>
                <button class="modal-close" onclick="closeCarDetailsModal()">&times;</button>
            </div>
            <div class="modal-body" id="modalBody">
                <!-- Contenido se carga dinámicamente -->
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    return modal;
}

function closeCarDetailsModal() {
    const modal = document.getElementById('carDetailModal');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
}

function