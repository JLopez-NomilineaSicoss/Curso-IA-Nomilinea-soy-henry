# Módulo de Utilidades de Negocio

Este módulo contiene funciones utilitarias para el procesamiento de datos de negocio, específicamente para cálculos de precios y reportes de órdenes.

## 📦 Funciones Disponibles

### `calculateFinal(total, iva?, discount?)` - Cálculo de Precio Final

Calcula el precio final de un producto aplicando IVA y descuentos.

**Parámetros:**
- `total` (number): Importe base antes de impuestos. Debe ser >= 0.
- `iva` (number, opcional): Tasa de IVA en rango [0, 1]. Por defecto 0.21 (21%).
- `discount` (number, opcional): Tasa de descuento en rango [0, 1]. Por defecto 0.

**Retorna:** Precio final redondeado a 2 decimales.

**Ejemplo de uso:**
```typescript
import { calculateFinal } from './price';

// IVA por defecto (21%) y sin descuento
calculateFinal(100); // 121.00

// Con IVA personalizado (13%) y descuento (10%)
calculateFinal(100, 0.13, 0.10); // 101.70

// Solo con descuento, IVA por defecto
calculateFinal(200, undefined, 0.15); // 205.70
```

**Limitaciones:**
- Solo acepta números finitos como parámetros
- El total debe ser >= 0
- Las tasas de IVA y descuento deben estar en el rango [0, 1]
- Redondeo a 2 decimales usando redondeo bancario simple

### `groupOrdersReport(orders)` - Reporte de Órdenes

Genera un reporte agregado con estadísticas de órdenes agrupadas por estado y usuario.

**Parámetros:**
- `orders` (Array): Array de objetos de órdenes

**Estructura esperada de cada orden:**
```typescript
{
  id?: string,           // ID de la orden (opcional)
  userId?: string,       // ID del usuario (opcional, usa 'unknown' por defecto)
  status?: string,       // Estado de la orden (opcional, usa 'unknown' por defecto)
  total: number,         // Total de la orden (requerido, debe ser número finito)
  createdAt: string      // Fecha de creación en formato ISO (requerido)
}
```

**Retorna:**
```typescript
{
  totalOrders: number,                    // Número total de órdenes válidas
  totalsByStatus: Record<string, number>, // Suma de totales agrupados por estado
  countByUser: Record<string, number>,    // Número de órdenes agrupadas por usuario
  newestOrderId: string | null            // ID de la orden más reciente
}
```

**Ejemplo de uso:**
```typescript
import { groupOrdersReport } from './orders';

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

const report = groupOrdersReport(orders);
// Resultado:
// {
//   totalOrders: 3,
//   totalsByStatus: { 'paid': 250, 'pending': 200 },
//   countByUser: { 'user1': 2, 'user2': 1 },
//   newestOrderId: '3'
// }
```

**Limitaciones:**
- Solo procesa órdenes con `total` como número finito
- Ignora órdenes con valores `null`, `undefined` o `total` inválido
- Usa valores por defecto ('unknown') para campos faltantes
- `newestOrderId` será `null` si ninguna orden tiene un `id` válido
- No valida el formato de fecha más allá de que sea parseable por `Date.parse()`

## 🧪 Testing

El módulo incluye tests unitarios completos con cobertura del 100%:

```bash
npm run test        # Ejecutar tests
npm run test:cov    # Ejecutar tests con reporte de cobertura
```

## 🔧 Refactoring Aplicado

La función `groupOrdersReport` ha sido refactorizada para:
- Reducir complejidad ciclomática
- Extraer funciones auxiliares (`isValidOrder`, `updateTotalsByStatus`, `updateCountByUser`)
- Mejorar nombres de variables y legibilidad
- Mantener el mismo comportamiento funcional

## 📋 Dependencias

- TypeScript 5.5+
- Jest para testing
- No dependencias externas de runtime
