from __future__ import annotations
import os, json, pickle, hashlib
import numpy as np
import faiss
from pathlib import Path
from openai import OpenAI

# xAI Client
def get_client():
    return OpenAI(
        api_key=os.environ.get("XAI_API_KEY", ""),
        base_url="https://api.x.ai/v1"
    )

GROK_MODEL = "grok-3-mini"
INDEX_PATH = "mandi_faiss.index"
META_PATH = "mandi_meta.pkl"
TOP_K = 8
DIM = 384


# =====================================================
# LOCAL EMBEDDINGS (NO API REQUIRED)
# =====================================================
def text_to_vector(text):
    vec = np.zeros(DIM, dtype="float32")
    words = text.lower().split()

    for word in words:
        h = int(hashlib.md5(word.encode()).hexdigest(), 16)
        idx = h % DIM
        vec[idx] += 1

    norm = np.linalg.norm(vec)
    return vec if norm == 0 else vec / norm


def embed(texts):
    return np.array([text_to_vector(t) for t in texts]).astype("float32")


# =====================================================
# LOAD INDEX
# =====================================================
def load_index():
    if not Path(INDEX_PATH).exists() or not Path(META_PATH).exists():
        return None, None

    index = faiss.read_index(INDEX_PATH)

    with open(META_PATH, "rb") as f:
        store = pickle.load(f)

    return index, store["docs"]


# =====================================================
# RETRIEVE
# =====================================================
def retrieve(query, index, docs, top_k=TOP_K):
    if index is None or not docs:
        return []

    q_vec = embed([query])
    _, idxs = index.search(q_vec, top_k)

    return [docs[i] for i in idxs[0] if i < len(docs)]


# =====================================================
# PROMPT
# =====================================================
SYSTEM_PROMPT = """
You are Mandi Mitra, expert mandi advisor for Indian farmers.

Reply in same language user selected.

Format:
- Estimated Price Range
- Fair Offer
- Market Trend
- Negotiation Tip
"""


def build_prompt(state, district, market, commodity, variety, grade, language, docs):
    context = "\n".join([f"• {d}" for d in docs])

    lang = {
        "English": "Respond in English.",
        "हिन्दी": "हिन्दी में जवाब दें।",
        "ಕನ್ನಡ": "ಕನ್ನಡದಲ್ಲಿ ಉತ್ತರಿಸಿ।"
    }.get(language, "Respond in English.")

    return f"""
{lang}

Market Data:
{context}

Commodity: {commodity}
Variety: {variety}
Grade: {grade}

Location:
{market}, {district}, {state}

Give smart mandi advice.
"""


# =====================================================
# MAIN QUERY
# =====================================================
def rag_query(state, district, market, commodity, variety, grade,
              offered_price=None, language="English",
              index=None, docs=None, client=None):

    if client is None:
        client = get_client()

    query = f"{commodity} {variety} {grade} {market} {district} {state}"

    retrieved = retrieve(query, index, docs or [])

    prompt = build_prompt(
        state, district, market,
        commodity, variety, grade,
        language, retrieved
    )

    resp = client.chat.completions.create(
        model=GROK_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.3
    )

    return resp.choices[0].message.content


# =====================================================
# OFFER EVALUATION
# =====================================================
def evaluate_offer(offered, retrieved_docs, commodity, language, client):

    context = "\n".join(retrieved_docs[:5])

    prompt = f"""
Based on mandi data:

{context}

Farmer asks Rs.{offered}

Reply ONLY JSON:

{{
"estimated_fair_price": 0,
"verdict":"FAIR",
"confidence_pct":80,
"advice":"text"
}}
"""

    resp = client.chat.completions.create(
        model=GROK_MODEL,
        messages=[
            {"role": "system", "content": "Return only JSON."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200,
        temperature=0.1
    )

    raw = resp.choices[0].message.content.strip()

    try:
        return json.loads(raw)
    except:
        return {
            "estimated_fair_price": offered,
            "verdict": "UNKNOWN",
            "confidence_pct": 50,
            "advice": raw
        }


# Dummy functions so frontend won't break
def fetch_live_prices(state, commodity):
    return []

def live_records_to_docs(records):
    return []
