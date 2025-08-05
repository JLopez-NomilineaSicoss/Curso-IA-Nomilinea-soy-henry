import pytest

from solucion import es_primo


# Test para números primos conocidos
@pytest.mark.parametrize("num", [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31])
def test_numeros_primos(num):
    assert es_primo(num) == True, f"Error: {num} debería ser primo"


# Test para números no primos conocidos
@pytest.mark.parametrize("num", [0, 1, 4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20])
def test_numeros_no_primos(num):
    assert es_primo(num) == False, f"Error: {num} no debería ser primo"


# Test para números negativos (todos deberían ser no primos)
@pytest.mark.parametrize("num", [-1, -2, -3, -5, -11, -13])
def test_numeros_negativos(num):
    assert es_primo(num) == False, f"Error: {num} no debería ser primo"


# Test para verificar la eficiencia con números grandes
def test_numeros_grandes():
    assert es_primo(1000003) == True, "Error: 1000003 debería ser primo"
    assert es_primo(1000004) == False, "Error: 1000004 no debería ser primo"


# Test para entradas no enteras
@pytest.mark.parametrize("num", [2.3, 3.9, "tres", None, True, False])
def test_entradas_no_enteras(num):
    with pytest.raises(TypeError):
        es_primo(num)


# Test para verificar el manejo de inputs inusuales
def test_inputs_inusuales():
    with pytest.raises(TypeError):
        es_primo("cinco")
    with pytest.raises(TypeError):
        es_primo(None)
    with pytest.raises(TypeError):
        es_primo([])


@pytest.mark.parametrize(
    "num, expected",
    [
        (19.000000000000004, True),
        (23.000000000000004, True),
    ],
)
def test_numeros_punto_flotante(num, expected):
    assert (
        es_primo(num) == expected
    ), f"Error: {num} (punto flotante) falló en devolver {expected}"
