import os
import json
from openai import OpenAI

# ======================================================
# CLIENT
# ======================================================

def get_client():
    return OpenAI(
        api_key=os.environ.get("XAI_API_KEY"),
        base_url="https://api.x.ai/v1"
    )

# ======================================================
# MODEL
# ======================================================

MODEL = "grok-2-latest"

# ======================================================
# MAIN QUERY
# ======================================================

def rag_query(
    state,
    district,
    market,
    commodity,
    variety,
    grade,
    language,
    client
):

    lang_map = {
        "English":"Respond in English.",
        "हिन्दी":"हिन्दी में उत्तर दें।",
        "ಕನ್ನಡ":"ಕನ್ನಡದಲ್ಲಿ ಉತ್ತರಿಸಿ."
    }

    prompt = f"""
{lang_map.get(language,"Respond in English.")}

You are an expert mandi advisor.

User selected:

State: {state}
District: {district}
Market: {market}
Commodity: {commodity}
Variety: {variety}
Grade: {grade}

Give:

1. Estimated Price Range
2. Fair Offer
3. Market Trend
4. Negotiation Tip

Use ₹ prices.
"""

    try:

        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role":"system","content":"You are Mandi Mitra AI."},
                {"role":"user","content":prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )

        return resp.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"

# ======================================================
# OFFER CHECK
# ======================================================

def evaluate_offer(price, commodity, language, client):

    prompt = f"""
Commodity: {commodity}

Farmer offer price = ₹{price}

Reply only JSON:

{{
"estimated_fair_price": 0,
"verdict":"FAIR or LOW or HIGH",
"confidence_pct":80,
"advice":"short advice"
}}
"""

    try:

        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role":"system","content":"Return only JSON"},
                {"role":"user","content":prompt}
            ],
            temperature=0.1,
            max_tokens=250
        )

        raw = resp.choices[0].message.content.strip()

        return json.loads(raw)

    except Exception as e:

        return {
            "estimated_fair_price":price,
            "verdict":"UNKNOWN",
            "confidence_pct":50,
            "advice":str(e)
        }
