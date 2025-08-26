from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_community.vectorstores.faiss import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
import os
import pandas as pd

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())  # read local .env file


llm = ChatGroq(
    model="llama3-70b-8192",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

embeddings_model_name = "sentence-transformers/all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)

db = FAISS.load_local(
    "./solution/index",
    embeddings,
    allow_dangerous_deserialization=True,
)
retriever = db.as_retriever(k=1)

from langchain.agents import tool


@tool
def get_balance_by_id(cedula_id: str) -> str:
    """Obtiene balance de la cuenta by cedula_id."""
    try:
        df = pd.read_csv("./saldos.csv")
        result = df[df["ID_Cedula"] == cedula_id]
        if result.empty:
            return f"No se encontró ninguna cuenta con la cédula {cedula_id}"
        return f"El balance de la cuenta {cedula_id} es: ${result['Balance'].values[0]:,.2f}"
    except Exception as e:
        return f"Error al consultar el balance: {str(e)}"


@tool
def get_bank_information(question: str) -> str:
    """Obtiene informacion general del banco sobre tramites de cuentas de ahorros, tarjetas de credito y transferencias."""
    try:
        bank_info_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            verbose=True,
        )
        response = bank_info_chain.run(question)
        return response
    except Exception as e:
        return f"Error al consultar la base de conocimientos: {str(e)}"


tools = [get_balance_by_id, get_bank_information]


agent = create_react_agent(llm, tools, prompt=hub.pull("hwchase17/react"))
agent_executor = AgentExecutor(agent=agent, tools=tools)


def main():
    """Función principal para probar el agente"""
    try:
        # Ejemplo de uso del agente
        result = agent_executor.invoke({"input": "Hola, ¿en qué puedo ayudarte?"})
        print("Respuesta del agente:", result["output"])
        
        # Ejemplos de consultas
        queries = [
            "¿Cómo abro una cuenta de ahorros en el banco?",
            "¿Cuál es el balance de la cuenta de la cédula V-91827364?",
            "¿Cuál es el sentido de la vida?"
        ]
        
        for query in queries:
            print(f"\n--- Consulta: {query} ---")
            result = agent_executor.invoke({"input": query})
            print(f"Respuesta: {result['output']}")
            
    except Exception as e:
        print(f"Error en la ejecución: {str(e)}")

if __name__ == "__main__":
    main()
