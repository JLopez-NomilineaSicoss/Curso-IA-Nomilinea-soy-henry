/**
 * Calcula el precio final aplicando IVA y descuento.
 *
 * @param total       Importe base antes de impuestos. Debe ser >= 0.
 * @param iva         Tasa de IVA en rango [0, 1]. Por defecto 0.21 (21%).
 * @param discount    Tasa de descuento en rango [0, 1]. Por defecto 0.
 * @returns Precio final redondeado a 2 decimales.
 * @example
 * // total 100, IVA por defecto 21% y sin descuento => 121.00
 * calculateFinal(100) // 121
 * @example
 * // total 100, IVA 13% y 10% de descuento => 100 * 1.13 * 0.9 = 101.7
 * calculateFinal(100, 0.13, 0.10) // 101.7
 */
export function calculateFinal(total: number, iva: number = 0.21, discount: number = 0): number {
  if (!Number.isFinite(total) || !Number.isFinite(iva) || !Number.isFinite(discount)) {
    throw new TypeError('Parámetros no numéricos o no finitos.');
  }
  if (total < 0) throw new RangeError('total debe ser >= 0');
  if (iva < 0 || iva > 1) throw new RangeError('iva debe estar en [0, 1]');
  if (discount < 0 || discount > 1) throw new RangeError('discount debe estar en [0, 1]');

  const raw = total * (1 + iva) * (1 - discount);
  // Redondeo bancario simple a 2 decimales
  return Math.round(raw * 100) / 100;
}
