/* Aides de caisse testables sans DOM ; aucun prix ou paiement n'est enregistré ici. */
import { parseCount } from './operation-math.mjs';

export function parseTender(value) {
  const text = String(value).trim().replace(/[\s\u202f\u00a0]/g, '');
  const match = /^(\d+)(?:[.,](\d{1,2}))?$/.exec(text);
  return match ? BigInt(match[1]) * 100n + BigInt((match[2] || '').padEnd(2, '0')) : null;
}

export function tenderInput(minor) {
  return typeof minor === 'bigint' && minor >= 0n ? `${minor / 100n},${(minor % 100n).toString().padStart(2, '0')}` : '';
}

export function changeEstimate(total, received) {
  const amount = parseTender(received);
  if (typeof total !== 'bigint' || total < 0n || amount === null) return null;
  return { received: amount, change: amount - total };
}

export function stockPlan({ lots, cart = [], medicine, quantity, lotId = '' }) {
  const reserved = new Map();
  for (const row of cart) {
    const count = parseCount(row.quantity);
    if (count !== null) reserved.set(String(row.lot), (reserved.get(String(row.lot)) || 0n) + count);
  }
  const candidates = lots.filter(lot => String(lot.medicine) === String(medicine) && (!lotId || String(lot.id) === String(lotId))).map(lot => {
    const physical = parseCount(lot.quantity) || 0n;
    const free = physical - (reserved.get(String(lot.id)) || 0n);
    return { ...lot, available: free > 0n ? free : 0n };
  }).sort((a, b) => {
    const date = String(a.expiryIso).localeCompare(String(b.expiryIso));
    if (date) return date;
    const aId = parseCount(a.id), bId = parseCount(b.id);
    return aId !== null && bId !== null ? (aId < bId ? -1 : aId > bId ? 1 : 0) : String(a.id).localeCompare(String(b.id));
  });
  const available = candidates.reduce((sum, lot) => sum + lot.available, 0n);
  const count = parseCount(quantity);
  let remaining = count || 0n;
  const allocation = [];
  for (const lot of candidates) {
    const take = remaining < lot.available ? remaining : lot.available;
    if (take > 0n) { allocation.push({ ...lot, take }); remaining -= take; }
    if (remaining === 0n) break;
  }
  return { available, count, complete: count !== null && count > 0n && remaining === 0n, candidates, allocation };
}
