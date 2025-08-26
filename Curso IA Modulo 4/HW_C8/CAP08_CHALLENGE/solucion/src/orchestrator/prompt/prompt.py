rag = """Usa la siguiente información como contexto para responder la pregunta. 
Por favor, sé informativo y proporciona respuestas extensas. 
Si no sabes la respuesta, simplemente di que no lo sabes, no inventes una respuesta.

IMPORTANTE: Al final de tu respuesta, cita las fuentes de donde obtuviste la información usando los enlaces proporcionados en el contexto.

{conversation_context}

Contexto de búsqueda:
{context}

Pregunta: {question}?

Recuerda: Siempre cita las fuentes al final de tu respuesta."""
