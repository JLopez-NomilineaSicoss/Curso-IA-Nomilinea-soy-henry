# Homework — Construcción asistida de pruebas y mejoras de código con Cursor IDE

Proyecto mínimo en TypeScript para practicar **tests con IA**, **refactor de code smells** y **documentación**.

## Requisitos
- Node.js 18+
- npm
- Cursor IDE instalado (o cualquier IDE con soporte de TypeScript/Jest)

## Instalación
```bash
npm i
```

## Comandos
```bash
npm run test       # Ejecuta los tests
npm run test:cov   # Ejecuta los tests con cobertura
npm run build      # Compila a ./dist
```

## Estructura
```
src/
  index.ts
  lib/
    price.ts        # calculateFinal() + JSDoc
    orders.ts       # groupOrdersReport() (implementación "smelly" para refactor)
    README.md
tests/
  price.test.ts     # Jest (AAA, nombres descriptivos)
jest.config.ts
tsconfig.json
package.json
```

## Objetivos del ejercicio
1) **Tests (price.ts):** Cubre IVA por defecto, descuento, decimales y errores de parámetros. Patrón AAA. Meta: cobertura ≥90% en `price.ts`.
2) **Refactor (orders.ts):** Pide a Cursor diagnóstico y refactor para `groupOrdersReport()` (extrae funciones, reduce complejidad < 10, mantiene comportamiento).
3) **Documentación:** JSDoc en ambas funciones + README en `src/lib` (incluido).

> Sugerencias de prompts: ver el enunciado original o reutilizar los prompts incluidos en tu consigna.
