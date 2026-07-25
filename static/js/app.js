document.addEventListener('DOMContentLoaded', () => {
  // Initialize Lucide Icons
  if (window.lucide) {
    lucide.createIcons();
  }

  // Real-time Clock Header
  const timeEl = document.getElementById('realtime-clock');
  const dateEl = document.getElementById('realtime-date');

  function updateClock() {
    const now = new Date();
    if (timeEl) {
      timeEl.textContent = now.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' }).replace(/\./g, ':');
    }
    if (dateEl) {
      dateEl.textContent = now.toLocaleDateString('id-ID', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
    }
  }

  updateClock();
  setInterval(updateClock, 1000);

  // Global Keyboard Shortcuts (Bonus feature: Alt+S for Search, Alt+D for Dashboard, Alt+A for Absensi)
  document.addEventListener('keydown', (e) => {
    if (e.altKey && e.key.toLowerCase() === 's') {
      e.preventDefault();
      const searchInput = document.getElementById('global-search-input');
      if (searchInput) searchInput.focus();
    }
  });
});

// Toast Notification Manager
window.showToast = function(message, type = 'success', title = '') {
  const toastContainer = document.getElementById('toast-container');
  if (!toastContainer) return;

  const toastId = 'toast-' + Math.random().toString(36).substring(2, 9);
  
  const iconMap = {
    success: 'check-circle',
    danger: 'x-circle',
    warning: 'alert-triangle',
    info: 'info'
  };

  const bgMap = {
    success: 'bg-emerald-50 border-emerald-200 text-emerald-800 dark:bg-emerald-950/80 dark:border-emerald-800 dark:text-emerald-200',
    danger: 'bg-rose-50 border-rose-200 text-rose-800 dark:bg-rose-950/80 dark:border-rose-800 dark:text-rose-200',
    warning: 'bg-amber-50 border-amber-200 text-amber-800 dark:bg-amber-950/80 dark:border-amber-800 dark:text-amber-200',
    info: 'bg-blue-50 border-blue-200 text-blue-800 dark:bg-blue-950/80 dark:border-blue-800 dark:text-blue-200'
  };

  const toast = document.createElement('div');
  toast.id = toastId;
  toast.className = `flex items-center gap-3 p-4 rounded-2xl border shadow-lg transition-all duration-300 transform translate-x-full opacity-0 max-w-md ${bgMap[type] || bgMap.info}`;
  
  toast.innerHTML = `
    <i data-lucide="${iconMap[type] || 'info'}" class="w-5 h-5 flex-shrink-0"></i>
    <div class="flex-1 text-sm font-medium">
      ${title ? `<div class="font-bold text-xs uppercase tracking-wider mb-0.5">${title}</div>` : ''}
      <div>${message}</div>
    </div>
    <button onclick="document.getElementById('${toastId}').remove()" class="text-xs opacity-70 hover:opacity-100 p-1">
      <i data-lucide="x" class="w-4 h-4"></i>
    </button>
  `;

  toastContainer.appendChild(toast);
  if (window.lucide) lucide.createIcons();

  requestAnimationFrame(() => {
    toast.classList.remove('translate-x-full', 'opacity-0');
  });

  setTimeout(() => {
    toast.classList.add('translate-x-full', 'opacity-0');
    setTimeout(() => toast.remove(), 300);
  }, 4000);
};

// Dark Mode Toggle Logic
window.toggleDarkMode = function() {
  document.documentElement.classList.add('theme-transitioning');
  const isDark = document.documentElement.classList.toggle('dark');
  localStorage.setItem('theme', isDark ? 'dark' : 'light');
  setTimeout(() => {
    document.documentElement.classList.remove('theme-transitioning');
  }, 300);
};

// Initial theme check (fallback if head script missed)
if (localStorage.getItem('theme') === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
  document.documentElement.classList.add('dark');
} else {
  document.documentElement.classList.remove('dark');
}
