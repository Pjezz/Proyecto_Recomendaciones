document.addEventListener('DOMContentLoaded', () => {
  let selectedFuel = null;
  const nextBtn = document.getElementById('next-btn');

  // Validar que venga de budget.html (cambiado de type.html)
  if (!localStorage.getItem('selectedBudget')) {
    window.location.href = 'budget.html';
    return;
  }

  // Configurar botones de combustible
  document.querySelectorAll('.fuel-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const fuelType = this.dataset.fuel;
      
      // Deseleccionar todos primero
      document.querySelectorAll('.fuel-btn').forEach(b => {
        b.classList.remove('selected');
      });
      
      // Seleccionar el actual
      this.classList.add('selected');
      selectedFuel = fuelType;
      
      // Habilitar siguiente
      nextBtn.disabled = false;
    });
  });

  // Configurar botón siguiente
  nextBtn.addEventListener('click', () => {
    if (selectedFuel) {
      localStorage.setItem('selectedFuel', selectedFuel);
      window.location.href = 'type.html'; // Redirige a type.html ahora
    }
  });
});