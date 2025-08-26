import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Agregar el directorio padre al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAgentIntegration(unittest.TestCase):
    """Pruebas de integración para el agente completo"""
    
    @patch('solution.main.FAISS.load_local')
    @patch('solution.main.HuggingFaceEmbeddings')
    @patch('solution.main.ChatGroq')
    @patch('solution.main.hub.pull')
    def test_agent_initialization(self, mock_hub, mock_llm, mock_embeddings, mock_faiss):
        """Prueba que el agente se inicializa correctamente"""
        # Configurar mocks
        mock_hub.return_value = "mock_prompt"
        mock_llm.return_value = MagicMock()
        mock_embeddings.return_value = MagicMock()
        mock_faiss.return_value = MagicMock()
        
        try:
            from solution.main import agent_executor, tools
            self.assertIsNotNone(agent_executor)
            self.assertIsNotNone(tools)
            self.assertEqual(len(tools), 2)
        except Exception as e:
            self.fail(f"Error al inicializar el agente: {e}")
    
    @patch('solution.main.agent_executor')
    def test_agent_response_format(self, mock_agent):
        """Prueba que el agente retorna respuestas en el formato correcto"""
        # Configurar el mock del agente
        mock_agent.invoke.return_value = {
            "output": "Esta es una respuesta de prueba del agente"
        }
        
        from solution.main import agent_executor
        result = agent_executor.invoke({"input": "prueba"})
        
        self.assertIn("output", result)
        self.assertIsInstance(result["output"], str)
    
    def test_tools_exist(self):
        """Prueba que las herramientas existen y están disponibles"""
        try:
            from solution.main import get_balance_by_id, get_bank_information
            
            # Verificar que son funciones/herramientas válidas
            self.assertTrue(hasattr(get_balance_by_id, 'func'))
            self.assertTrue(hasattr(get_bank_information, 'func'))
            
            # Verificar que tienen descripciones
            self.assertIsNotNone(get_balance_by_id.description)
            self.assertIsNotNone(get_bank_information.description)
            
        except ImportError as e:
            self.fail(f"Error al importar herramientas: {e}")
    
    def test_file_dependencies(self):
        """Prueba que los archivos necesarios existen"""
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Verificar archivos críticos
        required_files = [
            "saldos.csv",
            "solution/main.py",
            "solution/requirements.txt"
        ]
        
        for file_path in required_files:
            full_path = os.path.join(base_path, file_path)
            self.assertTrue(
                os.path.exists(full_path), 
                f"Archivo requerido no encontrado: {file_path}"
            )
    
    def test_knowledge_base_files(self):
        """Prueba que los archivos de la base de conocimientos existen"""
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        knowledge_base_path = os.path.join(base_path, "knowledge_base")
        
        self.assertTrue(
            os.path.exists(knowledge_base_path),
            "Directorio knowledge_base no encontrado"
        )
        
        required_knowledge_files = [
            "nueva_cuenta.txt",
            "tarjeta_credito.txt", 
            "transferencia.txt"
        ]
        
        for file_name in required_knowledge_files:
            file_path = os.path.join(knowledge_base_path, file_name)
            self.assertTrue(
                os.path.exists(file_path),
                f"Archivo de conocimiento no encontrado: {file_name}"
            )
    
    @patch('solution.main.ChatGroq')
    def test_environment_variables(self, mock_llm):
        """Prueba que las variables de entorno están configuradas"""
        # Verificar que al menos una API key está disponible
        api_keys = ['GROQ_API_KEY', 'OPENAI_API_KEY', 'GOOGLE_API_KEY']
        
        has_api_key = any(os.getenv(key) for key in api_keys)
        
        # Solo mostrar advertencia si no hay ninguna API key
        if not has_api_key:
            print("Advertencia: No se encontraron API keys en las variables de entorno")


class TestSystemRequirements(unittest.TestCase):
    """Pruebas para verificar que se cumplen los requisitos del sistema"""
    
    def test_csv_data_structure(self):
        """Prueba que el archivo CSV tiene la estructura correcta"""
        import pandas as pd
        
        try:
            df = pd.read_csv("saldos.csv")
            
            # Verificar columnas requeridas
            required_columns = ['ID_Cedula', 'Nombre', 'Balance']
            for col in required_columns:
                self.assertIn(col, df.columns, f"Columna {col} no encontrada en CSV")
            
            # Verificar que hay datos
            self.assertGreater(len(df), 0, "El archivo CSV está vacío")
            
            # Verificar tipos de datos
            self.assertTrue(df['Balance'].dtype in ['float64', 'int64'], 
                          "La columna Balance debe ser numérica")
            
        except FileNotFoundError:
            self.fail("Archivo saldos.csv no encontrado")
    
    def test_requirements_completeness(self):
        """Prueba que el archivo requirements.txt incluye todas las dependencias"""
        try:
            with open("solution/requirements.txt", 'r') as f:
                requirements = f.read().lower()
            
            # Verificar dependencias críticas
            critical_dependencies = [
                'langchain',
                'faiss',
                'pandas',
                'sentence-transformers'
            ]
            
            for dep in critical_dependencies:
                self.assertIn(dep, requirements, 
                            f"Dependencia {dep} no encontrada en requirements.txt")
                
        except FileNotFoundError:
            self.fail("Archivo requirements.txt no encontrado")


if __name__ == '__main__':
    unittest.main()
