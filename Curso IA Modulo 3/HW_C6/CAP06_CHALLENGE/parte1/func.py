def es_primo(num):
    # Validación de tipos - excluir booleanos específicamente
    if isinstance(num, bool):
        raise TypeError(f"Se esperaba un entero, se recibió {type(num).__name__}")
    
    # Manejo de números de punto flotante
    if isinstance(num, float):
        # Verificar si el flotante está extremadamente cerca de un entero
        if abs(num - round(num)) < 1e-10:
            num = round(num)
        else:
            raise TypeError(f"Se esperaba un entero, se recibió {type(num).__name__}")
    
    # Validación final para enteros
    if not isinstance(num, int):
        raise TypeError(f"Se esperaba un entero, se recibió {type(num).__name__}")
    
    # Manejo de casos especiales
    if num < 2:
        return False
    
    # Verificar divisibilidad desde 2 hasta la raíz cuadrada del número
    for i in range(2, int(num ** 0.5) + 1):
        if num % i == 0:
            return False
    return True


if __name__ == "__main__":
    print(es_primo(5))
