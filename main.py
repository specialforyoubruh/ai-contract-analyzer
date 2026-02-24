import os
import PyPDF2
from retriever import store_chunks
from rag_analyzer import analyze_risk

# --- КОНФИГУРАЦИЯ ---
PDF_FILENAME = "Dogovor.pdf"  # Убедись, что файл лежит рядом с main.py
CONTRACT_ID = "contract_001"

def extract_text_from_pdf(path):
    """Извлекает текст из PDF"""
    if not os.path.exists(path):
        print(f"❌ Файл {path} не найден!")
        return None
    
    text = ""
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            t = page.extract_text()
            if t: text += t + "\n"
    return text

def split_text(text, chunk_size=1000, overlap=100):
    """Разбивает текст на куски"""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunks.append(" ".join(words[i:i + chunk_size]))
    return chunks

def print_report(results):
    """Красивый вывод отчета в консоль"""
    print("\n" + "="*50)
    print(f"📑 ОТЧЕТ О РИСКАХ: {CONTRACT_ID}")
    print("="*50 + "\n")
    
    for res in results:
        level = res.get('risk_level', 'UNKNOWN')
        icon = "🔴" if level == "CRITICAL" else "🟠" if level == "HIGH" else "🟢"
        
        print(f"{icon} КАТЕГОРИЯ: {res['category'].upper()} ({level})")
        print(f"   📌 Пункт: {res.get('clause', '-')}")
        print(f"   📝 Суть: {res.get('description')}")
        print(f"   💡 Совет: {res.get('recommendation')}")
        print("-" * 50)

def main():
    # 1. Чтение PDF
    print("[1/4] Чтение PDF...")
    text = extract_text_from_pdf(PDF_FILENAME)
    if not text: return

    # 2. Обработка и сохранение в базу (Embedding)
    print("[2/4] Подготовка базы знаний...")
    chunks = split_text(text)
    store_chunks(chunks, CONTRACT_ID)
    
    # 3. Анализ рисков (Список вопросов к договору)
    print("[3/4] Анализ рисков через AI...")
    
    risk_checklist = [
        ("Штрафы", "Какие штрафы предусмотрены для Исполнителя за просрочку?"),
        ("Расторжение", "Может ли Заказчик расторгнуть договор в одностороннем порядке?"),
        ("Оплата", "В какой срок производится оплата? Есть ли отсрочки?"),
        ("Гарантия", "Какой гарантийный срок и с какого момента он начинается?")
    ]
    
    results = []
    for category, question in risk_checklist:
        res = analyze_risk(category, question, CONTRACT_ID)
        results.append(res)
        
    # 4. Вывод
    print_report(results)

if __name__ == "__main__":
    main()

# # app.py

# from pdf_parser import extract_text_from_pdf, split_text
# from vector_store import store_chunks
# from rag_analyzer import analyze_with_rag
# from report import format_report

# # =========================
# # 1. Вопросы для анализа (русские)
# # =========================
# RISK_QUESTIONS = {
#     "Штрафы": "Есть ли штрафы выше 1–2% от суммы договора?",
#     "Сроки": "Являются ли сроки выполнения работ нереалистичными для объёма работ?",
#     "Приложения": "Отсутствуют ли обязательные приложения (графики, сметы, сроки)?",
#     "Соответствие": "Соответствует ли договор стандартным условиям BI Group?"
# }

# # =========================
# # 2. Главная функция
# # =========================
# def main():
#     contract_path = "Dogovor.pdf"
#     contract_id = "Dogovor_001"

#     print("[INFO] Парсим PDF...")
#     text = extract_text_from_pdf(contract_path)
#     print(f"[DEBUG] Длина текста: {len(text)}")

#     if not text.strip():
#         print("[ERROR] PDF пустой или PyPDF не смог извлечь текст")
#         return

#     print("[INFO] Разбиваем на чанки...")
#     chunks = split_text(text)
#     print(f"[DEBUG] Количество чанков: {len(chunks)}")

#     print("[INFO] Сохраняем эмбеддинги...")
#     store_chunks(chunks, contract_id)

#     print("[INFO] Запускаем RAG-анализ...")
#     results = {}
#     for category, question in RISK_QUESTIONS.items():
#         print(f"[INFO] Анализируем: {category}...")
#         results[category] = analyze_with_rag(question=question, contract_id=contract_id)

#     print("[INFO] Формируем отчёт...")
#     format_report(results)
#     print("[INFO] Готово!")


# # =========================
# # 3. Точка входа
# # =========================
# if __name__ == "__main__":
#     main()
