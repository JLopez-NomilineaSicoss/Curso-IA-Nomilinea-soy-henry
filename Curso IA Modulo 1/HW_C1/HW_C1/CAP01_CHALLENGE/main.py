from fastapi import FastAPI, HTTPException, Depends, Request
from typing import List, Optional
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt
from fastapi import status
from fastapi.responses import JSONResponse

fake_db = {"users": {}}

app = FastAPI()

# =====================
# Modelos de datos
# =====================

class Payload(BaseModel):
    """
    Modelo para recibir una lista de números en los endpoints de lógica.
    Ejemplo: {"numbers": [1, 2, 3]}
    """
    numbers: List[int]

class BinarySearchPayload(BaseModel):
    """
    Modelo para búsqueda binaria: lista de números y el objetivo a buscar.
    Ejemplo: {"numbers": [1, 2, 3], "target": 2}
    """
    numbers: List[int]
    target: int

class UserRegister(BaseModel):
    """
    Modelo para el registro de usuario.
    """
    username: str
    password: str

class UserLogin(BaseModel):
    """
    Modelo para el login de usuario.
    """
    username: str
    password: str

# =====================
# Utilidades de seguridad y autenticación
# =====================

# Contexto de cifrado para contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Clave secreta para JWT (en producción debe ser más segura y estar oculta)
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"

def get_password_hash(password: str) -> str:
    """
    Genera el hash de una contraseña usando bcrypt.
    Args:
        password (str): Contraseña en texto plano.
    Returns:
        str: Contraseña cifrada.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si la contraseña proporcionada coincide con el hash almacenado.
    Args:
        plain_password (str): Contraseña en texto plano.
        hashed_password (str): Contraseña cifrada.
    Returns:
        bool: True si coinciden, False si no.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """
    Genera un token JWT con los datos proporcionados.
    Args:
        data (dict): Información a codificar en el token.
    Returns:
        str: Token JWT.
    """
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    """
    Decodifica y verifica el token JWT.
    Args:
        token (str): Token JWT recibido.
    Returns:
        str: Nombre de usuario extraído del token.
    Raises:
        HTTPException: Si el token es inválido o expirado.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

async def get_current_user(request: Request, token: Optional[str] = None):
    """
    Dependencia para obtener el usuario autenticado a partir del token JWT.
    El token debe recibirse como parámetro de consulta (?token=).
    Args:
        request (Request): Objeto de la petición para extraer el token si no se pasa directamente.
        token (str): Token JWT recibido como parámetro de consulta.
    Returns:
        str: Nombre de usuario autenticado.
    Raises:
        HTTPException: Si el token no está presente o es inválido.
    """
    if token is None:
        token = request.query_params.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="Token requerido")
    return verify_token(token)

# =====================
# Endpoints de autenticación
# =====================

@app.post("/register")
def register(user: UserRegister):
    """
    Registra un nuevo usuario en la base de datos simulada.
    Args:
        user (UserRegister): Datos del usuario a registrar.
    Returns:
        dict: Mensaje de éxito o error.
    """
    if user.username in fake_db["users"]:
        return JSONResponse(status_code=400, content={"message": "El usuario ya existe"})
    hashed_password = get_password_hash(user.password)
    fake_db["users"][user.username] = {"password": hashed_password}
    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: UserLogin):
    """
    Inicia sesión y devuelve un token JWT si las credenciales son válidas.
    Args:
        user (UserLogin): Datos de acceso del usuario.
    Returns:
        dict: Token de acceso o mensaje de error.
    """
    db_user = fake_db["users"].get(user.username)
    if not db_user or not verify_password(user.password, db_user["password"]):
        return JSONResponse(status_code=401, content={"message": "Credenciales Inválidas"})
    token = create_access_token({"sub": user.username})
    return {"access_token": token}

# =====================
# Endpoints de lógica de listas (protegidos)
# =====================

@app.post("/bubble-sort")
async def bubble_sort(payload: Payload, user: str = Depends(get_current_user)):
    """
    Ordena una lista de números usando el algoritmo Bubble Sort.
    Args:
        payload (Payload): Lista de números a ordenar.
        user (str): Usuario autenticado (obtenido por dependencia).
    Returns:
        dict: Lista ordenada.
    """
    numbers = payload.numbers.copy()
    n = len(numbers)
    for i in range(n):
        for j in range(0, n - i - 1):
            if numbers[j] > numbers[j + 1]:
                numbers[j], numbers[j + 1] = numbers[j + 1], numbers[j]
    return {"numbers": numbers}

@app.post("/filter-even")
async def filter_even(
    payload: Payload,
    user: str = Depends(get_current_user),
    page: int = 1,
    size: int = 10
):
    """
    Filtra y devuelve solo los números pares de la lista, con paginación opcional.
    Args:
        payload (Payload): Lista de números.
        user (str): Usuario autenticado.
        page (int, opcional): Número de página (por defecto 1).
        size (int, opcional): Tamaño de página (por defecto 10).
    Returns:
        dict: Lista de números pares paginada.
    """
    even_numbers = [num for num in payload.numbers if num % 2 == 0]
    start = (page - 1) * size
    end = start + size
    paginated = even_numbers[start:end]
    return {
        "even_numbers": paginated,
        "page": page,
        "size": size,
        "total": len(even_numbers)
    }

@app.post("/sum-elements")
async def sum_elements(payload: Payload, user: str = Depends(get_current_user)):
    """
    Devuelve la suma de los elementos de la lista.
    Args:
        payload (Payload): Lista de números.
        user (str): Usuario autenticado.
    Returns:
        dict: Suma de los números.
    """
    total = sum(payload.numbers)
    return {"sum": total}

@app.post("/max-value")
async def max_value(payload: Payload, user: str = Depends(get_current_user)):
    """
    Devuelve el valor máximo de la lista.
    Args:
        payload (Payload): Lista de números.
        user (str): Usuario autenticado.
    Returns:
        dict: Valor máximo.
    """
    if not payload.numbers:
        return JSONResponse(status_code=400, content={"message": "La lista no puede estar vacía"})
    max_num = max(payload.numbers)
    return {"max": max_num}

@app.post("/binary-search")
async def binary_search(payload: BinarySearchPayload, user: str = Depends(get_current_user)):
    """
    Realiza una búsqueda binaria en una lista ordenada.
    Args:
        payload (BinarySearchPayload): Lista ordenada y valor objetivo.
        user (str): Usuario autenticado.
    Returns:
        dict: Indica si se encontró el valor y su índice.
    """
    numbers = payload.numbers
    target = payload.target
    left, right = 0, len(numbers) - 1
    while left <= right:
        mid = (left + right) // 2
        if numbers[mid] == target:
            return {"found": True, "index": mid}
        elif numbers[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return {"found": False, "index": -1}

@app.post("/average")
async def average(payload: Payload, user: str = Depends(get_current_user)):
    """
    Calcula el promedio de los elementos de la lista.
    Args:
        payload (Payload): Lista de números.
        user (str): Usuario autenticado.
    Returns:
        dict: Promedio de los números.
    """
    if not payload.numbers:
        return JSONResponse(status_code=400, content={"message": "La lista no puede estar vacía"})
    avg = sum(payload.numbers) / len(payload.numbers)
    return {"average": avg}

@app.post("/quick-sort")
async def quick_sort(payload: Payload, user: str = Depends(get_current_user)):
    """
    Ordena una lista de números usando el algoritmo Quick Sort.
    Args:
        payload (Payload): Lista de números a ordenar.
        user (str): Usuario autenticado.
    Returns:
        dict: Lista ordenada.
    """
    def quicksort(arr):
        if len(arr) <= 1:
            return arr
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        return quicksort(left) + middle + quicksort(right)
    sorted_numbers = quicksort(payload.numbers)
    return {"numbers": sorted_numbers}
