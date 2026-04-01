"""
app.py — Mandi Mitra 🌾
Streamlit frontend: RAG + Grok LLM price intelligence
"""

import os, pickle
import streamlit as st
from pathlib import Path

# ── Page config (MUST be first Streamlit call) ────────────────
st.set_page_config(
    page_title="Mandi Mitra",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
# TRANSLATIONS
# ══════════════════════════════════════════════════════════════
T = {
    "English": {
        "app_title": "Mandi Mitra",
        "app_sub": "AI-Powered Agricultural Price Intelligence",
        "lang_label": "Language / भाषा / ಭಾಷೆ",
        "tab_predict": "📈 Price Intelligence",
        "tab_negotiate": "🤝 Negotiation Assistant",
        "tab_about": "ℹ️ About",
        "state": "State", "district": "District", "market": "Market",
        "commodity": "Commodity", "variety": "Variety", "grade": "Grade",
        "predict_btn": "🔍 Get Price Intelligence",
        "offer_label": "Your Offered Price (₹ per quintal)",
        "offer_placeholder": "e.g. 2500",
        "voice_label": "Or speak your offered price:",
        "evaluate_btn": "⚖️ Evaluate My Offer",
        "live_badge": "🟢 Live data included",
        "no_index": "⚠️ RAG index not found. Please run ingest.py first.",
        "no_key": "⚠️ XAI_API_KEY not set in Streamlit secrets.",
        "spinner_predict": "Consulting market data…",
        "spinner_eval": "Evaluating your offer…",
        "verdict_fair": "✅ Fair Price",
        "verdict_low": "❌ Too Low",
        "verdict_high": "🔺 Above Market",
        "verdict_unknown": "❓ Unknown",
        "fair_price": "Estimated Fair Price",
        "confidence": "Confidence",
        "advice": "Advice",
        "select_hint": "Select all fields to begin",
        "about_text": """
**Mandi Mitra** helps Indian farmers and traders make smarter decisions at the mandi.

**How it works:**
- Historical AGMARKNET data is embedded into a FAISS vector index
- Live prices are fetched from data.gov.in in real time
- Grok-3-mini LLM synthesises both to give you actionable advice

**Built with:** Streamlit · FAISS · sentence-transformers · xAI Grok · data.gov.in

**Languages:** English · हिन्दी · ಕನ್ನಡ
        """,
    },
    "हिन्दी": {
        "app_title": "मंडी मित्र",
        "app_sub": "AI-संचालित कृषि मूल्य सहायक",
        "lang_label": "Language / भाषा / ಭಾಷೆ",
        "tab_predict": "📈 मूल्य जानकारी",
        "tab_negotiate": "🤝 मोल-भाव सहायक",
        "tab_about": "ℹ️ परिचय",
        "state": "राज्य", "district": "जिला", "market": "मंडी",
        "commodity": "फसल", "variety": "किस्म", "grade": "ग्रेड",
        "predict_btn": "🔍 मूल्य जानें",
        "offer_label": "आपका प्रस्तावित मूल्य (₹ प्रति क्विंटल)",
        "offer_placeholder": "जैसे 2500",
        "voice_label": "या बोलकर बताएं:",
        "evaluate_btn": "⚖️ मूल्य जाँचें",
        "live_badge": "🟢 लाइव डेटा शामिल",
        "no_index": "⚠️ RAG इंडेक्स नहीं मिला। पहले ingest.py चलाएं।",
        "no_key": "⚠️ XAI_API_KEY सेट नहीं है।",
        "spinner_predict": "बाज़ार डेटा देख रहे हैं…",
        "spinner_eval": "आपका मूल्य जाँच रहे हैं…",
        "verdict_fair": "✅ उचित मूल्य",
        "verdict_low": "❌ बहुत कम",
        "verdict_high": "🔺 बाज़ार से ऊपर",
        "verdict_unknown": "❓ अज्ञात",
        "fair_price": "अनुमानित उचित मूल्य",
        "confidence": "विश्वास स्तर",
        "advice": "सलाह",
        "select_hint": "शुरू करने के लिए सभी विकल्प चुनें",
        "about_text": """
**मंडी मित्र** भारतीय किसानों और व्यापारियों को मंडी में बेहतर निर्णय लेने में मदद करता है।

**कैसे काम करता है:**
- AGMARKNET के ऐतिहासिक डेटा को FAISS वेक्टर इंडेक्स में संग्रहीत किया जाता है
- data.gov.in से लाइव कीमतें प्राप्त की जाती हैं
- Grok-3-mini LLM दोनों को मिलाकर सलाह देता है
        """,
    },
    "ಕನ್ನಡ": {
        "app_title": "ಮಂಡಿ ಮಿತ್ರ",
        "app_sub": "AI ಆಧಾರಿತ ಕೃಷಿ ಬೆಲೆ ಸಹಾಯಕ",
        "lang_label": "Language / भाषा / ಭಾಷೆ",
        "tab_predict": "📈 ಬೆಲೆ ಮಾಹಿತಿ",
        "tab_negotiate": "🤝 ಚೌಕಾಸಿ ಸಹಾಯಕ",
        "tab_about": "ℹ️ ಪರಿಚಯ",
        "state": "ರಾಜ್ಯ", "district": "ಜಿಲ್ಲೆ", "market": "ಮಾರುಕಟ್ಟೆ",
        "commodity": "ಬೆಳೆ", "variety": "ತಳಿ", "grade": "ದರ್ಜೆ",
        "predict_btn": "🔍 ಬೆಲೆ ತಿಳಿಯಿರಿ",
        "offer_label": "ನಿಮ್ಮ ಪ್ರಸ್ತಾಪಿತ ಬೆಲೆ (₹ ಪ್ರತಿ ಕ್ವಿಂಟಾಲ್)",
        "offer_placeholder": "ಉದಾ. 2500",
        "voice_label": "ಅಥವಾ ಮಾತನಾಡಿ:",
        "evaluate_btn": "⚖️ ಬೆಲೆ ಪರಿಶೀಲಿಸಿ",
        "live_badge": "🟢 ನೇರ ಡೇಟಾ ಸೇರಿದೆ",
        "no_index": "⚠️ RAG ಇಂಡೆಕ್ಸ್ ಕಾಣಿಸಿಲ್ಲ। ingest.py ಮೊದಲು ಚಲಾಯಿಸಿ.",
        "no_key": "⚠️ XAI_API_KEY ಸೆಟ್ ಆಗಿಲ್ಲ.",
        "spinner_predict": "ಮಾರುಕಟ್ಟೆ ಡೇಟಾ ಪರಿಶೀಲಿಸಲಾಗುತ್ತಿದೆ…",
        "spinner_eval": "ನಿಮ್ಮ ಬೆಲೆ ಪರಿಶೀಲಿಸಲಾಗುತ್ತಿದೆ…",
        "verdict_fair": "✅ ಸರಿಯಾದ ಬೆಲೆ",
        "verdict_low": "❌ ತುಂಬಾ ಕಡಿಮೆ",
        "verdict_high": "🔺 ಮಾರುಕಟ್ಟೆಗಿಂತ ಹೆಚ್ಚು",
        "verdict_unknown": "❓ ತಿಳಿದಿಲ್ಲ",
        "fair_price": "ಅಂದಾಜು ನ್ಯಾಯಯುತ ಬೆಲೆ",
        "confidence": "ವಿಶ್ವಾಸ ಮಟ್ಟ",
        "advice": "ಸಲಹೆ",
        "select_hint": "ಪ್ರಾರಂಭಿಸಲು ಎಲ್ಲಾ ಆಯ್ಕೆಗಳನ್ನು ಆರಿಸಿ",
        "about_text": """
**ಮಂಡಿ ಮಿತ್ರ** ಭಾರತೀಯ ರೈತರು ಮತ್ತು ವ್ಯಾಪಾರಿಗಳಿಗೆ ಮಂಡಿಯಲ್ಲಿ ಉತ್ತಮ ನಿರ್ಧಾರ ತೆಗೆದುಕೊಳ್ಳಲು ಸಹಾಯ ಮಾಡುತ್ತದೆ.
        """,
    },
}

# ══════════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tiro+Devanagari+Hindi&family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Root palette ── */
:root {
    --bg:        #0A1628;
    --surface:   #0F2040;
    --surface2:  #162952;
    --border:    #1E3A6E;
    --gold:      #F5A623;
    --gold-dim:  #C4811A;
    --green:     #2ECC71;
    --red:       #E74C3C;
    --blue:      #3498DB;
    --text:      #E8EDF5;
    --muted:     #7A90B8;
    --accent:    #00C9A7;
}

/* ── Global reset ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

/* ── Hero banner ── */
.hero {
    background: linear-gradient(135deg, #0F2040 0%, #0A1628 50%, #0D1F3C 100%);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(245,166,35,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -40px; left: -40px;
    width: 160px; height: 160px;
    background: radial-gradient(circle, rgba(0,201,167,0.10) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3rem;
    font-weight: 900;
    background: linear-gradient(135deg, #F5A623, #FFD700, #F5A623);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.1;
}
.hero-sub {
    color: var(--muted);
    font-size: 1rem;
    margin-top: 0.5rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-weight: 500;
}
.hero-emoji { font-size: 3.5rem; }

/* ── Stripe ── */
.stripe {
    height: 4px;
    background: linear-gradient(90deg, #F5A623, #00C9A7, #3498DB, #F5A623);
    border-radius: 2px;
    margin-bottom: 1.5rem;
    background-size: 200% 100%;
    animation: shimmer 3s linear infinite;
}
@keyframes shimmer {
    0%   { background-position: 0% 0%; }
    100% { background-position: 200% 0%; }
}

/* ── Cards ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.card-gold  { border-left: 4px solid var(--gold); }
.card-green { border-left: 4px solid var(--green); }
.card-red   { border-left: 4px solid var(--red); }
.card-blue  { border-left: 4px solid var(--blue); }

/* ── Section header ── */
.section-head {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    color: var(--gold);
    margin-bottom: 1rem;
    font-weight: 700;
}

/* ── Streamlit widget overrides ── */
[data-testid="stSelectbox"] label,
[data-testid="stNumberInput"] label,
[data-testid="stTextInput"] label,
[data-testid="stRadio"] label,
[data-testid="stAudioInput"] label {
    color: var(--muted) !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}

div[data-baseweb="select"] > div {
    background: var(--surface2) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
}

[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {
    background: var(--surface2) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
}

/* Buttons */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, var(--gold), var(--gold-dim)) !important;
    color: #0A1628 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.65rem 2rem !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.03em !important;
    transition: all 0.2s !important;
    width: 100% !important;
}
[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(245,166,35,0.35) !important;
}

/* Tabs */
[data-testid="stTabs"] [role="tablist"] {
    background: var(--surface) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid var(--border) !important;
}
[data-testid="stTabs"] [role="tab"] {
    color: var(--muted) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: var(--gold) !important;
    color: #0A1628 !important;
}

/* Metrics */
[data-testid="metric-container"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 1rem !important;
}
[data-testid="stMetricValue"] {
    color: var(--gold) !important;
    font-family: 'Playfair Display', serif !important;
    font-size: 2rem !important;
}

/* Progress bar */
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, var(--accent), var(--gold)) !important;
    border-radius: 4px !important;
}

/* Expander */
[data-testid="stExpander"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}

/* Success / warning / error */
[data-testid="stAlert"] {
    border-radius: 12px !important;
}

/* Sidebar radio */
[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    gap: 0.5rem !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SIDEBAR — Profile + Language + info
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    # ── Profile section ──
    st.markdown("""
    <div style="background:linear-gradient(135deg,#162952,#0F2040);border:1px solid #1E3A6E;
                border-radius:16px;padding:1.2rem;margin-bottom:1rem;text-align:center;">
        <div style="font-size:3rem;margin-bottom:0.4rem;">👨‍🌾</div>
        <div style="font-family:'Playfair Display',serif;font-size:1.1rem;
                    color:#F5A623;font-weight:700;">Mandi Mitra User</div>
        <div style="color:#7A90B8;font-size:0.78rem;margin-top:0.2rem;">Farmer / Trader</div>
        <div style="display:flex;justify-content:center;gap:1rem;margin-top:0.8rem;">
            <div style="text-align:center;">
                <div style="color:#F5A623;font-weight:700;font-size:1rem;">2,733</div>
                <div style="color:#7A90B8;font-size:0.7rem;">Records</div>
            </div>
            <div style="width:1px;background:#1E3A6E;"></div>
            <div style="text-align:center;">
                <div style="color:#00C9A7;font-weight:700;font-size:1rem;">Live</div>
                <div style="color:#7A90B8;font-size:0.7rem;">API</div>
            </div>
            <div style="width:1px;background:#1E3A6E;"></div>
            <div style="text-align:center;">
                <div style="color:#3498DB;font-weight:700;font-size:1rem;">3</div>
                <div style="color:#7A90B8;font-size:0.7rem;">Languages</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    lang = st.radio(
        "Language / भाषा / ಭಾಷೆ",
        ["English", "हिन्दी", "ಕನ್ನಡ"],
        index=0,
    )
    tx = T[lang]
    st.markdown("---")
    st.markdown(f'<p style="color:var(--muted);font-size:0.8rem;">🔗 Data: AGMARKNET + data.gov.in<br>🤖 LLM: Grok-3-mini (xAI)<br>🗄️ Vector DB: FAISS</p>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero">
  <div style="display:flex;align-items:center;gap:1.5rem;">
    <div class="hero-emoji">🌾</div>
    <div>
      <div class="hero-title">{tx['app_title']}</div>
      <div class="hero-sub">{tx['app_sub']}</div>
    </div>
  </div>
</div>
<div class="stripe"></div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# LOAD INDEX + CLIENT
# ══════════════════════════════════════════════════════════════
# Inject secret into env so rag_engine.py can find it via os.environ
if "XAI_API_KEY" not in os.environ:
    try:
        os.environ["XAI_API_KEY"] = st.secrets["XAI_API_KEY"]
    except Exception:
        pass

def has_api_key():
    return bool(os.environ.get("XAI_API_KEY", "").strip())

@st.cache_resource(show_spinner="Loading RAG index…")
def load_resources():
    from rag_engine import load_index, get_grok_client
    index, metas, docs = load_index()
    client = get_grok_client()
    return index, metas, docs, client

index, metas, docs, client = load_resources()

# ══════════════════════════════════════════════════════════════
# LOAD DROPDOWN OPTIONS FROM PICKLE
# ══════════════════════════════════════════════════════════════
@st.cache_data
def get_options():
    meta_path = Path("mandi_meta.pkl")
    if not meta_path.exists():
        return {}, {}, {}, {}, {}, {}
    with open(meta_path, "rb") as f:
        store = pickle.load(f)
    docs_list = store.get("docs", [])
    # Parse docs to extract unique values
    states = set(); districts = set(); markets = set()
    commodities = set(); varieties = set(); grades = set()
    for d in docs_list:
        parts = d.split(".")
        for p in parts:
            p = p.strip()
            if " in " in p:
                try:
                    loc = p.split(" in ")[-1]
                    bits = [b.strip() for b in loc.split(",")]
                    if len(bits) >= 3:
                        markets.add(bits[0]); districts.add(bits[1]); states.add(bits[2])
                except: pass
    # Fallback: common Indian states if parsing yields too little
    if len(states) < 3:
        states = {"Karnataka","Maharashtra","Uttar Pradesh","Punjab","Rajasthan",
                  "Madhya Pradesh","Gujarat","Andhra Pradesh","Tamil Nadu","Haryana",
                  "West Bengal","Bihar","Telangana","Odisha","Kerala"}
        districts = {"Bangalore","Mumbai","Lucknow","Amritsar","Jaipur","Bhopal",
                     "Ahmedabad","Hyderabad","Chennai","Chandigarh"}
        markets   = {"Yeshwanthpur","Vashi","Azadpur","Yelahanka","Hubli",
                     "Mysore","Davangere","Tumkur","Shimoga","Belgaum"}
        commodities = {"Onion","Tomato","Potato","Rice","Wheat","Maize","Soybean",
                       "Cotton","Groundnut","Jowar","Bajra","Sugarcane","Chilli","Garlic"}
        varieties   = {"Local","Hybrid","FAQ","Bold","Medium","Fine","Coarse","No.1","No.2","Other"}
        grades      = {"FAQ","Grade A","Grade B","Grade C","Super","Medium","Common"}
    return (sorted(states), sorted(districts), sorted(markets),
            sorted(commodities) if commodities else sorted({"Onion","Tomato","Potato","Rice","Wheat","Maize","Soybean","Cotton","Groundnut","Chilli"}),
            sorted(varieties) if varieties else ["Local","Hybrid","FAQ","Bold","Other"],
            sorted(grades) if grades else ["FAQ","Grade A","Grade B","Common"])

states_opt, districts_opt, markets_opt, commodities_opt, varieties_opt, grades_opt = get_options()

# ══════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs([tx["tab_predict"], tx["tab_negotiate"], tx["tab_about"]])

# ──────────────────────────────────────────────────────────────
# TAB 1 — PRICE INTELLIGENCE
# ──────────────────────────────────────────────────────────────
with tab1:
    if not index:
        st.error(tx["no_index"])
    elif not has_api_key():
        st.error(tx["no_key"])
        st.markdown("**To fix:** Go to Streamlit Cloud → App Settings → Secrets and add:\n```\nXAI_API_KEY = \"xai-your-key-here\"\n```")
    else:
        st.markdown('<div class="card card-gold">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-head">🗺️ {tx["commodity"]} Details</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            state     = st.selectbox(tx["state"],     [""] + states_opt,     key="p_state")
            commodity = st.selectbox(tx["commodity"], [""] + commodities_opt, key="p_commodity")
        with col2:
            district  = st.selectbox(tx["district"],  [""] + districts_opt,  key="p_district")
            variety   = st.selectbox(tx["variety"],   [""] + varieties_opt,  key="p_variety")
        with col3:
            market    = st.selectbox(tx["market"],    [""] + markets_opt,    key="p_market")
            grade     = st.selectbox(tx["grade"],     [""] + grades_opt,     key="p_grade")

        st.markdown("</div>", unsafe_allow_html=True)

        ready = all([state, district, market, commodity, variety, grade])

        if not ready:
            st.info(f"💡 {tx['select_hint']}")
        else:
            if st.button(tx["predict_btn"], key="btn_predict"):
                from rag_engine import rag_query, fetch_live_prices
                live = fetch_live_prices(state, commodity)
                if live:
                    st.toast(tx["live_badge"], icon="🟢")
                with st.spinner(tx["spinner_predict"]):
                    result_text = rag_query(
                        state, district, market, commodity, variety, grade,
                        offered_price=None, language=lang,
                        index=index, docs=docs, client=client, stream=False,
                    )
                st.session_state["predict_result"] = result_text
                st.session_state["last_query"] = dict(
                    state=state, district=district, market=market,
                    commodity=commodity, variety=variety, grade=grade,
                )
                st.toast("Analysis complete!", icon="✅")

        # Result rendered outside button block — no blank space
        if st.session_state.get("predict_result"):
            st.markdown('<div class="card card-gold">', unsafe_allow_html=True)
            st.markdown(f'<div class="section-head">🤖 Mandi Mitra Analysis</div>', unsafe_allow_html=True)
            st.markdown(st.session_state["predict_result"])
            st.markdown("</div>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# TAB 2 — NEGOTIATION
# ──────────────────────────────────────────────────────────────
with tab2:
    if not index:
        st.error(tx["no_index"])
    elif not has_api_key():
        st.error(tx["no_key"])
        st.markdown("**To fix:** Go to Streamlit Cloud → App Settings → Secrets and add:\n```\nXAI_API_KEY = \"xai-your-key-here\"\n```")
    else:
        st.markdown('<div class="card card-blue">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-head">🤝 {tx["tab_negotiate"]}</div>', unsafe_allow_html=True)

        last = st.session_state.get("last_query", {})

        col1, col2, col3 = st.columns(3)
        with col1:
            n_state     = st.selectbox(tx["state"],     [""] + states_opt,     index=(states_opt.index(last.get("state",""))+1) if last.get("state","") in states_opt else 0, key="n_state")
            n_commodity = st.selectbox(tx["commodity"], [""] + commodities_opt, index=(commodities_opt.index(last.get("commodity",""))+1) if last.get("commodity","") in commodities_opt else 0, key="n_commodity")
        with col2:
            n_district  = st.selectbox(tx["district"],  [""] + districts_opt,  key="n_district")
            n_variety   = st.selectbox(tx["variety"],   [""] + varieties_opt,  key="n_variety")
        with col3:
            n_market    = st.selectbox(tx["market"],    [""] + markets_opt,    key="n_market")
            n_grade     = st.selectbox(tx["grade"],     [""] + grades_opt,     key="n_grade")

        st.markdown("</div>", unsafe_allow_html=True)

        # Offer input
        st.markdown('<div class="card card-blue">', unsafe_allow_html=True)
        col_a, col_b = st.columns([1, 1])
        with col_a:
            offered_price = st.number_input(
                tx["offer_label"], min_value=0, step=50,
                placeholder=tx["offer_placeholder"], key="offered_price"
            )
        with col_b:
            st.markdown(f'<p style="color:var(--muted);font-size:0.82rem;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;">{tx["voice_label"]}</p>', unsafe_allow_html=True)
            audio = st.audio_input("🎙️", key="voice_offer", label_visibility="collapsed")
            if audio:
                st.info("🎙️ Audio recorded. Transcription requires a speech-to-text service (e.g. Whisper). Enter price manually above.")
        st.markdown("</div>", unsafe_allow_html=True)

        n_ready = all([n_state, n_district, n_market, n_commodity, n_variety, n_grade]) and offered_price > 0

        if not n_ready:
            st.info(f"💡 {tx['select_hint']}")
        else:
            if st.button(tx["evaluate_btn"], key="btn_evaluate"):
                with st.spinner(tx["spinner_eval"]):
                    from rag_engine import evaluate_offer, retrieve, fetch_live_prices, live_records_to_docs

                    live_records = fetch_live_prices(n_state, n_commodity)
                    live_docs    = live_records_to_docs(live_records)
                    query        = f"{n_commodity} {n_variety} {n_grade} price {n_market} {n_district} {n_state}"
                    retrieved    = retrieve(query, index, docs or [], live_docs=live_docs)

                    result = evaluate_offer(
                        int(offered_price), retrieved, n_commodity, lang, client
                    )

                    verdict = result.get("verdict", "UNKNOWN")
                    fair_p  = result.get("estimated_fair_price", 0)
                    conf    = result.get("confidence_pct", 50)
                    advice  = result.get("advice", "")

                    # Verdict card
                    verdict_map = {
                        "FAIR":    ("card-green", tx["verdict_fair"],  "success"),
                        "LOW":     ("card-red",   tx["verdict_low"],   "error"),
                        "HIGH":    ("card-blue",  tx["verdict_high"],  "info"),
                        "UNKNOWN": ("card-gold",  tx["verdict_unknown"],"warning"),
                    }
                    card_cls, verdict_label, alert_type = verdict_map.get(verdict, verdict_map["UNKNOWN"])

                    st.markdown(f'<div class="card {card_cls}">', unsafe_allow_html=True)

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("🏷️ " + tx["fair_price"], f"₹{fair_p:,}")
                    with col2:
                        st.metric("💸 Your Offer", f"₹{int(offered_price):,}",
                                  delta=f"{int(offered_price)-fair_p:+,}")
                    with col3:
                        st.metric("📊 " + tx["confidence"], f"{conf}%")

                    st.progress(conf / 100)

                    if alert_type == "success":
                        st.success(f"**{verdict_label}** — {advice}")
                    elif alert_type == "error":
                        st.error(f"**{verdict_label}** — {advice}")
                    elif alert_type == "info":
                        st.info(f"**{verdict_label}** — {advice}")
                    else:
                        st.warning(f"**{verdict_label}** — {advice}")

                    # Price band expander
                    with st.expander("📊 Price Band Analysis"):
                        band_low  = int(fair_p * 0.85)
                        band_high = int(fair_p * 1.15)
                        st.markdown(f"""
| Band | Price (₹/quintal) |
|------|-------------------|
| 🔴 Below Fair (reject) | < ₹{band_low:,} |
| 🟡 Negotiate Zone | ₹{band_low:,} – ₹{fair_p:,} |
| 🟢 Fair Price | ₹{fair_p:,} |
| 🔵 Above Market | > ₹{band_high:,} |
""")
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.toast("Evaluation complete!", icon="⚖️")

# ──────────────────────────────────────────────────────────────
# TAB 3 — ABOUT
# ──────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="card card-gold">', unsafe_allow_html=True)
    st.markdown(tx["about_text"])
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📋 System Status")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("RAG Index", "✅ Loaded" if index else "❌ Missing")
    with col2:
        st.metric("Grok API", "✅ Key Set" if has_api_key() else "❌ Not Set")
    with col3:
        st.metric("Live API", "✅ data.gov.in")
    st.markdown("</div>", unsafe_allow_html=True)
