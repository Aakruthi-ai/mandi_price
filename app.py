"""
app.py — Mandi Mitra 🌾
Streamlit frontend: RAG + Grok LLM price intelligence
"""

import os, pickle
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Mandi Mitra",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
# DROPDOWN OPTIONS — translated per language
# ══════════════════════════════════════════════════════════════
STATES = ["Andhra Pradesh","Bihar","Gujarat","Haryana","Karnataka","Kerala",
          "Madhya Pradesh","Maharashtra","Odisha","Punjab","Rajasthan",
          "Tamil Nadu","Telangana","Uttar Pradesh","West Bengal"]

DISTRICTS = ["Ahmedabad","Amritsar","Bangalore","Belgaum","Bhopal","Chandigarh",
             "Chennai","Davangere","Hubli","Hyderabad","Jaipur","Lucknow",
             "Mumbai","Mysore","Shimoga","Tumkur","Yelahanka","Yeshwanthpur"]

MARKETS = ["Azadpur","Belgaum","Davangere","Hubli","Mysore","Shimoga",
           "Tumkur","Vashi","Yelahanka","Yeshwanthpur"]

COMMODITIES_EN = ["Bajra","Chilli","Cotton","Garlic","Groundnut","Jowar",
                  "Maize","Onion","Potato","Rice","Soybean","Sugarcane","Tomato","Wheat"]
COMMODITIES_HI = ["बाजरा","मिर्च","कपास","लहसुन","मूंगफली","ज्वार",
                  "मक्का","प्याज","आलू","चावल","सोयाबीन","गन्ना","टमाटर","गेहूँ"]
COMMODITIES_KN = ["ಸಜ್ಜೆ","ಮೆಣಸಿನಕಾಯಿ","ಹತ್ತಿ","ಬೆಳ್ಳುಳ್ಳಿ","ಕಡಲೆಕಾಯಿ","ಜೋಳ",
                  "ಮೆಕ್ಕೆಜೋಳ","ಈರುಳ್ಳಿ","ಆಲೂಗಡ್ಡೆ","ಅಕ್ಕಿ","ಸೋಯಾಬೀನ್","ಕಬ್ಬು","ಟೊಮೆಟೊ","ಗೋಧಿ"]

VARIETIES_EN = ["Bold","Coarse","FAQ","Fine","Hybrid","Local","Medium","No.1","No.2","Other"]
VARIETIES_HI = ["मोटा","मोटा दाना","FAQ","बारीक","हाइब्रिड","देसी","मध्यम","नं.1","नं.2","अन्य"]
VARIETIES_KN = ["ದಪ್ಪ","ಒರಟು","FAQ","ನುಣ್ಣಗೆ","ಹೈಬ್ರಿಡ್","ದೇಸಿ","ಮಧ್ಯಮ","ನಂ.1","ನಂ.2","ಇತರ"]

GRADES_EN = ["Common","FAQ","Grade A","Grade B","Grade C","Medium","Super"]
GRADES_HI = ["सामान्य","FAQ","ग्रेड A","ग्रेड B","ग्रेड C","मध्यम","सुपर"]
GRADES_KN = ["ಸಾಮಾನ್ಯ","FAQ","ದರ್ಜೆ A","ದರ್ಜೆ B","ದರ್ಜೆ C","ಮಧ್ಯಮ","ಸೂಪರ್"]

# ══════════════════════════════════════════════════════════════
# TRANSLATIONS
# ══════════════════════════════════════════════════════════════
T = {
    "English": {
        "app_title": "Mandi Mitra",
        "app_sub": "AI-Powered Agricultural Price Intelligence",
        "tab_predict": "📈 Price Intelligence",
        "tab_negotiate": "🤝 Negotiation Assistant",
        "tab_about": "ℹ️ About",
        "state": "State", "district": "District", "market": "Market",
        "commodity": "Commodity", "variety": "Variety", "grade": "Grade",
        "predict_btn": "🔍 Get Price Intelligence",
        "offer_label": "Your Offered Price (Rs. per quintal)",
        "voice_label": "Or speak your offered price:",
        "evaluate_btn": "⚖️ Evaluate My Offer",
        "live_badge": "Live data included",
        "no_index": "RAG index not found. Please run ingest.py first.",
        "no_key": "XAI_API_KEY not set in Streamlit secrets.",
        "spinner_predict": "Consulting market data…",
        "spinner_eval": "Evaluating your offer…",
        "verdict_fair": "✅ Fair Price",
        "verdict_low": "❌ Too Low",
        "verdict_high": "🔺 Above Market",
        "verdict_unknown": "❓ Unknown",
        "fair_price": "Est. Fair Price",
        "your_offer": "Your Offer",
        "confidence": "Confidence",
        "select_hint": "Select all fields to begin",
        "analysis_head": "🤖 Mandi Mitra Analysis",
        "price_band": "📊 Price Band Analysis",
        "band_reject": "Below Fair (reject)",
        "band_neg": "Negotiate Zone",
        "band_fair": "Fair Price",
        "band_above": "Above Market",
        "commodities": COMMODITIES_EN,
        "varieties":   VARIETIES_EN,
        "grades":      GRADES_EN,
        "about_text": "**Mandi Mitra** helps Indian farmers and traders make smarter mandi decisions.\n\n**Stack:** Streamlit · FAISS · xAI Grok · data.gov.in\n\n**Languages:** English · हिन्दी · ಕನ್ನಡ",
    },
    "हिन्दी": {
        "app_title": "मंडी मित्र",
        "app_sub": "AI-संचालित कृषि मूल्य सहायक",
        "tab_predict": "📈 मूल्य जानकारी",
        "tab_negotiate": "🤝 मोल-भाव सहायक",
        "tab_about": "ℹ️ परिचय",
        "state": "राज्य", "district": "जिला", "market": "मंडी",
        "commodity": "फसल", "variety": "किस्म", "grade": "ग्रेड",
        "predict_btn": "🔍 मूल्य जानें",
        "offer_label": "आपका प्रस्तावित मूल्य (₹ प्रति क्विंटल)",
        "voice_label": "या बोलकर बताएं:",
        "evaluate_btn": "⚖️ मूल्य जाँचें",
        "live_badge": "लाइव डेटा शामिल",
        "no_index": "RAG इंडेक्स नहीं मिला।",
        "no_key": "XAI_API_KEY सेट नहीं है।",
        "spinner_predict": "बाज़ार डेटा देख रहे हैं…",
        "spinner_eval": "आपका मूल्य जाँच रहे हैं…",
        "verdict_fair": "✅ उचित मूल्य",
        "verdict_low": "❌ बहुत कम",
        "verdict_high": "🔺 बाज़ार से ऊपर",
        "verdict_unknown": "❓ अज्ञात",
        "fair_price": "उचित मूल्य",
        "your_offer": "आपका मूल्य",
        "confidence": "विश्वास स्तर",
        "select_hint": "शुरू करने के लिए सभी विकल्प चुनें",
        "analysis_head": "🤖 मंडी मित्र विश्लेषण",
        "price_band": "📊 मूल्य बैंड विश्लेषण",
        "band_reject": "बहुत कम (अस्वीकार करें)",
        "band_neg": "मोल-भाव क्षेत्र",
        "band_fair": "उचित मूल्य",
        "band_above": "बाज़ार से ऊपर",
        "commodities": COMMODITIES_HI,
        "varieties":   VARIETIES_HI,
        "grades":      GRADES_HI,
        "about_text": "**मंडी मित्र** भारतीय किसानों और व्यापारियों को मंडी में बेहतर निर्णय लेने में मदद करता है।\n\n**स्टैक:** Streamlit · FAISS · xAI Grok · data.gov.in",
    },
    "ಕನ್ನಡ": {
        "app_title": "ಮಂಡಿ ಮಿತ್ರ",
        "app_sub": "AI ಆಧಾರಿತ ಕೃಷಿ ಬೆಲೆ ಸಹಾಯಕ",
        "tab_predict": "📈 ಬೆಲೆ ಮಾಹಿತಿ",
        "tab_negotiate": "🤝 ಚೌಕಾಸಿ ಸಹಾಯಕ",
        "tab_about": "ℹ️ ಪರಿಚಯ",
        "state": "ರಾಜ್ಯ", "district": "ಜಿಲ್ಲೆ", "market": "ಮಾರುಕಟ್ಟೆ",
        "commodity": "ಬೆಳೆ", "variety": "ತಳಿ", "grade": "ದರ್ಜೆ",
        "predict_btn": "🔍 ಬೆಲೆ ತಿಳಿಯಿರಿ",
        "offer_label": "ನಿಮ್ಮ ಪ್ರಸ್ತಾಪಿತ ಬೆಲೆ (₹ ಪ್ರತಿ ಕ್ವಿಂಟಾಲ್)",
        "voice_label": "ಅಥವಾ ಮಾತನಾಡಿ:",
        "evaluate_btn": "⚖️ ಬೆಲೆ ಪರಿಶೀಲಿಸಿ",
        "live_badge": "ನೇರ ಡೇಟಾ ಸೇರಿದೆ",
        "no_index": "RAG ಇಂಡೆಕ್ಸ್ ಕಾಣಿಸಿಲ್ಲ.",
        "no_key": "XAI_API_KEY ಸೆಟ್ ಆಗಿಲ್ಲ.",
        "spinner_predict": "ಮಾರುಕಟ್ಟೆ ಡೇಟಾ ಪರಿಶೀಲಿಸಲಾಗುತ್ತಿದೆ…",
        "spinner_eval": "ನಿಮ್ಮ ಬೆಲೆ ಪರಿಶೀಲಿಸಲಾಗುತ್ತಿದೆ…",
        "verdict_fair": "✅ ಸರಿಯಾದ ಬೆಲೆ",
        "verdict_low": "❌ ತುಂಬಾ ಕಡಿಮೆ",
        "verdict_high": "🔺 ಮಾರುಕಟ್ಟೆಗಿಂತ ಹೆಚ್ಚು",
        "verdict_unknown": "❓ ತಿಳಿದಿಲ್ಲ",
        "fair_price": "ನ್ಯಾಯಯುತ ಬೆಲೆ",
        "your_offer": "ನಿಮ್ಮ ಬೆಲೆ",
        "confidence": "ವಿಶ್ವಾಸ ಮಟ್ಟ",
        "select_hint": "ಪ್ರಾರಂಭಿಸಲು ಎಲ್ಲಾ ಆಯ್ಕೆಗಳನ್ನು ಆರಿಸಿ",
        "analysis_head": "🤖 ಮಂಡಿ ಮಿತ್ರ ವಿಶ್ಲೇಷಣೆ",
        "price_band": "📊 ಬೆಲೆ ಬ್ಯಾಂಡ್ ವಿಶ್ಲೇಷಣೆ",
        "band_reject": "ತುಂಬಾ ಕಡಿಮೆ (ತಿರಸ್ಕರಿಸಿ)",
        "band_neg": "ಚೌಕಾಸಿ ವಲಯ",
        "band_fair": "ನ್ಯಾಯಯುತ ಬೆಲೆ",
        "band_above": "ಮಾರುಕಟ್ಟೆಗಿಂತ ಹೆಚ್ಚು",
        "commodities": COMMODITIES_KN,
        "varieties":   VARIETIES_KN,
        "grades":      GRADES_KN,
        "about_text": "**ಮಂಡಿ ಮಿತ್ರ** ಭಾರತೀಯ ರೈತರು ಮತ್ತು ವ್ಯಾಪಾರಿಗಳಿಗೆ ಮಂಡಿಯಲ್ಲಿ ಉತ್ತಮ ನಿರ್ಧಾರ ತೆಗೆದುಕೊಳ್ಳಲು ಸಹಾಯ ಮಾಡುತ್ತದೆ.\n\n**ಸ್ಟ್ಯಾಕ್:** Streamlit · FAISS · xAI Grok · data.gov.in",
    },
}

# ══════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&display=swap');
:root{--bg:#0A1628;--surface:#0F2040;--surface2:#162952;--border:#1E3A6E;
      --gold:#F5A623;--gold-dim:#C4811A;--green:#2ECC71;--red:#E74C3C;
      --blue:#3498DB;--text:#E8EDF5;--muted:#7A90B8;--accent:#00C9A7;}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--text)!important;font-family:'DM Sans',sans-serif!important;}
[data-testid="stSidebar"]{background:var(--surface)!important;border-right:1px solid var(--border)!important;}
.hero{background:linear-gradient(135deg,#0F2040,#0A1628,#0D1F3C);border:1px solid var(--border);
      border-radius:20px;padding:2rem 2.5rem;margin-bottom:1rem;position:relative;overflow:hidden;}
.hero::before{content:'';position:absolute;top:-60px;right:-60px;width:220px;height:220px;
              background:radial-gradient(circle,rgba(245,166,35,.12),transparent 70%);border-radius:50%;}
.hero-title{font-family:'Playfair Display',serif;font-size:2.6rem;font-weight:900;
            background:linear-gradient(135deg,#F5A623,#FFD700,#F5A623);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin:0;}
.hero-sub{color:var(--muted);font-size:.9rem;margin-top:.3rem;letter-spacing:.07em;text-transform:uppercase;}
.stripe{height:4px;border-radius:2px;margin-bottom:1.2rem;
        background:linear-gradient(90deg,#F5A623,#00C9A7,#3498DB,#F5A623);
        background-size:200%;animation:shimmer 3s linear infinite;}
@keyframes shimmer{0%{background-position:0%}100%{background-position:200%}}
.card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:1.3rem;margin-bottom:.8rem;}
.card-gold{border-left:4px solid var(--gold);}
.card-green{border-left:4px solid var(--green);}
.card-red{border-left:4px solid var(--red);}
.card-blue{border-left:4px solid var(--blue);}
.section-head{font-family:'Playfair Display',serif;font-size:1.15rem;color:var(--gold);margin-bottom:.7rem;font-weight:700;}
[data-testid="stSelectbox"] label,[data-testid="stNumberInput"] label,[data-testid="stAudioInput"] label{
    color:var(--muted)!important;font-size:.78rem!important;font-weight:600!important;
    letter-spacing:.06em!important;text-transform:uppercase!important;}
div[data-baseweb="select"]>div{background:var(--surface2)!important;border-color:var(--border)!important;
    color:var(--text)!important;border-radius:10px!important;}
[data-testid="stNumberInput"] input{background:var(--surface2)!important;border-color:var(--border)!important;
    color:var(--text)!important;border-radius:10px!important;}
[data-testid="stButton"]>button[kind="primary"]{
    background:linear-gradient(135deg,var(--gold),var(--gold-dim))!important;
    color:#0A1628!important;font-weight:700!important;border:none!important;
    border-radius:12px!important;padding:.6rem 1.8rem!important;width:100%!important;transition:all .2s!important;}
[data-testid="stButton"]>button[kind="primary"]:hover{transform:translateY(-2px)!important;
    box-shadow:0 8px 24px rgba(245,166,35,.35)!important;}
[data-testid="stButton"]>button[kind="secondary"]{
    background:transparent!important;color:var(--muted)!important;
    border:1px solid var(--border)!important;border-radius:12px!important;
    padding:.6rem 1.8rem!important;width:100%!important;transition:all .2s!important;}
[data-testid="stButton"]>button[kind="secondary"]:hover{border-color:var(--gold)!important;color:var(--gold)!important;}
[data-testid="stTabs"] [role="tablist"]{background:var(--surface)!important;border-radius:12px!important;
    padding:4px!important;border:1px solid var(--border)!important;margin-bottom:1rem!important;}
[data-testid="stTabs"] [role="tab"]{color:var(--muted)!important;border-radius:10px!important;font-weight:600!important;}
[data-testid="stTabs"] [role="tab"][aria-selected="true"]{background:var(--gold)!important;color:#0A1628!important;}
[data-testid="metric-container"]{background:var(--surface2)!important;border:1px solid var(--border)!important;
    border-radius:14px!important;padding:1rem!important;}
[data-testid="stMetricValue"]{color:var(--gold)!important;font-family:'Playfair Display',serif!important;font-size:1.7rem!important;}
[data-testid="stProgress"]>div>div{background:linear-gradient(90deg,var(--accent),var(--gold))!important;border-radius:4px!important;}
[data-testid="stExpander"]{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:12px!important;}
[data-testid="stAlert"]{border-radius:12px!important;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════
if "lang" not in st.session_state:
    st.session_state["lang"] = "English"

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#162952,#0F2040);border:1px solid #1E3A6E;
                border-radius:16px;padding:1.2rem;text-align:center;margin-bottom:1rem;">
        <div style="font-size:3rem;margin-bottom:.3rem;">👨‍🌾</div>
        <div style="font-family:'Playfair Display',serif;font-size:1.1rem;color:#F5A623;font-weight:700;">Mandi Mitra User</div>
        <div style="color:#7A90B8;font-size:.78rem;margin-top:.2rem;">Farmer / Trader</div>
        <div style="display:flex;justify-content:center;gap:1rem;margin-top:.8rem;">
            <div style="text-align:center;"><div style="color:#F5A623;font-weight:700;">2,733</div><div style="color:#7A90B8;font-size:.7rem;">Records</div></div>
            <div style="width:1px;background:#1E3A6E;"></div>
            <div style="text-align:center;"><div style="color:#00C9A7;font-weight:700;">Live</div><div style="color:#7A90B8;font-size:.7rem;">API</div></div>
            <div style="width:1px;background:#1E3A6E;"></div>
            <div style="text-align:center;"><div style="color:#3498DB;font-weight:700;">3</div><div style="color:#7A90B8;font-size:.7rem;">Languages</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<p style="color:#7A90B8;font-size:.75rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;margin-bottom:.4rem;">🌐 Language / भाषा / ಭಾಷೆ</p>', unsafe_allow_html=True)
    for _lbl, _key in [("🇬🇧  English","English"),("🇮🇳  हिन्दी","हिन्दी"),("🌿  ಕನ್ನಡ","ಕನ್ನಡ")]:
        if st.button(_lbl, key=f"sb_{_key}",
                     type="primary" if st.session_state["lang"]==_key else "secondary",
                     use_container_width=True):
            st.session_state["lang"] = _key
            st.rerun()
    st.markdown("---")
    st.markdown('<p style="color:#7A90B8;font-size:.8rem;">🔗 AGMARKNET + data.gov.in<br>🤖 Grok-3-mini (xAI)<br>🗄️ FAISS vector DB</p>', unsafe_allow_html=True)

lang = st.session_state["lang"]
tx   = T[lang]

# ══════════════════════════════════════════════════════════════
# INJECT SECRET + LOAD
# ══════════════════════════════════════════════════════════════
if "XAI_API_KEY" not in os.environ:
    try:
        os.environ["XAI_API_KEY"] = st.secrets["XAI_API_KEY"]
    except Exception:
        pass

def has_api_key():
    return bool(os.environ.get("XAI_API_KEY","").strip())

@st.cache_resource(show_spinner="Loading RAG index…")
def load_resources():
    from rag_engine import load_index, get_client
    index, docs = load_index()
    client = get_client()
    return index, docs, client

index, docs, client = load_resources()

# ══════════════════════════════════════════════════════════════
# HERO  (no language pill bar here)
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero">
  <div style="display:flex;align-items:center;gap:1.5rem;">
    <div style="font-size:3rem;">🌾</div>
    <div>
      <div class="hero-title">{tx['app_title']}</div>
      <div class="hero-sub">{tx['app_sub']}</div>
    </div>
  </div>
</div>
<div class="stripe"></div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# HELPER: map local label → English for RAG
# ══════════════════════════════════════════════════════════════
def to_english(local_val, local_list, en_list):
    try:
        return en_list[local_list.index(local_val)]
    except (ValueError, IndexError):
        return local_val

# ══════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs([tx["tab_predict"], tx["tab_negotiate"], tx["tab_about"]])

# ── TAB 1: PRICE INTELLIGENCE ─────────────────────────────────
with tab1:
    if not index:
        st.error(tx["no_index"])
    elif not has_api_key():
        st.error(tx["no_key"])
        st.code('XAI_API_KEY = "xai-your-key-here"', language="toml")
    else:
        st.markdown('<div class="card card-gold">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-head">🗺️ {tx["commodity"]} Details</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            state           = st.selectbox(tx["state"],     [""] + STATES,          key="p_state")
            commodity_local = st.selectbox(tx["commodity"], [""] + tx["commodities"],key="p_commodity")
        with col2:
            district        = st.selectbox(tx["district"],  [""] + DISTRICTS,       key="p_district")
            variety_local   = st.selectbox(tx["variety"],   [""] + tx["varieties"], key="p_variety")
        with col3:
            market          = st.selectbox(tx["market"],    [""] + MARKETS,         key="p_market")
            grade_local     = st.selectbox(tx["grade"],     [""] + tx["grades"],    key="p_grade")
        st.markdown("</div>", unsafe_allow_html=True)

        ready = all([state, district, market, commodity_local, variety_local, grade_local])
        if not ready:
            st.info(f"💡 {tx['select_hint']}")
        else:
            if st.button(tx["predict_btn"], key="btn_predict", type="primary"):
                commodity_en = to_english(commodity_local, tx["commodities"], COMMODITIES_EN)
                variety_en   = to_english(variety_local,   tx["varieties"],   VARIETIES_EN)
                grade_en     = to_english(grade_local,     tx["grades"],      GRADES_EN)
                from rag_engine import rag_query, fetch_live_prices
                live = fetch_live_prices(state, commodity_en)
                if live:
                    st.toast(f"🟢 {tx['live_badge']}")
                with st.spinner(tx["spinner_predict"]):
                    result_text = rag_query(state, district, market, commodity_en,
                                           variety_en, grade_en, language=lang,
                                           index=index, docs=docs, client=client)
                st.session_state["predict_result"] = result_text
                st.session_state["last_query"] = dict(
                    state=state, district=district, market=market,
                    commodity=commodity_local, variety=variety_local, grade=grade_local,
                    commodity_en=commodity_en)

        # Result outside button — no blank space
        if st.session_state.get("predict_result"):
            st.markdown('<div class="card card-gold">', unsafe_allow_html=True)
            st.markdown(f'<div class="section-head">{tx["analysis_head"]}</div>', unsafe_allow_html=True)
            st.markdown(st.session_state["predict_result"])
            st.markdown("</div>", unsafe_allow_html=True)

# ── TAB 2: NEGOTIATION ────────────────────────────────────────
with tab2:
    if not index:
        st.error(tx["no_index"])
    elif not has_api_key():
        st.error(tx["no_key"])
        st.code('XAI_API_KEY = "xai-your-key-here"', language="toml")
    else:
        last = st.session_state.get("last_query", {})
        st.markdown('<div class="card card-blue">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-head">🤝 {tx["tab_negotiate"]}</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            _si = (STATES.index(last.get("state",""))+1) if last.get("state","") in STATES else 0
            n_state           = st.selectbox(tx["state"],     [""] + STATES,          index=_si, key="n_state")
            _ci = (tx["commodities"].index(last.get("commodity",""))+1) if last.get("commodity","") in tx["commodities"] else 0
            n_commodity_local = st.selectbox(tx["commodity"], [""] + tx["commodities"],index=_ci, key="n_commodity")
        with col2:
            n_district        = st.selectbox(tx["district"],  [""] + DISTRICTS,       key="n_district")
            n_variety_local   = st.selectbox(tx["variety"],   [""] + tx["varieties"], key="n_variety")
        with col3:
            n_market          = st.selectbox(tx["market"],    [""] + MARKETS,         key="n_market")
            n_grade_local     = st.selectbox(tx["grade"],     [""] + tx["grades"],    key="n_grade")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="card card-blue">', unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            offered_price = st.number_input(tx["offer_label"], min_value=0, step=50, key="offered_price")
        with col_b:
            st.markdown(f'<p style="color:#7A90B8;font-size:.82rem;font-weight:600;letter-spacing:.06em;text-transform:uppercase;">{tx["voice_label"]}</p>', unsafe_allow_html=True)
            audio = st.audio_input("🎙️", key="voice_offer", label_visibility="collapsed")
            if audio:
                st.info("🎙️ Audio recorded. Enter price manually above.")
        st.markdown("</div>", unsafe_allow_html=True)

        n_ready = all([n_state, n_district, n_market, n_commodity_local,
                       n_variety_local, n_grade_local]) and offered_price > 0
        if not n_ready:
            st.info(f"💡 {tx['select_hint']}")
        else:
            if st.button(tx["evaluate_btn"], key="btn_evaluate", type="primary"):
                n_commodity_en = to_english(n_commodity_local, tx["commodities"], COMMODITIES_EN)
                n_variety_en   = to_english(n_variety_local,   tx["varieties"],   VARIETIES_EN)
                n_grade_en     = to_english(n_grade_local,     tx["grades"],      GRADES_EN)
                with st.spinner(tx["spinner_eval"]):
                    from rag_engine import evaluate_offer, retrieve, fetch_live_prices, live_records_to_docs
                    live_r    = fetch_live_prices(n_state, n_commodity_en)
                    live_d    = live_records_to_docs(live_r)
                    query     = f"{n_commodity_en} {n_variety_en} {n_grade_en} price {n_market} {n_district} {n_state}"
                    retrieved = retrieve(query, index, docs or [], live_docs=live_d, client=client)
                    result    = evaluate_offer(int(offered_price), retrieved, n_commodity_en, lang, client)

                verdict  = result.get("verdict","UNKNOWN")
                fair_p   = result.get("estimated_fair_price", 0)
                conf     = result.get("confidence_pct", 50)
                advice   = result.get("advice","")
                vmap = {
                    "FAIR":   ("card-green", tx["verdict_fair"],    "success"),
                    "LOW":    ("card-red",   tx["verdict_low"],     "error"),
                    "HIGH":   ("card-blue",  tx["verdict_high"],    "info"),
                    "UNKNOWN":("card-gold",  tx["verdict_unknown"], "warning"),
                }
                card_cls, vlabel, atype = vmap.get(verdict, vmap["UNKNOWN"])
                st.markdown(f'<div class="card {card_cls}">', unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                with c1: st.metric("🏷️ " + tx["fair_price"], f"₹{fair_p:,}")
                with c2: st.metric("💸 " + tx["your_offer"], f"₹{int(offered_price):,}",
                                   delta=f"{int(offered_price)-fair_p:+,}")
                with c3: st.metric("📊 " + tx["confidence"], f"{conf}%")
                st.progress(conf / 100)
                if atype=="success": st.success(f"**{vlabel}** — {advice}")
                elif atype=="error": st.error(f"**{vlabel}** — {advice}")
                elif atype=="info":  st.info(f"**{vlabel}** — {advice}")
                else:                st.warning(f"**{vlabel}** — {advice}")
                with st.expander(tx["price_band"]):
                    bl = int(fair_p*.85); bh = int(fair_p*1.15)
                    st.markdown(f"""
| | ₹/quintal |
|---|---|
| 🔴 {tx['band_reject']} | < ₹{bl:,} |
| 🟡 {tx['band_neg']} | ₹{bl:,} – ₹{fair_p:,} |
| 🟢 {tx['band_fair']} | ₹{fair_p:,} |
| 🔵 {tx['band_above']} | > ₹{bh:,} |
""")
                st.markdown("</div>", unsafe_allow_html=True)

# ── TAB 3: ABOUT ─────────────────────────────────────────────
with tab3:
    st.markdown('<div class="card card-gold">', unsafe_allow_html=True)
    st.markdown(tx["about_text"])
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📋 System Status")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("RAG Index", "✅ Loaded" if index else "❌ Missing")
    with c2: st.metric("Grok API",  "✅ Key Set" if has_api_key() else "❌ Not Set")
    with c3: st.metric("Live API",  "✅ data.gov.in")
    st.markdown("</div>", unsafe_allow_html=True)
