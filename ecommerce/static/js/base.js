const header = document.getElementById('siteHeader');
window.addEventListener('scroll', () => {
  header.classList.toggle('scrolled', window.scrollY > 8);
}, { passive: true });

const revealEls = document.querySelectorAll('.reveal');
if ('IntersectionObserver' in window && revealEls.length) {
  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('in');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });
  revealEls.forEach(el => io.observe(el));
} else {
  revealEls.forEach(el => el.classList.add('in'));
}

// Auto-remove toast messages from the DOM after they fade out
document.querySelectorAll('.toast').forEach(toast => {
  setTimeout(() => toast.remove(), 4000);
});
const adminToggle = document.getElementById('adminToggle');
const adminSidebar = document.getElementById('adminSidebar');
const adminOverlay = document.getElementById('adminOverlay');
const adminClose = document.getElementById('adminClose');
function closeAdminSidebar() {
  adminSidebar && adminSidebar.classList.remove('open');
  adminOverlay && adminOverlay.classList.remove('open');
}
if (adminToggle) {
  adminToggle.addEventListener('click', () => {
    adminSidebar.classList.toggle('open');
    adminOverlay.classList.toggle('open');
  });
  adminClose.addEventListener('click', closeAdminSidebar);
  adminOverlay.addEventListener('click', closeAdminSidebar);
}