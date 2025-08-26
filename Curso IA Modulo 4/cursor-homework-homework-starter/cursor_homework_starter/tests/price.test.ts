import { calculateFinal } from '../src/lib/price';

describe('calculateFinal', () => {
  test('usa IVA por defecto (21%) y sin descuento', () => {
    // Arrange
    const total = 100;
    // Act
    const result = calculateFinal(total);
    // Assert
    expect(result).toBe(121);
  });

  test('aplica descuento (10%) con IVA por defecto (21%)', () => {
    // Arrange
    const total = 200;
    const discount = 0.1;
    // Act
    const result = calculateFinal(total, undefined as unknown as number, discount);
    // Assert
    // 200 * 1.21 * 0.9 = 217.8
    expect(result).toBe(217.8);
  });

  test('maneja decimales correctamente (redondeo a 2 decimales implícito)', () => {
    // Arrange
    const total = 99.99;
    const iva = 0.13;
    const discount = 0.05;
    // Act
    const result = calculateFinal(total, iva, discount);
    // Assert
    // 99.99 * 1.13 * 0.95 = 107.34
    expect(result).toBe(107.34);
  });

  test('lanza error si total es negativo', () => {
    // Arrange
    const total = -1;
    // Act & Assert
    expect(() => calculateFinal(total)).toThrow(RangeError);
  });

  test('lanza error si iva está fuera de [0,1]', () => {
    // Arrange
    const total = 100;
    // Act & Assert
    expect(() => calculateFinal(total, 1.1)).toThrow(RangeError);
    expect(() => calculateFinal(total, -0.1)).toThrow(RangeError);
  });

  test('lanza error si discount está fuera de [0,1]', () => {
    // Arrange
    const total = 100;
    // Act & Assert
    expect(() => calculateFinal(total, 0.21, 1.5)).toThrow(RangeError);
    expect(() => calculateFinal(total, 0.21, -0.01)).toThrow(RangeError);
  });

  test('lanza error por parámetros no numéricos o no finitos', () => {
    // Arrange
    // Act & Assert
    expect(() => calculateFinal('100' as any)).toThrow(TypeError);
    expect(() => calculateFinal(100, NaN)).toThrow(TypeError);
    expect(() => calculateFinal(100, 0.21, Infinity)).toThrow(TypeError);
  });
});
