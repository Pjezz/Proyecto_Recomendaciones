// Manejo de localStorage
export const saveSelection = (key, data) => {
  localStorage.setItem(key, JSON.stringify(data));
};

export const loadSelection = (key) => {
  const data = localStorage.getItem(key);
  return data ? JSON.parse(data) : null;
};

// Redirección
export const redirectTo = (page) => {
  window.location.href = page;
};