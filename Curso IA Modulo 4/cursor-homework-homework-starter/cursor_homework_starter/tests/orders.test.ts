import { groupOrdersReport } from '../src/lib/orders';

describe('groupOrdersReport', () => {
  test('procesa órdenes válidas correctamente', () => {
    // Arrange
    const orders = [
      {
        id: '1',
        userId: 'user1',
        status: 'paid',
        total: 100,
        createdAt: '2024-01-01T10:00:00Z'
      },
      {
        id: '2',
        userId: 'user2',
        status: 'pending',
        total: 200,
        createdAt: '2024-01-02T10:00:00Z'
      },
      {
        id: '3',
        userId: 'user1',
        status: 'paid',
        total: 150,
        createdAt: '2024-01-03T10:00:00Z'
      }
    ];

    // Act
    const result = groupOrdersReport(orders);

    // Assert
    expect(result.totalOrders).toBe(3);
    expect(result.totalsByStatus).toEqual({
      'paid': 250,
      'pending': 200
    });
    expect(result.countByUser).toEqual({
      'user1': 2,
      'user2': 1
    });
    expect(result.newestOrderId).toBe('3');
  });

  test('maneja órdenes con valores por defecto', () => {
    // Arrange
    const orders = [
      {
        id: '1',
        total: 100,
        createdAt: '2024-01-01T10:00:00Z'
      },
      {
        total: 200,
        createdAt: '2024-01-02T10:00:00Z'
      }
    ];

    // Act
    const result = groupOrdersReport(orders);

    // Assert
    expect(result.totalOrders).toBe(2);
    expect(result.totalsByStatus).toEqual({
      'unknown': 300
    });
    expect(result.countByUser).toEqual({
      'unknown': 2
    });
    expect(result.newestOrderId).toBeNull();
  });

  test('ignora órdenes inválidas', () => {
    // Arrange
    const orders = [
      {
        id: '1',
        userId: 'user1',
        status: 'paid',
        total: 100,
        createdAt: '2024-01-01T10:00:00Z'
      },
      null,
      {
        id: '2',
        userId: 'user2',
        status: 'pending',
        total: 'invalid', // total no es número
        createdAt: '2024-01-02T10:00:00Z'
      },
      {
        id: '3',
        userId: 'user3',
        status: 'shipped',
        total: NaN, // total no es finito
        createdAt: '2024-01-03T10:00:00Z'
      }
    ];

    // Act
    const result = groupOrdersReport(orders);

    // Assert
    expect(result.totalOrders).toBe(1);
    expect(result.totalsByStatus).toEqual({
      'paid': 100
    });
    expect(result.countByUser).toEqual({
      'user1': 1
    });
    expect(result.newestOrderId).toBe('1');
  });

  test('lanza error si orders no es un array', () => {
    // Arrange & Act & Assert
    expect(() => groupOrdersReport(null as any)).toThrow(TypeError);
    expect(() => groupOrdersReport('not an array' as any)).toThrow(TypeError);
    expect(() => groupOrdersReport(123 as any)).toThrow(TypeError);
  });

  test('maneja array vacío', () => {
    // Arrange
    const orders: any[] = [];

    // Act
    const result = groupOrdersReport(orders);

    // Assert
    expect(result.totalOrders).toBe(0);
    expect(result.totalsByStatus).toEqual({});
    expect(result.countByUser).toEqual({});
    expect(result.newestOrderId).toBeNull();
  });

  test('identifica correctamente la orden más reciente', () => {
    // Arrange
    const orders = [
      {
        id: 'old',
        userId: 'user1',
        status: 'paid',
        total: 100,
        createdAt: '2024-01-01T10:00:00Z'
      },
      {
        id: 'newest',
        userId: 'user2',
        status: 'pending',
        total: 200,
        createdAt: '2024-01-03T10:00:00Z'
      },
      {
        id: 'middle',
        userId: 'user3',
        status: 'shipped',
        total: 150,
        createdAt: '2024-01-02T10:00:00Z'
      }
    ];

    // Act
    const result = groupOrdersReport(orders);

    // Assert
    expect(result.newestOrderId).toBe('newest');
  });
});
