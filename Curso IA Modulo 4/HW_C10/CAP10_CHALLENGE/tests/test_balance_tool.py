import unittest
import pandas as pd
import sys
import os

# Agregar el directorio padre al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution.main import get_balance_by_id


class TestBalanceTool(unittest.TestCase):
    """Pruebas para la herramienta de consulta de balances"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        # Crear un archivo CSV de prueba
        self.test_data = {
            'ID_Cedula': ['V-12345678', 'V-87654321', 'V-91827364'],
            'Nombre': ['Juan Pérez', 'María Gómez', 'Luis Méndez'],
            'Balance': [1250.5, 6820.75, 2580.0]
        }
        self.test_df = pd.DataFrame(self.test_data)
        self.test_csv_path = "test_saldos.csv"
        self.test_df.to_csv(self.test_csv_path, index=False)
        
        # Guardar el archivo CSV original para restaurarlo después
        self.original_csv_exists = os.path.exists("./saldos.csv")
        if self.original_csv_exists:
            os.rename("./saldos.csv", "./saldos_backup.csv")
        
        # Copiar el archivo de prueba
        self.test_df.to_csv("./saldos.csv", index=False)
    
    def tearDown(self):
        """Limpieza después de las pruebas"""
        # Restaurar el archivo original
        if os.path.exists("./saldos.csv"):
            os.remove("./saldos.csv")
        
        if self.original_csv_exists:
            os.rename("./saldos_backup.csv", "./saldos.csv")
        
        # Limpiar archivo de prueba
        if os.path.exists(self.test_csv_path):
            os.remove(self.test_csv_path)
    
    def test_balance_exists(self):
        """Prueba que se puede obtener el balance de una cédula existente"""
        result = get_balance_by_id.func("V-91827364")
        self.assertIn("2,580.00", result)
        self.assertIn("V-91827364", result)
    
    def test_balance_not_found(self):
        """Prueba el comportamiento cuando no se encuentra la cédula"""
        result = get_balance_by_id.func("V-99999999")
        self.assertIn("No se encontró", result)
        self.assertIn("V-99999999", result)
    
    def test_balance_format(self):
        """Prueba que el formato de respuesta es correcto"""
        result = get_balance_by_id.func("V-12345678")
        self.assertIn("$", result)
        self.assertIn("1,250.50", result)
    
    def test_invalid_input(self):
        """Prueba con entrada inválida"""
        result = get_balance_by_id.func("")
        self.assertIn("No se encontró", result)
    
    def test_balance_tool_description(self):
        """Prueba que la herramienta tiene la descripción correcta"""
        self.assertIsNotNone(get_balance_by_id.description)
        self.assertIn("cedula_id", get_balance_by_id.description)


if __name__ == '__main__':
    unittest.main()
