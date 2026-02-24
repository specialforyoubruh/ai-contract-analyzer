import os
import shutil
import json
import re
from fastapi import FastAPI, UploadFile, File, Body
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Принудительно загружаем переменные из .env
load_dotenv(override=True)

# Импортируем ваши функции
from main import extract_text_from_pdf, split_text
from retriever import store_chunks
from rag_analyzer import analyze_risk, ask_custom_question 

app = FastAPI()

# Словарь для хранения сессий (связь chat_id -> filename)
sessions = {}

# --- УЛУЧШЕННАЯ ФУНКЦИЯ МАСКИРОВКИ (PII-MASKING) ---
def mask_pii(text: str) -> str:
    """
    Усиленная маскировка с поддержкой казахских символов и паттернов договоров
    """
    # 1. Маскируем ИИН (12 цифр)
    text = re.sub(r'\b\d{12}\b', '[ID_HIDDEN]', text)
    
    # 2. Маскируем телефоны
    text = re.sub(r'(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}', '[PHONE_HIDDEN]', text)

    # 3. Маскируем ФИО после слов "гр.", "гражданин(-ка)", "лице"
    # Добавляем казахские буквы: ә, і, ң, ғ, ү, ұ, қ, ө, һ
    name_pattern = r'[А-ЯЁӘІҢҒҮҰҚӨҺ][а-яёәіңғүұқөһ]+\s[А-ЯЁӘІҢҒҮҰҚӨҺ][а-яёәіңғүұқөһ]+(\s[А-ЯЁӘІҢҒҮҰҚӨҺ][а-яёәіңғүұқөһ]+)?'
    
    # Маскировка после "гр."
    text = re.sub(r'(гр\.|гражданин\(?\-?ка\)?)\s+' + name_pattern, r'\1 [NAME_HIDDEN]', text)
    
    # Маскировка после "в лице"
    text = re.sub(r'(в лице)\s+' + name_pattern, r'\1 [NAME_HIDDEN]', text)

    # 4. ФИО КАПСОМ (включая казахские буквы)
    text = re.sub(r'\b[А-ЯЁӘІҢҒҮҰҚӨҺ]{2,}\s[А-ЯЁӘІҢҒҮҰҚӨҺ]{2,}(\s[А-ЯЁӘІҢҒҮҰҚӨҺ]{2,})?\b', '[NAME_HIDDEN]', text)

    # 5. Просто любые ФИО по тексту (казахские и русские)
    text = re.sub(r'\b' + name_pattern + r'\b', '[NAME_HIDDEN]', text)
    
    return text

@app.post("/analyze")
async def analyze(file: UploadFile = File(...), chat_id: str = Body(None)):
    try:
        # 1. Сохраняем временный файл
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Извлекаем текст
        raw_text = extract_text_from_pdf(temp_path)
        
        # 3. Применяем маскировку
        safe_text = mask_pii(raw_text)
        
        # ЛОГ ДЛЯ ПРОВЕРКИ (увидишь в консоли)
        print("\n--- ПРОВЕРКА МАСКИРОВКИ (ПЕРВЫЕ 300 СИМВОЛОВ) ---")
        print(safe_text[:300])
        print("-----------------------------------------------\n")

        # 4. Делим безопасный текст на чанки
        chunks = split_text(safe_text)
        
        # 5. Сохраняем в ChromaDB
        store_chunks(chunks, file.filename)

        if chat_id:
            sessions[chat_id] = file.filename

        # 6. Анализируем по категориям
        categories_to_check = [
            ("Штрафы", "Какие штрафы предусмотрены за нарушения? Укажи номер пункта."),
            ("Оплата", "Какие условия и сроки оплаты указаны? Укажи номер пункта."),
            ("Расторжение", "Каков порядок и условия расторжения договора? Укажи номер пункта."),
            ("Гарантия", "Какие гарантийные обязательства и сроки предусмотрены? Укажи номер пункта.")
        ]

        results = []
        for cat, q in categories_to_check:
            print(f"🔎 [ANALYZING] {cat}...")
            res = analyze_risk(cat, q, file.filename)
            results.append(res)

        if os.path.exists(temp_path):
            os.remove(temp_path)

        final_data = {
            "status": "success",
            "filename": file.filename,
            "analysis": results,
            "privacy": "enabled"
        }

        return JSONResponse(
            content=json.loads(json.dumps(final_data, ensure_ascii=False)),
            media_type="application/json; charset=utf-8"
        )

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/chat")
async def chat(chat_id: str = Body(...), question: str = Body(...)):
    try:
        filename = sessions.get(str(chat_id))
        if not filename:
            return {"answer": "Сначала загрузите файл."}

        answer = ask_custom_question(question, filename)
        
        return JSONResponse(
            content={"answer": answer},
            media_type="application/json; charset=utf-8"
        )
    except Exception as e:
        return {"answer": f"Ошибка: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
# import os
# import shutil
# import json
# from fastapi import FastAPI, UploadFile, File, Body
# from fastapi.responses import JSONResponse
# from dotenv import load_dotenv

# # Принудительно загружаем переменные из .env
# load_dotenv(override=True)

# # Импортируем ваши функции
# from main import extract_text_from_pdf, split_text
# from retriever import store_chunks
# from rag_analyzer import analyze_risk, ask_custom_question 

# print("--- ПРОВЕРКА КЛЮЧА ---")
# current_key = os.getenv("OPENAI_API_KEY")
# if current_key:
#     print(f"Программа видит ключ, начинающийся на: {current_key[:12]}")
# else:
#     print("Программа НЕ ВИДИТ ключ в .env!")
# print("----------------------")

# app = FastAPI()

# # Словарь для хранения сессий (связь chat_id -> filename)
# sessions = {}

# @app.post("/analyze")
# async def analyze(file: UploadFile = File(...), chat_id: str = Body(None)):
#     try:
#         # 1. Сохраняем временный файл
#         temp_path = f"temp_{file.filename}"
#         with open(temp_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         # 2. Извлекаем текст и делим на чанки
#         text = extract_text_from_pdf(temp_path)
#         chunks = split_text(text)
        
#         # 3. Сохраняем в ChromaDB (используя новый retriever.py)
#         store_chunks(chunks, file.filename)

#         # Сохраняем имя файла для текущего чата
#         if chat_id:
#             sessions[chat_id] = file.filename

#         # 4. Анализируем по категориям
#         categories_to_check = [
#             ("Штрафы", "Какие штрафы предусмотрены за нарушения? Укажи номер пункта."),
#             ("Оплата", "Какие условия и сроки оплаты указаны? Укажи номер пункта."),
#             ("Расторжение", "Каков порядок и условия расторжения договора? Укажи номер пункта."),
#             ("Гарантия", "Какие гарантийные обязательства и сроки предусмотрены? Укажи номер пункта.")
#         ]

#         results = []
#         for cat, q in categories_to_check:
#             print(f"🔎 [ANALYZING] Категория: {cat}...")
#             res = analyze_risk(cat, q, file.filename)
#             results.append(res)

#         # Удаляем временный файл
#         if os.path.exists(temp_path):
#             os.remove(temp_path)

#         # Формируем итоговый объект
#         final_data = {
#             "status": "success",
#             "filename": file.filename,
#             "analysis": results
#         }

#         # Возвращаем JSONResponse с поддержкой казахских символов (UTF-8)
#         return JSONResponse(
#             content=json.loads(json.dumps(final_data, ensure_ascii=False)),
#             media_type="application/json; charset=utf-8"
#         )

#     except Exception as e:
#         print(f"❌ Ошибка в /analyze: {e}")
#         return JSONResponse(
#             status_code=500,
#             content={"status": "error", "message": str(e)}
#         )

# @app.post("/chat")
# async def chat(chat_id: str = Body(...), question: str = Body(...)):
#     try:
#         filename = sessions.get(str(chat_id))
#         if not filename:
#             return {"answer": "Пожалуйста, сначала загрузите файл договора для анализа."}

#         # Получаем ответ через RAG
#         answer = ask_custom_question(question, filename)
        
#         return JSONResponse(
#             content={"answer": answer},
#             media_type="application/json; charset=utf-8"
#         )
#     except Exception as e:
#         print(f"❌ Ошибка в /chat: {e}")
#         return {"answer": f"Произошла ошибка: {str(e)}"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
# from fastapi import FastAPI, UploadFile, File, Body
# import os
# import shutil
# from main import extract_text_from_pdf, split_text
# from retriever import store_chunks
# from rag_analyzer import analyze_risk, ask_custom_question 

# print("--- ПРОВЕРКА КЛЮЧА ---")
# current_key = os.getenv("OPENAI_API_KEY")
# if current_key:
#     print(f"Программа видит ключ, начинающийся на: {current_key[:12]}")
# else:
#     print("Программа НЕ ВИДИТ ключ в .env!")
# print("----------------------")

# app = FastAPI()


# sessions = {}

# @app.post("/analyze")
# async def analyze(file: UploadFile = File(...), chat_id: str = Body(None)):
#     temp_path = f"n8n_{file.filename}"
#     with open(temp_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     text = extract_text_from_pdf(temp_path)
#     chunks = split_text(text)
#     store_chunks(chunks, file.filename)

    
#     if chat_id:
#         sessions[chat_id] = file.filename

#     categories_to_check = [
#         ("Штрафы", "Какие штрафы предусмотрены за нарушения?, Укажи номер пункта."),
#         ("Оплата", "Какие условия и сроки оплаты указаны?, Укажи номер пункта."),
#         ("Расторжение", "Каков порядок и условия расторжения договора?, Укажи номер пункта."),
#         ("Гарантия", "Какие гарантийные обязательства и сроки предусмотрены?, Укажи номер пункта.")
#     ]

#     results = []
#     for cat, q in categories_to_check:
#         res = analyze_risk(cat, q, file.filename)
#         results.append(res)

#     os.remove(temp_path)
#     return {"filename": file.filename, "analysis": results}

# @app.post("/chat")
# async def chat(chat_id: str = Body(...), question: str = Body(...)):
    
#     filename = sessions.get(chat_id)
#     if not filename:
#         return {"answer": "Пожалуйста, сначала загрузите файл договора для анализа."}

    
#     answer = ask_custom_question(question, filename)
    
#     return {"answer": answer}