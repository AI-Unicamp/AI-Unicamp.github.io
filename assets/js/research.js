/* Progressive enhancement: all publications remain visible without JS. */
(() => {
  'use strict';
  const list = document.querySelector('[data-publications-list]');
  const more = document.querySelector('[data-publications-more]');
  if (!list || !more) return;

  const portuguese = document.documentElement.lang.toLowerCase().startsWith('pt');
  const entries = [...list.querySelectorAll('.publication-item')];
  const groups = [...list.querySelectorAll('.publication-year-group')];
  const pageSize = Math.max(1, Number.parseInt(list.dataset.pageSize || '10', 10) || 10);
  let shown = Math.min(pageSize, entries.length);

  function update() {
    entries.forEach((entry, index) => { entry.hidden = index >= shown; });
    groups.forEach(group => {
      group.hidden = ![...group.querySelectorAll('.publication-item')].some(item => !item.hidden);
    });
    more.hidden = shown >= entries.length;
    if (!more.hidden) {
      const next = Math.min(pageSize, entries.length - shown);
      more.setAttribute('aria-label', portuguese
        ? `Mostrar mais ${next} publicações`
        : `Show ${next} more publications`);
    }
  }

  more.addEventListener('click', () => {
    shown = Math.min(shown + pageSize, entries.length);
    update();
  });
  update();
})();
