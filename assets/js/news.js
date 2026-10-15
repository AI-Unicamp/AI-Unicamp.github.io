/* AIMS News: progressive enhancement. Without JavaScript, all items are visible. */
(() => {
  'use strict';
  const list = document.querySelector('[data-news-list]');
  const button = document.querySelector('[data-news-more]');
  if (!list || !button) return;

  const items = Array.from(list.querySelectorAll('.news-entry'));
  const pageSize = Math.max(1, Number(list.dataset.pageSize) || 5);
  let visible = Math.min(pageSize, items.length);
  const isPortuguese = document.documentElement.lang.toLowerCase().startsWith('pt');

  function update() {
    items.forEach((item, index) => { item.hidden = index >= visible; });
    button.hidden = visible >= items.length;
    button.setAttribute('aria-label', isPortuguese
      ? `Mostrar mais notícias. ${visible} de ${items.length} visíveis.`
      : `Show more news. ${visible} of ${items.length} visible.`);
  }

  function revealHash() {
    const id = decodeURIComponent(location.hash.slice(1));
    if (!id) return;
    const index = items.findIndex(item => item.id === id);
    if (index < 0 || index < visible) return;
    visible = Math.min(items.length, Math.ceil((index + 1) / pageSize) * pageSize);
    update();
    items[index].scrollIntoView();
  }

  button.addEventListener('click', () => {
    visible = Math.min(items.length, visible + pageSize);
    update();
  });

  update();
  revealHash();
  window.addEventListener('hashchange', revealHash);
})();
