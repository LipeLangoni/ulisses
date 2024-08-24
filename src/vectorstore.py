from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from uuid import uuid4


embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db",  # Where to save data locally, remove if not neccesary
)

def split_topics(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    topics = text.split(';\n')
    topics = [topic.strip() for topic in topics if topic.strip()]
    
    return topics

file_path = 'glossario.txt'

topics = split_topics(file_path)