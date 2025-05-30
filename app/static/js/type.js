document.addEventListener('DOMContentLoaded', () => {
  const selectedTypes = new Set();
  const nextBtn = document.getElementById('next-btn');

  // Configurar botones de tipo
  document.querySelectorAll('.type-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const type = this.dataset.type;
      
      this.classList.toggle('selected');
      
      if (this.classList.contains('selected')) {
        selectedTypes.add(type);
      } else {
        selectedTypes.delete(type);
      }
      
      // Habilitar/deshabilitar botón según selección
      nextBtn.disabled = selectedTypes.size === 0;
    });
  });

  // Configurar botón siguiente
  nextBtn.addEventListener('click', async () => {
    if (selectedTypes.size > 0) {
      try {
        const response = await fetch('/api/save-types', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ types: Array.from(selectedTypes) })
        });
        
        if (response.ok) {
          window.location.href = '/transmission';
        } else {
          console.error('Error al guardar tipos');
        }
      } catch (error) {
        console.error('Error:', error);
      }
    }
  });
});