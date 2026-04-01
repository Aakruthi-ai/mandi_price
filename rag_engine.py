"""
rag_engine.py — Mandi Mitra RAG Engine (OpenAI version)
"""

import os
import pickle
import faiss
import numpy as np
import requests
import matplotlib.pyplot as plt
from openai import OpenAI

# ---------------- CONFIG ----------------
MODEL = "gpt-4o-mini"
INDEX_PATH = "mandi_faiss.index"
META_PATH = "mandi_meta.pkl"
TOP_K = 6

# ---------------- CLIENT ----------------
def get_client():
    """
    Uses OPENAI_API_KEY from environment (Streamlit secrets handled in app.py)
    """
    return OpenAI()

# ---------------- LOAD INDEX ----------------
def load_index():
    if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
        return None, [], []

    index = faiss.read_index(INDEX_PATH)

    with open(META_PATH, "rb") as f:
        store = pickle.load(f)

    return index, store.get("metas", []), store.get("docs", [])

# ---------------- EMBEDDING (LAZY LOAD) ----------------
_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder

# ---------------- RETRIEVAL ----------------
def retrieve(query, index, docs, top_k=TOP_K):
    if index is None or not docs:
        return []

    embedder = get_embedder()
    q_vec = embedder.encode([query]).astype("float32")

    _, idxs = index.search(q_vec, top_k)

    results = []
    for i in idxs[0]:
        if i < len(docs):
            results.append(docs[i])

    return results

# ---------------- SPEECH TO TEXT ----------------
def speech_to_text(audio_path, client):
    try:
        with open(audio_path, "rb") as audio:
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=audio
            )
        return transcript.text
    except Exception as e:
        print("STT Error:", e)
        return ""

# ---------------- PRICE TREND GRAPH ----------------
def generate_price_trend(docs):
    prices = []

    for d in docs:
        try:
            if "Rs." in d:
                val = d.split("Rs.")[1].split()[0]
                prices.append(int(val))
        except:
            continue

    if len(prices) < 2:
        return None

    prices = prices[:10]

    fig, ax = plt.subplots()
    ax.plot(prices, marker="o")
    ax.set_title("Price Trend")
    ax.set_xlabel("Data Points")
    ax.set_ylabel("₹ Price")

    return fig

# ---------------- PROMPT BUILDER ----------------
def build_prompt(state, district, market, commodity, variety, grade, language, docs):
    
    lang_map = {
        "English": "Respond strictly in English.",
        "हिन्दी": "केवल हिंदी में उत्तर दें।",
        "ಕನ್ನಡ": "ಕನ್ನಡದಲ್ಲಿ ಮಾತ್ರ ಉತ್ತರಿಸಿ."
    }

    lang_instruction = lang_map.get(language, "Respond in English.")

    context = "\n".join([f"- {d}" for d in docs])

    prompt = f"""
{lang_instruction}

You are an expert agricultural advisor.

Market Data:
{context}

User Query:
Commodity: {commodity}
Variety: {variety}
Grade: {grade}
Location: {market}, {district}, {state}

Provide:
1. Estimated Price Range (₹ per quintal)
2. Fair Price
3. Market Trend (1-2 lines)
4. Negotiation Advice
"""

    return prompt

# ---------------- MAIN RAG QUERY ----------------
def rag_query(state, district, market, commodity, variety, grade, language="English"):
    
    client = get_client()

    index, metas, docs = load_index()

    query = f"{commodity} {market} {district} {state}"
    retrieved_docs = retrieve(query, index, docs)

    prompt = build_prompt(
        state, district, market,
        commodity, variety, grade,
        language, retrieved_docs
    )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a mandi price expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )

        answer = response.choices[0].message.content

        return answer, retrieved_docs

    except Exception as e:
        print("LLM Error:", e)
        return "⚠️ Unable to fetch AI response. Please try again.", retrieved_docs

# ---------------- OFFER EVALUATION (BONUS) ----------------
def evaluate_offer(offered_price, docs, commodity, language):
    client = get_client()

    context = "\n".join(docs[:5])

    prompt = f"""
Based on mandi prices:

{context}

User offered ₹{offered_price} for {commodity}.

Respond in {language} and return:
- Fair price
- Verdict (Fair / Low / High)
- Advice
"""

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        return resp.choices[0].message.content

    except:
        return "⚠️ Could not evaluate offer."
