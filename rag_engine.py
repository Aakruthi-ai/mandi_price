import os, json, requests, pickle
import numpy as np
import faiss
from openai import OpenAI
import matplotlib.pyplot as plt

MODEL = "gpt-4o-mini"

# ---------- CLIENT ----------
def get_client():
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise ValueError("Missing OPENAI_API_KEY")
    return OpenAI(api_key=key)

# ---------- LOAD INDEX ----------
def load_index():
    if not os.path.exists("mandi_faiss.index"):
        return None, None, None
    index = faiss.read_index("mandi_faiss.index")
    with open("mandi_meta.pkl", "rb") as f:
        store = pickle.load(f)
    return index, store["metas"], store["docs"]

# ---------- RETRIEVE ----------
def retrieve(query, index, docs, top_k=5):
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    q_vec = model.encode([query]).astype("float32")
    _, idxs = index.search(q_vec, top_k)
    return [docs[i] for i in idxs[0]]

# ---------- SPEECH TO TEXT ----------
def speech_to_text(audio_path, client):
    try:
        with open(audio_path, "rb") as audio:
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=audio
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
    ax.plot(prices, marker='o')
    ax.set_title("Price Trend")
    ax.set_xlabel("Data Points")
    ax.set_ylabel("₹ Price")
    return fig

# ---------- RAG ----------
def rag_query(state, district, market, commodity, variety, grade, language="English"):
    client = get_client()

    index, _, docs = load_index()

    query = f"{commodity} {market} {district} {state}"
    retrieved = retrieve(query, index, docs)

    prompt = f"""
Respond in {language}

Data:
{retrieved}

Give:
- Price range
- Fair price
- Trend
- Advice
"""

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return resp.choices[0].message.content, retrieved
    except:
        return "Error generating response", retrieved
