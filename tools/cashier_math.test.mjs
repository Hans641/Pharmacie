import test from 'node:test';
import assert from 'node:assert/strict';
import { parseTender, tenderInput, changeEstimate, stockPlan } from '../static/js/cashier-math.mjs';
const lots = [
  { id: '10', medicine: '1', expiryIso: '2027-12-01', quantity: '10' },
  { id: '2', medicine: '1', expiryIso: '2027-01-01', quantity: '2' },
  { id: '3', medicine: '2', expiryIso: '2026-12-01', quantity: '99' },
];

test('espèces : virgule, point et espaces français', () => {
  for (const value of ['20000', '20 000,00', '20\u202f000,00', '20000.00']) assert.equal(parseTender(value), 2000000n);
  assert.equal(parseTender('0,01'), 1n);
});
test('espèces : aucune interprétation ambiguë', () => {
  for (const value of ['', '-1', '1e5', '1,000', '2.3.4', 'abc', '20,']) assert.equal(parseTender(value), null);
});
test('montant reçu exact sans flottants', () => {
  assert.equal(parseTender('9007199254740993,01'), 900719925474099301n);
  assert.equal(tenderInput(1500000n), '15000,00');
  assert.equal(tenderInput(1n), '0,01');
  assert.equal(tenderInput(-1n), '');
});
test('monnaie à rendre positive, exacte ou insuffisante', () => {
  assert.deepEqual(changeEstimate(1500000n, '20000'), { received: 2000000n, change: 500000n });
  assert.equal(changeEstimate(1500000n, '15000').change, 0n);
  assert.equal(changeEstimate(110n, '1,05').change, -5n);
  assert.equal(changeEstimate(1500000n, ''), null);
});
test('FEFO trie les dates et répartit la quantité', () => {
  const plan = stockPlan({ lots, medicine: '1', quantity: '4' });
  assert.equal(plan.available, 12n);
  assert.equal(plan.complete, true);
  assert.deepEqual(plan.allocation.map(lot => [lot.id, lot.take]), [['2', 2n], ['10', 2n]]);
});
test('FEFO départage les dates identiques par identifiant numérique', () => {
  const sameDate = [
    { id: '10', medicine: '1', expiryIso: '2027-01-01', quantity: '1' },
    { id: '2', medicine: '1', expiryIso: '2027-01-01', quantity: '1' },
  ];
  assert.equal(stockPlan({ lots: sameDate, medicine: '1', quantity: '1' }).allocation[0].id, '2');
});
test('les lignes déjà au panier sont déduites du lot concerné', () => {
  const cart = [{ lot: '2', quantity: '1' }, { lot: '2', quantity: '1' }, { lot: '10', quantity: '3' }];
  const plan = stockPlan({ lots, cart, medicine: '1', quantity: '4' });
  assert.equal(plan.available, 7n);
  assert.deepEqual(plan.allocation.map(lot => [lot.id, lot.take]), [['10', 4n]]);
});
test('lot explicite : ne pas utiliser un autre lot pour compléter', () => {
  const plan = stockPlan({ lots, medicine: '1', quantity: '3', lotId: '2' });
  assert.equal(plan.available, 2n);
  assert.equal(plan.complete, false);
  assert.deepEqual(plan.allocation.map(lot => lot.id), ['2']);
});
test('ne pas changer de médicament pour trouver du stock', () => {
  const plan = stockPlan({ lots, medicine: '1', quantity: '15' });
  assert.equal(plan.available, 12n);
  assert.equal(plan.complete, false);
  assert(!plan.candidates.some(lot => lot.medicine === '2'));
});
test('stock déjà consommé : aucun disponible négatif', () => {
  const plan = stockPlan({ lots, cart: [{ lot: '2', quantity: '200' }, { lot: '10', quantity: '10' }], medicine: '1', quantity: '1' });
  assert.equal(plan.available, 0n);
  assert.equal(plan.complete, false);
  assert.deepEqual(plan.allocation, []);
});
test('quantités nulles ou invalides ne donnent pas de proposition complète', () => {
  for (const quantity of ['', '0', '-1', '1.5']) assert.equal(stockPlan({ lots, medicine: '1', quantity }).complete, false);
});
test('une liste vide reste une estimation vide', () => {
  const plan = stockPlan({ lots: [], medicine: '1', quantity: '1' });
  assert.equal(plan.available, 0n);
  assert.equal(plan.complete, false);
});
