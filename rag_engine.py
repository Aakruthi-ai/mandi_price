"""
rag_engine.py — Clean Stable Version
"""

import os
import pickle
import faiss
import numpy as np
import matplotlib.pyplot as plt
from openai import OpenAI

MODEL = "gpt-4o-mini"

# ---------- CLIENT ----------
def get_client():
    return OpenAI()  # reads from environment

# ---------- LOAD INDEX ----------
def load_index():
    try:
        index = faiss.read_index("mandi_faiss.index")
        with open("mandi_meta.pkl", "rb") as f:
            store = pickle.load(f)
        return index, store.get("docs", [])
    except:
        return None, []

# ---------- EMBEDDING ----------
_embedder = None
def get_embedder():
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder

# ---------- RETRIEVE ----------
def retrieve(query, index, docs, top_k=5):
    if index is None or not docs:
        return ["No market data available"]

    embedder = get_embedder()
    q_vec = embedder.encode([query]).astype("float32")
    _, idxs = index.search(q_vec, top_k)

    return [docs[i] for i in idxs[0] if i < len(docs)]

# ---------- SPEECH ----------
def speech_to_text(audio_path, client):
    try:
        with open(audio_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=f
            )
        return transcript.text
    except:
        return ""

# ---------- GRAPH ----------
def generate_price_trend(docs):
    prices = []
    for d in docs:
        try:
            if "Rs." in d:
                prices.append(int(d.split("Rs.")[1].split()[0]))
        except:
            pass

    if len(prices) < 2:
        return None

    fig, ax = plt.subplots()
    ax.plot(prices, marker="o")
    ax.set_title("Price Trend")
    ax.set_xlabel("Samples")
    ax.set_ylabel("₹ Price")
    return fig

# ---------- RAG ----------
def rag_query(state, district, market, commodity, variety, grade, language="English"):
    try:
        client = get_client()

        index, docs = load_index()

        query = f"{commodity} {market} {district} {state}"
        retrieved = retrieve(query, index, docs)

        lang_map = {
            "English": "Respond strictly in English.",
            "हिन्दी": "केवल हिंदी में उत्तर दें। अंग्रेजी का उपयोग न करें।",
            "ಕನ್ನಡ": "ಕನ್ನಡದಲ್ಲಿ ಮಾತ್ರ ಉತ್ತರಿಸಿ. ಇಂಗ್ಲಿಷ್ ಬಳಸದಿರಿ."
        }

        prompt = f"""
{lang_map.get(language)}

Commodity: {commodity}
Location: {market}, {district}, {state}

Data:
{retrieved}

Give:
- Price Range
- Fair Price
- Trend
- Advice
"""

        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        return resp.choices[0].message.content, retrieved

    except Exception as e:
        return f"❌ Error: {str(e)}", []
