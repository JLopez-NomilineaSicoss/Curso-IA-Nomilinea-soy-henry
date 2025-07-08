# Task Manager API

## Español

### Descripción general
Esta es una API para la gestión de tareas construida con FastAPI. Permite crear, consultar, actualizar y eliminar tareas, así como eliminar todas las tareas de la base de datos. Incluye autenticación básica, logging, manejo de errores personalizado y pruebas automatizadas.

### Estructura del proyecto
```
CAP02_CHALLENGE/
├── app/
│   ├── main.py              # Punto de entrada de la app
│   ├── db.py                # Base de datos simulada en memoria
│   ├── models.py            # Modelos de datos (Pydantic)
│   ├── routers/
│   │   └── tasks_router.py  # Endpoints de tareas
│   ├── test_validation.py   # Pruebas de validación
│   ├── test_auth.py         # Pruebas de autenticación
│   ├── test_errors.py       # Pruebas de manejo de errores
│   ├── test_crud.py         # Pruebas CRUD
│   └── README.md            # Este archivo
├── challenge.md             # Historial de cambios y consignas
```

### Instalación y ejecución
1. Crea y activa el entorno virtual:
   ```
   python -m venv venv
   # En Windows
   .\venv\Scripts\activate
   # En Unix/Mac
   source venv/bin/activate
   ```
2. Instala las dependencias:
   ```
   pip install -r app/requirements.txt
   ```
3. Ejecuta la aplicación desde la carpeta CAP02_CHALLENGE:
   ```
   uvicorn app.main:app --reload
   ```

### Pruebas automatizadas
Para ejecutar las pruebas, asegúrate de estar en la carpeta CAP02_CHALLENGE y usa:
```
$env:PYTHONPATH = (Get-Location).Path; pytest app/test_nombre.py
```
Reemplaza `test_nombre.py` por el archivo de pruebas que desees ejecutar.

### Endpoints principales
- `GET /tasks/` - Lista todas las tareas
- `POST /tasks/` - Crea una nueva tarea
- `GET /tasks/{task_id}` - Consulta una tarea por ID
- `PUT /tasks/{task_id}` - Actualiza una tarea
- `DELETE /tasks/{task_id}` - Elimina una tarea (requiere autenticación básica)
- `DELETE /tasks/` - Elimina todas las tareas (requiere autenticación básica)

### Autenticación
Para eliminar tareas (individual o todas), debes usar autenticación básica:
- Usuario: `admin`
- Contraseña: `admin123`

### Logging
Todas las operaciones importantes y errores se registran en consola y en el archivo `app/app.log`.

### Manejo de errores
- Si una tarea no existe, la API responde con un mensaje personalizado y código 404.
- Otros errores se manejan con respuestas claras y uniformes.

---

# English

### General description
This is a task management API built with FastAPI. It allows you to create, retrieve, update, and delete tasks, as well as delete all tasks from the database. It includes basic authentication, logging, custom error handling, and automated tests.

### Project structure
```
CAP02_CHALLENGE/
├── app/
│   ├── main.py              # App entry point
│   ├── db.py                # In-memory fake database
│   ├── models.py            # Data models (Pydantic)
│   ├── routers/
│   │   └── tasks_router.py  # Task endpoints
│   ├── test_validation.py   # Validation tests
│   ├── test_auth.py         # Auth tests
│   ├── test_errors.py       # Error handling tests
│   ├── test_crud.py         # CRUD tests
│   └── README.md            # This file
├── challenge.md             # Change log and instructions
```

### Installation and running
1. Create and activate the virtual environment:
   ```
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On Unix/Mac
   source venv/bin/activate
   ```
2. Install dependencies:
   ```
   pip install -r app/requirements.txt
   ```
3. Run the app from the CAP02_CHALLENGE folder:
   ```
   uvicorn app.main:app --reload
   ```

### Automated tests
To run the tests, make sure you are in the CAP02_CHALLENGE folder and use:
```
$env:PYTHONPATH = (Get-Location).Path; pytest app/test_name.py
```
Replace `test_name.py` with the test file you want to run.

### Main endpoints
- `GET /tasks/` - List all tasks
- `POST /tasks/` - Create a new task
- `GET /tasks/{task_id}` - Get a task by ID
- `PUT /tasks/{task_id}` - Update a task
- `DELETE /tasks/{task_id}` - Delete a task (requires basic auth)
- `DELETE /tasks/` - Delete all tasks (requires basic auth)

### Authentication
To delete tasks (single or all), you must use basic authentication:
- User: `admin`
- Password: `admin123`

### Logging
All important operations and errors are logged to the console and to the file `app/app.log`.

### Error handling
- If a task does not exist, the API responds with a custom message and 404 code.
- Other errors are handled with clear and uniform responses.