document.addEventListener('DOMContentLoaded', () => {
  let selectedTransmission = null;
  const nextBtn = document.getElementById('next-btn');

  // Configurar botones de transmisión
  document.querySelectorAll('.transmission-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const transmission = this.dataset.transmission;
      
      // Deseleccionar otros
      document.querySelectorAll('.transmission-btn').forEach(b => 
        b.classList.remove('selected')
      );
      
      // Seleccionar actual
      this.classList.add('selected');
      selectedTransmission = transmission;
      
      // Habilitar siguiente
      nextBtn.disabled = false;
    });
  });

  // Configurar botón siguiente
  nextBtn.addEventListener('click', async () => {
    if (selectedTransmission) {
      try {
        const response = await fetch('/api/save-transmission', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ transmission: selectedTransmission })
        });
        
        if (response.ok) {
          window.location.href = '/recommendations';
        } else {
          console.error('Error al guardar transmisión');
        }
      } catch (error) {
        console.error('Error:', error);
      }
    }
  });
});