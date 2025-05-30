document.addEventListener('DOMContentLoaded', () => {
  let selectedFuel = null;
  const nextBtn = document.getElementById('next-btn');

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
  nextBtn.addEventListener('click', async () => {
    if (selectedFuel) {
      try {
        const response = await fetch('/api/save-fuel', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ fuel: selectedFuel })
        });
        
        if (response.ok) {
          window.location.href = '/type';
        } else {
          console.error('Error al guardar combustible');
        }
      } catch (error) {
        console.error('Error:', error);
      }
    }
  });
});