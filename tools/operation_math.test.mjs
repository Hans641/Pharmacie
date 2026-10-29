import test from 'node:test';
import assert from 'node:assert/strict';
import { parseCount, formatMoney, formatUnits, inventoryEstimate, lineEstimate, restockIssue } from '../static/js/operation-math.mjs';

test('comptage entier, zéro et refus des saisies ambiguës', () => {
  assert.equal(parseCount('0'), 0n);
  assert.equal(parseCount(' 20 '), 20n);
  for (const value of ['', '-1', '1.5', '1e3', 'abc']) assert.equal(parseCount(value), null);
});
test('monnaie française exacte, même au-delà des entiers sûrs de Number', () => {
  assert.equal(formatMoney(1500000n), '15\u202f000,00 Ar');
  assert.equal(formatMoney(-1n), '-0,01 Ar');
  assert.equal(formatMoney(900719925474099301n), '9\u202f007\u202f199\u202f254\u202f740\u202f993,01 Ar');
});
test('quantités signées sans ambiguïté de couleur', () => {
  assert.equal(formatUnits(3n, true), '+3 unités');
  assert.equal(formatUnits(-1n, true), '-1 unité');
  assert.equal(formatUnits(0n, true), '0 unités');
});
test('inventaire : diminution, zéro physique et aucun écart', () => {
  assert.deepEqual(inventoryEstimate('20', '17'), { counted: 17n, delta: -3n });
  assert.deepEqual(inventoryEstimate('20', '0'), { counted: 0n, delta: -20n });
  assert.deepEqual(inventoryEstimate('20', '20'), { counted: 20n, delta: 0n });
  assert.equal(inventoryEstimate('20', ''), null);
});
test('réception partielle : reliquat et valeur des marchandises', () => {
  assert.deepEqual(lineEstimate('8', '20', '125050'), { count: 8n, remaining: 12n, amount: 1000400n });
});
test('retour : ne pas dépasser les unités encore retournables', () => {
  assert.deepEqual(lineEstimate('2', '3', '150000'), { count: 2n, remaining: 1n, amount: 300000n });
  for (const count of ['0', '-1', '4', '1.5', '']) assert.equal(lineEstimate(count, '3', '150000'), null);
  assert.equal(lineEstimate('1', '0', '150000'), null);
});
test('multiplication exacte pour les quantités et montants élevés', () => {
  assert.equal(lineEstimate('1000000000', '1000000000', '99999999999999').amount, 99999999999999000000000n);
});
test('retour sans réintégration possible même si lot bloqué ou périmé', () => {
  assert.equal(restockIssue(false, true, '2020-01-01', '2026-10-29'), '');
});
test('remise en stock : blocage et péremption signalés précisément', () => {
  assert.match(restockIssue(true, true, '2027-01-01', '2026-10-29'), /bloqué/);
  assert.match(restockIssue(true, false, '2026-10-28', '2026-10-29'), /périmé/);
  assert.equal(restockIssue(true, false, '2026-10-29', '2026-10-29'), '');
});
