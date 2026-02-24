import streamlit as st
import os
from main import extract_text_from_pdf, split_text
from retriever import store_chunks
from rag_analyzer import analyze_risk

st.set_page_config(page_title="AI Lawyer - Risk Analysis", layout="wide")

st.title("⚖️ Construction Contract Analyzer")
st.write("Upload a PDF contract, and AI will identify hidden risks in seconds.")

# --- CHANGE 1: Language Selection ---
language = st.radio("Select Language / Выберите язык / Тілді таңдаңыз", ["EN", "RU", "KZ"], horizontal=True)

# --- CHANGE 2: Multilingual Questions & Labels ---
if language == "EN":
    risk_checklist = [
        ("Penalties", "What penalties are provided for the Contractor for delay?"),
        ("Termination", "Can the Client terminate the contract unilaterally?"),
        ("Payment", "What is the payment timeframe?"),
        ("Warranty", "What is the warranty period?")
    ]
    labels = {"clause": "Clause", "desc": "Description", "adv": "Advice", "loading": "Analyzing"}
elif language == "KZ":
    risk_checklist = [
        ("Айыппұлдар", "Мердігер үшін мерзімін өткізіп алғаны үшін қандай айыппұлдар қарастырылған?"),
        ("Бұзу", "Тапсырыс беруші шартты біржақты тәртіппен бұза ала ма?"),
        ("Төлем", "Төлем қандай мерзімде жүзеге асырылады?"),
        ("Кепілдік", "Кепілдік мерзімі қандай?")
    ]
    labels = {"clause": "Тармақ", "desc": "Сипаттама", "adv": "Кеңес", "loading": "Талдау"}
else:  # RU
    risk_checklist = [
        ("Штрафы", "Какие штрафы предусмотрены для Исполнителя за просрочку?"),
        ("Расторжение", "Может ли Заказчик расторгнуть договор в одностороннем порядке?"),
        ("Оплата", "В какой срок производится оплата?"),
        ("Гарантия", "Какой гарантийный срок?")
    ]
    labels = {"clause": "Пункт", "desc": "Описание", "adv": "Совет", "loading": "Анализируем"}

uploaded_file = st.file_uploader("Upload PDF file", type="pdf")

if uploaded_file:
    temp_path = os.path.join("temp_" + uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.info(f"Processing file: {uploaded_file.name}...")

    text = extract_text_from_pdf(temp_path)
    if text:
        chunks = split_text(text)
        contract_id = uploaded_file.name 
        store_chunks(chunks, contract_id)

        st.subheader("📊 Analysis Results")
        
        cols = st.columns(2) 
        for i, (category, question) in enumerate(risk_checklist):
            with cols[i % 2]:
                with st.spinner(f"{labels['loading']}: {category}..."):
                    # --- FIXED LINE: Added language=language ---
                    res = analyze_risk(category, question, contract_id, language=language)
                    
                    # UI color logic
                    color = "red" if res['risk_level'] in ["CRITICAL", "HIGH"] else "orange" if res['risk_level'] == "MEDIUM" else "green"
                    
                    st.markdown(f"### :{color}[{category} - {res['risk_level']}]")
                    st.write(f"**{labels['clause']}:** {res.get('clause', 'N/A')}")
                    st.info(f"**{labels['desc']}:** {res['description']}")
                    st.success(f"**{labels['adv']}:** {res['recommendation']}")
                    st.divider()

    os.remove(temp_path)
# import streamlit as st
# import os
# from main import extract_text_from_pdf, split_text
# from retriever import store_chunks
# from rag_analyzer import analyze_risk

# st.set_page_config(page_title="AI Lawyer - Risk Analysis", layout="wide")

# st.title("⚖️ Construction Contract Analyzer")
# st.write("Upload a PDF contract, and AI will identify hidden risks in seconds.")

# # --- CHANGE 1: Language Selection ---
# language = st.radio("Select Language / Выберите язык / Тілді таңдаңыз", ["EN", "RU", "KZ"], horizontal=True)

# # --- CHANGE 2: Multilingual Questions & Labels ---
# if language == "EN":
#     risk_checklist = [
#         ("Penalties", "What penalties are provided for the Contractor for delay?"),
#         ("Termination", "Can the Client terminate the contract unilaterally?"),
#         ("Payment", "What is the payment timeframe?"),
#         ("Warranty", "What is the warranty period?")
#     ]
#     labels = {"clause": "Clause", "desc": "Description", "adv": "Advice", "loading": "Analyzing"}
# elif language == "KZ":
#     risk_checklist = [
#         ("Айыппұлдар", "Мердігер үшін мерзімін өткізіп алғаны үшін қандай айыппұлдар қарастырылған?"),
#         ("Бұзу", "Тапсырыс беруші шартты біржақты тәртіппен бұза ала ма?"),
#         ("Төлем", "Төлем қандай мерзімде жүзеге асырылады?"),
#         ("Кепілдік", "Кепілдік мерзімі қандай?")
#     ]
#     labels = {"clause": "Тармақ", "desc": "Сипаттама", "adv": "Кеңес", "loading": "Талдау"}
# else:  # RU
#     risk_checklist = [
#         ("Штрафы", "Какие штрафы предусмотрены для Исполнителя за просрочку?"),
#         ("Расторжение", "Может ли Заказчик расторгнуть договор в одностороннем порядке?"),
#         ("Оплата", "В какой срок производится оплата?"),
#         ("Гарантия", "Какой гарантийный срок?")
#     ]
#     labels = {"clause": "Пункт", "desc": "Описание", "adv": "Совет", "loading": "Анализируем"}

# uploaded_file = st.file_uploader("Upload PDF file", type="pdf")

# if uploaded_file:
#     temp_path = os.path.join("temp_" + uploaded_file.name)
#     with open(temp_path, "wb") as f:
#         f.write(uploaded_file.getbuffer())

#     st.info(f"Processing file: {uploaded_file.name}...")

#     text = extract_text_from_pdf(temp_path)
#     if text:
#         chunks = split_text(text)
#         contract_id = uploaded_file.name 
#         store_chunks(chunks, contract_id)

#         st.subheader("📊 Analysis Results")
        
#         cols = st.columns(2) 
#         for i, (category, question) in enumerate(risk_checklist):
#             with cols[i % 2]:
#                 with st.spinner(f"{labels['loading']}: {category}..."):
#                     res = analyze_risk(category, question, contract_id)
                    
#                     # UI color logic
#                     color = "red" if res['risk_level'] in ["CRITICAL", "HIGH"] else "orange" if res['risk_level'] == "MEDIUM" else "green"
                    
#                     st.markdown(f"### :{color}[{category} - {res['risk_level']}]")
#                     st.write(f"**{labels['clause']}:** {res.get('clause', 'N/A')}")
#                     st.info(f"**{labels['desc']}:** {res['description']}")
#                     st.success(f"**{labels['adv']}:** {res['recommendation']}")
#                     st.divider()

#     os.remove(temp_path)
# import streamlit as st
# import os
# from main import extract_text_from_pdf, split_text
# from retriever import store_chunks
# from rag_analyzer import analyze_risk


# st.set_page_config(page_title="AI Юрист - Анализ рисков", layout="wide")

# st.title("⚖️ Анализатор строительных договоров")
# st.write("Загрузите PDF-договор, и ИИ найдет скрытые риски за 30 секунд.")


# uploaded_file = st.file_uploader("Выберите файл PDF", type="pdf")

# if uploaded_file:
   
#     temp_path = os.path.join("temp_" + uploaded_file.name)
#     with open(temp_path, "wb") as f:
#         f.write(uploaded_file.getbuffer())

#     st.info(f"обработка файла: {uploaded_file.name}...")

    
#     text = extract_text_from_pdf(temp_path)
#     if text:
#         chunks = split_text(text)
        
#         contract_id = uploaded_file.name 
#         store_chunks(chunks, contract_id)

        
#         risk_checklist = [
#             ("Штрафы", "Какие штрафы предусмотрены для Исполнителя за просрочку?"),
#             ("Расторжение", "Может ли Заказчик расторгнуть договор в одностороннем порядке?"),
#             ("Оплата", "В какой срок производится оплата?"),
#             ("Гарантия", "Какой гарантийный срок?")
#         ]

#         st.subheader("📊 Результаты анализа")
        
        
#         cols = st.columns(2) 
#         for i, (category, question) in enumerate(risk_checklist):
#             with cols[i % 2]:
#                 with st.spinner(f"Анализируем: {category}..."):
#                     res = analyze_risk(category, question, contract_id)
                    
                   
#                     color = "red" if res['risk_level'] in ["CRITICAL", "HIGH"] else "orange" if res['risk_level'] == "MEDIUM" else "green"
                    
#                     st.markdown(f"### :{color}[{category} - {res['risk_level']}]")
#                     st.write(f"**Пункт:** {res.get('clause', 'Не найден')}")
#                     st.info(f"**Описание:** {res['description']}")
#                     st.success(f"**Совет:** {res['recommendation']}")
#                     st.divider()

    
#     os.remove(temp_path)