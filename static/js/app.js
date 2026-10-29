/* PharmaGest : amélioration progressive. Aucune écriture métier par fetch. */
(() => {
  'use strict';
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const announce = text => { const region = $('#interaction-status'); if (region) region.textContent = text; };

  // Navigation mobile : clavier, focus et arrière-plan inerte uniquement à l'ouverture.
  const navigation = $('#navigation-panel');
  const workspace = $('#workspace');
  const openButton = $('[data-nav-open]');
  const closeButton = $('[data-nav-close]');
  const mobile = matchMedia('(max-width: 900px)');
  function closeNavigation(restore = true) {
    if (!navigation) return;
    navigation.classList.remove('is-open');
    navigation.removeAttribute('role');
    navigation.removeAttribute('aria-modal');
    document.body.classList.remove('drawer-active');
    if (workspace) workspace.inert = false;
    if (openButton) openButton.setAttribute('aria-expanded', 'false');
    if (restore && mobile.matches) openButton?.focus();
  }
  function openNavigation() {
    navigation.classList.add('is-open');
    navigation.setAttribute('role', 'dialog');
    navigation.setAttribute('aria-modal', 'true');
    document.body.classList.add('drawer-active');
    workspace.inert = true;
    openButton.setAttribute('aria-expanded', 'true');
    closeButton.focus();
  }
  if (navigation && openButton && closeButton) {
    openButton.hidden = false;
    closeButton.hidden = false;
    openButton.addEventListener('click', openNavigation);
    closeButton.addEventListener('click', () => closeNavigation());
    mobile.addEventListener('change', () => closeNavigation(false));
    document.addEventListener('pointerdown', event => {
      if (navigation.classList.contains('is-open') && !navigation.contains(event.target) && !openButton.contains(event.target)) closeNavigation();
    });
    document.addEventListener('keydown', event => {
      if (!navigation.classList.contains('is-open')) return;
      if (event.key === 'Escape') { event.preventDefault(); closeNavigation(); }
      if (event.key === 'Tab') {
        const controls = $$('a, button', navigation).filter(el => el.getClientRects().length && !el.disabled);
        const first = controls[0], last = controls.at(-1);
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
      }
    });
  }
  document.documentElement.classList.add('js');

  // Mot de passe et impression : aucun bouton inopérant sans JavaScript.
  $$('[data-password-toggle]').forEach(button => {
    button.hidden = false;
    button.addEventListener('click', () => {
      const input = document.getElementById(button.dataset.passwordToggle);
      const reveal = input.type === 'password';
      input.type = reveal ? 'text' : 'password';
      button.textContent = reveal ? 'Masquer' : 'Afficher';
      button.setAttribute('aria-pressed', String(reveal));
    });
  });
  $$('[data-print]').forEach(button => { button.hidden = false; button.addEventListener('click', () => window.print()); });

  // Confirmation des formulaires sensibles, puis soumission native avec CSRF intact.
  const dialog = $('#confirm-dialog');
  document.addEventListener('submit', event => {
    const form = event.target;
    if (!(form instanceof HTMLFormElement) || form.method.toLowerCase() !== 'post' || form.getAttribute('method') === 'dialog') return;
    if (form.dataset.submitting === 'true') { event.preventDefault(); return; }
    if (form.dataset.confirm && !form.dataset.confirmed && dialog?.showModal) {
      event.preventDefault();
      const submitter = event.submitter;
      $('#confirm-title').textContent = form.dataset.confirmTitle || 'Confirmer l’opération';
      $('#confirm-description').textContent = form.dataset.confirm;
      const confirmButton = $('#confirm-submit');
      confirmButton.textContent = form.dataset.confirmLabel || 'Confirmer';
      confirmButton.classList.toggle('btn-primary', form.dataset.confirmIntent === 'primary');
      confirmButton.classList.toggle('btn-danger', form.dataset.confirmIntent !== 'primary');
      dialog.returnValue = '';
      dialog.addEventListener('close', () => {
        if (dialog.returnValue === 'confirm') {
          form.dataset.confirmed = 'true';
          form.requestSubmit(submitter);
        } else submitter?.focus();
      }, { once: true });
      dialog.showModal();
      return;
    }
    form.dataset.submitting = 'true';
    form.setAttribute('aria-busy', 'true');
    // Reporter la désactivation après la construction des données du formulaire.
    setTimeout(() => {
      $$('button[type="submit"], button:not([type]), input[type="submit"]', form).forEach(button => {
        if (button.disabled) return;
        button.dataset.submitLocked = 'true';
        button.disabled = true;
        button.setAttribute('aria-disabled', 'true');
      });
    }, 0);
    announce('Enregistrement en cours. Patientez.');
  });
  window.addEventListener('pageshow', () => {
    $$('form[data-submitting]').forEach(form => {
      delete form.dataset.submitting;
      delete form.dataset.confirmed;
      form.removeAttribute('aria-busy');
    });
    $$('[data-submit-locked]').forEach(button => {
      button.disabled = false;
      button.removeAttribute('aria-disabled');
      delete button.dataset.submitLocked;
    });
  });
  const errorSummary = $('[data-error-summary]');
  if (errorSummary) errorSummary.focus();

  // Recherche des listes : GET serveur, temporisation, annulation et repli natif.
  // L'ensemble du document est reçu : la pagination et les permissions restent serveur.
  const resultRoot = $('[data-list-results]');
  if (resultRoot && window.fetch && window.AbortController) {
    let timer, controller, sequence = 0;
    const loading = $('[data-search-loading]');
    const loadingState = state => {
      if (loading) {
        loading.hidden = state === 'idle';
        loading.classList.toggle('is-error', state === 'error');
        $('.loading-copy', loading).textContent = state === 'error' ? 'Recherche automatique indisponible. Utilisez le bouton Rechercher.' : 'Recherche en cours…';
        $('.loading-bars', loading).hidden = state === 'error';
      }
      if (state === 'busy') resultRoot.setAttribute('aria-busy', 'true');
      else resultRoot.removeAttribute('aria-busy');
    };
    const search = $('form[data-live-search] input[name="q"]');
    if (search) {
      search.addEventListener('input', () => {
        clearTimeout(timer);
        controller?.abort();
        const current = ++sequence;
        loadingState('idle');
        timer = setTimeout(async () => {
          controller = new AbortController();
          const form = search.form;
          const url = new URL(form.action || location.href);
          url.search = new URLSearchParams(new FormData(form)).toString();
          url.searchParams.delete('page');
          loadingState('busy');
          announce('Recherche en cours.');
          let failed = false;
          try {
            const response = await fetch(url, { signal: controller.signal, headers: { 'X-Requested-With': 'XMLHttpRequest' } });
            if (!response.ok || response.redirected) throw new Error('Recherche indisponible');
            const html = new DOMParser().parseFromString(await response.text(), 'text/html');
            const replacement = $('[data-list-results]', html);
            if (current !== sequence) return;
            if (!replacement) throw new Error('Résultats indisponibles');
            resultRoot.replaceChildren(...replacement.childNodes);
            history.replaceState(null, '', url);
            announce('Résultats mis à jour.');
          } catch (error) {
            if (error.name !== 'AbortError' && current === sequence) {
              failed = true;
              loadingState('error');
              announce('Recherche automatique indisponible. Utilisez le bouton Rechercher.');
            }
          } finally {
            if (current === sequence && !failed) loadingState('idle');
          }
        }, 450);
      });
    }
  }
})();
