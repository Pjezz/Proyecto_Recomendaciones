document.addEventListener('DOMContentLoaded', () => {
  let selectedBudget = null;
  const continueBtn = document.getElementById('continue-btn');

  // Configurar botones de presupuesto
  document.querySelectorAll('.budget-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const budgetRange = this.dataset.budget;
      
      // Deseleccionar todos primero
      document.querySelectorAll('.budget-btn').forEach(b => {
        b.classList.remove('selected');
      });
      
      // Seleccionar el actual
      this.classList.add('selected');
      selectedBudget = budgetRange;
      
      // Habilitar botón continuar
      continueBtn.disabled = false;
    });
  });

  // Configurar botón continuar
  continueBtn.addEventListener('click', async () => {
    if (selectedBudget) {
      try {
        const response = await fetch('/api/save-budget', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ budget: selectedBudget })
        });
        
        if (response.ok) {
          window.location.href = '/fuel';
        } else {
          console.error('Error al guardar presupuesto');
        }
      } catch (error) {
        console.error('Error:', error);
      }
    }
  });
});