from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.routers.tasks_router import tasks_router, TaskNotFoundException
import logging
from app.models import Task, UpdateTaskModel, TaskList
from app.db import db

app = FastAPI()

app.include_router(tasks_router, prefix="/tasks", tags=["tasks"])

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log', encoding='utf-8')
    ]
)
logger = logging.getLogger("task_manager")

@app.get("/")
async def root():
    logger.info("Acceso a la ruta raíz /")
    return {"message": "Task Manager API"}

@app.exception_handler(TaskNotFoundException)
async def task_not_found_exception_handler(request: Request, exc: TaskNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"detail": "La tarea no fue encontrada"}
    )
