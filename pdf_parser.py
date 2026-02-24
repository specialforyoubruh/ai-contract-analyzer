from PyPDF2 import PdfReader

# Простой класс для разбиения текста на чанки
class SimpleTextSplitter:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> list[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunks.append(text[start:end])
            start += self.chunk_size - self.chunk_overlap
        return chunks

def extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def split_text(text: str, chunk_size=1000, chunk_overlap=200) -> list[str]:
    splitter = SimpleTextSplitter(chunk_size, chunk_overlap)
    return splitter.split_text(text)



# import os
# import json
# from dotenv import load_dotenv
# from pypdf import PdfReader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from openai import OpenAI

# # =========================
# # 1. ENV + OpenAI client
# # =========================
# load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# # =========================
# # 2. PDF text extraction
# # =========================
# def extract_text_from_pdf(pdf_path: str) -> str:
#     reader = PdfReader(pdf_path)
#     full_text = ""

#     for i, page in enumerate(reader.pages):
#         text = page.extract_text()
#         print(f"[DEBUG] Page {i} text length:", 0 if text is None else len(text))
#         if text:
#             full_text += text + "\n"

#     return full_text


# # =========================
# # 3. Text chunking
# # =========================
# def split_text(text: str) -> list[str]:
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1200,
#         chunk_overlap=150
#     )
#     chunks = splitter.split_text(text)
#     print("[DEBUG] Total chunks:", len(chunks))
#     return chunks


# =========================
# 4. LLM risk analysis
# =========================
# def analyze_chunks(chunks: list[str]) -> list[dict]:
#     results = []

#     for i, chunk in enumerate(chunks):
#         print(f"[DEBUG] Processing chunk {i + 1}/{len(chunks)}")

#         prompt = f"""
# You are a senior legal analyst at a large construction holding (BI Group).

# Analyze the contract text below and identify risks in these categories:

# 1. Penalties above market level (>1–2% of contract value)
# 2. Unrealistic deadlines considering construction industry norms
# 3. Missing mandatory appendices (schedules, cost estimates, timelines)
# 4. Non-compliance with standard BI Group contract terms

# For EACH identified issue return a JSON object with:
# - risk_type (penalty | deadline | appendix | compliance)
# - risk_level (CRITICAL | HIGH | OK)
# - clause (if applicable)
# - description
# - recommendation

# If NO risks are found, return an empty list [].

# Contract text:
# \"\"\"
# {chunk}
# \"\"\"
# """

#         try:
#             response = client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=[
#                     {"role": "system", "content": "You analyze construction contracts for risk."},
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=0
#             )

#             content = response.choices[0].message.content.strip()

#             # защита от некорректного JSON
#             parsed = json.loads(content)
#             results.extend(parsed)

#         except Exception as e:
#             print("[ERROR]", e)

#     return results


# # =========================
# # 5. Report formatting
# # =========================
# def format_report(risks: list[dict]) -> None:
#     if not risks:
#         print("\n✓ OK: Существенные риски не выявлены.")
#         return

#     print("\n========== FINAL RISK REPORT ==========\n")

#     for r in risks:
#         level = r["risk_level"]
#         prefix = {
#             "CRITICAL": "⚠️ КРИТИЧЕСКИЙ РИСК",
#             "HIGH": "⚡ ВЫСОКИЙ РИСК",
#             "OK": "✓ OK"
#         }.get(level, "ℹ️")

#         print(f"{prefix}: {r['description']}")
#         if r.get("clause"):
#             print(f"Пункт договора: {r['clause']}")
#         print(f"Рекомендация: {r['recommendation']}\n")


# # =========================
# # 6. Main pipeline
# # =========================
# def main(pdf_path: str):
#     print("[INFO] Extracting text from PDF...")
#     text = extract_text_from_pdf(pdf_path)

#     if not text.strip():
#         print("[ERROR] No text extracted from PDF")
#         return

#     print("[INFO] Splitting text into chunks...")
#     chunks = split_text(text)

#     print("[INFO] Analyzing risks with LLM...")
#     risks = analyze_chunks(chunks)

#     format_report(risks)


# # =========================
# # 7. Entry point
# # =========================
# if __name__ == "__main__":
    # main("Dogovor.pdf")
