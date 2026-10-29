/* Calculs de présentation purs, sans dépendance au DOM et sans flottants. */
export function parseCount(value) {
  const text = String(value).trim();
  return /^\d+$/.test(text) ? BigInt(text) : null;
}

export function formatUnits(value, signed = false) {
  if (typeof value !== 'bigint') return '—';
  const prefix = signed && value > 0n ? '+' : '';
  return `${prefix}${new Intl.NumberFormat('fr-FR').format(value)} unité${value === 1n || value === -1n ? '' : 's'}`;
}

export function formatMoney(minor) {
  if (typeof minor !== 'bigint') return '—';
  const absolute = minor < 0n ? -minor : minor;
  const whole = new Intl.NumberFormat('fr-FR').format(absolute / 100n);
  const fraction = (absolute % 100n).toString().padStart(2, '0');
  return `${minor < 0n ? '-' : ''}${whole},${fraction} Ar`;
}

export function inventoryEstimate(before, counted) {
  const original = parseCount(before), actual = parseCount(counted);
  return original === null || actual === null ? null : { counted: actual, delta: actual - original };
}

export function lineEstimate(quantity, remaining, unitMinor) {
  const count = parseCount(quantity), available = parseCount(remaining), cost = parseCount(unitMinor);
  if (count === null || available === null || cost === null || count < 1n || count > available) return null;
  return { count, remaining: available - count, amount: count * cost };
}

export function restockIssue(requested, blocked, expiry, today) {
  if (!requested) return '';
  if (blocked) return 'Ce lot est bloqué. Décochez la remise en stock pour enregistrer un retour sans réintégration.';
  if (expiry && today && expiry < today) return 'Ce lot est périmé. Décochez la remise en stock pour enregistrer un retour sans réintégration.';
  return '';
}
