// Utilidades para manejar requests a Flask
export const apiRequest = async (endpoint, data = null, method = 'GET') => {
  const options = {
    method: method,
    headers: {
      'Content-Type': 'application/json',
    }
  };
  
  if (data && method !== 'GET') {
    options.body = JSON.stringify(data);
  }
  
  try {
    const response = await fetch(endpoint, options);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Request error:', error);
    throw error;
  }
};

// Función para guardar datos en el servidor
export const saveToServer = async (endpoint, data) => {
  return await apiRequest(endpoint, data, 'POST');
};

// Redirección con verificación
export const redirectTo = (page) => {
  // Asegurar que la URL comience con /
  if (!page.startsWith('/')) {
    page = '/' + page;
  }
  window.location.href = page;
};

// Manejo de errores de UI
export const showError = (message, container = null) => {
  const errorDiv = document.createElement('div');
  errorDiv.className = 'error-message';
  errorDiv.innerHTML = `
    <div class="alert alert-error">
      <strong>Error:</strong> ${message}
    </div>
  `;
  
  if (container) {
    container.appendChild(errorDiv);
  } else {
    document.body.appendChild(errorDiv);
  }
  
  // Auto-remove después de 5 segundos
  setTimeout(() => {
    errorDiv.remove();
  }, 5000);
};

// Manejo de loading states
export const toggleLoading = (show, element = null) => {
  if (element) {
    if (show) {
      element.disabled = true;
      element.textContent = 'Cargando...';
    } else {
      element.disabled = false;
      element.textContent = element.dataset.originalText || 'Continuar';
    }
  }
};

// Validación de formularios
export const validateForm = (formData, requiredFields) => {
  const errors = [];
  
  requiredFields.forEach(field => {
    if (!formData[field] || formData[field].toString().trim() === '') {
      errors.push(`El campo ${field} es requerido`);
    }
  });
  
  return {
    isValid: errors.length === 0,
    errors: errors
  };
};

// Utilidad para debugging
export const logUserSelection = (step, data) => {
  if (window.console && console.log) {
    console.log(`[${step}] Usuario seleccionó:`, data);
  }
};