// Configuración
const TOTAL_GROUPS = 4;
let currentGroup = 1;
const selectedBrands = {};

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
  initGroups();
  setupEventListeners();
});

function initGroups() {
  // Mostrar solo el primer grupo
  document.querySelectorAll('.brands-group').forEach((group, index) => {
    group.style.opacity = index === 0 ? '1' : '0';
    group.style.pointerEvents = index === 0 ? 'all' : 'none';
  });
}

function setupEventListeners() {
  // Botones de marca
  document.querySelectorAll('.brands-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const group = this.closest('.brands-group').dataset.group;
      const brand = this.dataset.brand;
      
      // Deseleccionar otros en el mismo grupo
      document.querySelectorAll(`.brands-group[data-group="${group}"] .brands-btn`)
        .forEach(b => b.classList.remove('selected'));
      
      // Seleccionar actual
      this.classList.add('selected');
      selectedBrands[group] = brand;
      
      // Habilitar siguiente
      document.getElementById('next-btn').disabled = false;
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

function switchGroup(nextGroup) {
  // Efecto crossfade
  const currentEl = document.querySelector(`.brands-group[data-group="${currentGroup}"]`);
  const nextEl = document.querySelector(`.brands-group[data-group="${nextGroup}"]`);
  
  currentEl.style.opacity = '0';
  currentEl.style.pointerEvents = 'none';
  
  nextEl.style.opacity = '1';
  nextEl.style.pointerEvents = 'all';
  
  currentGroup = nextGroup;
  document.getElementById('next-btn').disabled = true;
}

function saveSelections() {
  localStorage.setItem('selectedBrands', JSON.stringify(selectedBrands));
  window.location.href = 'budget.html';
}