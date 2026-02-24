import os
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

# Загружаем с принудительным обновлением
load_dotenv(override=True)

api_key = os.getenv("OPENAI_API_KEY")

# Инициализируем прямой клиент OpenAI
# (Это самый надежный способ для ключей sk-svcacct)
client = OpenAI(api_key=api_key)

PERSIST_DIRECTORY = "./chroma_db"
chroma_client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
collection = chroma_client.get_or_create_collection(name="contracts")

def get_embeddings(texts):
    """
    Прямой вызов API для создания векторов.
    Если здесь вылетает 401 — значит у ключа нет доступа к модели.
    """
    try:
        # Пытаемся вызвать эмбеддинги через основной клиент
        response = client.embeddings.create(
            input=texts,
            model="text-embedding-3-small" 
        )
        return [item.embedding for item in response.data]
    except Exception as e:
        print(f"❌ Ошибка API при создании эмбеддингов: {e}")
        # Если новая модель запрещена, попробуем старую как запасной вариант
        if "401" in str(e) or "403" in str(e):
            print("🔄 Пробую запасную модель (text-embedding-ada-002)...")
            response = client.embeddings.create(
                input=texts,
                model="text-embedding-ada-002"
            )
            return [item.embedding for item in response.data]
        raise e

def store_chunks(chunks: list[str], contract_id: str):
    if not chunks: return
    try:
        print(f"🔄 Процесс: Создание векторов для {len(chunks)} фрагментов...")
        vectors = get_embeddings(chunks)
        
        ids = [f"{contract_id}_{i}" for i in range(len(chunks))]
        metadatas = [{"contract_id": contract_id} for _ in range(len(chunks))]

        collection.add(
            documents=chunks,
            embeddings=vectors,
            metadatas=metadatas,
            ids=ids
        )
        print(f"✅ Документ {contract_id} готов.")
    except Exception as e:
        print(f"❌ Ошибка в store_chunks: {e}")

def retrieve_relevant_chunks(query: str, top_k: int = 5, contract_id: str = None) -> list[str]:
    try:
        # Получаем вектор вопроса тем же способом
        query_vector = get_embeddings([query])[0]
        
        where_filter = {"contract_id": contract_id} if contract_id else None
        
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            where=where_filter
        )
        return results['documents'][0] if results['documents'] else []
    except Exception as e:
        print(f"❌ Ошибка поиска: {e}")
        return []
# import os
# import chromadb
# from openai import OpenAI  # Будем использовать прямой клиент
# from dotenv import load_dotenv

# load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# PERSIST_DIRECTORY = "./chroma_db"
# chroma_client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
# collection = chroma_client.get_or_create_collection(name="contracts")

# # Функция для получения эмбеддингов напрямую через OpenAI
# def get_embeddings(texts):
#     try:
#         response = client.embeddings.create(
#             input=texts,
#             model="text-embedding-3-small"
#         )
#         return [item.embedding for item in response.data]
#     except Exception as e:
#         print(f"❌ Критическая ошибка OpenAI Embeddings: {e}")
#         raise e

# def store_chunks(chunks: list[str], contract_id: str):
#     if not chunks: return
    
#     try:
#         print(f"🔄 Генерация векторов для {len(chunks)} чанков через прямой клиент...")
#         # Используем нашу новую функцию вместо LangChain
#         vectors = get_embeddings(chunks)
        
#         ids = [f"{contract_id}_{i}" for i in range(len(chunks))]
#         metadatas = [{"contract_id": contract_id} for _ in range(len(chunks))]

#         collection.add(
#             documents=chunks,
#             embeddings=vectors,
#             metadatas=metadatas,
#             ids=ids
#         )
#         print(f"✅ Документ {contract_id} успешно проиндексирован.")
#     except Exception as e:
#         print(f"❌ Ошибка при сохранении в ChromaDB: {e}")

# def retrieve_relevant_chunks(query: str, top_k: int = 5, contract_id: str = None) -> list[str]:
#     try:
#         # Здесь тоже используем прямой клиент
#         query_vector = get_embeddings([query])[0]
        
#         where_filter = {"contract_id": contract_id} if contract_id else None
        
#         results = collection.query(
#             query_embeddings=[query_vector],
#             n_results=top_k,
#             where=where_filter
#         )
        
#         if results and 'documents' in results and results['documents']:
#             return results['documents'][0]
#         return []
#     except Exception as e:
#         print(f"❌ Ошибка поиска в ChromaDB: {e}")
#         return []
# import os
# import chromadb
# from langchain_openai import OpenAIEmbeddings
# from dotenv import load_dotenv

# # 1. Загружаем переменные окружения
# load_dotenv()

# PERSIST_DIRECTORY = "./chroma_db"
# chroma_client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
# collection = chroma_client.get_or_create_collection(name="contracts")

# # 2. Получаем ключ и проверяем его наличие
# api_key = os.getenv("OPENAI_API_KEY")

# if not api_key:
#     print("❌ ОШИБКА: API-ключ не найден в файле .env!")

# # 3. Явно передаем ключ и указываем модель
# embeddings = OpenAIEmbeddings(
#     openai_api_key=api_key, 
#     model="text-embedding-3-small"  # Используем современную и дешевую модель
# )

# def store_chunks(chunks: list[str], contract_id: str):
#     if not chunks:
#         print("⚠️ Список чанков пуст.")
#         return

#     try:
#         print(f"🔄 Генерация векторов для {len(chunks)} чанков...")
#         # Здесь происходит обращение к OpenAI, которое выдавало 401
#         vectors = embeddings.embed_documents(chunks)
        
#         ids = [f"{contract_id}_{i}" for i in range(len(chunks))]
#         metadatas = [{"contract_id": contract_id} for _ in range(len(chunks))]

#         collection.add(
#             documents=chunks,
#             embeddings=vectors,
#             metadatas=metadatas,
#             ids=ids
#         )
#         print(f"✅ Документ {contract_id} проиндексирован в ChromaDB.")
#     except Exception as e:
#         print(f"❌ Ошибка при сохранении в ChromaDB: {e}")

# def retrieve_relevant_chunks(query: str, top_k: int = 5, contract_id: str = None) -> list[str]:
#     try:
#         # Проверка наличия ключа перед запросом
#         query_vector = embeddings.embed_query(query)
        
#         where_filter = {"contract_id": contract_id} if contract_id else None
        
#         results = collection.query(
#             query_embeddings=[query_vector],
#             n_results=top_k,
#             where=where_filter
#         )
        
#         if results and 'documents' in results and results['documents']:
#             return results['documents'][0]
#         return []
#     except Exception as e:
#         print(f"❌ Ошибка поиска в ChromaDB: {e}")
#         return []


# import os
# import chromadb
# from langchain_openai import OpenAIEmbeddings
# from dotenv import load_dotenv

# load_dotenv()


# PERSIST_DIRECTORY = "./chroma_db"


# chroma_client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
# collection = chroma_client.get_or_create_collection(name="contracts")


# api_key = os.getenv("OPENAI_API_KEY")
# if not api_key:
#     raise ValueError("OPENAI_API_KEY не найден в .env файле")

# embeddings = OpenAIEmbeddings(openai_api_key=api_key)

# def store_chunks(chunks: list[str], contract_id: str):
#     """Сохраняет чанки в базу данных."""
#     if not chunks:
#         print("⚠️ [WARNING] Нет текста для сохранения.")
#         return

#     print(f"🔄 [INFO] Генерация векторов для {len(chunks)} чанков...")
    
#     try:
     
#         vectors = embeddings.embed_documents(chunks)
        
       
#         ids = [f"{contract_id}_{i}" for i in range(len(chunks))]
#         metadatas = [{"contract_id": contract_id} for _ in range(len(chunks))]

        
#         collection.add(
#             documents=chunks,
#             embeddings=vectors,
#             metadatas=metadatas,
#             ids=ids
#         )
#         print(f"✅ [SUCCESS] Чанки контракта '{contract_id}' сохранены.")
#     except Exception as e:
#         print(f"❌ [ERROR] Ошибка сохранения: {e}")

# def retrieve_relevant_chunks(query: str, top_k: int = 5, contract_id: str = None) -> list[str]:
#     """Поиск похожих фрагментов в базе."""
#     try:
#         query_vector = embeddings.embed_query(query)
        
#         where_filter = {"contract_id": contract_id} if contract_id else None
        
#         results = collection.query(
#             query_embeddings=[query_vector],
#             n_results=top_k,
#             where=where_filter
#         )
        
#         if results and results['documents']:
#             return results['documents'][0]
#         return []
#     except Exception as e:
#         print(f"❌ [ERROR] Ошибка поиска: {e}")
#         return []


