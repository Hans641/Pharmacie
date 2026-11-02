/* Préférence visuelle uniquement ; aucune donnée métier stockée. */
(() => {
  'use strict';
  const key = 'pharmagest-theme';
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  const chromeColors = { light: '#f4f7f5', dark: '#101916' };
  let preference = 'system';
  try { preference = localStorage.getItem(key) || 'system'; } catch {}
  const valid = value => ['system', 'light', 'dark'].includes(value) ? value : 'system';
  const apply = value => {
    preference = valid(value);
    if (preference === 'system') delete document.documentElement.dataset.theme;
    else document.documentElement.dataset.theme = preference;
    const resolved = preference === 'system' ? (system.matches ? 'dark' : 'light') : preference;
    document.querySelectorAll('meta[name="theme-color"]').forEach(meta => { meta.content = chromeColors[resolved]; });
    const select = document.querySelector('[data-theme-preference]');
    if (select) select.value = preference;
  };
  apply(preference);
  system.addEventListener('change', () => apply(preference));
  document.addEventListener('DOMContentLoaded', () => {
    const select = document.querySelector('[data-theme-preference]');
    if (!select) return;
    select.value = preference;
    select.closest('[data-theme-control]').hidden = false;
    select.addEventListener('change', () => {
      apply(select.value);
      try {
        if (preference === 'system') localStorage.removeItem(key);
        else localStorage.setItem(key, preference);
      } catch {}
    });
  });
  window.addEventListener('storage', event => { if (event.key === key || event.key === null) apply(event.newValue); });
})();
