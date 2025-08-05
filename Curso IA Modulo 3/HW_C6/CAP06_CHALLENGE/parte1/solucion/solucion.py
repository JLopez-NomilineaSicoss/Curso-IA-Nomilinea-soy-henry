def es_primo(num):
    if isinstance(num, bool):
        raise TypeError("El input no debe ser un valor booleano.")

    if not isinstance(num, (int, float)):
        raise TypeError("El input debe ser un número entero.")

    if isinstance(num, float):
        if abs(num - round(num)) < 1e-9:
            num = round(num)
        else:
            raise TypeError("El input debe ser un número entero.")

    num = int(num)

    if num < 2:
        return False
    if num < 4:
        return True
    if num % 2 == 0 or num % 3 == 0:
        return False
    i = 5
    while i * i <= num:
        if num % i == 0 or num % (i + 2) == 0:
            return False
        i += 6
    return True
