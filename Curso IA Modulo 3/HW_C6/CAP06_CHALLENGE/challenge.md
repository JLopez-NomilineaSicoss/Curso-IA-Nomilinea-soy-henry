# Challenge de Testing con AI.

## Parte 1

El objetivo de esta parte del challenge es escribir pruebas unitarias completas y detalladas para una función de Python llamada `es_primo`. Esta función determina si un número dado es primo o no.

La función `es_primo` proporcionada tiene una implementación básica y puede no manejar correctamente todos los casos de uso. Deberás escribir pruebas unitarias que cubran tanto los happy paths como los edge cases. A medida que desarrollas estas pruebas, descubrirás deficiencias en la función que deberán ser corregidas en etapas posteriores del curso.

### Especificación de la Función

La función `es_primo` se define de la siguiente manera:

```python
def es_primo(num):
    for i in range(2, num):
        if num % i == 0:
            return False
    return True
```

### Tareas

1. **Entender la Función**: Revisa y comprende cómo funciona la función `es_primo`. Identifica qué casos están siendo cubiertos adecuadamente y qué casos podrían estar faltando.

2. **Escribir Pruebas Unitarias**:
   - **Happy Paths**: Incluye pruebas para números que son claramente primos (como 2, 3, 5, 11, etc.) y números que no son primos (como 1, 4, 6, 8, etc.).
   - **Edge Cases**:
     - Prueba la función con el número 0 y números negativos.
     - Prueba con tipos de datos no enteros, como flotantes y strings.
     - Considera el rendimiento de la función con números extremadamente grandes.
     - Evalúa cómo la función maneja inputs inusuales, como `None` o datos de tipo booleano.

### Requerimientos para la Función \`es_primo\`

1 **Validación de Números Primos Conocidos**:
   - La función debe identificar correctamente como primos los siguientes números: 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31.

2. **Validación de Números No Primos Conocidos**:
   - La función debe identificar correctamente como no primos los siguientes números: 0, 1, 4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20.

3. **Manejo de Números Negativos**:
   - La función debe determinar que todos los números negativos no son primos. Esto incluye los números -1, -2, -3, -5, -11, -13.

4. **Eficiencia con Números Grandes**:
   - La función debe ser capaz de evaluar eficientemente la primalidad de números grandes, y determinar que 1000003 es primo y que 1000004 no es primo.

5. **Manejo de Entradas No Enteras**:
   - La función debe lanzar un error de tipo (`TypeError`) cuando se le pasan valores que no son enteros numéricos, como 2.3, 3.9, "tres", `None`, `True`, y `False`.

6. **Manejo de Inputs Inusuales**:
   - La función debe lanzar un error de tipo (`TypeError`) cuando se enfrenta a entradas inusuales como la cadena `"cinco"`, `None`, y listas vacías (`[]`).

7. **Precisión en Punto Flotante**:
   - La función debe ser capaz de manejar y aprobar como primos números de punto flotante que están extremadamente cerca de números primos enteros, como `19.000000000000004` y `23.000000000000004`, reconociendo su primalidad.



### Estructura de Parte 1

El ejercicio consta de dos componentes principales dentro del directorio `parte1/`:

1. **func.py**: Este archivo contiene la implementación base de la función `es_primo` que ustedes, los estudiantes, deberán evaluar, iterar y mejorar a través de pruebas unitarias.

2. **reference_test.py**: Este archivo contiene un conjunto de pruebas de referencia que nosotros, como organizadores, utilizaremos para evaluar la función `es_primo`. Este archivo no debe ser modificado por los estudiantes. Al ejecutar este archivo con `pytest`, se muestra que 12 pruebas fallan y 28 pasan, indicando las áreas de mejora necesarias para la función.

3. **func_test.py**: Este es el archivo en el que deberán escribir sus pruebas unitarias. Su objetivo es cubrir tanto los casos esperados como los edge cases para asegurarse de que la función `es_primo` funcione correctamente bajo diversas condiciones.

### Instrucciones para las Pruebas Unitarias

- **Cobertura de Casos**: Deben asegurarse de escribir pruebas que cubran una amplia gama de casos, desde los más simples hasta los más complejos y poco comunes.
  
- **Identificación de Defectos**: Sus pruebas deberían poder identificar las deficiencias que hacen que las pruebas en `reference_test.py` fallen.


Para ejecutar sus pruebas, naveguen a la carpeta del proyecto y utilicen los siguientes comandos en la terminal:
#### Ejecuta tu función
```bash
pytest parte1/func_test.py
```


#### Pruebas a desarrollar
```bash
pytest parte1/func_test.py
```

#### Pruebas de referencia
```bash
pytest parte1/reference_test.py
```
