import { saveSelection, redirectTo } from './shared.js';

export function selectBudget(range) {
  const button = event.currentTarget;
  document.querySelectorAll('.budget-btn').forEach(btn => {
    btn.classList.remove('selected');
  });
  button.classList.add('selected');
  
  saveSelection('selectedBudget', range);
  document.getElementById('continue-btn').disabled = false;
}

export function initBudgetPage() {
  // Configurar botón
  document.getElementById('continue-btn')?.addEventListener('click', () => {
    if (localStorage.getItem('selectedBudget')) {
      window.location.href = 'fuel.html'; // Cambiado a fuel.html
    }
  });
}