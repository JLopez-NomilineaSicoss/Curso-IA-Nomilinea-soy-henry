/**
 * Genera un reporte agregado de órdenes con estadísticas por estado y usuario.
 * 
 * @param orders - Array de órdenes a procesar. Cada orden debe tener la estructura:
 *   {
 *     id?: string,           // ID de la orden (opcional)
 *     userId?: string,       // ID del usuario (opcional, usa 'unknown' por defecto)
 *     status?: string,       // Estado de la orden (opcional, usa 'unknown' por defecto)
 *     total: number,         // Total de la orden (requerido, debe ser número finito)
 *     createdAt: string      // Fecha de creación en formato ISO (requerido)
 *   }
 * 
 * @returns Objeto con estadísticas agregadas:
 *   {
 *     totalOrders: number,                    // Número total de órdenes válidas
 *     totalsByStatus: Record<string, number>, // Suma de totales agrupados por estado
 *     countByUser: Record<string, number>,    // Número de órdenes agrupadas por usuario
 *     newestOrderId: string | null            // ID de la orden más reciente (null si ninguna tiene ID)
 *   }
 * 
 * @throws {TypeError} Si orders no es un array
 * 
 * @example
 * const orders = [
 *   { id: '1', userId: 'user1', status: 'paid', total: 100, createdAt: '2024-01-01T10:00:00Z' },
 *   { id: '2', userId: 'user2', status: 'pending', total: 200, createdAt: '2024-01-02T10:00:00Z' }
 * ];
 * 
 * const report = groupOrdersReport(orders);
 * // Resultado:
 * // {
 * //   totalOrders: 2,
 * //   totalsByStatus: { 'paid': 100, 'pending': 200 },
 * //   countByUser: { 'user1': 1, 'user2': 1 },
 * //   newestOrderId: '2'
 * // }
 */
export function groupOrdersReport(orders: Array<any>) {
  if (!Array.isArray(orders)) {
    throw new TypeError('orders debe ser un array');
  }

  const totalsByStatus: Record<string, number> = {};
  const countByUser: Record<string, number> = {};
  let totalOrders = 0;
  let newestOrderId: string | null = null;
  let newestOrderDate: number = -Infinity;

  for (const order of orders) {
    if (!isValidOrder(order)) continue;

    totalOrders++;

    updateTotalsByStatus(totalsByStatus, order);
    updateCountByUser(countByUser, order);
    
    // Actualizar la orden más reciente
    const orderDate = Date.parse(order.createdAt);
    if (Number.isFinite(orderDate) && orderDate > newestOrderDate) {
      newestOrderDate = orderDate;
      newestOrderId = typeof order.id === 'string' ? order.id : null;
    }
  }

  return {
    totalOrders,
    totalsByStatus,
    countByUser,
    newestOrderId
  };
}

/**
 * Valida si una orden es válida para procesamiento
 */
function isValidOrder(order: any): boolean {
  return order && 
         typeof order === 'object' && 
         typeof order.total === 'number' && 
         Number.isFinite(order.total);
}

/**
 * Actualiza el mapa de totales por estado
 */
function updateTotalsByStatus(totalsByStatus: Record<string, number>, order: any): void {
  const status = order.status || 'unknown';
  totalsByStatus[status] = (totalsByStatus[status] || 0) + order.total;
}

/**
 * Actualiza el mapa de conteo por usuario
 */
function updateCountByUser(countByUser: Record<string, number>, order: any): void {
  const userId = order.userId || 'unknown';
  countByUser[userId] = (countByUser[userId] || 0) + 1;
}


