import asyncio
import json
import os
from typing import AsyncGenerator
from util import logger
from dotenv import load_dotenv

import prompt
from retrieval import Retriever
from retrieval.serper_search import SerperSearcher
from retrieval.scraper import ScraperLocal, ScraperRemote
from retrieval.embeddings import OpenAIEmbeddings
from retrieval.splitter import LangChainSplitter
from retrieval.source_formatter import SourceFormatter
from llm import GroqClient
from memory import ConversationMemory

# Cargar variables de entorno
load_dotenv()


async def stream_chat(prompt: str, context: str = ""):
    """Función de streaming usando Groq Cloud"""
    groq_client = GroqClient()
    
    messages = []
    if context:
        messages.append({
            "role": "system", 
            "content": f"Usa la siguiente información como contexto: {context}"
        })
    
    messages.append({
        "role": "user",
        "content": prompt
    })
    
    async for token in groq_client.stream_chat(messages, temperature=0.7):
        yield token


async def event_generator(query: str, memory: ConversationMemory) -> AsyncGenerator[dict, None]:
    embeddings = OpenAIEmbeddings()
    serper_searcher = SerperSearcher()
    scraper = ScraperLocal()
    splitter = LangChainSplitter(chunk_size=400, chunk_overlap=50, length_function=len)
    source_formatter = SourceFormatter()

    retriever = Retriever(
        searcher=serper_searcher,
        scraper=scraper,
        embeddings=embeddings,
        splitter=splitter,
    )
    async for event in retriever.get_context(query=query, cache_treshold=0.85, k=10):
        yield event
        if event["event"] == "context":
            # Extraer y formatear fuentes
            sources = source_formatter.extract_sources_from_search(
                await serper_searcher.search(query)
            )
            sources_for_prompt = source_formatter.format_sources_for_prompt(sources)
            
            # Obtener contexto de conversación
            conversation_context = memory.get_context_for_llm(query)
            
            # Crear prompt con memoria y fuentes
            final_prompt = prompt.rag.format(
                conversation_context=conversation_context,
                context=event["data"] + sources_for_prompt,
                question=query
            )

            yield {"event": "prompt", "data": final_prompt, "sources": sources}

            async for text in stream_chat(prompt=final_prompt, context=event["data"]):
                yield {"event": "token", "data": text}


async def main(query: str, memory: ConversationMemory):
    # Agregar mensaje del usuario a la memoria
    memory.add_user_message(query)
    
    response_text = ""
    sources = []
    
    async for event in event_generator(query, memory):
        if event["event"] == "search":
            print("🔍 **Búsqueda en internet**")
            for link in json.loads(event["data"])["items"]:
                print(f"  📄 {link['link']}")
            print()

        if event["event"] == "token":
            response_text += event["data"]
            print(event["data"], end="", flush=True)
        
        # Capturar fuentes para la memoria
        if event["event"] == "prompt" and "sources" in event:
            sources = event["sources"]
    
    # Agregar respuesta del asistente a la memoria
    if response_text.strip():
        memory.add_assistant_message(response_text, sources)
        
        # Mostrar fuentes al final
        if sources:
            print("\n\n📚 **Referencias:**")
            for i, source in enumerate(sources, 1):
                title = source.get("title", "Sin título")
                url = source.get("url", "")
                domain = source.get("domain", "")
                print(f"{i}. [{title}]({url})")
                if domain:
                    print(f"   📍 {domain}")


if __name__ == "__main__":
    # Inicializar memoria de conversación
    memory = ConversationMemory(max_messages=50)
    
    print("🤖 **Chatbot con Memoria de Conversación**")
    print("💡 Escribe 'help' para comandos disponibles")
    print("💾 Escribe 'memory' para ver estadísticas de la conversación")
    print("🗑️  Escribe 'clear' para limpiar la memoria")
    print("📤 Escribe 'export' para exportar la conversación")
    print("❌ Escribe 'quit' para salir")
    print()
    
    while True:
        try:
            print("")
            query = input("> Tu pregunta: ").strip()
            
            if not query:
                continue
                
            if query.lower() == 'quit':
                print("👋 ¡Hasta luego!")
                break
                
            if query.lower() == 'help':
                print("📚 **Comandos disponibles:**")
                print("  help     - Mostrar esta ayuda")
                print("  memory   - Ver estadísticas de la conversación")
                print("  clear    - Limpiar memoria de conversación")
                print("  export   - Exportar conversación a archivo")
                print("  quit     - Salir del chatbot")
                continue
                
            if query.lower() == 'memory':
                summary = memory.get_conversation_summary()
                print("🧠 **Estadísticas de la Conversación:**")
                print(f"  ID: {summary['conversation_id']}")
                print(f"  Total mensajes: {summary['total_messages']}")
                print(f"  Mensajes usuario: {summary['user_messages']}")
                print(f"  Mensajes asistente: {summary['assistant_messages']}")
                print(f"  Fuentes citadas: {summary['total_sources_cited']}")
                continue
                
            if query.lower() == 'clear':
                memory.clear_memory()
                print("🗑️ Memoria de conversación limpiada")
                continue
                
            if query.lower() == 'export':
                filename = f"conversation_{memory.conversation_id}.json"
                memory.export_conversation(filename)
                print(f"📤 Conversación exportada a: {filename}")
                continue
            
            print("")
            asyncio.run(main(query, memory))
            print("")
            
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.error(f"Error en bucle principal: {e}")
