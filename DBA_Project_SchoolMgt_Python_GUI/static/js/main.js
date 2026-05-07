// main.js

// ─── Confirm Delete Modal ───────────────────────────────────
function confirmDelete(formId, itemName) {
  const overlay = document.getElementById('deleteModal');
  const desc    = document.getElementById('modalDesc');
  desc.textContent = `Are you sure you want to delete "${itemName}"? This cannot be undone.`;
  overlay.classList.add('active');

  document.getElementById('modalConfirmBtn').onclick = () => {
    document.getElementById(formId).submit();
    overlay.classList.remove('active');
  };
  document.getElementById('modalCancelBtn').onclick = () => {
    overlay.classList.remove('active');
  };
}

// ─── Auto-dismiss alerts ────────────────────────────────────
document.querySelectorAll('.alert').forEach(alert => {
  setTimeout(() => {
    alert.style.transition = 'opacity .5s';
    alert.style.opacity = '0';
    setTimeout(() => alert.remove(), 500);
  }, 4000);
});

// ─── Active nav highlight ───────────────────────────────────
const currentPath = window.location.pathname.split('/')[1];
document.querySelectorAll('.nav-item').forEach(link => {
  const href = link.getAttribute('href') || '';
  if (href.includes(currentPath) && currentPath !== '') {
    link.classList.add('active');
  }
});

// ─── Mobile sidebar toggle ──────────────────────────────────
const menuToggle = document.getElementById('menuToggle');
const sidebar    = document.querySelector('.sidebar');
if (menuToggle) {
  menuToggle.addEventListener('click', () => {
    sidebar.classList.toggle('open');
  });
}