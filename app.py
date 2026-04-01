import streamlit as st
import os
from rag_engine import rag_query, speech_to_text, generate_price_trend, get_client

st.set_page_config(page_title="Mandi Mitra 🌾", layout="wide")

# ---------- LOAD API KEY ----------
if "OPENAI_API_KEY" not in os.environ:
    try:
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    except:
        st.error("API key missing")

# ---------- LANGUAGE ----------
T = {
    "English": {"title": "Mandi Mitra", "btn": "Get Insight"},
    "हिन्दी": {"title": "मंडी मित्र", "btn": "मूल्य देखें"},
    "ಕನ್ನಡ": {"title": "ಮಂಡಿ ಮಿತ್ರ", "btn": "ಬೆಲೆ ನೋಡಿ"}
}

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("## 👤 Profile")
    name = st.text_input("Name", "Farmer")
    lang = st.radio("Language", ["English", "हिन्दी", "ಕನ್ನಡ"])

tx = T[lang]

# ---------- INDIAN THEME ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #FFF3E0, #E8F5E9);
}
h1 {
    color: #FF6F00;
    font-weight: 800;
}
button {
    background: linear-gradient(135deg, #FF9933, #138808) !important;
    color: white !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- TITLE ----------
st.title(f"🌾 {tx['title']}")

# ---------- DATA ----------
states = ["Karnataka","Maharashtra","Punjab","UP"]
districts = ["Bangalore","Mumbai","Lucknow"]
markets = ["Yeshwanthpur","Vashi","Azadpur"]
commodities = ["Onion","Rice","Wheat"]
varieties = ["Local","Hybrid"]
grades = ["FAQ","A","B"]

# ---------- TABS ----------
tab1, tab2, tab3 = st.tabs(["📊 Price", "🤝 Negotiation", "ℹ️ About"])

# ---------- TAB 1 ----------
with tab1:
    col1, col2, col3 = st.columns(3)

    with col1:
        state = st.selectbox("State", states)
        commodity = st.selectbox("Commodity", commodities)

    with col2:
        district = st.selectbox("District", districts)
        variety = st.selectbox("Variety", varieties)

    with col3:
        market = st.selectbox("Market", markets)
        grade = st.selectbox("Grade", grades)

    if st.button(tx["btn"]):
        result, docs = rag_query(state, district, market, commodity, variety, grade, lang)
        st.write(result)

        fig = generate_price_trend(docs)
        if fig:
            st.pyplot(fig)

# ---------- TAB 2 ----------
with tab2:
    price = st.number_input("Enter Price ₹", step=50)

    audio = st.audio_input("🎙 Speak")

    if audio:
        with open("temp.wav", "wb") as f:
            f.write(audio.read())

        text = speech_to_text("temp.wav", get_client())
        st.success(f"Recognized: {text}")

    if st.button("Evaluate"):
        result, _ = rag_query("Karnataka","Bangalore","Yeshwanthpur","Onion","Local","FAQ", lang)
        st.write(result)

# ---------- TAB 3 ----------
with tab3:
    st.markdown("""
    ## 🌾 Mandi Mitra

    AI-powered agricultural price intelligence system.

    ### Features:
    - 📊 Price prediction
    - 🎙 Voice input
    - 🤝 Negotiation help
    - 🌐 Multi-language

    Built for farmers 🚜
    """)
