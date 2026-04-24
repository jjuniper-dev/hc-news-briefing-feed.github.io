(function () {
  function renderSharedNav(currentId) {
    const mount = document.querySelector('[data-shared-nav]');
    if (!mount) return;

    const allLinks = mount.querySelectorAll('a[href]');
    allLinks.forEach((link) => link.removeAttribute('aria-current'));

    if (currentId) {
      const current = mount.querySelector(`a[href*="/${currentId === 'dashboard' ? 'index.html' : ''}"]`);
      if (currentId === 'dashboard') {
        const dashboard = mount.querySelector('a[href$="/index.html"]');
        if (dashboard) dashboard.setAttribute('aria-current', 'page');
        return;
      }
      const byMap = {
        posts: '/status-site/intelligence.html',
        pptx: '/status-site/pptx-builder.html',
        'diagram-lab': '/status-site/diagram-lab.html',
        settings: '/status-site/settings.html',
        backlog: '/status-site/backlog.html',
        editor: '/intelligence-editor.html'
      };
      const href = byMap[currentId];
      if (href) {
        const target = mount.querySelector(`a[href$="${href}"]`);
        if (target) target.setAttribute('aria-current', 'page');
      }
      return;
    }

    const path = window.location.pathname;
    const target = Array.from(mount.querySelectorAll('a[href]')).find((link) => {
      try {
        return new URL(link.getAttribute('href'), window.location.origin).pathname === path;
      } catch (_) {
        return false;
      }
    });
    if (target) target.setAttribute('aria-current', 'page');
  }

  window.renderSharedNav = renderSharedNav;
  document.addEventListener('DOMContentLoaded', function () {
    const mount = document.querySelector('[data-shared-nav]');
    if (!mount) return;
    renderSharedNav(mount.getAttribute('data-current') || '');
  });
})();
