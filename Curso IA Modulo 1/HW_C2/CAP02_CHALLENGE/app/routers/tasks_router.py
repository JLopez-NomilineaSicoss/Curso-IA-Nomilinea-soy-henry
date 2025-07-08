from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.models import Task, UpdateTaskModel, TaskList
from app.db import db
import secrets
import logging

tasks_router = APIRouter()

security = HTTPBasic()

USERNAME = "admin"
PASSWORD = "admin123"

logger = logging.getLogger("task_manager")

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, USERNAME)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials


@tasks_router.post("/", response_model=Task)
async def create_task(task: Task):
    """
    Crea una nueva tarea y la agrega a la base de datos.
    Args:
        task (Task): Objeto con los datos de la tarea a crear.
    Returns:
        Task: La tarea creada con su ID asignado.
    """
    logger.info(f"Creando tarea: {task.title}")
    return db.add_task(task)


class TaskNotFoundException(Exception):
    pass


@tasks_router.get("/{task_id}", response_model=Task)
async def get_task(task_id: int):
    """
    Obtiene una tarea específica por su ID.
    Args:
        task_id (int): ID de la tarea a buscar.
    Returns:
        Task: La tarea encontrada.
    Raises:
        TaskNotFoundException: Si la tarea no existe.
    """
    logger.info(f"Consultando tarea con ID: {task_id}")
    task = db.get_task(task_id)
    if task is None:
        logger.warning(f"Tarea con ID {task_id} no encontrada")
        raise TaskNotFoundException()
    return task


@tasks_router.get("/", response_model=TaskList)
async def get_tasks():
    """
    Obtiene la lista de todas las tareas almacenadas en la base de datos.
    Returns:
        TaskList: Lista de todas las tareas.
    """
    logger.info("Consultando todas las tareas")
    tasks = db.get_tasks()
    return TaskList(tasks=tasks)


@tasks_router.put("/{task_id}", response_model=Task)
async def update_task(task_id: int, task_update: UpdateTaskModel):
    """
    Actualiza los datos de una tarea existente.
    Args:
        task_id (int): ID de la tarea a actualizar.
        task_update (UpdateTaskModel): Datos nuevos para la tarea.
    Returns:
        Task: La tarea actualizada.
    Raises:
        TaskNotFoundException: Si la tarea no existe.
    """
    logger.info(f"Actualizando tarea con ID: {task_id}")
    updated_task = db.update_task(task_id, task_update)
    if updated_task is None:
        logger.warning(f"Tarea con ID {task_id} no encontrada para actualizar")
        raise TaskNotFoundException()
    return updated_task


@tasks_router.delete("/{task_id}")
async def delete_task(task_id: int, credentials: HTTPBasicCredentials = Depends(authenticate)):
    """
    Elimina una tarea específica por su ID.
    Args:
        task_id (int): ID de la tarea a eliminar.
    Returns:
        dict: Mensaje de confirmación.
    Raises:
        TaskNotFoundException: Si la tarea no existe.
    """
    logger.info(f"Eliminando tarea con ID: {task_id}")
    task = db.get_task(task_id)
    if task is None:
        logger.warning(f"Tarea con ID {task_id} no encontrada para eliminar")
        raise TaskNotFoundException()
    db.delete_task(task_id)
    return {"message": "Task deleted successfully"}


@tasks_router.delete("/")
async def delete_all_tasks(credentials: HTTPBasicCredentials = Depends(authenticate)):
    """
    Elimina todas las tareas de la base de datos.
    Returns:
        dict: Mensaje de confirmación.
    """
    logger.info("Eliminando todas las tareas")
    db.delete_all_tasks()
    return {"message": "All tasks deleted"}
