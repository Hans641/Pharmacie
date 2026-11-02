'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { composite, contrast } = require('./ux_presentation.cjs');
test('noir et blanc : contraste maximal 21:1 dans les deux sens', () => {
  assert.equal(contrast([0, 0, 0], [255, 255, 255]), 21);
  assert.equal(contrast([255, 255, 255], [0, 0, 0]), 21);
});
test('couleurs identiques : contraste 1:1', () => assert.equal(contrast([25, 39, 32], [25, 39, 32]), 1));
test('seuil texte : gris 118 conforme, gris 119 insuffisant sur blanc', () => {
  assert(contrast([118, 118, 118], [255, 255, 255]) >= 4.5);
  assert(contrast([119, 119, 119], [255, 255, 255]) < 4.5);
});
test('alpha : transparent, opaque et semi-transparent', () => {
  assert.deepEqual(composite([255, 0, 0, 0], [10, 20, 30]), [10, 20, 30]);
  assert.deepEqual(composite([255, 0, 0], [10, 20, 30]), [255, 0, 0]);
  assert.deepEqual(composite([0, 0, 0, 0.5], [200, 200, 200]), [100, 100, 100]);
});
test('fonds successifs transparents composés dans le bon ordre', () => {
  const background = [[255, 255, 255], [0, 0, 0, 0.5], [255, 0, 0, 0.5]]
    .reduce((back, front) => composite(front, back), [255, 255, 255]);
  assert.deepEqual(background, [191.25, 63.75, 63.75]);
});
