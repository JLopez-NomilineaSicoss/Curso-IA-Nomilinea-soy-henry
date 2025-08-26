import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Agregar el directorio padre al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock para evitar cargar el modelo real durante las pruebas
with patch('solution.main.FAISS.load_local'):
    with patch('solution.main.HuggingFaceEmbeddings'):
        with patch('solution.main.ChatGroq'):
            from solution.main import get_bank_information


class TestBankInformationTool(unittest.TestCase):
    """Pruebas para la herramienta de información bancaria"""
    
    @patch('solution.main.RetrievalQA.from_chain_type')
    def test_bank_information_query(self, mock_retrieval_qa):
        """Prueba que se puede hacer una consulta de información bancaria"""
        # Configurar el mock
        mock_chain = MagicMock()
        mock_chain.run.return_value = "Para abrir una cuenta necesitas tu cédula..."
        mock_retrieval_qa.return_value = mock_chain
        
        result = get_bank_information.func("¿Cómo abro una cuenta?")
        
        self.assertIsInstance(result, str)
        self.assertIn("cuenta", result.lower())
    
    @patch('solution.main.RetrievalQA.from_chain_type')
    def test_bank_information_error_handling(self, mock_retrieval_qa):
        """Prueba el manejo de errores en la consulta"""
        # Configurar el mock para lanzar una excepción
        mock_retrieval_qa.side_effect = Exception("Error de conexión")
        
        result = get_bank_information.func("¿Cómo abro una cuenta?")
        
        self.assertIn("Error al consultar", result)
        self.assertIn("Error de conexión", result)
    
    def test_bank_information_tool_description(self):
        """Prueba que la herramienta tiene la descripción correcta"""
        self.assertIsNotNone(get_bank_information.description)
        self.assertIn("banco", get_bank_information.description.lower())
        self.assertIn("credito", get_bank_information.description.lower())
    
    @patch('solution.main.RetrievalQA.from_chain_type')
    def test_empty_question(self, mock_retrieval_qa):
        """Prueba con pregunta vacía"""
        mock_chain = MagicMock()
        mock_chain.run.return_value = "Por favor, especifica tu consulta"
        mock_retrieval_qa.return_value = mock_chain
        
        result = get_bank_information.func("")
        
        self.assertIsInstance(result, str)
        # Debe manejar preguntas vacías sin errores
    
    @patch('solution.main.RetrievalQA.from_chain_type')
    def test_specific_banking_queries(self, mock_retrieval_qa):
        """Prueba consultas específicas sobre servicios bancarios"""
        mock_chain = MagicMock()
        
        queries_and_responses = [
            ("¿Cómo solicito una tarjeta de crédito?", "Para solicitar una tarjeta de crédito..."),
            ("¿Qué necesito para transferencias?", "Para realizar transferencias necesitas..."),
            ("¿Cuáles son los requisitos para cuenta de ahorros?", "Los requisitos son...")
        ]
        
        for query, expected_response in queries_and_responses:
            mock_chain.run.return_value = expected_response
            mock_retrieval_qa.return_value = mock_chain
            
            result = get_bank_information.func(query)
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0)


if __name__ == '__main__':
    unittest.main()
