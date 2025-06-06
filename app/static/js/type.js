document.addEventListener('DOMContentLoaded', () => {
  const selectedTypes = new Set();
  const nextBtn = document.getElementById('next-btn');
  const selectionSummary = document.getElementById('selection-summary');
  const selectedCount = document.getElementById('selected-count');

  // Configurar botones de tipo
  document.querySelectorAll('.type-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const type = this.dataset.type;
      
      this.classList.toggle('selected');
      
      if (this.classList.contains('selected')) {
        selectedTypes.add(type);
        // Añadir efecto visual
        this.style.transform = 'scale(1.05)';
        setTimeout(() => {
          this.style.transform = '';
        }, 200);
      } else {
        selectedTypes.delete(type);
      }
      
      updateSelectionDisplay();
    });

    // Añadir efecto hover mejorado
    btn.addEventListener('mouseenter', function() {
      if (!this.classList.contains('selected')) {
        this.style.transform = 'translateY(-5px)';
      }
    });

    btn.addEventListener('mouseleave', function() {
      if (!this.classList.contains('selected')) {
        this.style.transform = '';
      }
    });
  });

  function updateSelectionDisplay() {
    const count = selectedTypes.size;
    
    // Actualizar contador
    selectedCount.textContent = count;
    
    // Mostrar/ocultar resumen
    if (count > 0) {
      selectionSummary.style.display = 'block';
      nextBtn.disabled = false;
      
      // Actualizar texto del botón
      if (count === 1) {
        nextBtn.textContent = 'Siguiente (1 tipo seleccionado)';
      } else {
        nextBtn.textContent = `Siguiente (${count} tipos seleccionados)`;
      }
      
      // Efecto en el resumen
      selectionSummary.style.animation = 'none';
      setTimeout(() => {
        selectionSummary.style.animation = 'fadeInScale 0.3s ease';
      }, 10);
      
    } else {
      selectionSummary.style.display = 'none';
      nextBtn.disabled = true;
      nextBtn.textContent = 'Selecciona al menos un tipo';
    }
  }

  // Configurar botón siguiente
  nextBtn.addEventListener('click', async () => {
    if (selectedTypes.size > 0) {
      try {
        // Mostrar loading
        nextBtn.disabled = true;
        nextBtn.textContent = 'Guardando selección...';
        
        const response = await fetch('/api/save-types', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ types: Array.from(selectedTypes) })
        });
        
        if (response.ok) {
          // Efecto de éxito
          nextBtn.style.background = '#27ae60';
          nextBtn.textContent = '¡Guardado! Redirigiendo...';
          
          setTimeout(() => {
            window.location.href = '/transmission';
          }, 500);
        } else {
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
      } catch (error) {
        console.error('Error guardando tipos:', error);
        alert('Error al guardar la selección. Por favor, intenta de nuevo.');
        
        // Restaurar botón
        nextBtn.disabled = false;
        updateSelectionDisplay();
      }
    }
  });

  // Función para limpiar todas las selecciones (útil para testing)
  function clearAllSelections() {
    selectedTypes.clear();
    document.querySelectorAll('.type-btn.selected').forEach(btn => {
      btn.classList.remove('selected');
    });
    updateSelectionDisplay();
  }

  // Función para seleccionar tipos automáticamente (útil para testing)
  function selectTypes(types) {
    clearAllSelections();
    types.forEach(type => {
      const btn = document.querySelector(`[data-type="${type}"]`);
      if (btn) {
        btn.click();
      }
    });
  }

  // Funciones de recomendación inteligente basada en demografía
  function getSmartRecommendations() {
    // Esta función podría sugerir tipos basados en el perfil del usuario
    // Por ahora, simplemente mostrar sugerencias generales
    showTypeRecommendations();
  }

  function showTypeRecommendations() {
    // Crear elemento de sugerencias si no existe
    let suggestionsEl = document.getElementById('type-suggestions');
    if (!suggestionsEl) {
      suggestionsEl = document.createElement('div');
      suggestionsEl.id = 'type-suggestions';
      suggestionsEl.className = 'type-suggestions';
      
      const container = document.querySelector('.container');
      container.insertBefore(suggestionsEl, document.querySelector('.types-grid'));
    }

    // Obtener perfil del usuario desde la sesión (esto sería desde el servidor)
    // Por ahora, usar localStorage como fallback
    const userProfile = JSON.parse(localStorage.getItem('userProfile') || '{}');
    
    let suggestions = [];
    
    if (userProfile.gender === 'femenino' && ['26-35', '36-45'].includes(userProfile.ageRange)) {
      suggestions = ['suv', 'sedan'];
    } else if (userProfile.gender === 'masculino' && userProfile.ageRange === '18-25') {
      suggestions = ['coupe', 'convertible'];
    } else if (['46-55', '56+'].includes(userProfile.ageRange)) {
      suggestions = ['sedan', 'suv'];
    }

    if (suggestions.length > 0) {
      const suggestionNames = suggestions.map(type => {
        const typeNames = {
          'sedan': 'Sedán',
          'suv': 'SUV',
          'coupe': 'Coupé',
          'convertible': 'Convertible',
          'hatchback': 'Hatchback',
          'pickup': 'Pickup'
        };
        return typeNames[type] || type;
      });

      suggestionsEl.innerHTML = `
        <div class="suggestion-card">
          <h3>💡 Sugerencias para ti</h3>
          <p>Basado en tu perfil, te recomendamos: <strong>${suggestionNames.join(', ')}</strong></p>
          <button onclick="selectTypes(${JSON.stringify(suggestions)})" class="suggestion-btn">
            Seleccionar sugerencias
          </button>
        </div>
      `;
      suggestionsEl.style.display = 'block';
    }
  }

  // Mostrar sugerencias después de un breve delay
  setTimeout(getSmartRecommendations, 1000);

  // Hacer funciones disponibles globalmente para debugging
  window.clearAllSelections = clearAllSelections;
  window.selectTypes = selectTypes;
  window.selectedTypes = selectedTypes;
});

// Función para mostrar información de tipos
function showTypeInfo(type) {
  const typeInfo = {
    'sedan': {
      description: 'Autos elegantes con 4 puertas, ideales para uso urbano y familiar.',
      pros: ['Eficiencia de combustible', 'Fácil estacionamiento', 'Precio accesible'],
      cons: ['Espacio limitado', 'Menor capacidad de carga']
    },
    'suv': {
      description: 'Vehículos altos y espaciosos, perfectos para familias y aventuras.',
      pros: ['Mucho espacio', 'Posición de manejo elevada', 'Versatilidad'],
      cons: ['Mayor consumo', 'Precio más alto']
    },
    'hatchback': {
      description: 'Compactos y eficientes, ideales para la ciudad.',
      pros: ['Muy económicos', 'Fácil manejo', 'Estacionamiento sencillo'],
      cons: ['Espacio limitado', 'Menos confort en viajes largos']
    },
    'pickup': {
      description: 'Resistentes y funcionales, para trabajo y carga.',
      pros: ['Gran capacidad de carga', 'Durabilidad', 'Versatilidad'],
      cons: ['Mayor consumo', 'Tamaño grande']
    },
    'coupe': {
      description: 'Deportivos de 2 puertas, para quienes buscan estilo y performance.',
      pros: ['Diseño atractivo', 'Performance', 'Exclusividad'],
      cons: ['Espacio limitado', 'Precio alto', 'Mantenimiento costoso']
    },
    'convertible': {
      description: 'Autos descapotables para disfrutar del aire libre.',
      pros: ['Experiencia única', 'Estilo', 'Diversión'],
      cons: ['Precio alto', 'Menos seguridad', 'Ruido']
    }
  };

  const info = typeInfo[type];
  if (info) {
    alert(`${type.toUpperCase()}\n\n${info.description}\n\nVentajas: ${info.pros.join(', ')}\n\nDesventajas: ${info.cons.join(', ')}`);
  }
}