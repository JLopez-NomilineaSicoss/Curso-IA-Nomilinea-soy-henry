# Homework — Construcción asistida de pruebas y mejoras de código con Cursor IDE

## 🎯 Objetivo
Poner en práctica **Cursor** para:
- Generar pruebas.
- Refactorizar código con *code smells*.
- Documentar en contexto.
- Mantener el control técnico sobre cada cambio.

---

## 📌 Qué vas a trabajar
Usaremos un proyecto mínimo en **TypeScript** con funciones sencillas pero ideales para ejercitar IA en el IDE:

- `calculateFinal(total, iva, discount)` → (precio final).
- `groupOrdersReport(orders)` → (función larga con duplicación y nombres poco claros).

**Descarga el repo starter:** 📦 `cursor_homework_starter.zip`  
**Requisitos:** Node 18+, Cursor IDE instalado.  
**Comandos:**  
```bash
npm i
npm run test
npm run test:cov
````

---

## 📝 Tareas (obligatorias)

### 1. Pruebas unitarias con IA (`price.ts`)

* Pídele a Cursor que genere tests para `calculateFinal`.
* Casos:

  * IVA por defecto.
  * Con descuento.
  * Manejo de decimales.
  * Errores por parámetros inválidos.
* Usa **patrón AAA** y nombres descriptivos.
* **Meta:** cobertura ≥ 90% en `price.ts` y ≥ 70% global.

---

### 2. Refactor seguro (`orders.ts`)

* Solicita diagnóstico de *code smells* y refactor de `groupOrdersReport`.
* Pide:

  * Reducir complejidad `< 10`.
  * Extraer funciones.
  * Mejorar nombres.
* No cambies el comportamiento.
* Valida corriendo los tests.

---

### 3. Documentación

* Agrega **JSDoc** a `calculateFinal` y `groupOrdersReport`.
* Crea/actualiza un **README** en `src/lib` con:

  * Propósito.
  * Ejemplo de uso.
  * Limitaciones.

---

## 💡 Sugerencias de Prompts (para usar en Cursor)

### Tests

```
Genera tests para src/lib/price.ts (función calculateFinal). 
Cubre IVA por defecto, descuento, manejo de decimales y errores por parámetros inválidos. 
Usa Jest con patrón AAA y nombres descriptivos. 
Objetivo: cobertura ≥90% en price.ts.
```

### Smells + Refactor

```
Analiza src/lib/orders.ts y sugiere refactor para groupOrdersReport(): 
extrae funciones, reduce complejidad <10, usa nombres claros y mantiene el mismo comportamiento. 
Dame el diff propuesto.
```

### Documentación

```
Agrega JSDoc a calculateFinal y groupOrdersReport (descripción breve, params, return, ejemplo). 
Genera un README para src/lib con propósito, ejemplo de uso y limitaciones (Markdown).
```

---

## 📦 ¿Qué debes preparar al finalizar?
No es necesario entregar esta homework, pero te invitamos a preparar los siguientes elementos para cerrar el ejercicio con una buena práctica profesional:

* Proyecto actualizado (en GitHub o en .zip)
* Captura de pantalla del reporte de cobertura después de tus cambios.
* Archivo README en src/lib/ con la documentación del módulo.
* 1–2 commits con mensajes claros (idealmente usando *Conventional Commits*).

