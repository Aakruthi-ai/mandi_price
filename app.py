import streamlit as st
import numpy as np
import pickle
import re
import speech_recognition as sr
from word2number import w2n
import tempfile
import os

# ══════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="Mandi Mitra",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════
# MULTILINGUAL STRINGS
# ══════════════════════════════════════════════
LANG_STRINGS = {
    "English": {
        "title": "Mandi Mitra",
        "subtitle": "AI-Powered Agricultural Price Intelligence",
        "location_section": "Location & Market",
        "commodity_section": "Commodity Details",
        "state": "State", "district": "District", "market": "Market",
        "commodity": "Commodity", "variety": "Variety", "grade": "Grade",
        "predict_btn": "🔮 Predict Mandi Price",
        "negotiate_tab": "🎙️ Voice Negotiation",
        "predict_tab": "📊 Price Prediction",
        "about_tab": "ℹ️ About",
        "predicted_label": "Predicted Modal Price",
        "your_offer": "Your Offer",
        "mandi_price": "Market Price",
        "confidence": "Confidence Score",
        "evaluate_btn": "⚖️ Evaluate My Offer",
        "type_offer": "Or type your offer price (₹)",
        "fair_offer": "Fair Offer",
        "low_offer": "Below Market",
        "voice_tip": 'Speak in **English, Hindi or Kannada** — e.g. *"I can sell for 2000"* · *"Do hazaar"* · *"Eradu saavira"*',
        "no_price_warning": "⚠️ Please run price prediction first (use the Prediction tab).",
        "no_offer_warning": "Could not detect a price. Speak clearly or type your offer below.",
        "sidebar_about": "Mandi Mitra uses a trained **Random Forest** model on historical AGMARKNET data to predict modal mandi prices.",
        "features_list": ["Price prediction across India", "Voice input in 3 languages", "Negotiation score & advice", "Confidence scoring"],
        "per_quintal": "per quintal · historical mandi data",
        "advice_fair": "🟢 Strong position! This offer is competitive. The buyer is likely to accept.",
        "advice_near": "🟡 Close to market rate. Nudge slightly higher for a stronger deal.",
        "advice_low": "🔴 Significantly below market. Negotiate in stages or reconsider.",
        "record_label": "🎤 Record your offer",
        "placeholder_title": "Your prediction will appear here",
        "placeholder_body": "Fill in the location and commodity, then click Predict.",
        "price_band": "Price Band Analysis",
        "heard": "Heard",
        "eval_complete": "Evaluation complete!",
        "about_content": """
### About Mandi Mitra
**Mandi Mitra** (मंडी मित्र / ಮಾರ್ಕೆಟ್ ಮಿತ್ರ) is an AI-powered assistant built for Indian farmers and traders.

#### How it works
1. Select your **location** and **commodity** from the dropdowns
2. Click **Predict** to get the AI-estimated mandi price
3. Switch to the **Negotiation** tab, speak or type your offered price
4. Get instant feedback on whether your offer is fair

#### Model
- Algorithm: **Random Forest Regressor**
- Data source: AGMARKNET (historical mandi arrivals & prices)
- Languages: English · हिन्दी · ಕನ್ನಡ

#### Disclaimer
Predictions are estimates based on historical data. Actual prices may vary.
        """,
    },
    "हिन्दी": {
        "title": "मंडी मित्र",
        "subtitle": "AI-आधारित कृषि मूल्य सहायक",
        "location_section": "स्थान और बाज़ार",
        "commodity_section": "फसल विवरण",
        "state": "राज्य", "district": "जिला", "market": "बाज़ार",
        "commodity": "फसल", "variety": "किस्म", "grade": "श्रेणी",
        "predict_btn": "🔮 मंडी मूल्य जानें",
        "negotiate_tab": "🎙️ आवाज़ से बातचीत",
        "predict_tab": "📊 मूल्य अनुमान",
        "about_tab": "ℹ️ जानकारी",
        "predicted_label": "अनुमानित मंडी मूल्य",
        "your_offer": "आपका प्रस्ताव",
        "mandi_price": "बाज़ार मूल्य",
        "confidence": "विश्वास स्कोर",
        "evaluate_btn": "⚖️ मेरा प्रस्ताव जाँचें",
        "type_offer": "या अपना मूल्य टाइप करें (₹)",
        "fair_offer": "उचित प्रस्ताव",
        "low_offer": "कम मूल्य",
        "voice_tip": '**हिन्दी, अंग्रेज़ी या कन्नड़** में बोलें — जैसे *"दो हज़ार"* · *"Teen hazaar milega"*',
        "no_price_warning": "⚠️ पहले मूल्य अनुमान करें (अनुमान टैब)।",
        "no_offer_warning": "मूल्य समझ नहीं आया। स्पष्ट बोलें या नीचे टाइप करें।",
        "sidebar_about": "मंडी मित्र AGMARKNET के ऐतिहासिक डेटा पर प्रशिक्षित **Random Forest** मॉडल का उपयोग करता है।",
        "features_list": ["पूरे भारत में मूल्य अनुमान", "3 भाषाओं में आवाज़ इनपुट", "बातचीत स्कोर और सलाह", "विश्वास स्कोरिंग"],
        "per_quintal": "प्रति क्विंटल · ऐतिहासिक मंडी डेटा",
        "advice_fair": "🟢 मजबूत स्थिति! यह प्रस्ताव प्रतिस्पर्धी है।",
        "advice_near": "🟡 बाज़ार दर के करीब। थोड़ा बढ़ाएं।",
        "advice_low": "🔴 बाज़ार से काफी कम। धीरे-धीरे बातचीत करें।",
        "record_label": "🎤 अपना प्रस्ताव रिकॉर्ड करें",
        "placeholder_title": "आपका अनुमान यहाँ दिखेगा",
        "placeholder_body": "स्थान और फसल भरें, फिर अनुमान लगाएं।",
        "price_band": "मूल्य बैंड विश्लेषण",
        "heard": "सुना",
        "eval_complete": "जाँच पूरी!",
        "about_content": """
### मंडी मित्र के बारे में
**मंडी मित्र** भारतीय किसानों और व्यापारियों के लिए बनाया गया AI सहायक है।

#### उपयोग कैसे करें
1. ड्रॉपडाउन से **स्थान** और **फसल** चुनें
2. **मूल्य जानें** बटन दबाएं
3. **बातचीत** टैब पर जाएं, अपना मूल्य बोलें या टाइप करें
4. तुरंत जानें कि आपका प्रस्ताव उचित है या नहीं

#### मॉडल
- एल्गोरिदम: **Random Forest Regressor**
- डेटा स्रोत: AGMARKNET
- भाषाएं: English · हिन्दी · ಕನ್ನಡ
        """,
    },
    "ಕನ್ನಡ": {
        "title": "ಮಾರ್ಕೆಟ್ ಮಿತ್ರ",
        "subtitle": "AI ಆಧಾರಿತ ಕೃಷಿ ಬೆಲೆ ಸಹಾಯಕ",
        "location_section": "ಸ್ಥಳ ಮತ್ತು ಮಾರುಕಟ್ಟೆ",
        "commodity_section": "ಸರಕು ವಿವರ",
        "state": "ರಾಜ್ಯ", "district": "ಜಿಲ್ಲೆ", "market": "ಮಾರುಕಟ್ಟೆ",
        "commodity": "ಸರಕು", "variety": "ತಳಿ", "grade": "ದರ್ಜೆ",
        "predict_btn": "🔮 ಮಾರ್ಕೆಟ್ ಬೆಲೆ ತಿಳಿಯಿರಿ",
        "negotiate_tab": "🎙️ ಧ್ವನಿ ಮಾತುಕತೆ",
        "predict_tab": "📊 ಬೆಲೆ ಅಂದಾಜು",
        "about_tab": "ℹ️ ಮಾಹಿತಿ",
        "predicted_label": "ಅಂದಾಜು ಮಾರ್ಕೆಟ್ ಬೆಲೆ",
        "your_offer": "ನಿಮ್ಮ ಪ್ರಸ್ತಾವ",
        "mandi_price": "ಮಾರ್ಕೆಟ್ ಬೆಲೆ",
        "confidence": "ವಿಶ್ವಾಸ ಸ್ಕೋರ್",
        "evaluate_btn": "⚖️ ನನ್ನ ಪ್ರಸ್ತಾವ ಪರಿಶೀಲಿಸಿ",
        "type_offer": "ಅಥವಾ ನಿಮ್ಮ ಬೆಲೆ ಟೈಪ್ ಮಾಡಿ (₹)",
        "fair_offer": "ಸರಿಯಾದ ಪ್ರಸ್ತಾವ",
        "low_offer": "ಕಡಿಮೆ ಬೆಲೆ",
        "voice_tip": '**ಕನ್ನಡ, ಹಿಂದಿ ಅಥವಾ ಇಂಗ್ಲಿಷ್** ನಲ್ಲಿ ಮಾತಾಡಿ — ಉದಾ: *"ಎರಡು ಸಾವಿರ"* · *"Do hazaar"*',
        "no_price_warning": "⚠️ ಮೊದಲು ಬೆಲೆ ಅಂದಾಜು ಮಾಡಿ (ಅಂದಾಜು ಟ್ಯಾಬ್).",
        "no_offer_warning": "ಬೆಲೆ ಅರ್ಥವಾಗಲಿಲ್ಲ. ಸ್ಪಷ್ಟವಾಗಿ ಮಾತಾಡಿ ಅಥವಾ ಕೆಳಗೆ ಟೈಪ್ ಮಾಡಿ.",
        "sidebar_about": "ಮಾರ್ಕೆಟ್ ಮಿತ್ರ AGMARKNET ಡೇಟಾ ಮೇಲೆ ತರಬೇತಿ ಪಡೆದ **Random Forest** ಮಾದರಿ ಬಳಸುತ್ತದೆ.",
        "features_list": ["ಭಾರತಾದ್ಯಂತ ಬೆಲೆ ಅಂದಾಜು", "3 ಭಾಷೆಗಳಲ್ಲಿ ಧ್ವನಿ ಇನ್‌ಪುಟ್", "ಮಾತುಕತೆ ಸ್ಕೋರ್ ಮತ್ತು ಸಲಹೆ", "ವಿಶ್ವಾಸ ಸ್ಕೋರಿಂಗ್"],
        "per_quintal": "ಪ್ರತಿ ಕ್ವಿಂಟಾಲ್ · ಐತಿಹಾಸಿಕ ಡೇಟಾ",
        "advice_fair": "🟢 ಉತ್ತಮ ಸ್ಥಿತಿ! ಈ ಪ್ರಸ್ತಾವ ಸ್ಪರ್ಧಾತ್ಮಕವಾಗಿದೆ.",
        "advice_near": "🟡 ಮಾರ್ಕೆಟ್ ದರಕ್ಕೆ ಹತ್ತಿರ. ಸ್ವಲ್ಪ ಹೆಚ್ಚಿಸಿ.",
        "advice_low": "🔴 ಮಾರ್ಕೆಟ್‌ಗಿಂತ ತುಂಬಾ ಕಡಿಮೆ. ಹಂತ ಹಂತವಾಗಿ ಮಾತಾಡಿ.",
        "record_label": "🎤 ನಿಮ್ಮ ಪ್ರಸ್ತಾವ ರೆಕಾರ್ಡ್ ಮಾಡಿ",
        "placeholder_title": "ನಿಮ್ಮ ಅಂದಾಜು ಇಲ್ಲಿ ಕಾಣಿಸುತ್ತದೆ",
        "placeholder_body": "ಸ್ಥಳ ಮತ್ತು ಸರಕು ಆಯ್ಕೆ ಮಾಡಿ, ನಂತರ ಅಂದಾಜು ಮಾಡಿ.",
        "price_band": "ಬೆಲೆ ಬ್ಯಾಂಡ್ ವಿಶ್ಲೇಷಣೆ",
        "heard": "ಕೇಳಿದ್ದು",
        "eval_complete": "ಮೌಲ್ಯಮಾಪನ ಪೂರ್ಣ!",
        "about_content": """
### ಮಾರ್ಕೆಟ್ ಮಿತ್ರ ಬಗ್ಗೆ
**ಮಾರ್ಕೆಟ್ ಮಿತ್ರ** ಭಾರತೀಯ ರೈತರು ಮತ್ತು ವ್ಯಾಪಾರಿಗಳಿಗಾಗಿ ನಿರ್ಮಿಸಲಾದ AI ಸಹಾಯಕ.

#### ಹೇಗೆ ಬಳಸುವುದು
1. ಡ್ರಾಪ್‌ಡೌನ್‌ನಿಂದ **ಸ್ಥಳ** ಮತ್ತು **ಸರಕು** ಆಯ್ಕೆ ಮಾಡಿ
2. **ಬೆಲೆ ತಿಳಿಯಿರಿ** ಬಟನ್ ಒತ್ತಿರಿ
3. **ಮಾತುಕತೆ** ಟ್ಯಾಬ್‌ಗೆ ಹೋಗಿ, ನಿಮ್ಮ ಬೆಲೆ ಹೇಳಿ ಅಥವಾ ಟೈಪ್ ಮಾಡಿ
4. ನಿಮ್ಮ ಪ್ರಸ್ತಾವ ಉಚಿತವೇ ಎಂದು ತಕ್ಷಣ ತಿಳಿಯಿರಿ

#### ಮಾದರಿ
- ಅಲ್ಗಾರಿದಮ್: **Random Forest Regressor**
- ಡೇಟಾ: AGMARKNET
- ಭಾಷೆಗಳು: English · हिन्दी · ಕನ್ನಡ
        """,
    }
}

# ══════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Yatra+One&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');

:root {
    --bg:      #030D1A;
    --card:    #0C2235;
    --teal:    #00B4A6;
    --teal2:   #00D4C4;
    --saffron: #FF6B1A;
    --gold:    #FFD166;
    --cream:   #EEF2F7;
    --muted:   #6B8FA5;
    --green:   #06D6A0;
    --red:     #EF476F;
    --border:  rgba(0,180,166,0.2);
}

html, body, .stApp {
    background: var(--bg) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--cream);
}

/* Ambient glow */
.stApp::before {
    content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
    background:
        radial-gradient(ellipse 55% 45% at 8% 15%, rgba(0,180,166,.13) 0%, transparent 65%),
        radial-gradient(ellipse 45% 35% at 92% 85%, rgba(255,107,26,.10) 0%, transparent 65%),
        radial-gradient(ellipse 35% 25% at 50% 50%, rgba(255,209,102,.05) 0%, transparent 70%);
}

/* Rainbow top stripe */
.stApp::after {
    content:''; position:fixed; top:0; left:0; right:0; height:3px; z-index:9999;
    background: linear-gradient(90deg, var(--teal), var(--gold), var(--saffron), var(--teal));
    background-size:200% 100%;
    animation: stripe 5s linear infinite;
}
@keyframes stripe { 0%{background-position:0%} 100%{background-position:200%} }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #071828 !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] li { color: var(--cream) !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--card) !important; border-radius:14px !important;
    padding:4px !important; gap:4px !important;
    border:1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius:10px !important; color:var(--muted) !important;
    font-weight:600 !important; font-size:.85rem !important;
    letter-spacing:.04em !important; padding:.5rem 1.4rem !important;
}
.stTabs [aria-selected="true"] {
    background:linear-gradient(135deg,var(--teal),#007F76) !important;
    color:#fff !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top:1.4rem !important; }

/* Selectbox */
.stSelectbox label {
    color:var(--teal2) !important; font-size:.75rem !important;
    font-weight:700 !important; letter-spacing:.1em !important;
    text-transform:uppercase !important;
}
div[data-baseweb="select"] > div {
    background:var(--card) !important; border-color:var(--border) !important;
    color:var(--cream) !important; border-radius:10px !important;
}
div[data-baseweb="select"] span { color:var(--cream) !important; }
div[data-baseweb="popover"] { background:#0C2235 !important; border:1px solid var(--border) !important; }
li[role="option"] { color:var(--cream) !important; background:var(--card) !important; }
li[role="option"]:hover { background:rgba(0,180,166,.18) !important; }

/* Text input */
.stTextInput label {
    color:var(--teal2) !important; font-size:.75rem !important;
    font-weight:700 !important; letter-spacing:.1em !important; text-transform:uppercase !important;
}
.stTextInput input {
    background:var(--card) !important; border:1px solid var(--border) !important;
    color:var(--cream) !important; border-radius:10px !important; font-size:1rem !important;
}
.stTextInput input:focus { border-color:var(--teal) !important; box-shadow:0 0 0 2px rgba(0,180,166,.25) !important; }

/* Audio input */
.stAudioInput label {
    color:var(--teal2) !important; font-size:.75rem !important;
    font-weight:700 !important; letter-spacing:.1em !important; text-transform:uppercase !important;
}

/* Buttons */
.stButton > button {
    background:linear-gradient(135deg,var(--saffron),#D45A0A) !important;
    color:#fff !important; border:none !important; border-radius:12px !important;
    font-family:'DM Sans',sans-serif !important; font-weight:700 !important;
    font-size:.9rem !important; letter-spacing:.06em !important;
    padding:.65rem 2rem !important; text-transform:uppercase !important;
    box-shadow:0 4px 20px rgba(255,107,26,.35) !important;
    transition:all .2s ease !important;
}
.stButton > button:hover { transform:translateY(-2px) !important; box-shadow:0 8px 28px rgba(255,107,26,.5) !important; }

/* st.metric */
[data-testid="stMetric"] {
    background:var(--card) !important; border:1px solid var(--border) !important;
    border-radius:14px !important; padding:1rem 1.2rem !important;
}
[data-testid="stMetricLabel"] {
    color:var(--teal2) !important; font-size:.72rem !important;
    font-weight:700 !important; letter-spacing:.1em !important; text-transform:uppercase !important;
}
[data-testid="stMetricValue"] {
    font-family:'Yatra One',cursive !important;
    color:var(--gold) !important; font-size:2rem !important;
}
[data-testid="stMetricDelta"] { font-size:.8rem !important; font-weight:600 !important; }

/* Progress bar */
.stProgress > div > div { background:rgba(0,180,166,.12) !important; border-radius:99px !important; }
.stProgress > div > div > div { background:linear-gradient(90deg,var(--teal),var(--gold)) !important; border-radius:99px !important; }

/* Expander */
details summary {
    background:var(--card) !important; border:1px solid var(--border) !important;
    border-radius:10px !important; color:var(--cream) !important;
    font-weight:600 !important; padding:.6rem 1rem !important;
}

/* Alerts */
.stAlert { border-radius:12px !important; }

/* Radio */
.stRadio [data-testid="stWidgetLabel"] { color:var(--teal2) !important; font-weight:700 !important; }
.stRadio label { color:var(--cream) !important; }

/* Caption */
.stCaption { color:var(--muted) !important; }

/* Divider */
hr { border-color:var(--border) !important; }

/* Section pill */
.sec-pill {
    display:inline-flex; align-items:center; gap:.4rem;
    background:linear-gradient(135deg,rgba(0,180,166,.15),rgba(0,180,166,.05));
    border:1px solid rgba(0,180,166,.3); border-radius:99px;
    padding:.22rem .9rem; font-size:.7rem; font-weight:700;
    letter-spacing:.12em; text-transform:uppercase; color:var(--teal2);
    margin-bottom:.7rem; position:relative; z-index:1;
}

/* Tip box */
.tip-box {
    background:rgba(255,209,102,.07); border-left:3px solid var(--gold);
    border-radius:0 10px 10px 0; padding:.7rem 1rem;
    font-size:.84rem; color:rgba(238,242,247,.75);
    margin:.5rem 0 1rem; position:relative; z-index:1;
}

/* Placeholder card */
.ph-card {
    background:var(--card); border:1px dashed rgba(0,180,166,.25);
    border-radius:18px; padding:2.8rem 1.5rem;
    text-align:center; position:relative; z-index:1;
}

/* Hero */
.hero-wrap { text-align:center; padding:1.8rem 1rem .5rem; position:relative; z-index:1; }
.hero-title {
    font-family:'Yatra One',cursive; font-size:clamp(2.2rem,5.5vw,3.8rem);
    background:linear-gradient(135deg,var(--teal2),var(--gold),var(--saffron));
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    letter-spacing:.02em; line-height:1.1; margin:0;
    filter:drop-shadow(0 0 28px rgba(0,180,166,.25));
}
.hero-sub { color:var(--muted); font-size:.88rem; letter-spacing:.12em; text-transform:uppercase; margin-top:.35rem; font-weight:300; }
.hero-divider { display:flex; align-items:center; gap:.8rem; justify-content:center; margin:1.1rem auto; max-width:380px; }
.hero-divider span { flex:1; height:1px; background:linear-gradient(90deg,transparent,var(--teal),transparent); }
.hero-divider em { color:var(--gold); font-style:normal; font-size:1rem; }

/* Footer */
.footer { text-align:center; padding:2rem; color:rgba(107,143,165,.4); font-size:.7rem; letter-spacing:.1em; text-transform:uppercase; position:relative; z-index:1; }

.block-container { position:relative; z-index:1; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# LOAD MODEL
# ══════════════════════════════════════════════
@st.cache_resource
def load_model():
    with open("price_model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("label_encoders.pkl", "rb") as f:
        label_encoders = pickle.load(f)
    return model, label_encoders

try:
    model, label_encoders = load_model()
    model_loaded = True
except Exception as e:
    model_loaded = False
    model_error = str(e)

FEATURES = ['State', 'District', 'Market', 'Commodity', 'Variety', 'Grade']

# ══════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════
INDIAN_NUMBER_MAP = {
    "ek": 1, "do": 2, "teen": 3, "char": 4, "paanch": 5,
    "hazaar": 1000, "hazar": 1000,
    "ondu": 1, "eradu": 2, "mooru": 3,
    "nalku": 4, "aidu": 5, "saavira": 1000,
}

def extract_price(text):
    text = text.lower()
    digits = re.findall(r"\d+", text)
    if digits:
        return int(digits[0])
    try:
        return w2n.word_to_num(text)
    except Exception:
        pass
    total, tokens = 0, text.split()
    for i, word in enumerate(tokens):
        if word in INDIAN_NUMBER_MAP:
            value = INDIAN_NUMBER_MAP[word]
            if value < 10 and i + 1 < len(tokens):
                nxt = tokens[i + 1]
                if nxt in INDIAN_NUMBER_MAP and INDIAN_NUMBER_MAP[nxt] >= 1000:
                    total += value * INDIAN_NUMBER_MAP[nxt]
                    continue
            total += value
    return total if total > 0 else None

def speech_to_text(audio_bytes):
    if not audio_bytes:
        return ""
    recognizer = sr.Recognizer()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        with sr.AudioFile(tmp_path) as source:
            audio_data = recognizer.record(source)
        return recognizer.recognize_google(audio_data)
    except Exception:
        return ""
    finally:
        os.unlink(tmp_path)

def predict_price(state, district, market, commodity, variety, grade):
    if not model_loaded:
        return None
    vals = {'State': state, 'District': district, 'Market': market,
            'Commodity': commodity, 'Variety': variety, 'Grade': grade}
    encoded = []
    for col in FEATURES:
        le = label_encoders[col]
        if vals[col] not in le.classes_:
            return None
        encoded.append(le.transform([vals[col]])[0])
    X = np.array(encoded).reshape(1, -1)
    return int(model.predict(X)[0])

# ══════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1rem 0 .5rem;'>
      <span style='font-family:"Yatra One",cursive;font-size:1.5rem;
            background:linear-gradient(135deg,#00D4C4,#FFD166,#FF6B1A);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
        🌿 Mandi Mitra
      </span>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    lang = st.radio(
        "🌐 Language / भाषा / ಭಾಷೆ",
        options=["English", "हिन्दी", "ಕನ್ನಡ"],
        key="lang_choice",
    )
    L = LANG_STRINGS[lang]

    st.divider()
    st.markdown("**Features**" if lang == "English" else ("**विशेषताएं**" if lang == "हिन्दी" else "**ವೈಶಿಷ್ಟ್ಯಗಳು**"))
    for feat in L["features_list"]:
        st.markdown(f"• {feat}")

    st.divider()
    st.caption(L["sidebar_about"])
    st.divider()

    if model_loaded:
        st.success("✅ Model ready")
    else:
        st.error("❌ Model not found")

    st.markdown("""
    <div style='margin-top:1.2rem;text-align:center;font-size:.68rem;
                color:rgba(107,143,165,.45);letter-spacing:.08em;'>
      AGMARKNET · RANDOM FOREST<br>EN · HI · KN
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════
st.markdown(f"""
<div class="hero-wrap">
  <div class="hero-title">{L['title']}</div>
  <div class="hero-sub">{L['subtitle']}</div>
  <div class="hero-divider"><span></span><em>✦</em><span></span></div>
</div>
""", unsafe_allow_html=True)

if not model_loaded:
    st.error(f"⚠️ Model files not found. Ensure `price_model.pkl` and `label_encoders.pkl` are in the working directory.\n\n`{model_error}`")
    st.stop()

dropdowns = {col: sorted(label_encoders[col].classes_.tolist()) for col in FEATURES}

# ══════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════
tab_predict, tab_negotiate, tab_about = st.tabs(
    [L["predict_tab"], L["negotiate_tab"], L["about_tab"]]
)

# ──────────────────────────────────────────────
# TAB 1 — PREDICTION
# ──────────────────────────────────────────────
with tab_predict:
    col_form, col_result = st.columns([1.05, 1], gap="large")

    with col_form:
        st.markdown(f'<div class="sec-pill">📍 {L["location_section"]}</div>', unsafe_allow_html=True)
        r1a, r1b = st.columns(2)
        with r1a:
            state = st.selectbox(L["state"], dropdowns['State'], key="state")
        with r1b:
            district = st.selectbox(L["district"], dropdowns['District'], key="district")
        market = st.selectbox(L["market"], dropdowns['Market'], key="market")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="sec-pill">🌾 {L["commodity_section"]}</div>', unsafe_allow_html=True)
        r2a, r2b = st.columns(2)
        with r2a:
            commodity = st.selectbox(L["commodity"], dropdowns['Commodity'], key="commodity")
            grade     = st.selectbox(L["grade"],     dropdowns['Grade'],     key="grade")
        with r2b:
            variety   = st.selectbox(L["variety"],   dropdowns['Variety'],   key="variety")

        st.markdown("<br>", unsafe_allow_html=True)
        predict_clicked = st.button(L["predict_btn"], use_container_width=True)

    with col_result:
        st.markdown("<br>", unsafe_allow_html=True)

        if predict_clicked:
            with st.spinner("Calculating…"):
                pred = predict_price(
                    st.session_state.state, st.session_state.district,
                    st.session_state.market, st.session_state.commodity,
                    st.session_state.variety, st.session_state.grade
                )
            if pred is None:
                st.error("❌ Could not predict — some selected values may be unseen by the model.")
            else:
                st.session_state["predicted_price"] = pred
                st.toast(f"✅ Predicted: ₹{pred:,}", icon="🌿")

        if "predicted_price" in st.session_state:
            p = st.session_state["predicted_price"]

            # Native st.metric
            st.metric(label=L["predicted_label"], value=f"₹{p:,}")
            st.caption(L["per_quintal"])

            st.markdown("<br>", unsafe_allow_html=True)

            # Price band table inside expander
            with st.expander(f"📊 {L['price_band']}"):
                floor = int(p * 0.75)
                low   = int(p * 0.90)
                high  = int(p * 1.10)
                st.markdown(f"""
| Zone | Range |
|------|-------|
| 🔴 Below floor | < ₹{floor:,} |
| 🟡 Negotiate   | ₹{floor:,} – ₹{low:,} |
| 🟢 Fair zone   | ₹{low:,} – ₹{high:,} |
| ⭐ Premium     | > ₹{high:,} |
                """)
                st.progress(0.90, text="Fair threshold: 90% of predicted price")
        else:
            st.markdown(f"""
            <div class="ph-card">
                <div style="font-size:2.8rem;margin-bottom:.6rem;">🌾</div>
                <div style="font-weight:600;color:#EEF2F7;margin-bottom:.4rem;">{L['placeholder_title']}</div>
                <div style="color:#6B8FA5;font-size:.85rem;">{L['placeholder_body']}</div>
            </div>
            """, unsafe_allow_html=True)

# ──────────────────────────────────────────────
# TAB 2 — NEGOTIATION
# ──────────────────────────────────────────────
with tab_negotiate:
    if "predicted_price" not in st.session_state:
        st.warning(L["no_price_warning"])
    else:
        predicted_price = st.session_state["predicted_price"]
        n_left, n_right = st.columns([1, 1], gap="large")

        with n_left:
            st.markdown(f'<div class="sec-pill">🎙️ {L["negotiate_tab"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="tip-box">{L["voice_tip"]}</div>', unsafe_allow_html=True)

            audio_input = st.audio_input(L["record_label"], key="audio_rec")
            audio_bytes = audio_input.read() if audio_input is not None else None

            manual_price = st.text_input(
                L["type_offer"],
                placeholder="e.g. 1800",
                key="manual_price"
            )

            st.markdown("<br>", unsafe_allow_html=True)
            evaluate_clicked = st.button(L["evaluate_btn"], use_container_width=True)

        with n_right:
            # Always show reference price
            st.metric(label=L["mandi_price"], value=f"₹{predicted_price:,}")
            st.markdown("<br>", unsafe_allow_html=True)

            if evaluate_clicked:
                spoken_text, offered = "", None

                if audio_bytes:
                    with st.spinner("Transcribing…"):
                        spoken_text = speech_to_text(audio_bytes)
                    if spoken_text:
                        offered = extract_price(spoken_text)

                if offered is None and manual_price.strip():
                    digits = re.findall(r"\d+", manual_price)
                    if digits:
                        offered = int(digits[0])
                        spoken_text = f"₹{offered} (manual)"

                if offered is None:
                    st.warning(L["no_offer_warning"])
                else:
                    diff     = offered - predicted_price
                    diff_pct = diff / predicted_price * 100
                    conf     = max(0.0, min(100.0, 100 - abs(diff_pct)))
                    is_fair  = offered >= predicted_price * 0.95

                    # Three metrics in a row
                    m1, m2, m3 = st.columns(3)
                    m1.metric(L["your_offer"],  f"₹{offered:,}", delta=f"{diff_pct:+.1f}%")
                    m2.metric(L["mandi_price"], f"₹{predicted_price:,}")
                    m3.metric(L["confidence"],  f"{conf:.1f}%")

                    st.markdown("<br>", unsafe_allow_html=True)

                    # Status + progress
                    status_label = L["fair_offer"] if is_fair else L["low_offer"]
                    icon = "✅" if is_fair else "⚠️"
                    st.caption(f"{icon} {status_label}")
                    st.progress(conf / 100)

                    st.markdown("<br>", unsafe_allow_html=True)

                    # Advice box
                    if is_fair:
                        st.success(L["advice_fair"])
                    elif diff_pct >= -10:
                        st.warning(L["advice_near"])
                    else:
                        st.error(L["advice_low"])

                    if spoken_text:
                        st.caption(f"🎤 {L['heard']}: *{spoken_text}*")

                    st.toast(f"⚖️ {L['eval_complete']}", icon="✅")

# ──────────────────────────────────────────────
# TAB 3 — ABOUT
# ──────────────────────────────────────────────
with tab_about:
    a1, a2 = st.columns([1.6, 1], gap="large")
    with a1:
        st.markdown(L["about_content"])
    with a2:
        st.markdown("#### 📈 Model Stats" if lang == "English" else "#### 📈 मॉडल जानकारी" if lang == "हिन्दी" else "#### 📈 ಮಾದರಿ ಮಾಹಿತಿ")
        st.metric("Algorithm", "Random Forest")
        st.metric("Data", "AGMARKNET")
        st.metric("Languages", "3")
        st.metric("Features", "6")

# ══════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════
st.markdown("""
<div class="footer">
  Mandi Mitra · AI Price Intelligence · India 🇮🇳 &nbsp;·&nbsp;
  English &nbsp;·&nbsp; हिन्दी &nbsp;·&nbsp; ಕನ್ನಡ &nbsp;·&nbsp;
  Random Forest &nbsp;·&nbsp; AGMARKNET
</div>
""", unsafe_allow_html=True)
