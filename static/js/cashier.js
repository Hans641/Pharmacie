/* Poste de caisse : aides locales et clavier, sans écriture via fetch. */
import { parseCount, formatMoney, formatUnits } from './operation-math.mjs';
import { stockPlan, changeEstimate, tenderInput } from './cashier-math.mjs';

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const say = text => { const region = $('#interaction-status'); if (region && region.textContent !== text) region.textContent = text; };
const refresh = control => control?.form?.dispatchEvent(new CustomEvent('pharmagest:validation-update', { detail: { control } }));
const search = $('#cash-search');
const cartForm = $('[data-cart-add]');
const medicine = $('[name="medicine"]', cartForm || document);
const quantity = $('[name="quantity"]', cartForm || document);
const lotSelect = $('[name="lot"]', cartForm || document);
const checkout = $('[data-checkout]');

if (cartForm && medicine && quantity && lotSelect) {
  const lotTemplate = $('#lot-data');
  const lots = lotTemplate ? $$('span', lotTemplate.content).map(node => ({ ...node.dataset })) : [];
  const prices = new Map([...medicine.options].filter(option => option.value).map(option => [option.value, parseCount(option.dataset.priceMinor)]));
  const cart = $$('[data-cart-lot]').map(row => ({ lot: row.dataset.cartLot, quantity: row.dataset.cartQuantity }));
  const hint = $('[data-lot-hint]');
  const preview = $('[data-item-preview]');
  const addButton = $('[data-add-to-cart]');
  const baseMax = quantity.getAttribute('max');
  const put = (selector, text) => { const node = $(selector, preview); if (node && node.textContent !== text) node.textContent = text; };

  function updateItem() {
    // Un changement de médicament réinitialise seulement un lot devenu incompatible.
    let resetLot = false;
    for (const option of lotSelect.options) {
      if (!option.value) continue;
      const compatible = lots.some(lot => lot.id === option.value && lot.medicine === medicine.value);
      option.hidden = !compatible;
      option.disabled = !compatible;
      if (option.selected && !compatible) resetLot = true;
    }
    if (resetLot) { lotSelect.value = ''; say('Le choix du lot est revenu à FEFO pour ce médicament.'); }
    const plan = stockPlan({ lots, cart, medicine: medicine.value, quantity: quantity.value, lotId: lotSelect.value });
    const max = medicine.value ? plan.available.toString() : baseMax;
    const localError = medicine.value && plan.available === 0n ? 'Aucun stock disponible pour cet ajout. Actualisez la page ou choisissez un autre médicament.' : '';
    let changed = false;
    if (quantity.getAttribute('max') !== max) {
      if (max === null) quantity.removeAttribute('max'); else quantity.max = max;
      changed = true;
    }
    if ((quantity.validity.customError ? quantity.validationMessage : '') !== localError) {
      quantity.setCustomValidity(localError);
      changed = true;
    }
    if (changed) refresh(quantity);
    if (addButton) addButton.disabled = cartForm.dataset.submitting === 'true' || !medicine.value || plan.available === 0n;
    if (preview) {
      preview.hidden = !medicine.value;
      const price = prices.get(medicine.value);
      put('[data-item-price]', formatMoney(price));
      put('[data-item-available]', formatUnits(plan.available));
      put('[data-item-subtotal]', price !== undefined && price !== null && plan.count !== null && plan.count > 0n ? formatMoney(price * plan.count) : '—');
    }
    const first = plan.allocation[0] || plan.candidates.find(lot => lot.available > 0n);
    const soon = plan.allocation.some(lot => lot.state === 'soon') || (!plan.allocation.length && first?.state === 'soon');
    hint.classList.toggle('warning', Boolean(medicine.value && (plan.available === 0n || (plan.count !== null && plan.count > plan.available) || soon)));
    let text = 'Choisissez un médicament. Le lot automatique suit la méthode FEFO.';
    if (medicine.value && !plan.available) text = 'Aucun stock délivrable disponible pour cet ajout. La quantité déjà au panier a été déduite. Actualisez la page pour revérifier la disponibilité.';
    else if (medicine.value && first) {
      const label = lotSelect.value ? 'Lot choisi' : 'Suggestion FEFO';
      text = `${label} : ${first.number} · péremption ${first.expiry}. `;
      if (plan.allocation.length > 1) text += `La quantité sera proposée sur ${plan.allocation.length} lots. `;
      if (plan.count !== null && plan.count > plan.available) text += `Quantité demandée supérieure aux ${formatUnits(plan.available)} affichées. `;
      if (soon) text += 'Attention : au moins un lot arrive à péremption sous 90 jours. ';
      text += 'Les lots et le stock seront revérifiés lors de l’ajout.';
    }
    if (hint.textContent !== text) hint.textContent = text;
  }
  medicine.addEventListener('change', () => {
    quantity.value ||= '1';
    updateItem();
    quantity.focus();
    quantity.select();
  });
  lotSelect.addEventListener('change', updateItem);
  quantity.addEventListener('input', updateItem);
  quantity.addEventListener('change', updateItem);
  document.addEventListener('submit', event => { if (event.target === cartForm) updateItem(); }, true);
  if (!medicine.value && medicine.options.length === 2 && new URL(location.href).searchParams.has('q')) medicine.selectedIndex = 1;
  if (medicine.value) quantity.value ||= '1';
  updateItem();
  window.addEventListener('pageshow', updateItem);
}

// F4 fonctionne aussi pour un compte qui encaisse sans modifier le panier.
document.addEventListener('keydown', event => {
  if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey || $('#confirm-dialog')?.open || $('#navigation-panel')?.classList.contains('is-open')) return;
  if (event.key === 'F2' && search) { event.preventDefault(); search.focus(); search.select(); }
  if (event.key === 'F4' && $('#checkout')) {
    event.preventDefault();
    ($('[name="method"]:checked', checkout || document) || $('#checkout')).focus();
  }
});

const summaryError = $('[data-error-summary]');
const operationError = $('.alert.error');
const hashTarget = location.hash === '#cart' ? $('#cart') : location.hash === '#checkout' ? $('#checkout') : null;
if (!summaryError) {
  if (operationError) { operationError.tabIndex = -1; operationError.focus(); }
  else if (hashTarget) hashTarget.focus();
  else if (search && medicine && quantity) {
    if (medicine.value && new URL(location.href).searchParams.has('q')) { quantity.focus(); quantity.select(); }
    else search.focus();
  }
}

if (checkout) {
  const received = $('#cash-received');
  const change = $('#cash-change');
  const changeLabel = $('[data-change-label]');
  const feedback = $('#cash-received-feedback');
  const cashTools = $('[data-cash-tools]');
  const electronicTools = $('[data-electronic-tools]');
  const exact = $('[data-cash-exact]');
  const total = parseCount(checkout.dataset.totalMinor);
  let tenderTouched = false;
  function updateTender() {
    const estimate = changeEstimate(total, received.value);
    const invalid = received.value.trim() !== '' && !estimate;
    const shortage = estimate && estimate.change < 0n;
    changeLabel.textContent = shortage ? 'Montant manquant' : 'Monnaie à rendre';
    change.textContent = estimate ? formatMoney(shortage ? -estimate.change : estimate.change) : '—';
    change.parentElement.classList.toggle('warning', Boolean(shortage));
    feedback.textContent = invalid && tenderTouched ? 'Saisissez un montant comme 20 000,00 ou 20000.00.' : shortage ? 'Le montant indiqué est inférieur au total. Vérifiez les espèces réellement reçues avant de confirmer.' : '';
    if (invalid && tenderTouched) received.setAttribute('aria-invalid', 'true'); else received.removeAttribute('aria-invalid');
  }
  function paymentChanged() {
    const cash = $('[name="method"]:checked', checkout)?.value === 'cash';
    cashTools.hidden = !cash;
    if (electronicTools) {
      electronicTools.hidden = cash;
      $$('input', electronicTools).forEach(input => {
        input.disabled = cash;
        input.required = !cash;
        refresh(input);
      });
    }
  }
  $$('[name="method"]', checkout).forEach(input => input.addEventListener('change', paymentChanged));
  received.addEventListener('input', updateTender);
  received.addEventListener('blur', () => { tenderTouched = true; updateTender(); });
  if (exact && total !== null) {
    exact.hidden = false;
    exact.addEventListener('click', () => { received.value = tenderInput(total); tenderTouched = true; updateTender(); received.focus(); });
  }
  const prescription = $('[name="prescription_checked"]', checkout);
  const prescriptionRequired = $$('[data-prescription="1"]').length > 0;
  if (prescription) prescription.required = prescriptionRequired;
  const prescriptionNotice = $('[data-prescription-notice]');
  if (prescriptionNotice) prescriptionNotice.hidden = !prescriptionRequired;
  paymentChanged();
  updateTender();
}
