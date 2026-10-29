/* Récapitulatifs indicatifs ; les services Django restent seuls décisionnaires. */
import { parseCount, formatUnits, formatMoney, inventoryEstimate, lineEstimate, restockIssue } from './operation-math.mjs';

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

for (const form of $$('form[data-operation]')) {
  const kind = form.dataset.operation;
  const preview = $('[data-operation-preview]', form);
  if (!preview) continue;
  const quantity = $('[name="quantity"]', form);
  const lineSelect = $('[name="line"]', form);
  const countInput = $('[name="counted"]', form);
  const restock = $('[name="restock"]', form);
  const blocked = $('[name="blocked"]', form);
  const lines = $$('[data-operation-line]').map(node => ({ ...node.dataset }));
  const baseMax = quantity?.getAttribute('max');
  const status = $('[data-preview-status]', preview);
  const put = (selector, value) => { const target = $(selector, preview); if (target && target.textContent !== value) target.textContent = value; };
  const refreshField = control => form.dispatchEvent(new CustomEvent('pharmagest:validation-update', { detail: { control } }));

  function setLimit(limit) {
    if (!quantity || quantity.getAttribute('max') === limit) return;
    if (limit === null) quantity.removeAttribute('max');
    else quantity.max = limit;
    refreshField(quantity);
  }
  function setRestockError(message) {
    if (!restock || (restock.validity.customError ? restock.validationMessage : '') === message) return;
    restock.setCustomValidity(message);
    refreshField(restock);
  }
  function showStatus(message, warning = false) {
    if (status.textContent !== message) status.textContent = message;
    preview.classList.toggle('has-warning', warning);
  }

  const expiryInput = $('[name="expires_on"]', form);
  if (expiryInput && form.dataset.today) expiryInput.min = form.dataset.today;

  function update() {
    if (kind === 'inventory') {
      const estimate = inventoryEstimate(form.dataset.stockBefore, countInput.value);
      put('[data-preview-count]', estimate ? formatUnits(estimate.counted) : 'Saisissez un comptage entier');
      put('[data-preview-delta]', estimate ? formatUnits(estimate.delta, true) : '—');
      put('[data-preview-blocked]', blocked.checked ? 'Bloqué à la vente' : 'Non bloqué (péremption toujours contrôlée)');
      showStatus(!estimate ? 'Indiquez une quantité entière positive ou nulle.' : estimate.delta === 0n ? 'Aucun écart de quantité. Le motif et le statut du lot seront tout de même tracés.' : 'La différence sera ajoutée au journal des mouvements. Le stock peut avoir évolué depuis l’ouverture de cette page.', Boolean(estimate && estimate.delta < 0n));
      if (estimate) {
        form.dataset.confirmTitle = 'Confirmer cet inventaire';
        form.dataset.confirm = `Comptage : ${formatUnits(estimate.counted)}. Écart estimé : ${formatUnits(estimate.delta, true)}. ${blocked.checked ? 'Le lot sera bloqué à la vente.' : 'Le lot ne sera pas bloqué ; sa péremption restera contrôlée.'} Le serveur recalculera la différence sur le stock courant.`;
        form.dataset.confirmLabel = 'Enregistrer l’inventaire';
        form.dataset.confirmIntent = estimate.delta < 0n || blocked.checked ? 'danger' : 'primary';
      }
      return;
    }
    const line = lines.find(item => item.lineId === lineSelect.value);
    setLimit(line ? line.remaining : baseMax);
    const quantityError = line && line.remaining === '0' ? 'Cette ligne n’a plus de quantité disponible. Choisissez une autre ligne.' : '';
    if ((quantity.validity.customError ? quantity.validationMessage : '') !== quantityError) {
      quantity.setCustomValidity(quantityError);
      refreshField(quantity);
    }
    put('[data-preview-name]', line?.name || 'Choisissez une ligne');
    const estimate = line ? lineEstimate(quantity.value, line.remaining, line.unitMinor) : null;
    put('[data-preview-count]', estimate ? formatUnits(estimate.count) : '—');
    put('[data-preview-remaining]', estimate ? formatUnits(estimate.remaining) : '—');
    put('[data-preview-amount]', estimate ? formatMoney(estimate.amount) : '—');
    const issue = kind === 'return' && line ? restockIssue(restock.checked, line.blocked === '1', line.expires, form.dataset.today) : '';
    setRestockError(issue);
    put('[data-preview-stock]', !estimate ? '—' : issue ? 'Réintégration impossible pour ce lot' : kind === 'receipt' || restock?.checked ? formatUnits(estimate.count, true) : 'Aucune réintégration');
    if (!line) {
      showStatus('Sélectionnez la ligne concernée pour afficher son récapitulatif.');
      return;
    }
    if (!estimate) {
      const available = parseCount(line.remaining);
      showStatus(available === 0n ? 'Cette ligne n’a plus de quantité disponible pour cette opération.' : `Indiquez une quantité entière comprise entre 1 et ${new Intl.NumberFormat('fr-FR').format(available)}.`, true);
      return;
    }
    if (kind === 'receipt') {
      const expiry = expiryInput.value;
      if (expiry && expiry < form.dataset.today) put('[data-preview-stock]', 'Réception impossible : lot périmé');
      showStatus(expiry && expiry < form.dataset.today ? 'La date saisie est passée : le serveur refusera la réception de ce lot périmé.' : 'Seules les unités de cette livraison seront ajoutées au stock ; le reste de la commande reste inchangé.', Boolean(expiry && expiry < form.dataset.today));
    } else {
      showStatus(issue || (restock.checked ? 'Remise en stock demandée après contrôle de l’éligibilité du produit. Le remboursement doit déjà avoir été effectué.' : 'Retour tracé sans réintégration au stock. Le remboursement doit déjà avoir été effectué.'), Boolean(issue));
      form.dataset.confirmTitle = 'Confirmer ce retour';
      form.dataset.confirm = `${line.name} : ${formatUnits(estimate.count)}. Remboursement déjà réalisé à consigner : ${formatMoney(estimate.amount)}. ${restock.checked ? 'Remise en stock demandée après contrôle.' : 'Aucune remise en stock.'} Référence du remboursement : ${$('[name="refund_reference"]', form).value.trim()}. Le motif saisi sera conservé.`;
      form.dataset.confirmLabel = 'Enregistrer le retour';
      form.dataset.confirmIntent = 'danger';
    }
  }
  form.addEventListener('input', update);
  form.addEventListener('change', update);
  // Dernière actualisation avant que le dialogue commun lise son récapitulatif.
  document.addEventListener('submit', event => { if (event.target === form) update(); }, true);
  update();
  preview.hidden = false;
}
