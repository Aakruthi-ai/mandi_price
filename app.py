"""
rag_engine.py  — Mandi Mitra RAG engine
════════════════════════════════════════
Embeddings : sentence-transformers (FREE, local, no API credits)
LLM        : Grok-3-mini via xAI (only for reasoning/chat)
Vector DB  : FAISS (local)
Live data  : data.gov.in commodity API (free)
"""

from __future__ import annotations
import os, json, time, pickle, requests
import numpy as np
import faiss
from pathlib import Path
from typing import Optional
from openai import OpenAI

# ── Lazy-load embedder so Streamlit startup stays fast ────────
_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder

# ── Grok client (xAI) — for LLM only ─────────────────────────
def get_grok_client() -> OpenAI:
    return OpenAI(
        api_key  = os.environ.get("XAI_API_KEY", ""),
        base_url = "https://api.x.ai/v1",
    )

GROK_MODEL  = "grok-3-mini"
INDEX_PATH  = "mandi_faiss.index"
META_PATH   = "mandi_meta.pkl"
TOP_K       = 8

# ── data.gov.in live API ──────────────────────────────────────
DATGOV_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
DATGOV_KEY = os.environ.get("DATAGOV_API_KEY",
             "579b464db66ec23bdd000001cdd3946e44ce4aab0ddc1fb668bcf87")

# ══════════════════════════════════════════════════════════════
# INDEX LOAD / SAVE
# ══════════════════════════════════════════════════════════════
def load_index():
    if not Path(INDEX_PATH).exists() or not Path(META_PATH).exists():
        return None, None, None
    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "rb") as f:
        store = pickle.load(f)
    return index, store["metas"], store["docs"]

# ══════════════════════════════════════════════════════════════
# LIVE DATA
# ══════════════════════════════════════════════════════════════
def fetch_live_prices(state: str, commodity: str, limit: int = 5) -> list[dict]:
    try:
        r = requests.get(DATGOV_URL, params={
            "api-key": DATGOV_KEY,
            "format":  "json",
            "limit":   limit,
            "filters[state.keyword]":     state,
            "filters[commodity.keyword]": commodity,
        }, timeout=8)
        r.raise_for_status()
        return r.json().get("records", [])
    except Exception as e:
        print(f"[WARN] Live API: {e}")
        return []

def live_records_to_docs(records: list[dict]) -> list[str]:
    docs = []
    for r in records:
        docs.append(
            f"LIVE — In {r.get('market','?')}, {r.get('district','?')}, "
            f"{r.get('state','?')}: {r.get('commodity','?')} "
            f"(Grade {r.get('grade','FAQ')}). "
            f"Modal Rs.{r.get('modal_price','?')} per quintal. "
            f"Min Rs.{r.get('min_price','?')}, Max Rs.{r.get('max_price','?')}. "
            f"Date: {r.get('arrival_date','today')}."
        )
    return docs

# ══════════════════════════════════════════════════════════════
# RETRIEVAL  (local embeddings — free)
# ══════════════════════════════════════════════════════════════
def retrieve(
    query: str,
    index,
    docs: list[str],
    top_k: int = TOP_K,
    live_docs: list[str] | None = None,
) -> list[str]:
    embedder = get_embedder()
    q_vec = embedder.encode([query], normalize_embeddings=True).astype("float32")
    _, idxs = index.search(q_vec, top_k)
    retrieved = [docs[i] for i in idxs[0] if i < len(docs)]
    if live_docs:
        retrieved = live_docs + retrieved
    return retrieved[:top_k + len(live_docs or [])]

# ══════════════════════════════════════════════════════════════
# PROMPT
# ══════════════════════════════════════════════════════════════
SYSTEM_PROMPT = """You are Mandi Mitra, an expert agricultural market advisor for Indian farmers and traders.
You have access to historical AGMARKNET mandi price data and real-time market prices.
Respond in the same language the user used (English / Hindi / Kannada).
Format your response with:
- **Estimated Price Range**: Rs.X – Rs.Y per quintal
- **Fair Offer**: Rs.Z (minimum the farmer should accept)
- **Market Trend**: 1-2 sentences
- **Negotiation Tip**: One practical tip
Keep it concise and farmer-friendly."""

def build_prompt(state, district, market, commodity, variety, grade,
                 offered_price, language, retrieved_docs) -> str:
    context = "\n".join(f"  • {d}" for d in retrieved_docs)
    offer_line = (
        f"\nThe farmer is offering Rs.{offered_price:,} per quintal. Is this fair?"
        if offered_price else ""
    )
    lang_instr = {
        "English": "Respond in English.",
        "हिन्दी":  "हिन्दी में जवाब दें।",
        "ಕನ್ನಡ":  "ಕನ್ನಡದಲ್ಲಿ ಉತ್ತರಿಸಿ.",
    }.get(language, "Respond in English.")

    return f"""{lang_instr}

## Market Data
{context}

## Query
Commodity : {commodity} ({variety}, Grade: {grade})
Location  : {market}, {district}, {state}
{offer_line}

Provide price intelligence and negotiation advice based on the data above."""

# ══════════════════════════════════════════════════════════════
# MAIN RAG QUERY
# ══════════════════════════════════════════════════════════════
def rag_query(state, district, market, commodity, variety, grade,
              offered_price=None, language="English",
              index=None, docs=None, client=None, stream=True):

    if client is None:
        client = get_grok_client()

    live_records = fetch_live_prices(state, commodity)
    live_docs    = live_records_to_docs(live_records)

    query     = f"{commodity} {variety} {grade} price {market} {district} {state}"
    retrieved = retrieve(query, index, docs or [], live_docs=live_docs)

    prompt   = build_prompt(state, district, market, commodity, variety, grade,
                            offered_price, language, retrieved)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": prompt},
    ]

    if stream:
        resp = client.chat.completions.create(
            model=GROK_MODEL, messages=messages,
            stream=True, max_tokens=600, temperature=0.3,
        )
        def _gen():
            for chunk in resp:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        return _gen()
    else:
        resp = client.chat.completions.create(
            model=GROK_MODEL, messages=messages,
            stream=False, max_tokens=600, temperature=0.3,
        )
        return resp.choices[0].message.content

# ══════════════════════════════════════════════════════════════
# OFFER EVALUATION
# ══════════════════════════════════════════════════════════════
def evaluate_offer(offered, retrieved_docs, commodity, language, client) -> dict:
    context = "\n".join(f"• {d}" for d in retrieved_docs[:5])
    prompt  = f"""Based on these mandi prices for {commodity}:
{context}

Farmer offers Rs.{offered:,} per quintal.
Reply ONLY with valid JSON (no markdown, no extra text):
{{
  "estimated_fair_price": <integer>,
  "verdict": "FAIR" | "LOW" | "HIGH",
  "confidence_pct": <0-100>,
  "advice": "<one sentence in {language}>"
}}"""
    resp = client.chat.completions.create(
        model=GROK_MODEL,
        messages=[
            {"role": "system", "content": "You are a mandi price expert. Return only valid JSON."},
            {"role": "user",   "content": prompt},
        ],
        max_tokens=200, temperature=0.1,
    )
    raw = resp.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
    try:
        return json.loads(raw)
    except Exception:
        return {"estimated_fair_price": offered, "verdict": "UNKNOWN",
                "confidence_pct": 50, "advice": raw}
