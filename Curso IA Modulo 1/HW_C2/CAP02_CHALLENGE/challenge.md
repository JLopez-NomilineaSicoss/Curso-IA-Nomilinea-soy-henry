El siguiente challenge está diseñado para que aprendas a enfrentarte a un repositorio relativamente grande por primera vez, con la ayuda de un asistente como Cody.

## Explora
1. Crea un nuevo Chat con Cody.
2. Haciendo referencia al main.py dentro de /app, preguntale de qué trata el aplicativo.
* ejemplo : 
`@CAP02_CHALLENGE/path/to/file Que hace esta app?`
### Haciendo uso de Cody, encuentra las respuestas a:
- 3.1 Que hace el archivo tasks_router.py?
- 3.2 Cual és son los diferentes endpoints y que hacen?
- 3.3 Como esta construida la base de datos?
- 3.4 Como se inicializa el aplicativo?

## Extiende
1. Añade un nuevo endpoint al aplicativo que permita eliminar TODOS los registros de db.
2. Documenta el modulo `app/routers/tasks_router.py`

## Corrige
1. Encuentra 5 mejoras potenciales haciendo uso del comando "Code Smells" sobre `app/routers/tasks_router.py`
2. Implementa alguna de las mejoras propuestas por Cody AI.

## Cambios Actividad

- Se agregó un endpoint DELETE /tasks/ que elimina todos los registros de la base de datos simulada.
- Se documentaron todas las funciones del archivo app/routers/tasks_router.py con docstrings explicativos.
- Se crearon pruebas unitarias en test_validation.py para validar la entrada de datos en los endpoints de tareas (campos obligatorios, tipos de datos, IDs válidos).
- Todas las pruebas de validación de entradas pasaron correctamente (5/5).
- Se implementó autenticación básica (HTTP Basic Auth) en los endpoints DELETE (eliminar tarea y eliminar todas las tareas) para proteger operaciones críticas.
- Se crearon pruebas unitarias en test_auth.py para verificar el acceso a los endpoints protegidos (sin auth, con auth incorrecta y con auth correcta).
- Todas las pruebas de autenticación pasaron correctamente (5/5).
- Se implementó una excepción personalizada (TaskNotFoundException) y un manejador global de errores en FastAPI para devolver mensajes uniformes cuando una tarea no es encontrada.
- Se crearon pruebas unitarias en test_errors.py para verificar el manejo de errores personalizados en los endpoints de tareas.
- Todas las pruebas de manejo de errores pasaron correctamente (3/3).
- Se implementó logging para registrar operaciones clave y errores tanto en consola como en el archivo app.log.
- Se verificó manualmente que los logs se generan correctamente al interactuar con los endpoints.
- Se crearon pruebas unitarias en app/test_crud.py para cubrir los endpoints de listar, crear y actualizar tareas (CRUD básico).
- Para ejecutar correctamente las pruebas, se debe establecer el PYTHONPATH: $env:PYTHONPATH = (Get-Location).Path; pytest app/test_crud.py
- Todas las pruebas CRUD pasaron correctamente (3/3).
- Se amplió y mejoró la documentación técnica en app/README.md, incluyendo secciones completas en español e inglés con descripción del proyecto, estructura, endpoints, autenticación, logging, manejo de errores y pruebas.
