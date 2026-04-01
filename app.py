import streamlit as st
import os
from rag_engine import rag_query, speech_to_text, generate_price_trend, get_client

st.set_page_config(page_title="Mandi Mitra 🌾", layout="wide")



# ---------------- LANGUAGE DICTIONARY ----------------
T = {
    "English": {
        "title": "Mandi Mitra",
        "tab1": "📈 Price Intelligence",
        "tab2": "🤝 Negotiation",
        "tab3": "ℹ️ About",
        "state": "State",
        "district": "District",
        "market": "Market",
        "commodity": "Commodity",
        "variety": "Variety",
        "grade": "Grade",
        "btn": "Get Insight",
        "offer": "Enter Offered Price",
        "about": "Mandi Mitra helps farmers with AI-based price insights using real-time and historical mandi data."
    },
    "हिन्दी": {
        "title": "मंडी मित्र",
        "tab1": "📈 मूल्य जानकारी",
        "tab2": "🤝 मोलभाव",
        "tab3": "ℹ️ जानकारी",
        "state": "राज्य",
        "district": "जिला",
        "market": "मंडी",
        "commodity": "फसल",
        "variety": "किस्म",
        "grade": "ग्रेड",
        "btn": "मूल्य देखें",
        "offer": "अपना प्रस्तावित मूल्य दर्ज करें",
        "about": "मंडी मित्र किसानों को AI आधारित मूल्य सुझाव देता है।"
    },
    "ಕನ್ನಡ": {
        "title": "ಮಂಡಿ ಮಿತ್ರ",
        "tab1": "📈 ಬೆಲೆ ಮಾಹಿತಿ",
        "tab2": "🤝 ಚರ್ಚೆ",
        "tab3": "ℹ️ ಮಾಹಿತಿ",
        "state": "ರಾಜ್ಯ",
        "district": "ಜಿಲ್ಲೆ",
        "market": "ಮಾರುಕಟ್ಟೆ",
        "commodity": "ಬೆಳೆ",
        "variety": "ತಳಿ",
        "grade": "ದರ್ಜೆ",
        "btn": "ಬೆಲೆ ನೋಡಿ",
        "offer": "ನಿಮ್ಮ ಬೆಲೆ ನಮೂದಿಸಿ",
        "about": "ಮಂಡಿ ಮಿತ್ರ ರೈತರಿಗೆ AI ಮೂಲಕ ಬೆಲೆ ಸಲಹೆ ನೀಡುತ್ತದೆ."
    }
}

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## 👤 User Profile")
    name = st.text_input("Name", "Farmer")
    role = st.selectbox("Role", ["Farmer", "Trader"])

    lang = st.radio("Language", ["English", "हिन्दी", "ಕನ್ನಡ"])
    tx = T[lang]

# ---------------- STYLE ----------------
st.markdown("""
<style>
body {background-color: #FDF6E3;}
.stApp {background: linear-gradient(135deg,#FFF3E0,#E8F5E9);}
h1, h2, h3 {color: #FF9933;}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title(f"🌾 {tx['title']}")

# ---------------- DROPDOWNS ----------------
states = ["Karnataka","Maharashtra","Punjab","UP"]
districts = ["Bangalore","Mumbai","Lucknow"]
markets = ["Yeshwanthpur","Vashi","Azadpur"]
commodities = ["Onion","Tomato","Rice","Wheat"]
varieties = ["Local","Hybrid","FAQ"]
grades = ["A","B","FAQ"]

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs([tx["tab1"], tx["tab2"], tx["tab3"]])

# =========================================================
# 📈 TAB 1: PRICE INTELLIGENCE
# =========================================================
with tab1:
    col1, col2, col3 = st.columns(3)

    with col1:
        state = st.selectbox(tx["state"], states)
        commodity = st.selectbox(tx["commodity"], commodities)

    with col2:
        district = st.selectbox(tx["district"], districts)
        variety = st.selectbox(tx["variety"], varieties)

    with col3:
        market = st.selectbox(tx["market"], markets)
        grade = st.selectbox(tx["grade"], grades)

    if st.button(tx["btn"]):
        result, docs = rag_query(state, district, market, commodity, variety, grade, lang)

        st.subheader("📊 Result")
        st.write(result)

        fig = generate_price_trend(docs)
        if fig:
            st.pyplot(fig)

# =========================================================
# 🤝 TAB 2: NEGOTIATION
# =========================================================
with tab2:
    st.subheader(tx["offer"])

    offer_price = st.number_input("₹", step=50)

    audio = st.audio_input("🎙 Speak your price")

    if audio:
        with open("temp.wav", "wb") as f:
            f.write(audio.read())

        client = get_client()
        text = speech_to_text("temp.wav", client)

        st.success(f"Recognized: {text}")

    if st.button("Evaluate Deal"):
        result, _ = rag_query("Karnataka","Bangalore","Yeshwanthpur","Onion","Local","FAQ", lang)
        st.write(result)

# =========================================================
# ℹ️ TAB 3: ABOUT
# =========================================================
with tab3:
    st.markdown(f"""
    ### 🌾 {tx['title']}

    {tx["about"]}

    #### 🚀 Features:
    - AI Price Prediction
    - Voice Input (Hindi/Kannada)
    - Smart Negotiation
    - Live Market Trends

    #### 🧠 Tech Stack:
    - Streamlit
    - OpenAI
    - FAISS
    """)
