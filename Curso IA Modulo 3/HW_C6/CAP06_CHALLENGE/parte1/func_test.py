import pytest
import subprocess
import sys
import os

from func import es_primo


# Sección 1: Pruebas para números 0, 1 y negativos
class TestNumerosEspeciales:
    """Pruebas para el manejo de números especiales (0, 1, negativos)"""
    
    def test_numero_cero(self):
        """El número 0 no debería ser considerado primo"""
        assert es_primo(0) == False, "El número 0 no debería ser primo"
    
    def test_numero_uno(self):
        """El número 1 no debería ser considerado primo"""
        assert es_primo(1) == False, "El número 1 no debería ser primo"
    
    @pytest.mark.parametrize("num", [-1, -2, -3, -5, -11, -13])
    def test_numeros_negativos(self, num):
        """Los números negativos no deberían ser considerados primos"""
        assert es_primo(num) == False, f"El número {num} no debería ser primo"
    
    def test_numeros_negativos_grandes(self):
        """Números negativos grandes no deberían ser primos"""
        assert es_primo(-1000003) == False, "El número -1000003 no debería ser primo"


# Sección 2: Pruebas para validación de tipos
class TestValidacionTipos:
    """Pruebas para la validación de tipos de entrada"""
    
    def test_booleanos_true(self):
        """True debería lanzar TypeError"""
        with pytest.raises(TypeError):
            es_primo(True)
    
    def test_booleanos_false(self):
        """False debería lanzar TypeError"""
        with pytest.raises(TypeError):
            es_primo(False)
    
    def test_strings(self):
        """Strings deberían lanzar TypeError"""
        with pytest.raises(TypeError):
            es_primo("tres")
        with pytest.raises(TypeError):
            es_primo("cinco")
    
    def test_none(self):
        """None debería lanzar TypeError"""
        with pytest.raises(TypeError):
            es_primo(None)
    
    def test_lista_vacia(self):
        """Lista vacía debería lanzar TypeError"""
        with pytest.raises(TypeError):
            es_primo([])
    
    def test_flotantes(self):
        """Números flotantes deberían lanzar TypeError"""
        with pytest.raises(TypeError):
            es_primo(2.3)
        with pytest.raises(TypeError):
            es_primo(3.9)


# Sección 3: Pruebas para números de punto flotante cercanos a primos
class TestNumerosPuntoFlotante:
    """Pruebas para el manejo de números de punto flotante cercanos a primos"""
    
    def test_flotantes_cercanos_a_primos(self):
        """Números flotantes extremadamente cercanos a primos deberían ser reconocidos como primos"""
        assert es_primo(19.000000000000004) == True, "19.000000000000004 debería ser reconocido como primo"
        assert es_primo(23.000000000000004) == True, "23.000000000000004 debería ser reconocido como primo"
    
    def test_flotantes_cercanos_a_no_primos(self):
        """Números flotantes cercanos a no primos deberían ser reconocidos como no primos"""
        assert es_primo(4.000000000000001) == False, "4.000000000000001 debería ser reconocido como no primo"
        assert es_primo(6.000000000000001) == False, "6.000000000000001 debería ser reconocido como no primo"
    
    def test_flotantes_con_precision_estandar(self):
        """Números flotantes con precisión estándar deberían ser manejados correctamente"""
        assert es_primo(7.0) == True, "7.0 debería ser reconocido como primo"
        assert es_primo(8.0) == False, "8.0 debería ser reconocido como no primo"


# Sección 4: Pruebas unitarias completas y adicionales
class TestNumerosPrimosConocidos:
    """Pruebas para números primos conocidos según las especificaciones"""
    
    @pytest.mark.parametrize("num", [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31])
    def test_numeros_primos_conocidos(self, num):
        """Números primos conocidos deberían ser identificados correctamente"""
        assert es_primo(num) == True, f"El número {num} debería ser identificado como primo"


class TestNumerosNoPrimosConocidos:
    """Pruebas para números no primos conocidos según las especificaciones"""
    
    @pytest.mark.parametrize("num", [0, 1, 4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20])
    def test_numeros_no_primos_conocidos(self, num):
        """Números no primos conocidos deberían ser identificados correctamente"""
        assert es_primo(num) == False, f"El número {num} no debería ser identificado como primo"


class TestEficienciaNumerosGrandes:
    """Pruebas para verificar la eficiencia con números grandes"""
    
    def test_numeros_grandes_primos(self):
        """Números grandes que son primos deberían ser identificados correctamente"""
        assert es_primo(1000003) == True, "1000003 debería ser identificado como primo"
    
    def test_numeros_grandes_no_primos(self):
        """Números grandes que no son primos deberían ser identificados correctamente"""
        assert es_primo(1000004) == False, "1000004 no debería ser identificado como primo"


class TestCasosEdgeAdicionales:
    """Pruebas para casos edge adicionales no cubiertos anteriormente"""
    
    def test_numeros_muy_grandes(self):
        """Números muy grandes deberían ser manejados eficientemente"""
        # 1000000007 es un número primo conocido
        assert es_primo(1000000007) == True, "1000000007 debería ser identificado como primo"
    
    def test_numeros_cuadrados_perfectos(self):
        """Números que son cuadrados perfectos no deberían ser primos"""
        assert es_primo(25) == False, "25 (5²) no debería ser identificado como primo"
        assert es_primo(49) == False, "49 (7²) no debería ser identificado como primo"
        assert es_primo(121) == False, "121 (11²) no debería ser identificado como primo"
    
    def test_numeros_compuestos_pequeños(self):
        """Números compuestos pequeños deberían ser identificados correctamente"""
        assert es_primo(21) == False, "21 (3×7) no debería ser identificado como primo"
        assert es_primo(33) == False, "33 (3×11) no debería ser identificado como primo"
        assert es_primo(35) == False, "35 (5×7) no debería ser identificado como primo"
    
    def test_primos_gemelos(self):
        """Números primos gemelos deberían ser identificados correctamente"""
        assert es_primo(17) == True, "17 debería ser identificado como primo"
        assert es_primo(19) == True, "19 debería ser identificado como primo"
        assert es_primo(29) == True, "29 debería ser identificado como primo"
        assert es_primo(31) == True, "31 debería ser identificado como primo"


# Sección 5: Pruebas para cobertura completa
class TestCoberturaCompleta:
    """Pruebas para alcanzar 100% de cobertura de código"""
    
    def test_main_block_execution(self):
        """Prueba la ejecución del bloque if __name__ == '__main__'"""
        # Ejecutar el archivo func.py directamente para cubrir el bloque main
        result = subprocess.run([sys.executable, 'parte1/func.py'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        assert result.returncode == 0, "La ejecución del archivo func.py debería ser exitosa"
        assert "True" in result.stdout, "La salida debería contener 'True' para es_primo(5)"
