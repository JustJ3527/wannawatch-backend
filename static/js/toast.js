
function showToast(message, type='success', duration=3000) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.classList.add('toast', `toast-${type}`);

  // Choix de l’icône
  const icons = { success: '✅', error: '❌', info: 'ℹ️' };
  const icon = icons[type] || '';

  toast.innerHTML = `<span class="toast-icon">${icon}</span><span>${message}</span>`;
  container.appendChild(toast);

  // Forcer une frame avant d’ajouter la classe "show"
  requestAnimationFrame(() => toast.classList.add('show'));

  // Disparition après X secondes
  setTimeout(() => {
    toast.classList.remove('show');
    toast.classList.add('hide');
    // Supprime l’élément sans affecter HTMX
    setTimeout(() => {
      if (toast.parentElement) toast.parentElement.removeChild(toast);
    }, 400);
  }, duration);
}

// Gestion automatique des réponses JSON de HTMX
document.body.addEventListener('htmx:afterRequest', (evt) => {
  const xhr = evt.detail.xhr;
  // Si le serveur a répondu du JSON
  try {
    const data = JSON.parse(xhr.responseText);
    if (data && data.message) {
      showToast(data.message, data.type || 'success');
    }
  } catch {
    // réponse non JSON -> on ignore
  }
});