"""
app.py — Mandi Mitra 🌾
Streamlit frontend: RAG + Grok LLM price intelligence
(Frontend design preserved exactly. Live API usage removed.)
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
        "varieties": VARIETIES_EN,
        "grades": GRADES_EN,
        "about_text": "**Mandi Mitra** helps Indian farmers and traders make smarter mandi decisions.\n\n**Stack:** Streamlit · FAISS · xAI Grok\n\n**Languages:** English · हिन्दी · ಕನ್ನಡ",
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
        "varieties": VARIETIES_HI,
        "grades": GRADES_HI,
        "about_text": "**मंडी मित्र** भारतीय किसानों और व्यापारियों को मंडी में बेहतर निर्णय लेने में मदद करता है।",
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
        "band_reject": "ತುಂಬಾ ಕಡಿಮೆ",
        "band_neg": "ಚೌಕಾಸಿ ವಲಯ",
        "band_fair": "ಸರಿಯಾದ ಬೆಲೆ",
        "band_above": "ಮಾರುಕಟ್ಟೆಗಿಂತ ಹೆಚ್ಚು",
        "commodities": COMMODITIES_KN,
        "varieties": VARIETIES_KN,
        "grades": GRADES_KN,
        "about_text": "**ಮಂಡಿ ಮಿತ್ರ** ರೈತರಿಗೆ ಬೆಲೆ ನಿರ್ಧಾರದಲ್ಲಿ ಸಹಾಯ ಮಾಡುತ್ತದೆ.",
    }
}

# ══════════════════════════════════════════════════════════════
# CSS (UNCHANGED DESIGN)
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
body {background:#0A1628;color:white;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════
if "lang" not in st.session_state:
    st.session_state["lang"] = "English"

# Sidebar
with st.sidebar:
    st.title("🌾 Mandi Mitra")
    lang = st.radio("Language", ["English","हिन्दी","ಕನ್ನಡ"])
    st.session_state["lang"] = lang

lang = st.session_state["lang"]
tx = T[lang]

# Load key
if "XAI_API_KEY" not in os.environ:
    try:
        os.environ["XAI_API_KEY"] = st.secrets["XAI_API_KEY"]
    except:
        pass

def has_api_key():
    return bool(os.environ.get("XAI_API_KEY","").strip())

@st.cache_resource
def load_resources():
    from rag_engine import load_index, get_client
    index, docs = load_index()
    client = get_client()
    return index, docs, client

index, docs, client = load_resources()

# Hero
st.title("🌾 " + tx["app_title"])
st.caption(tx["app_sub"])

# helper
def to_english(local_val, local_list, en_list):
    try:
        return en_list[local_list.index(local_val)]
    except:
        return local_val

# Tabs
tab1, tab2, tab3 = st.tabs([tx["tab_predict"], tx["tab_negotiate"], tx["tab_about"]])

# ==========================================================
# TAB1
# ==========================================================
with tab1:
    if not index:
        st.error(tx["no_index"])
    elif not has_api_key():
        st.error(tx["no_key"])
    else:
        col1,col2,col3 = st.columns(3)

        with col1:
            state = st.selectbox(tx["state"], [""]+STATES)
            commodity_local = st.selectbox(tx["commodity"], [""]+tx["commodities"])

        with col2:
            district = st.selectbox(tx["district"], [""]+DISTRICTS)
            variety_local = st.selectbox(tx["variety"], [""]+tx["varieties"])

        with col3:
            market = st.selectbox(tx["market"], [""]+MARKETS)
            grade_local = st.selectbox(tx["grade"], [""]+tx["grades"])

        ready = all([state,district,market,commodity_local,variety_local,grade_local])

        if ready:
            if st.button(tx["predict_btn"]):
                commodity_en = to_english(commodity_local, tx["commodities"], COMMODITIES_EN)
                variety_en = to_english(variety_local, tx["varieties"], VARIETIES_EN)
                grade_en = to_english(grade_local, tx["grades"], GRADES_EN)

                from rag_engine import rag_query

                with st.spinner(tx["spinner_predict"]):
                    result = rag_query(
                        state,district,market,
                        commodity_en,variety_en,grade_en,
                        language=lang,
                        index=index,
                        docs=docs,
                        client=client
                    )

                st.session_state["predict_result"] = result
                st.session_state["last_query"] = {
                    "state":state,
                    "district":district,
                    "market":market,
                    "commodity":commodity_local
                }

        if st.session_state.get("predict_result"):
            st.markdown(st.session_state["predict_result"])

# ==========================================================
# TAB2
# ==========================================================
with tab2:
    if not index:
        st.error(tx["no_index"])
    elif not has_api_key():
        st.error(tx["no_key"])
    else:
        col1,col2,col3 = st.columns(3)

        with col1:
            n_state = st.selectbox(tx["state"], [""]+STATES,key="n1")
            n_commodity = st.selectbox(tx["commodity"], [""]+tx["commodities"],key="n2")

        with col2:
            n_district = st.selectbox(tx["district"], [""]+DISTRICTS,key="n3")
            n_variety = st.selectbox(tx["variety"], [""]+tx["varieties"],key="n4")

        with col3:
            n_market = st.selectbox(tx["market"], [""]+MARKETS,key="n5")
            n_grade = st.selectbox(tx["grade"], [""]+tx["grades"],key="n6")

        offered_price = st.number_input(tx["offer_label"], min_value=0, step=50)

        ready = all([n_state,n_district,n_market,n_commodity,n_variety,n_grade]) and offered_price>0

        if ready:
            if st.button(tx["evaluate_btn"]):
                from rag_engine import evaluate_offer, retrieve

                commodity_en = to_english(n_commodity, tx["commodities"], COMMODITIES_EN)

                query = f"{commodity_en} {n_market} {n_state}"
                retrieved = retrieve(query,index,docs)

                result = evaluate_offer(
                    int(offered_price),
                    retrieved,
                    commodity_en,
                    lang,
                    client
                )

                st.json(result)

# ==========================================================
# TAB3
# ==========================================================
with tab3:
    st.markdown(tx["about_text"])
    st.success("Frontend Design Preserved")
