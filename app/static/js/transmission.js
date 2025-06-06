document.addEventListener('DOMContentLoaded', () => {
  let selectedTransmission = null;
  const nextBtn = document.getElementById('next-btn');

  // Configurar botones de transmisión
  document.querySelectorAll('.transmission-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const transmission = this.dataset.transmission;
      
      // Deseleccionar otros
      document.querySelectorAll('.transmission-btn').forEach(b => {
        b.classList.remove('selected');
      });
      
      // Seleccionar actual
      this.classList.add('selected');
      selectedTransmission = transmission;
      
      // Efecto visual mejorado
      this.style.transform = 'scale(1.05)';
      setTimeout(() => {
        this.style.transform = '';
      }, 200);
      
      // Habilitar siguiente
      nextBtn.disabled = false;
      updateButtonText(transmission);
    });

    // Efectos hover mejorados
    btn.addEventListener('mouseenter', function() {
      if (!this.classList.contains('selected')) {
        this.style.transform = 'translateY(-5px) scale(1.02)';
      }
    });

    btn.addEventListener('mouseleave', function() {
      if (!this.classList.contains('selected')) {
        this.style.transform = '';
      }
    });
  });

  function updateButtonText(transmission) {
    const transmissionNames = {
      'automatic': 'Automática',
      'manual': 'Manual',
      'semiautomatic': 'Semiautomática'
    };
    
    const name = transmissionNames[transmission] || transmission;
    nextBtn.innerHTML = `🎯 Ver Recomendaciones (${name}) <span style="margin-left: 0.5rem;">🚀</span>`;
  }

  // Configurar botón siguiente
  nextBtn.addEventListener('click', async () => {
    if (selectedTransmission) {
      try {
        // Mostrar loading con animación
        nextBtn.disabled = true;
        nextBtn.innerHTML = '⏳ Guardando y generando recomendaciones...';
        nextBtn.style.background = '#f39c12';
        
        const response = await fetch('/api/save-transmission', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ transmission: selectedTransmission })
        });
        
        if (response.ok) {
          // Efecto de éxito con confetti virtual
          nextBtn.style.background = 'linear-gradient(135deg, #27ae60, #2ecc71)';
          nextBtn.innerHTML = '🎉 ¡Listo! Cargando recomendaciones personalizadas...';
          
          // Mostrar progreso final
          updateProgressBar(100);
          
          // Efectos visuales de celebración
          setTimeout(() => {
            showSuccessAnimation();
          }, 500);
          
          setTimeout(() => {
            window.location.href = '/recommendations';
          }, 1500);
          
        } else {
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
      } catch (error) {
        console.error('Error guardando transmisión:', error);
        
        // Mostrar error
        nextBtn.style.background = '#e74c3c';
        nextBtn.innerHTML = '❌ Error - Intenta de nuevo';
        
        setTimeout(() => {
          // Restaurar botón
          nextBtn.disabled = false;
          nextBtn.style.background = 'linear-gradient(135deg, #27ae60, #2ecc71)';
          updateButtonText(selectedTransmission);
        }, 2000);
      }
    }
  });

  function updateProgressBar(percentage) {
    const progressFill = document.querySelector('.progress-fill');
    if (progressFill) {
      progressFill.style.width = percentage + '%';
    }
  }

  function showSuccessAnimation() {
    // Crear elementos de confetti
    for (let i = 0; i < 20; i++) {
      createConfetti();
    }
    
    // Efecto de pulso en el contenedor
    const container = document.querySelector('.container');
    container.style.animation = 'successPulse 0.6s ease';
    
    setTimeout(() => {
      container.style.animation = '';
    }, 600);
  }

  function createConfetti() {
    const confetti = document.createElement('div');
    confetti.style.cssText = `
      position: fixed;
      width: 10px;
      height: 10px;
      background: ${getRandomColor()};
      top: -10px;
      left: ${Math.random() * 100}vw;
      border-radius: 50%;
      pointer-events: none;
      animation: confettiFall ${2 + Math.random() * 3}s linear forwards;
      z-index: 9999;
    `;
    
    document.body.appendChild(confetti);
    
    setTimeout(() => {
      confetti.remove();
    }, 5000);
  }

  function getRandomColor() {
    const colors = ['#6200ea', '#27ae60', '#f39c12', '#e74c3c', '#3498db'];
    return colors[Math.floor(Math.random() * colors.length)];
  }

  // Mostrar recomendación inteligente basada en otros criterios
  function showSmartRecommendation() {
    // Esta función podría analizar las selecciones previas para recomendar transmisión
    setTimeout(() => {
      const recommendation = getTransmissionRecommendation();
      if (recommendation) {
        showRecommendationToast(recommendation);
      }
    }, 1000);
  }

  function getTransmissionRecommendation() {
    // Obtener datos de la sesión (simulado)
    const sessionData = {
      types: JSON.parse(localStorage.getItem('selectedTypes') || '[]'),
      fuel: localStorage.getItem('selectedFuel'),
      userProfile: JSON.parse(localStorage.getItem('userProfile') || '{}')
    };

    let recommendation = null;

    // Lógica de recomendación
    if (sessionData.types.includes('coupe') || sessionData.types.includes('convertible')) {
      recommendation = {
        type: 'manual',
        reason: 'Los autos deportivos suelen ser más divertidos con transmisión manual'
      };
    } else if (sessionData.userProfile.ageRange === '18-25') {
      recommendation = {
        type: 'manual',
        reason: 'Para una experiencia de manejo más conectada'
      };
    } else if (sessionData.types.includes('suv') && sessionData.userProfile.gender === 'femenino') {
      recommendation = {
        type: 'automatic',
        reason: 'Más cómoda para uso familiar y ciudad'
      };
    } else if (sessionData.fuel === 'electrico') {
      recommendation = {
        type: 'automatic',
        reason: 'Los vehículos eléctricos típicamente usan transmisión automática'
      };
    }

    return recommendation;
  }

  function showRecommendationToast(recommendation) {
    const toast = document.createElement('div');
    toast.className = 'recommendation-toast';
    toast.innerHTML = `
      <div class="toast-content">
        <h4>💡 Sugerencia personalizada</h4>
        <p><strong>${getTransmissionName(recommendation.type)}</strong></p>
        <small>${recommendation.reason}</small>
        <button onclick="selectRecommendation('${recommendation.type}')" class="toast-btn">
          Seleccionar
        </button>
        <button onclick="dismissToast()" class="toast-dismiss">×</button>
      </div>
    `;
    
    document.body.appendChild(toast);
    
    // Animar entrada
    setTimeout(() => {
      toast.style.opacity = '1';
      toast.style.transform = 'translateY(0)';
    }, 100);
    
    // Auto-dismiss después de 8 segundos
    setTimeout(() => {
      dismissToast();
    }, 8000);
  }

  function getTransmissionName(type) {
    const names = {
      'automatic': 'Transmisión Automática',
      'manual': 'Transmisión Manual',
      'semiautomatic': 'Transmisión Semiautomática'
    };
    return names[type] || type;
  }

  // Funciones globales para el toast
  window.selectRecommendation = function(type) {
    const btn = document.querySelector(`[data-transmission="${type}"]`);
    if (btn) {
      btn.click();
    }
    dismissToast();
  };

  window.dismissToast = function() {
    const toast = document.querySelector('.recommendation-toast');
    if (toast) {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(-20px)';
      setTimeout(() => {
        toast.remove();
      }, 300);
    }
  };

  // Mostrar información detallada de transmisión
  function showTransmissionInfo(type) {
    const info = {
      'automatic': {
        description: 'La transmisión automática cambia las marchas por ti usando un convertidor de torque.',
        pros: ['Fácil de manejar', 'Ideal para tráfico', 'Menos fatiga', 'Más cómoda'],
        cons: ['Consumo ligeramente mayor', 'Menos control', 'Mantenimiento más caro'],
        bestFor: 'Ciudad, tráfico pesado, conductores principiantes'
      },
      'manual': {
        description: 'La transmisión manual te permite controlar completamente los cambios de marcha.',
        pros: ['Mayor control', 'Mejor eficiencia', 'Mantenimiento más barato', 'Más divertida'],
        cons: ['Requiere más habilidad', 'Cansancio en tráfico', 'Curva de aprendizaje'],
        bestFor: 'Carretera, conductores experimentados, autos deportivos'
      },
      'semiautomatic': {
        description: 'Combina lo mejor de ambos mundos: comodidad automática con control manual.',
        pros: ['Versatilidad', 'Control cuando quieras', 'Comodidad automática', 'Eficiencia'],
        cons: ['Más compleja', 'Costo mayor', 'Menos común'],
        bestFor: 'Conductores que quieren opciones, uso mixto ciudad/carretera'
      }
    };

    const data = info[type];
    if (data) {
      alert(`${getTransmissionName(type).toUpperCase()}\n\n${data.description}\n\nVentajas:\n• ${data.pros.join('\n• ')}\n\nDesventajas:\n• ${data.cons.join('\n• ')}\n\nMejor para: ${data.bestFor}`);
    }
  }

  // Agregar event listeners para información
  document.querySelectorAll('.transmission-btn').forEach(btn => {
    const infoBtn = document.createElement('button');
    infoBtn.textContent = 'ℹ️';
    infoBtn.className = 'info-btn';
    infoBtn.onclick = (e) => {
      e.stopPropagation();
      showTransmissionInfo(btn.dataset.transmission);
    };
    btn.appendChild(infoBtn);
  });

  // Inicializar recomendación inteligente
  showSmartRecommendation();

  // Funciones disponibles globalmente para debugging
  window.selectTransmission = function(type) {
    const btn = document.querySelector(`[data-transmission="${type}"]`);
    if (btn) {
      btn.click();
    }
  };
  
  window.selectedTransmission = selectedTransmission;
});

// Estilos CSS adicionales para el toast y efectos
const additionalStyles = `
<style>
.recommendation-toast {
  position: fixed;
  top: 100px;
  right: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  padding: 1.5rem;
  max-width: 300px;
  z-index: 9999;
  opacity: 0;
  transform: translateY(-20px);
  transition: all 0.3s ease;
  border-left: 4px solid #6200ea;
}

.toast-content h4 {
  margin: 0 0 0.5rem 0;
  color: #333;
  font-size: 1rem;
}

.toast-content p {
  margin: 0.5rem 0;
  color: #6200ea;
  font-weight: bold;
}

.toast-content small {
  color: #666;
  display: block;
  margin-bottom: 1rem;
  line-height: 1.4;
}

.toast-btn {
  background: #6200ea;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  margin-right: 0.5rem;
}

.toast-btn:hover {
  background: #3700b3;
}

.toast-dismiss {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #999;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toast-dismiss:hover {
  background: #f0f0f0;
  color: #333;
}

.info-btn {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.7;
  transition: opacity 0.3s ease;
}

.transmission-btn:hover .info-btn {
  opacity: 1;
}

@keyframes confettiFall {
  to {
    transform: translateY(100vh) rotate(360deg);
    opacity: 0;
  }
}

@keyframes successPulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.02); }
  100% { transform: scale(1); }
}

body.dark-theme .recommendation-toast {
  background: #2d2d2d;
  color: #e0e0e0;
}

body.dark-theme .toast-content h4 {
  color: #e0e0e0;
}

body.dark-theme .toast-content small {
  color: #b0b0b0;
}

body.dark-theme .info-btn {
  background: rgba(0, 0, 0, 0.7);
  color: white;
}
</style>
`;

// Inyectar estilos
document.head.insertAdjacentHTML('beforeend', additionalStyles);