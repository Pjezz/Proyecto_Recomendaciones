document.addEventListener('DOMContentLoaded', () => {
  const selectedTypes = new Set();
  const nextBtn = document.getElementById('next-btn');

  // Validar que venga de fuel.html (cambiado de budget.html)
  if (!localStorage.getItem('selectedFuel')) {
    window.location.href = 'fuel.html';
    return;
  }

  // Resto del código permanece igual...
  document.querySelectorAll('.type-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const type = this.dataset.type;
      
      this.classList.toggle('selected');
      
      if (this.classList.contains('selected')) {
        selectedTypes.add(type);
      } else {
        selectedTypes.delete(type);
      }
      
      nextBtn.disabled = selectedTypes.size === 0;
    });
  });

  nextBtn.addEventListener('click', () => {
    if (selectedTypes.size > 0) {
      localStorage.setItem('selectedTypes', JSON.stringify(Array.from(selectedTypes)));
      window.location.href = 'transmission.html';
    }
  });
});