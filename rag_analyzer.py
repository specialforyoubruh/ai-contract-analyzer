import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from retriever import retrieve_relevant_chunks

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_risk(category: str, question: str, contract_id: str, language: str) -> dict:
    print(f"🔎 [ANALYZING] Category: {category} in {language}...") 
    
    chunks = retrieve_relevant_chunks(question, top_k=5, contract_id=contract_id)
    
    if not chunks:
        # Fallback messages based on language
        fallbacks = {
            "EN": "Information not found in the document.",
            "RU": "Информация не найдена в документе.",
            "KZ": "Құжатта ақпарат табылмады."
        }
        return {
            "category": category,
            "risk_level": "UNKNOWN",
            "description": fallbacks.get(language, "Information not found."),
            "recommendation": "Manual review required."
        }
    
    context = "\n---\n".join(chunks)

    # Force the target language based on the UI selection
    lang_map = {
        "EN": "English",
        "RU": "Russian",
        "KZ": "Kazakh"
    }
    target_lang = lang_map.get(language, "English")

    prompt = f"""
    Analyze the contract fragment provided in the CONTEXT.
    
    Category: {category}
    Question: {question}
    
    CONTEXT:
    {context}
    
    RETURN ONLY JSON:
    {{
        "risk_level": "CRITICAL/HIGH/MEDIUM/LOW",
        "clause": "clause number",
        "description": "detailed description written STRICTLY in {target_lang}",
        "recommendation": "legal advice written STRICTLY in {target_lang}"
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {
                    "role": "system", 
                    "content": f"You are a legal expert. You MUST respond strictly in {target_lang}. Do not switch to any other language."
                }, 
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        content = response.choices[0].message.content.strip().replace("```json", "").replace("```", "")
        result = json.loads(content)
        result['category'] = category
        return result
    except Exception as e:
        return {"category": category, "risk_level": "ERROR", "description": str(e)}

def ask_custom_question(question: str, contract_id: str, language: str) -> str:
    chunks = retrieve_relevant_chunks(question, top_k=7, contract_id=contract_id)
    
    if not chunks:
        return "Sorry, I couldn't find this information."

    context = "\n---\n".join(chunks)
    
    lang_map = {"EN": "English", "RU": "Russian", "KZ": "Kazakh"}
    target_lang = lang_map.get(language, "English")

    prompt = f"""
    Answer the question using the excerpts provided.
    STRICTLY RESPOND IN {target_lang}.
    
    EXCERPTS:
    {context}
    
    QUESTION:
    {question}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a legal assistant. Respond only in {target_lang}."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"
# import os
# import json
# from openai import OpenAI
# from dotenv import load_dotenv
# from retriever import retrieve_relevant_chunks

# load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# def analyze_risk(category: str, question: str, contract_id: str) -> dict:
#     print(f"🔎 [ANALYZING] Категория: {category}...") 
    
#     chunks = retrieve_relevant_chunks(question, top_k=5, contract_id=contract_id)
    
#     if not chunks:
#         print(f"⚠️ [WARNING] Данные по категории {category} не найдены.")
#         return {
#             "category": category,
#             "risk_level": "UNKNOWN",
#             "description": "Данные не найдены в базе. / Мәліметтер табылмады.",
#             "recommendation": "Требуется ручной анализ. / Қолмен тексеру қажет."
#         }
    
#     context = "\n---\n".join(chunks)

#     # Добавлена инструкция про язык
#     prompt = f"""
#     Ты — ведущий юрист BI Group. Проанализируй фрагмент договора.
#     ВАЖНО: Отвечай строго на том языке, на котором задан вопрос (русский или казахский).
    
#     Категория анализа: {category}
#     Вопрос: {question}
    
#     КОНТЕКСТ:
#     {context}
    
#     ВЕРНИ ТОЛЬКО JSON БЕЗ РАЗМЕТКИ Markdown:
#     {{
#         "risk_level": "CRITICAL/HIGH/MEDIUM/LOW",
#         "clause": "номер пункта / тармақ нөмірі",
#         "description": "описание проблемы на языке вопроса",
#         "recommendation": "рекомендация на языке вопроса"
#     }}
#     """

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini", 
#             messages=[
#                 {"role": "system", "content": "Ты юридический эксперт. Отвечаешь на языке пользователя (қазақша немесе орысша)."}, 
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0
#         )
#         content = response.choices[0].message.content.strip().replace("```json", "").replace("```", "")
#         result = json.loads(content)
#         result['category'] = category
#         print(f"✅ [SUCCESS] Анализ {category} завершен.")
#         return result
#     except Exception as e:
#         print(f"❌ [ERROR] Ошибка: {e}")
#         return {"category": category, "risk_level": "ERROR", "description": str(e)}

# def ask_custom_question(question: str, contract_id: str) -> str:
#     print(f"❓ [CHAT] Вопрос: {question}")
#     chunks = retrieve_relevant_chunks(question, top_k=7, contract_id=contract_id)
    
#     if not chunks:
#         return "🤖 Я не нашел информацию в документе. / Кешіріңіз, бұл құжатта ақпарат табылмады."

#     context = "\n---\n".join(chunks)

#     # Инструкция для двуязычного чата
#     prompt = f"""
#     Используй предоставленные выдержки из договора, чтобы ответить на вопрос. 
#     ОТВЕЧАЙ СТРОГО НА ТОМ ЯЗЫКЕ, НА КОТОРОМ ЗАДАН ВОПРОС.
#     Если вопрос на казахском — отвечай на казахском. Если на русском — на русском.
    
#     ТЕКСТ ИЗ БАЗЫ (ChromaDB):
#     {context}
    
#     ВОПРОС:
#     {question}
#     """

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "Ты — юридический ассистент компании BI Group. Сен BI Group заңгер көмекшісісің."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.3
#         )
#         answer = response.choices[0].message.content.strip()
#         print(f"✅ [CHAT] Ответ готов.")
#         return answer
#     except Exception as e:
#         return f"❌ Ошибка/Қате: {e}"
# import os
# import json
# from openai import OpenAI
# from dotenv import load_dotenv
# from retriever import retrieve_relevant_chunks

# load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# def analyze_risk(category: str, question: str, contract_id: str) -> dict:
#     chunks = retrieve_relevant_chunks(question, top_k=5, contract_id=contract_id)
    
#     if not chunks:
#         return {
#             "category": category,
#             "risk_level": "UNKNOWN",
#             "description": "Данные не найдены в базе.",
#             "recommendation": "Требуется ручной анализ."
#         }
    
#     context = "\n---\n".join(chunks)

#     prompt = f"""
#     Ты — ведущий юрист BI Group. Проанализируй фрагмент договора.
#     Категория анализа: {category}
#     Вопрос: {question}
    
#     КОНТЕКСТ:
#     {context}
    
#     ВЕРНИ ТОЛЬКО JSON БЕЗ ЛИШНИХ СЛОВ:
#     {{
#         "risk_level": "CRITICAL/HIGH/MEDIUM/LOW",
#         "clause": "номер пункта",
#         "description": "что не так",
#         "recommendation": "что сделать"
#     }}
#     """

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini", 
#             messages=[{"role": "system", "content": "Ты выдаешь только чистый JSON."}, 
#                       {"role": "user", "content": prompt}],
#             temperature=0
#         )
#         content = response.choices[0].message.content.strip().replace("```json", "").replace("```", "")
#         result = json.loads(content)
#         result['category'] = category
#         return result
#     except Exception as e:
#         return {"category": category, "risk_level": "ERROR", "description": str(e)}

# def ask_custom_question(question: str, contract_id: str) -> str:
   
#     chunks = retrieve_relevant_chunks(question, top_k=7, contract_id=contract_id)
    
#     if not chunks:
#         return "🤖 Я не нашел упоминаний об этом в текущем документе."

#     context = "\n---\n".join(chunks)

#     prompt = f"""
#     Используй предоставленные выдержки из договора, чтобы ответить на вопрос. 
#     Если в тексте нет ответа, честно скажи, что информации недостаточно.
    
#     ТЕКСТ ИЗ БАЗЫ (ChromaDB):
#     {context}
    
#     ВОПРОС:
#     {question}
#     """

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "Ты — юридический ассистент компании BI Group. Отвечаешь строго по тексту документа."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.3 # Небольшая креативность для связности текста
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         return f"❌ Ошибка при генерации ответа: {e}"
# import os
# import json
# from openai import OpenAI
# from dotenv import load_dotenv
# from retriever import retrieve_relevant_chunks

# load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# def analyze_risk(category: str, question: str, contract_id: str) -> dict:
#     """
#     1. Ищет информацию в базе.
#     2. Спрашивает у LLM.
#     3. Возвращает JSON.
#     """
#     print(f"🔎 [ANALYZING] Категория: {category}...")
    
   
#     chunks = retrieve_relevant_chunks(question, top_k=5, contract_id=contract_id)
    
#     if not chunks:
#         return {
#             "category": category,
#             "risk_level": "UNKNOWN",
#             "description": "В документе не найдены релевантные разделы.",
#             "recommendation": "Проверить вручную."
#         }
    
#     context = "\n---\n".join(chunks)

#     prompt = f"""
#     Ты профессиональный юрист строительной компании. 
#     Проанализируй текст договора на предмет риска в категории: "{category}".
    
#     Твоя задача ответить на вопрос: "{question}"
    
#     КОНТЕКСТ ДОГОВОРА:
#     {context}
    
#     ВЕРНИ ОТВЕТ ТОЛЬКО В ФОРМАТЕ JSON:
#     {{
#         "risk_level": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
#         "clause": "Номер пункта (если есть)",
#         "description": "Краткое описание найденного условия",
#         "recommendation": "Твоя рекомендация для юриста"
#     }}
#     """

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini", 
#             messages=[
#                 {"role": "system", "content": "Ты JSON-помощник юриста."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0
#         )
        
#         content = response.choices[0].message.content.strip()
        
        
#         if content.startswith("```"):
#             content = content.replace("```json", "").replace("```", "")
            
#         result = json.loads(content)
#         result['category'] = category
#         return result

#     except Exception as e:
#         return {
#             "category": category,
#             "risk_level": "ERROR",
#             "description": f"Ошибка AI: {e}",
#             "recommendation": "-"
#         }


# rag_analyzer.py

# import os
# import json
# from dotenv import load_dotenv
# from openai import OpenAI
# from retriever import retrieve_relevant_chunks  # функция поиска по ChromaDB

# # =========================
# # 1. OpenAI client
# # =========================

# load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# # =========================
# # 2. RAG-анализ
# # =========================

# def analyze_with_rag(question: str, contract_id: str, top_k: int = 5) -> dict:
#     """
#     Выполняет RAG-анализ для вопроса о рисках.
#     Возвращает JSON с полями: risk_level, clause, description, recommendation
#     """

#     context_chunks = retrieve_relevant_chunks(query=question, top_k=top_k, contract_id=contract_id)

#     if not context_chunks:
#         return {
#             "risk_level": "OK",
#             "clause": None,
#             "description": "Релевантные пункты договора не найдены.",
#             "recommendation": "Действий не требуется."
#         }

#     context = "\n\n".join(context_chunks)

#     prompt = f"""
# Вы — старший юридический аналитик BI Group.

# Используя ТОЛЬКО контекст договора ниже, ответьте на вопрос:

# Вопрос:
# {question}

# Контекст:
# \"\"\"
# {context}
# \"\"\"

# Верните корректный JSON с полями:
# - risk_level: CRITICAL | HIGH | OK
# - clause: номер пункта договора, если применимо, иначе null
# - description: краткое объяснение найденного риска
# - recommendation: конкретная рекомендация действий
# """

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "Вы анализируете строительные контракты на риски."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0
#         )

#         content = response.choices[0].message.content.strip()
#         return json.loads(content)

#     except json.JSONDecodeError:
#         return {
#             "risk_level": "HIGH",
#             "clause": None,
#             "description": content,
#             "recommendation": "Требуется ручная проверка."
#         }

#     except Exception as e:
#         return {
#             "risk_level": "HIGH",
#             "clause": None,
#             "description": f"Ошибка LLM: {e}",
#             "recommendation": "Требуется ручная проверка."
#         }
