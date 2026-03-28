import streamlit as st
import pandas as pd
import numpy as np
import pickle
import re
import speech_recognition as sr
from word2number import w2n
import tempfile
import os


# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Mandi Mitra – Price Negotiation",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===============================
# CUSTOM CSS — Earthy, Bold, Agrarian
# ===============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Sans+3:wght@300;400;600&display=swap');

/* ── Root Palette ── */
:root {
    --soil:     #2C1A0E;
    --earth:    #5C3D1E;
    --clay:     #A0522D;
    --wheat:    #D4A853;
    --harvest:  #E8C87A;
    --cream:    #FDF6E3;
    --sage:     #7A9E6B;
    --moss:     #4A7A40;
    --sky:      #5B8DB8;
    --alert:    #C0392B;
    --card-bg:  rgba(253,246,227,0.92);
}

/* ── Global ── */
html, body, .stApp {
    background: var(--soil) !important;
    font-family: 'Source Sans 3', sans-serif;
    color: var(--cream);
}

/* Grain overlay */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
    opacity: 0.5;
}

/* ── Hero Banner ── */
.hero {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    position: relative;
    z-index: 1;
}
.hero h1 {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.2rem, 5vw, 3.8rem);
    font-weight: 900;
    color: var(--harvest);
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin: 0 0 0.3rem;
    text-shadow: 0 3px 20px rgba(0,0,0,0.4);
}
.hero p {
    color: var(--wheat);
    font-size: 1.05rem;
    font-weight: 300;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    opacity: 0.85;
}
.divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--wheat), transparent);
    margin: 1.5rem auto;
    max-width: 500px;
}

/* ── Card ── */
.card {
    background: var(--card-bg);
    border-radius: 16px;
    padding: 1.6rem 1.8rem;
    border: 1px solid rgba(212,168,83,0.25);
    box-shadow: 0 8px 32px rgba(0,0,0,0.35);
    backdrop-filter: blur(8px);
    margin-bottom: 1.2rem;
    position: relative;
    z-index: 1;
}
.card h3 {
    font-family: 'Playfair Display', serif;
    font-size: 1.15rem;
    color: var(--earth);
    margin: 0 0 1rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

/* ── Section labels ── */
.section-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--wheat);
    margin-bottom: 0.5rem;
    margin-top: 0.2rem;
    position: relative;
    z-index: 1;
}

/* ── Streamlit widget overrides ── */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(212,168,83,0.4) !important;
    border-radius: 10px !important;
    color: var(--cream) !important;
}
.stSelectbox label {
    color: var(--wheat) !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
}
div[data-baseweb="select"] > div {
    background: rgba(44,26,14,0.6) !important;
    border-color: rgba(212,168,83,0.35) !important;
    color: var(--cream) !important;
}

/* ── Primary button ── */
.stButton > button {
    background: linear-gradient(135deg, var(--moss), var(--sage)) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.7rem 2.5rem !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 16px rgba(74,122,64,0.4) !important;
    text-transform: uppercase !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(74,122,64,0.5) !important;
}

/* ── Result boxes ── */
.result-box {
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin: 0.5rem 0;
    position: relative;
    z-index: 1;
    backdrop-filter: blur(6px);
}
.result-fair {
    background: linear-gradient(135deg, rgba(74,122,64,0.2), rgba(122,158,107,0.15));
    border: 1px solid rgba(122,158,107,0.5);
}
.result-low {
    background: linear-gradient(135deg, rgba(192,57,43,0.2), rgba(192,57,43,0.1));
    border: 1px solid rgba(192,57,43,0.4);
}
.result-neutral {
    background: linear-gradient(135deg, rgba(91,141,184,0.2), rgba(91,141,184,0.1));
    border: 1px solid rgba(91,141,184,0.4);
}
.price-tag {
    font-family: 'Playfair Display', serif;
    font-size: 2.6rem;
    font-weight: 900;
    color: var(--harvest);
    line-height: 1;
}
.price-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--wheat);
    opacity: 0.8;
    margin-bottom: 0.3rem;
}
.metric-row {
    display: flex;
    gap: 1.2rem;
    align-items: flex-end;
    flex-wrap: wrap;
}

/* Confidence bar */
.conf-bar-wrap {
    background: rgba(0,0,0,0.25);
    border-radius: 99px;
    height: 8px;
    margin-top: 0.6rem;
    overflow: hidden;
}
.conf-bar-fill {
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, var(--sage), var(--harvest));
    transition: width 0.8s ease;
}

/* Badge */
.badge {
    display: inline-block;
    padding: 0.2rem 0.75rem;
    border-radius: 99px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.badge-fair { background: rgba(74,122,64,0.35); color: #a8d8a8; border: 1px solid #7A9E6B; }
.badge-low  { background: rgba(192,57,43,0.25); color: #e8a09a; border: 1px solid #C0392B; }

/* ── Tips strip ── */
.tip-strip {
    background: rgba(212,168,83,0.1);
    border-left: 3px solid var(--wheat);
    border-radius: 0 10px 10px 0;
    padding: 0.7rem 1rem;
    font-size: 0.85rem;
    color: var(--wheat);
    margin-top: 0.6rem;
    position: relative;
    z-index: 1;
}

/* ── Audio recorder container ── */
.audio-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem;
}

/* ── Footer ── */
.footer {
    text-align: center;
    padding: 1.5rem;
    color: rgba(253,246,227,0.3);
    font-size: 0.75rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    position: relative;
    z-index: 1;
}

/* Responsive tweaks */
@media (max-width: 640px) {
    .metric-row { flex-direction: column; gap: 0.6rem; }
}
</style>
""", unsafe_allow_html=True)


# ===============================
# LOAD MODEL & ENCODERS
# ===============================
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

# ===============================
# INDIAN NUMBER MAP
# ===============================
INDIAN_NUMBER_MAP = {
    "ek": 1, "do": 2, "teen": 3, "char": 4,
    "paanch": 5, "hazaar": 1000, "hazar": 1000,
    "ondu": 1, "eradu": 2, "mooru": 3,
    "nalku": 4, "aidu": 5, "saavira": 1000
}

# ===============================
# HELPERS
# ===============================
def extract_price(text):
    text = text.lower()
    digits = re.findall(r"\d+", text)
    if digits:
        return int(digits[0])
    try:
        return w2n.word_to_num(text)
    except:
        pass
    total = 0
    tokens = text.split()
    for i, word in enumerate(tokens):
        if word in INDIAN_NUMBER_MAP:
            value = INDIAN_NUMBER_MAP[word]
            if value < 10 and i + 1 < len(tokens):
                nxt = tokens[i + 1]
                if nxt in INDIAN_NUMBER_MAP and INDIAN_NUMBER_MAP[nxt] >= 1000:
                    total += value * INDIAN_NUMBER_MAP[nxt]
            else:
                total += value
    return total if total > 0 else None


def speech_to_text(audio_bytes):
    if audio_bytes is None:
        return ""
    recognizer = sr.Recognizer()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        with sr.AudioFile(tmp_path) as source:
            audio_data = recognizer.record(source)
        return recognizer.recognize_google(audio_data)
    except:
        return ""
    finally:
        os.unlink(tmp_path)


def predict_price(state, district, market, commodity, variety, grade):
    if not model_loaded:
        return None
    input_data = {
        'State': state, 'District': district, 'Market': market,
        'Commodity': commodity, 'Variety': variety, 'Grade': grade
    }
    encoded = []
    for col in FEATURES:
        le = label_encoders[col]
        if input_data[col] not in le.classes_:
            return None
        encoded.append(le.transform([input_data[col]])[0])
    X = np.array(encoded).reshape(1, -1)
    return int(model.predict(X)[0])


# ===============================
# HERO
# ===============================
st.markdown("""
<div class="hero">
    <h1>🌾 Mandi Mitra</h1>
    <p>AI-powered price prediction &amp; voice negotiation</p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)

if not model_loaded:
    st.error(f"⚠️ Could not load model files. Make sure `price_model.pkl` and `label_encoders.pkl` are in the working directory.\n\n`{model_error}`")
    st.stop()

dropdowns = {col: sorted(label_encoders[col].classes_.tolist()) for col in FEATURES}

# ===============================
# LAYOUT — Two columns
# ===============================
left_col, right_col = st.columns([1.1, 1], gap="large")

# ── LEFT: Inputs ──
with left_col:
    st.markdown('<div class="section-label">📍 Location & Market</div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            state     = st.selectbox("State",    dropdowns['State'],    key="state")
        with c2:
            district  = st.selectbox("District", dropdowns['District'], key="district")
        market    = st.selectbox("Market",    dropdowns['Market'],   key="market")

    st.markdown('<div class="section-label" style="margin-top:1rem;">🌽 Commodity Details</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        commodity = st.selectbox("Commodity", dropdowns['Commodity'], key="commodity")
        variety   = st.selectbox("Variety",   dropdowns['Variety'],   key="variety")
    with c4:
        grade     = st.selectbox("Grade",     dropdowns['Grade'],     key="grade")

    st.markdown("<br>", unsafe_allow_html=True)

    # Predict button
    predict_clicked = st.button("📊 Predict Mandi Price", use_container_width=True)

    if predict_clicked:
        pred = predict_price(state, district, market, commodity, variety, grade)
        if pred is None:
            st.error("❌ Could not predict — one or more selections are unseen by the model.")
        else:
            st.session_state["predicted_price"] = pred
            st.session_state["pred_inputs"] = (state, district, market, commodity, variety, grade)

    # Show prediction result under button
    if "predicted_price" in st.session_state:
        p = st.session_state["predicted_price"]
        st.markdown(f"""
        <div class="result-box result-neutral" style="margin-top:1rem;">
            <div class="price-label">Predicted Modal Price</div>
            <div class="price-tag">₹{p:,}</div>
            <div style="color:rgba(253,246,227,0.55); font-size:0.8rem; margin-top:0.3rem;">per quintal · based on historical mandi data</div>
        </div>
        """, unsafe_allow_html=True)

# ── RIGHT: Negotiation ──
with right_col:
    st.markdown('<div class="section-label">🎙️ Voice Negotiation</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="tip-strip">
        Speak your offered price in <b>English, Hindi, or Kannada</b><br>
        <span style="opacity:0.7">e.g. "I can sell for 2000" &nbsp;·&nbsp; "Do hazaar milega?" &nbsp;·&nbsp; "Eradu saavira"</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Built-in Streamlit audio input (no extra package needed, requires Streamlit ≥ 1.31)
    audio_input = st.audio_input("🎤 Record your offer price", key="audio_rec")
    audio_bytes = audio_input.read() if audio_input is not None else None

    # Manual fallback
    manual_price = st.text_input(
        "Or type your offer price (₹)",
        placeholder="e.g. 1800",
        key="manual_price",
        help="Type a number if you prefer not to use voice."
    )

    st.markdown("<br>", unsafe_allow_html=True)
    negotiate_clicked = st.button("🤝 Evaluate My Offer", use_container_width=True)

    if negotiate_clicked:
        if "predicted_price" not in st.session_state:
            st.warning("⚠️ Please predict the mandi price first (left panel).")
        else:
            predicted_price = st.session_state["predicted_price"]
            spoken_text = ""
            offered = None

            # Voice input
            if audio_bytes:
                with st.spinner("Transcribing your audio…"):
                    spoken_text = speech_to_text(audio_bytes)
                if spoken_text:
                    offered = extract_price(spoken_text)

            # Manual fallback
            if offered is None and manual_price.strip():
                digits = re.findall(r"\d+", manual_price)
                if digits:
                    offered = int(digits[0])
                    spoken_text = f"Manual entry: ₹{offered}"

            if offered is None:
                st.markdown("""
                <div class="result-box result-neutral">
                    🎤 Couldn't detect a price. Try speaking clearly or type your offer.<br><br>
                    <span style="opacity:0.7;font-size:0.85rem;">
                    Examples: "Two thousand" · "Do hazaar" · "Eradu saavira"
                    </span>
                </div>
                """, unsafe_allow_html=True)
            else:
                diff        = offered - predicted_price
                diff_pct    = diff / predicted_price * 100
                confidence  = max(0, 100 - abs(diff_pct))
                is_fair     = offered >= predicted_price * 0.95

                badge_cls   = "badge-fair" if is_fair else "badge-low"
                badge_text  = "✅ Fair Offer" if is_fair else "⚠️ Low Offer"
                box_cls     = "result-fair" if is_fair else "result-low"

                diff_str = (f"+₹{diff:,}" if diff >= 0 else f"-₹{abs(diff):,}")
                diff_color = "#a8d8a8" if diff >= 0 else "#e8a09a"

                # Build negotiation advice
                if is_fair:
                    advice = "This is a competitive offer. The buyer is likely to accept or make a minor counter-offer."
                elif diff_pct >= -10:
                    advice = "Slightly below market. Try nudging to at least ₹{:,} for a stronger position.".format(int(predicted_price * 0.97))
                else:
                    advice = "Significantly below market rate. Consider raising your offer or negotiating in stages."

                st.markdown(f"""
                <div class="result-box {box_cls}">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.8rem;">
                        <span class="badge {badge_cls}">{badge_text}</span>
                        <span style="font-size:0.78rem; color:rgba(253,246,227,0.5);">{spoken_text}</span>
                    </div>

                    <div class="metric-row">
                        <div>
                            <div class="price-label">Your Offer</div>
                            <div class="price-tag">₹{offered:,}</div>
                        </div>
                        <div style="color:{diff_color}; font-size:1.4rem; font-weight:700; padding-bottom:0.3rem;">{diff_str}</div>
                        <div>
                            <div class="price-label">Mandi Price</div>
                            <div class="price-tag" style="color:var(--sky);">₹{predicted_price:,}</div>
                        </div>
                    </div>

                    <div style="margin-top:1rem;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:0.25rem;">
                            <span style="font-size:0.78rem; color:var(--wheat);">Confidence Score</span>
                            <span style="font-size:0.78rem; font-weight:700; color:var(--harvest);">{confidence:.1f}%</span>
                        </div>
                        <div class="conf-bar-wrap">
                            <div class="conf-bar-fill" style="width:{confidence}%;"></div>
                        </div>
                    </div>

                    <div style="margin-top:1rem; font-size:0.85rem; color:rgba(253,246,227,0.75); border-top: 1px solid rgba(255,255,255,0.08); padding-top:0.8rem;">
                        💡 {advice}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ===============================
# FOOTER
# ===============================
st.markdown("""
<div class="divider" style="margin-top:2.5rem;"></div>
<div class="footer">
    Mandi Mitra · AI Price Intelligence for Indian Agriculture<br>
    Powered by Random Forest · Supports English · Hindi · Kannada
</div>
""", unsafe_allow_html=True)
