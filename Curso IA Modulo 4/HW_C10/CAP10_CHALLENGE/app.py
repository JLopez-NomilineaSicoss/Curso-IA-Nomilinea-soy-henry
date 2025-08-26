import streamlit as st
import sys
import os

# Agregar el directorio solution al path para importar modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'solution'))

from solution.main import agent_executor, get_balance_by_id, get_bank_information

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Atención al Cliente - Banco Henry",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #1976d2;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #7b1fa2;
    }
    .sidebar-content {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<h1 class="main-header">🏦 Sistema de Atención al Cliente - Banco Henry</h1>', unsafe_allow_html=True)

# Sidebar con información
with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.header("📋 Funcionalidades")
    st.markdown("""
    **Este sistema puede ayudarte con:**
    
    🔍 **Consultas de Balance**
    - Consultar saldo de cuentas por cédula
    
    🏛️ **Información Bancaria**
    - Apertura de cuentas
    - Solicitud de tarjetas de crédito
    - Procedimientos de transferencias
    
    💬 **Consultas Generales**
    - Preguntas diversas usando IA
    """)
    
    st.header("📝 Ejemplos de consultas")
    st.markdown("""
    - "¿Cuál es el balance de la cédula V-91827364?"
    - "¿Cómo abro una cuenta de ahorros?"
    - "¿Cómo solicito una tarjeta de crédito?"
    - "¿Cuáles son los requisitos para transferencias?"
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# Inicializar el historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Mensaje de bienvenida
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "¡Hola! Soy el asistente virtual del Banco Henry. ¿En qué puedo ayudarte hoy? Puedo consultar balances de cuentas, proporcionar información sobre nuestros servicios bancarios o responder preguntas generales."
    })

# Mostrar historial de chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input del usuario
if prompt := st.chat_input("Escribe tu consulta aquí..."):
    # Agregar mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Procesar la consulta con el agente
    with st.chat_message("assistant"):
        with st.spinner("Procesando tu consulta..."):
            try:
                # Ejecutar el agente
                result = agent_executor.invoke({"input": prompt})
                response = result["output"]
                
                # Mostrar respuesta
                st.markdown(response)
                
                # Agregar respuesta al historial
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_message = f"❌ Lo siento, ocurrió un error al procesar tu consulta: {str(e)}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})

# Sección de pruebas rápidas
st.markdown("---")
st.header("🚀 Pruebas Rápidas")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💰 Consultar Balance", key="balance_test"):
        test_query = "¿Cuál es el balance de la cuenta de la cédula V-91827364?"
        st.session_state.messages.append({"role": "user", "content": test_query})
        with st.spinner("Consultando balance..."):
            try:
                result = agent_executor.invoke({"input": test_query})
                response = result["output"]
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")

with col2:
    if st.button("🏦 Info Bancaria", key="bank_info_test"):
        test_query = "¿Cómo abro una cuenta de ahorros?"
        st.session_state.messages.append({"role": "user", "content": test_query})
        with st.spinner("Consultando información bancaria..."):
            try:
                result = agent_executor.invoke({"input": test_query})
                response = result["output"]
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")

with col3:
    if st.button("❓ Pregunta General", key="general_test"):
        test_query = "¿Qué es la inteligencia artificial?"
        st.session_state.messages.append({"role": "user", "content": test_query})
        with st.spinner("Procesando pregunta..."):
            try:
                result = agent_executor.invoke({"input": test_query})
                response = result["output"]
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Botón para limpiar historial
if st.button("🗑️ Limpiar Historial", key="clear_history"):
    st.session_state.messages = [{
        "role": "assistant", 
        "content": "¡Hola! Soy el asistente virtual del Banco Henry. ¿En qué puedo ayudarte hoy?"
    }]
    st.rerun()

# Footer
st.markdown("---")
st.markdown("**💡 Tip:** Puedes hacer preguntas específicas sobre balances usando el formato de cédula (ej: V-12345678) o consultar información general sobre servicios bancarios.")
