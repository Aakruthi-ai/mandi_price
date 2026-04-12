import os
import streamlit as st

st.set_page_config(
    page_title="Mandi Mitra",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================================
# DATA
# ======================================================

STATES = [
    "Andhra Pradesh","Bihar","Gujarat","Haryana","Karnataka",
    "Kerala","Madhya Pradesh","Maharashtra","Odisha","Punjab",
    "Rajasthan","Tamil Nadu","Telangana","Uttar Pradesh","West Bengal"
]

DISTRICTS = [
    "Ahmedabad","Amritsar","Bangalore","Belgaum","Bhopal","Chandigarh",
    "Chennai","Davangere","Hubli","Hyderabad","Jaipur","Lucknow",
    "Mumbai","Mysore","Shimoga","Tumkur","Yelahanka","Yeshwanthpur"
]

MARKETS = [
    "Azadpur","Belgaum","Davangere","Hubli","Mysore",
    "Shimoga","Tumkur","Vashi","Yelahanka","Yeshwanthpur"
]

COMMODITIES_EN = [
    "Bajra","Chilli","Cotton","Garlic","Groundnut","Jowar",
    "Maize","Onion","Potato","Rice","Soybean","Sugarcane",
    "Tomato","Wheat"
]

COMMODITIES_HI = [
    "बाजरा","मिर्च","कपास","लहसुन","मूंगफली","ज्वार",
    "मक्का","प्याज","आलू","चावल","सोयाबीन","गन्ना",
    "टमाटर","गेहूँ"
]

COMMODITIES_KN = [
    "ಸಜ್ಜೆ","ಮೆಣಸಿನಕಾಯಿ","ಹತ್ತಿ","ಬೆಳ್ಳುಳ್ಳಿ","ಕಡಲೆಕಾಯಿ","ಜೋಳ",
    "ಮೆಕ್ಕೆಜೋಳ","ಈರುಳ್ಳಿ","ಆಲೂಗಡ್ಡೆ","ಅಕ್ಕಿ","ಸೋಯಾಬೀನ್",
    "ಕಬ್ಬು","ಟೊಮೆಟೊ","ಗೋಧಿ"
]

VARIETIES_EN = ["Bold","Coarse","FAQ","Fine","Hybrid","Local","Medium","No.1","No.2","Other"]
VARIETIES_HI = ["मोटा","मोटा दाना","FAQ","बारीक","हाइब्रिड","देसी","मध्यम","नं.1","नं.2","अन्य"]
VARIETIES_KN = ["ದಪ್ಪ","ಒರಟು","FAQ","ನುಣ್ಣಗೆ","ಹೈಬ್ರಿಡ್","ದೇಸಿ","ಮಧ್ಯಮ","ನಂ.1","ನಂ.2","ಇತರ"]

GRADES_EN = ["Common","FAQ","Grade A","Grade B","Grade C","Medium","Super"]
GRADES_HI = ["सामान्य","FAQ","ग्रेड A","ग्रेड B","ग्रेड C","मध्यम","सुपर"]
GRADES_KN = ["ಸಾಮಾನ್ಯ","FAQ","ದರ್ಜೆ A","ದರ್ಜೆ B","ದರ್ಜೆ C","ಮಧ್ಯಮ","ಸೂಪರ್"]

T = {
    "English": {
        "title":"Mandi Mitra",
        "sub":"AI Powered Agricultural Price Intelligence",
        "commodity":"Commodity",
        "variety":"Variety",
        "grade":"Grade",
        "state":"State",
        "district":"District",
        "market":"Market",
        "predict":"🔍 Get Price Intelligence",
        "offer":"Your Offered Price (₹ / quintal)",
        "evaluate":"⚖️ Evaluate My Offer",
        "about":"About",
        "commodities":COMMODITIES_EN,
        "varieties":VARIETIES_EN,
        "grades":GRADES_EN
    },

    "हिन्दी": {
        "title":"मंडी मित्र",
        "sub":"AI संचालित कृषि मूल्य सहायक",
        "commodity":"फसल",
        "variety":"किस्म",
        "grade":"ग्रेड",
        "state":"राज्य",
        "district":"जिला",
        "market":"मंडी",
        "predict":"🔍 मूल्य जानें",
        "offer":"आपका प्रस्तावित मूल्य (₹ / क्विंटल)",
        "evaluate":"⚖️ मूल्य जाँचें",
        "about":"परिचय",
        "commodities":COMMODITIES_HI,
        "varieties":VARIETIES_HI,
        "grades":GRADES_HI
    },

    "ಕನ್ನಡ": {
        "title":"ಮಂಡಿ ಮಿತ್ರ",
        "sub":"AI ಆಧಾರಿತ ಕೃಷಿ ಬೆಲೆ ಸಹಾಯಕ",
        "commodity":"ಬೆಳೆ",
        "variety":"ತಳಿ",
        "grade":"ದರ್ಜೆ",
        "state":"ರಾಜ್ಯ",
        "district":"ಜಿಲ್ಲೆ",
        "market":"ಮಾರುಕಟ್ಟೆ",
        "predict":"🔍 ಬೆಲೆ ತಿಳಿಯಿರಿ",
        "offer":"ನಿಮ್ಮ ಪ್ರಸ್ತಾಪಿತ ಬೆಲೆ (₹ / ಕ್ವಿಂಟಾಲ್)",
        "evaluate":"⚖️ ಬೆಲೆ ಪರಿಶೀಲಿಸಿ",
        "about":"ಪರಿಚಯ",
        "commodities":COMMODITIES_KN,
        "varieties":VARIETIES_KN,
        "grades":GRADES_KN
    }
}

# ======================================================
# CSS
# ======================================================

st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"]{
background:#08111f;
color:white;
}

section[data-testid="stSidebar"]{
background:#111827;
}

button[kind="primary"]{
background:#f59e0b !important;
color:black !important;
font-weight:700 !important;
}

.stSelectbox label,.stNumberInput label{
font-weight:700;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# SESSION
# ======================================================

if "lang" not in st.session_state:
    st.session_state.lang = "English"

# ======================================================
# SIDEBAR
# ======================================================

with st.sidebar:
    st.title("🌾 Mandi Mitra")

    lang = st.radio(
        "Language",
        ["English","हिन्दी","ಕನ್ನಡ"],
        index=["English","हिन्दी","ಕನ್ನಡ"].index(st.session_state.lang)
    )

    st.session_state.lang = lang

lang = st.session_state.lang
tx = T[lang]

# ======================================================
# API KEY
# ======================================================

if "XAI_API_KEY" not in os.environ:
    try:
        os.environ["XAI_API_KEY"] = st.secrets["XAI_API_KEY"]
    except:
        pass

# ======================================================
# LOAD
# ======================================================

from rag_engine import get_client, rag_query, evaluate_offer

client = get_client()

# ======================================================
# UI
# ======================================================

st.title("🌾 " + tx["title"])
st.caption(tx["sub"])

tab1, tab2, tab3 = st.tabs(["📈 Price", "🤝 Negotiate", "ℹ️ About"])

# ======================================================
# TAB1
# ======================================================

with tab1:

    c1,c2,c3 = st.columns(3)

    with c1:
        state = st.selectbox(tx["state"], STATES)
        commodity = st.selectbox(tx["commodity"], tx["commodities"])

    with c2:
        district = st.selectbox(tx["district"], DISTRICTS)
        variety = st.selectbox(tx["variety"], tx["varieties"])

    with c3:
        market = st.selectbox(tx["market"], MARKETS)
        grade = st.selectbox(tx["grade"], tx["grades"])

    if st.button(tx["predict"], use_container_width=True):

        with st.spinner("Loading..."):

            result = rag_query(
                state,
                district,
                market,
                commodity,
                variety,
                grade,
                lang,
                client
            )

        st.markdown(result)

# ======================================================
# TAB2
# ======================================================

with tab2:

    price = st.number_input(tx["offer"], min_value=0, step=50)

    if st.button(tx["evaluate"], use_container_width=True):

        result = evaluate_offer(price, commodity, lang, client)

        st.json(result)

# ======================================================
# TAB3
# ======================================================

with tab3:
    st.markdown("""
### 🌾 Mandi Mitra

AI assistant for farmers.

✅ Grok AI Powered  
✅ Multi-language  
✅ Smart Price Guidance  
✅ Negotiation Assistant
""")
