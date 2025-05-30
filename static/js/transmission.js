document.addEventListener('DOMContentLoaded', () => {
  let selectedTransmission = null;
  const nextBtn = document.getElementById('next-btn');

  // Validar que venga de types.html
  if (!localStorage.getItem('selectedTypes')) {
    window.location.href = 'types.html';
    return;
  }

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
  nextBtn.addEventListener('click', () => {
    if (selectedTransmission) {
      localStorage.setItem('selectedTransmission', selectedTransmission);
      window.location.href = 'recommendations.html';
    }
  });
});