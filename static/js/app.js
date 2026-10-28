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
      $('#confirm-description').textContent = form.dataset.confirm;
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

  // Aide de saisie native : ne remplace aucune validation serveur.
  document.addEventListener('focusout', event => {
    const input = event.target;
    if (input.matches('input:not([type="hidden"]),select,textarea') && input.willValidate && !input.validity.valid) input.setAttribute('aria-invalid', 'true');
  });
  document.addEventListener('input', event => {
    const input = event.target;
    if (input.willValidate && input.validity.valid && !input.closest('.has-error')) input.removeAttribute('aria-invalid');
  });

  // Caisse : recherche puis quantité ; aucune validation de vente automatique.
  const cashSearch = $('#cash-search');
  const medicine = $('[data-cart-add] [name="medicine"]');
  const quantity = $('[data-cart-add] [name="quantity"]');
  const lotSelect = $('[data-cart-add] [name="lot"]');
  const lotData = $('#lot-data');
  if (cashSearch && medicine && quantity) {
    if (!errorSummary) {
      if (!medicine.value && medicine.options.length === 2 && new URL(location.href).searchParams.has('q')) medicine.selectedIndex = 1;
      if (medicine.value && new URL(location.href).searchParams.has('q')) { quantity.value ||= '1'; quantity.focus(); quantity.select(); }
      else cashSearch.focus();
    }
    medicine.addEventListener('change', () => { quantity.value ||= '1'; });
    document.addEventListener('keydown', event => {
      if (dialog?.open || navigation?.classList.contains('is-open')) return;
      if (event.key === 'F2') { event.preventDefault(); cashSearch.focus(); cashSearch.select(); }
      if (event.key === 'F4') { event.preventDefault(); ($('[data-checkout] [name="method"]:checked') || $('#checkout'))?.focus(); }
    });
  }
  if (medicine && lotSelect && lotData) {
    const reserved = new Map();
    $$('[data-cart-lot]').forEach(row => reserved.set(row.dataset.cartLot, (reserved.get(row.dataset.cartLot) || 0) + Number(row.dataset.cartQuantity)));
    const lots = $$('span', lotData.content).map(node => ({ ...node.dataset, quantity: Number(node.dataset.quantity) - (reserved.get(node.dataset.id) || 0) })).filter(lot => lot.quantity > 0);
    const hint = $('[data-lot-hint]');
    function suggestLot() {
      const available = lots.filter(lot => lot.medicine === medicine.value);
      for (const option of lotSelect.options) {
        if (!option.value) continue;
        const matches = available.some(lot => lot.id === option.value);
        option.hidden = !matches;
        option.disabled = !matches;
      }
      if (lotSelect.selectedOptions[0]?.disabled) lotSelect.value = '';
      const chosen = available.find(lot => lot.id === lotSelect.value) || available[0];
      hint.classList.toggle('warning', chosen?.state === 'soon');
      hint.textContent = !medicine.value ? 'Choisissez un médicament. Le lot automatique suit la méthode FEFO.' : !chosen ? 'Aucun lot délivrable actuellement. La disponibilité est contrôlée par le serveur.' : `${lotSelect.value ? 'Lot choisi' : 'Suggestion FEFO'} : ${chosen.number} · ${chosen.quantity} unités · péremption ${chosen.expiry}${chosen.state === 'soon' ? ' — sous 90 jours' : ''}. Le besoin peut se répartir sur plusieurs lots. Stock revérifié à l’encaissement.`;
    }
    medicine.addEventListener('change', suggestLot);
    lotSelect.addEventListener('change', suggestLot);
    suggestLot();
  }

  // Calcul en centimes pour éviter les erreurs d'arrondi en monnaie.
  const checkout = $('[data-checkout]');
  const parseCents = value => {
    const normalized = value.trim().replace(/[\s\u202f\u00a0]/g, '').replace(',', '.');
    if (!/^\d+(?:\.\d{1,2})?$/.test(normalized)) return null;
    const [whole, fraction = ''] = normalized.split('.');
    const result = Number(whole) * 100 + Number(fraction.padEnd(2, '0'));
    return Number.isSafeInteger(result) ? result : null;
  };
  const formatCents = value => new Intl.NumberFormat('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value / 100) + ' Ar';
  if (checkout) {
    const received = $('#cash-received');
    const change = $('#cash-change');
    const cashTools = $('[data-cash-tools]');
    const electronicTools = $('[data-electronic-tools]');
    function paymentChanged() {
      const cash = $('[name="method"]:checked', checkout)?.value === 'cash';
      cashTools.hidden = !cash;
      if (electronicTools) {
        electronicTools.hidden = cash;
        $$('input', electronicTools).forEach(input => { input.disabled = cash; });
      }
    }
    $$('[name="method"]', checkout).forEach(input => input.addEventListener('change', paymentChanged));
    paymentChanged();
    received.addEventListener('input', () => {
      const paid = parseCents(received.value);
      const total = parseCents(checkout.dataset.total);
      change.textContent = paid === null || total === null ? 'Saisissez un montant valide' : paid < total ? `Il manque ${formatCents(total - paid)}` : formatCents(paid - total);
    });
  }

  // Recherche des listes : GET serveur, temporisation, annulation et repli natif.
  // L'ensemble du document est reçu : la pagination et les permissions restent serveur.
  const resultRoot = $('[data-list-results]');
  if (resultRoot && window.fetch && window.AbortController) {
    let timer, controller, sequence = 0;
    const search = $('form[data-live-search] input[name="q"]');
    if (search) {
      search.addEventListener('input', () => {
        clearTimeout(timer);
        controller?.abort();
        const current = ++sequence;
        resultRoot.removeAttribute('aria-busy');
        timer = setTimeout(async () => {
          controller = new AbortController();
          const form = search.form;
          const url = new URL(form.action || location.href);
          url.search = new URLSearchParams(new FormData(form)).toString();
          url.searchParams.delete('page');
          resultRoot.setAttribute('aria-busy', 'true');
          announce('Recherche en cours.');
          try {
            const response = await fetch(url, { signal: controller.signal, headers: { 'X-Requested-With': 'XMLHttpRequest' } });
            if (!response.ok || response.redirected) throw new Error('Recherche indisponible');
            const html = new DOMParser().parseFromString(await response.text(), 'text/html');
            const replacement = $('[data-list-results]', html);
            if (!replacement || current !== sequence) return;
            resultRoot.replaceChildren(...replacement.childNodes);
            history.replaceState(null, '', url);
            announce('Résultats mis à jour.');
          } catch (error) {
            if (error.name !== 'AbortError') announce('Recherche automatique indisponible. Utilisez le bouton Rechercher.');
          } finally {
            if (current === sequence) resultRoot.removeAttribute('aria-busy');
          }
        }, 450);
      });
    }
  }
})();
