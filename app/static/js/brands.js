// Configuración
const TOTAL_GROUPS = 4;
let currentGroup = 1;
const selectedBrands = {}; // Ahora permite múltiples selecciones por grupo

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
  initGroups();
  setupEventListeners();
  updateGroupIndicator();
});

function initGroups() {
  // Mostrar solo el primer grupo
  document.querySelectorAll('.brands-group').forEach((group, index) => {
    group.style.opacity = index === 0 ? '1' : '0';
    group.style.pointerEvents = index === 0 ? 'all' : 'none';
    group.classList.toggle('active', index === 0);
  });
}

function updateGroupIndicator() {
  const indicator = document.getElementById('current-group');
  if (indicator) {
    indicator.textContent = currentGroup;
  }
}

function setupEventListeners() {
  // Botones de marca
  document.querySelectorAll('.brands-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const group = this.closest('.brands-group').dataset.group;
      const brand = this.dataset.brand;
      
      // Toggle de selección (permitir múltiples selecciones)
      if (this.classList.contains('selected')) {
        // Deseleccionar
        this.classList.remove('selected');
        delete selectedBrands[`${group}_${brand}`];
      } else {
        // Seleccionar
        this.classList.add('selected');
        selectedBrands[`${group}_${brand}`] = brand;
      }
      
      // Verificar si se puede continuar (al menos una marca seleccionada en total)
      const hasAnySelection = Object.keys(selectedBrands).length > 0;
      document.getElementById('next-btn').disabled = !hasAnySelection;
      
      // Actualizar contador visual
      updateSelectionCounter();
    });
  });

  // Botón siguiente
  document.getElementById('next-btn').addEventListener('click', () => {
    if (currentGroup < TOTAL_GROUPS) {
      switchGroup(currentGroup + 1);
    } else {
      saveSelections();
    }
  });
}

function updateSelectionCounter() {
  // Mostrar cuántas marcas están seleccionadas
  const totalSelected = Object.keys(selectedBrands).length;
  const nextBtn = document.getElementById('next-btn');
  
  if (totalSelected > 0) {
    nextBtn.textContent = `Siguiente (${totalSelected} marcas seleccionadas)`;
    nextBtn.disabled = false;
  } else {
    nextBtn.textContent = 'Selecciona al menos una marca';
    nextBtn.disabled = true;
  }
}

function switchGroup(nextGroup) {
  // Efecto crossfade
  const currentEl = document.querySelector(`.brands-group[data-group="${currentGroup}"]`);
  const nextEl = document.querySelector(`.brands-group[data-group="${nextGroup}"]`);
  
  if (currentEl && nextEl) {
    currentEl.style.opacity = '0';
    currentEl.style.pointerEvents = 'none';
    currentEl.classList.remove('active');
    
    setTimeout(() => {
      nextEl.style.opacity = '1';
      nextEl.style.pointerEvents = 'all';
      nextEl.classList.add('active');
    }, 200);
    
    currentGroup = nextGroup;
    updateGroupIndicator();
    
    // Actualizar texto del botón para el último grupo
    if (currentGroup === TOTAL_GROUPS) {
      document.getElementById('next-btn').textContent = 'Continuar con mi selección';
    }
    
    // Verificar si hay selecciones en el nuevo grupo
    updateSelectionCounter();
  }
}

async function saveSelections() {
  try {
    // Convertir selecciones a formato más simple para el backend
    const brandsArray = Object.values(selectedBrands);
    
    console.log('Guardando marcas seleccionadas:', brandsArray);
    
    const response = await fetch('/api/save-brands', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ brands: brandsArray })
    });
    
    if (response.ok) {
      const result = await response.json();
      console.log('Marcas guardadas exitosamente:', result);
      window.location.href = '/budget';
    } else {
      console.error('Error al guardar selecciones:', response.status);
      alert('Error al guardar las selecciones. Por favor, intenta de nuevo.');
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Error de conexión. Por favor, verifica tu conexión e intenta de nuevo.');
  }
}

// Función para limpiar todas las selecciones (útil para testing)
function clearAllSelections() {
  Object.keys(selectedBrands).forEach(key => {
    delete selectedBrands[key];
  });
  
  document.querySelectorAll('.brands-btn.selected').forEach(btn => {
    btn.classList.remove('selected');
  });
  
  updateSelectionCounter();
}

// Función para seleccionar marcas por grupo (útil para testing)
function selectBrandsByGroup(groupSelections) {
  // Ejemplo: selectBrandsByGroup({1: ['Toyota'], 2: ['Honda', 'Mercedes'], 3: ['Audi']})
  clearAllSelections();
  
  Object.entries(groupSelections).forEach(([group, brands]) => {
    brands.forEach(brand => {
      const btn = document.querySelector(`[data-group="${group}"] [data-brand="${brand}"]`);
      if (btn) {
        btn.click();
      }
    });
  });
}

// Hacer funciones disponibles globalmente para debugging
window.clearAllSelections = clearAllSelections;
window.selectBrandsByGroup = selectBrandsByGroup;
window.selectedBrands = selectedBrands;