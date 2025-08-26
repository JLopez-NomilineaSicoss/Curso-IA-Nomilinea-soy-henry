from langchain_community.document_loaders.directory import DirectoryLoader
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings

loader = DirectoryLoader("./knowledge_base", glob="**/*.txt")

docs = loader.load()

embeddings_model_name = "sentence-transformers/all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)

db = FAISS.from_documents(docs, embeddings)

db.save_local("./solution/index")
