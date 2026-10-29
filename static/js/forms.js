/* Formulaires progressifs : un POST natif, aucune sauvegarde intermédiaire.
   La validation locale aide à corriger la saisie ; Django décide de l'enregistrement. */
(() => {
  'use strict';
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const wizards = new Map();
  const formControls = root => $$('input, select, textarea', root).filter(control => control.willValidate);
  const numberLabel = value => new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 12 }).format(Number(value));

  function localError(control) {
    if (!control.willValidate) return '';
    const validity = control.validity;
    if (validity.customError) return control.validationMessage;
    if (validity.badInput) return 'Saisissez un nombre valide.';
    if (validity.valueMissing) {
      if (control.type === 'checkbox') return 'Cochez cette confirmation pour continuer.';
      if (control.tagName === 'SELECT' || control.type === 'radio') return 'Choisissez une option pour continuer.';
      return 'Renseignez ce champ pour continuer.';
    }
    if (control.required && ['text', 'textarea', 'search'].includes(control.type) && !control.value.trim()) return 'Saisissez une valeur ; les espaces seuls ne suffisent pas.';
    if (validity.typeMismatch) return control.type === 'email' ? 'Saisissez une adresse e-mail complète, par exemple nom@exemple.mg.' : 'Vérifiez le format de cette valeur.';
    if (validity.rangeUnderflow && control.type === 'date') return `Choisissez une date égale ou postérieure au ${control.min.split('-').reverse().join('/')}.`;
    if (validity.rangeUnderflow) return `Saisissez une valeur supérieure ou égale à ${numberLabel(control.min)}.`;
    if (validity.rangeOverflow) return `Saisissez une valeur inférieure ou égale à ${numberLabel(control.max)}.`;
    if (validity.stepMismatch) return control.step === '1' ? 'Saisissez un nombre entier.' : 'Vérifiez le nombre de décimales autorisé pour ce montant.';
    if (validity.tooLong) return `Limitez la saisie à ${control.maxLength} caractères.`;
    if (validity.tooShort) return `Saisissez au moins ${control.minLength} caractères.`;
    if (validity.patternMismatch || validity.customError) return 'Vérifiez le format indiqué dans l’aide de ce champ.';
    if (control.type === 'file' && control.files.length) {
      const clear = $('input[type="checkbox"]', control.closest('[data-field-name]'));
      if (clear?.checked) return 'Choisissez entre remplacer la photo et la supprimer ; décochez « Effacer » pour conserver le nouveau fichier.';
      const file = control.files[0];
      if (control.dataset.maxBytes && file.size > Number(control.dataset.maxBytes)) return 'Choisissez une image de 5 Mo maximum.';
      if (!/\.(jpe?g|png|webp)$/i.test(file.name)) return 'Choisissez une image JPEG, PNG ou WebP. Son contenu sera vérifié à l’enregistrement.';
    }
    return validity.valid ? '' : 'Vérifiez cette valeur avant de continuer.';
  }

  function validateField(field) {
    const controls = formControls(field);
    let issue = null;
    for (const control of controls) {
      const message = localError(control);
      if (!issue && message) issue = { control, message };
      if (message) control.setAttribute('aria-invalid', 'true');
      else if (!$('[data-server-errors]', field)) control.removeAttribute('aria-invalid');
    }
    field.classList.toggle('has-local-error', Boolean(issue));
    const feedback = $('[data-field-feedback]', field);
    if (feedback) feedback.textContent = issue?.message || '';
    return issue;
  }

  function collectIssues(form, scope = form) {
    const issues = [];
    $$('[data-field-name]', scope).forEach(field => {
      const issue = validateField(field);
      if (issue) issues.push(issue);
    });
    // Préserver aussi les contraintes natives des contrôles hors composant commun.
    formControls(scope).filter(control => !control.closest('[data-field-name]')).forEach(control => {
      const message = localError(control);
      if (message) issues.push({ control, message });
    });
    return issues;
  }

  function exposeAndFocus(form, issue) {
    wizards.get(form)?.reveal(issue.control);
    const details = issue.control.closest('details');
    if (details) details.open = true;
    issue.control.focus();
    const region = $('#interaction-status');
    if (region) region.textContent = issue.message;
    if (!issue.control.closest('[data-field-name]')) issue.control.reportValidity();
  }

  function createWizard(form) {
    const steps = $$('[data-wizard-step]', form);
    const indicators = $$('[data-wizard-go]', form);
    const progress = $('[data-wizard-progress]', form);
    const caption = $('[data-wizard-caption]', form);
    const previous = $('[data-wizard-previous]', form);
    const next = $('[data-wizard-next]', form);
    const submit = $('[data-wizard-submit]', form);
    if (!steps.length || !progress || !previous || !next || !submit) return null;
    let current = 0;
    let visited = 0;
    const completed = new Set();

    function fieldValue(field) {
      const controls = $$('input,select,textarea', field);
      const control = controls.find(input => input.name === field.dataset.fieldName);
      if (!control) return 'Non renseigné';
      if (control.tagName === 'SELECT') return [...control.selectedOptions].filter(option => option.value).map(option => option.textContent).join(', ') || 'Non renseigné';
      if (control.type === 'checkbox') return control.checked ? 'Oui' : 'Non';
      if (control.type === 'file') {
        if ($('input[type="checkbox"]', field)?.checked) return 'Photo supprimée après enregistrement';
        return control.files[0]?.name || control.dataset.currentFile || 'Aucune photo';
      }
      if (control.type === 'number' && control.value !== '') {
        if (['purchase_price', 'sale_price'].includes(control.name)) return new Intl.NumberFormat('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(Number(control.value)) + ' Ar';
        return numberLabel(control.value);
      }
      return control.value.trim() || 'Non renseigné';
    }

    function renderSummary() {
      const target = $('[data-wizard-summary]', form);
      if (!target) return;
      target.replaceChildren();
      steps.forEach((step, index) => {
        const section = document.createElement('section');
        section.className = 'review-section';
        const heading = document.createElement('div');
        heading.className = 'review-section-heading';
        const title = document.createElement('h3');
        title.textContent = $('legend', step).textContent;
        const edit = document.createElement('button');
        edit.type = 'button';
        edit.className = 'btn btn-ghost';
        edit.textContent = 'Modifier';
        edit.setAttribute('aria-label', `Modifier : ${title.textContent}`);
        edit.addEventListener('click', () => {
          show(index, true);
          formControls(step)[0]?.focus();
        });
        heading.append(title, edit);
        const list = document.createElement('dl');
        list.className = 'review-list';
        $$('[data-field-name]', step).forEach(field => {
          const row = document.createElement('div');
          const label = document.createElement('dt');
          label.textContent = field.dataset.fieldLabel;
          const value = document.createElement('dd');
          // Les valeurs utilisateur sont toujours rendues comme du texte.
          value.textContent = fieldValue(field);
          row.append(label, value);
          list.append(row);
        });
        section.append(heading, list);
        target.append(section);
      });
    }

    function show(index, focus = false) {
      current = index;
      visited = Math.max(visited, current);
      steps.forEach((step, stepIndex) => { step.hidden = stepIndex !== current; });
      indicators.forEach((indicator, stepIndex) => {
        indicator.disabled = stepIndex > visited;
        if (stepIndex === current) indicator.setAttribute('aria-current', 'step');
        else indicator.removeAttribute('aria-current');
        indicator.classList.toggle('is-complete', completed.has(stepIndex));
        $('[data-step-number]', indicator).hidden = completed.has(stepIndex);
        $('[data-step-complete]', indicator).hidden = !completed.has(stepIndex);
        $('[data-step-state]', indicator).textContent = stepIndex === current ? ' — étape en cours' : completed.has(stepIndex) ? ' — étape vérifiée' : ' — à compléter';
      });
      previous.hidden = current === 0;
      next.hidden = current === steps.length - 1;
      submit.hidden = current !== steps.length - 1;
      caption.textContent = `Étape ${current + 1} sur ${steps.length} — ${$('legend', steps[current]).textContent}`;
      if (current === steps.length - 1) renderSummary();
      if (focus) $('legend', steps[current]).focus();
    }

    function forward() {
      const issues = collectIssues(form, steps[current]);
      if (issues.length) { exposeAndFocus(form, issues[0]); return; }
      completed.add(current);
      show(Math.min(current + 1, steps.length - 1), true);
    }
    const api = {
      forward,
      isLast: () => current === steps.length - 1,
      reveal(control) {
        const index = steps.findIndex(step => step.contains(control));
        if (index >= 0) show(index);
      },
    };
    previous.addEventListener('click', () => show(Math.max(0, current - 1), true));
    next.addEventListener('click', forward);
    indicators.forEach((indicator, index) => indicator.addEventListener('click', () => {
      if (index <= current) show(index, true);
      else {
        // Même une étape déjà visitée revérifie les étapes intermédiaires.
        for (let stepIndex = current; stepIndex < index; stepIndex++) {
          const issues = collectIssues(form, steps[stepIndex]);
          if (issues.length) { exposeAndFocus(form, issues[0]); return; }
          completed.add(stepIndex);
        }
        show(index, true);
      }
    }));
    form.addEventListener('input', event => {
      const index = steps.findIndex(step => step.contains(event.target));
      if (index >= 0) for (const stepIndex of [...completed]) if (stepIndex >= index) completed.delete(stepIndex);
      if (current === steps.length - 1) renderSummary();
    });
    form.addEventListener('change', () => { if (current === steps.length - 1) renderSummary(); });
    const serverError = $('[data-server-errors]', form);
    const initial = serverError ? steps.findIndex(step => step.contains(serverError)) : 0;
    progress.hidden = false;
    $('[data-wizard-review]', form).hidden = false;
    form.classList.add('wizard-enhanced');
    show(Math.max(initial, 0));
    return api;
  }

  for (const form of $$('form[method="post"]')) {
    if (!$('[data-field-name]', form)) continue;
    if (form.hasAttribute('data-wizard')) {
      const wizard = createWizard(form);
      if (wizard) wizards.set(form, wizard);
    }
    form.addEventListener('pharmagest:validation-update', event => {
      const control = event.detail?.control;
      const field = control?.closest('[data-field-name]');
      if (field && form.contains(field) && (field.dataset.touched || field.classList.contains('has-local-error'))) validateField(field);
    });
    // noValidate uniquement après installation des gestionnaires : sans JS, HTML natif.
    form.addEventListener('focusout', event => {
      const field = event.target.closest('[data-field-name]');
      if (field && form.contains(field)) { field.dataset.touched = 'true'; validateField(field); }
    });
    form.addEventListener('change', event => {
      const field = event.target.closest('[data-field-name]');
      if (field) { field.dataset.touched = 'true'; validateField(field); }
    });
    form.addEventListener('input', event => {
      const field = event.target.closest('[data-field-name]');
      if (field?.dataset.touched) validateField(field);
    });
    form.addEventListener('submit', event => {
      if (wizards.has(form) && !wizards.get(form).isLast()) {
        event.preventDefault();
        event.stopImmediatePropagation();
        wizards.get(form).forward();
        return;
      }
      const issues = collectIssues(form);
      if (issues.length) {
        event.preventDefault();
        event.stopImmediatePropagation();
        exposeAndFocus(form, issues[0]);
      }
    }, true);
    form.noValidate = true;
  }

  // Un lien d'erreur doit aussi ouvrir l'étape contenant sa cible.
  document.addEventListener('click', event => {
    const link = event.target.closest('[data-error-summary] a');
    if (!link) return;
    const target = document.getElementById(link.getAttribute('href').slice(1));
    if (!target) return;
    const wizard = wizards.get(target.form);
    if (wizard) { event.preventDefault(); wizard.reveal(target); target.focus(); }
  });

  // Succès fermables sans disparition automatique ; les erreurs restent persistantes.
  $$('[data-dismiss-toast]').forEach(button => {
    button.hidden = false;
    button.addEventListener('click', () => {
      const toast = button.closest('[data-toast]');
      const focused = toast.contains(document.activeElement);
      toast.remove();
      if (focused) $('#main-content')?.focus();
    });
  });
})();
