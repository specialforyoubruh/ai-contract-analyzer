import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
import chromadb
from chromadb.config import Settings

# -----------------------
# 1. Загружаем .env
# -----------------------
load_dotenv()  # <- обязательно, чтобы OPENAI_API_KEY подхватился

# -----------------------
# 2. Инициализация ChromaDB
# -----------------------
chroma_client = chromadb.Client(
    Settings(
        persist_directory="./chroma_db",
        anonymized_telemetry=False
    )
)

collection = chroma_client.get_or_create_collection(
    name="contracts"
)

# -----------------------
# 3. Модель для эмбеддингов
# -----------------------
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY не найден. Проверь .env или переменные окружения.")

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=api_key
)

# -----------------------
# 4. Функция сохранения чанков
# -----------------------
def store_chunks(chunks: list[str], contract_id: str):
    if not chunks:
        print("[WARNING] Нет чанков для сохранения")
        return

    try:
        vectors = embeddings.embed_documents(chunks)

        collection.add(
            documents=chunks,
            embeddings=vectors,
            metadatas=[{"contract_id": contract_id}] * len(chunks),
            ids=[f"{contract_id}_{i}" for i in range(len(chunks))]
        )

        chroma_client.persist()
        print("[INFO] Чанки успешно сохранены в ChromaDB")

    except Exception as e:
        print(f"[ERROR] Ошибка при сохранении чанков: {e}")
