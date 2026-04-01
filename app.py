import streamlit as st
import os
from rag_engine import rag_query, speech_to_text, generate_price_trend, get_client

st.set_page_config(page_title="Mandi Mitra", layout="wide")

# ---------- API KEY ----------
if "OPENAI_API_KEY" not in os.environ:
    try:
        os.environ["OPENAI_API_KEY"] = st.secrets["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"]
    except:
        pass

# ---------- SIDEBAR ----------
with st.sidebar:
    st.title("👤 Profile")
    name = st.text_input("Name", "Farmer")
    lang = st.radio("Language", ["English", "हिन्दी", "ಕನ್ನಡ"])

# ---------- MAIN ----------
st.title("🌾 Mandi Mitra")

state = st.text_input("State")
district = st.text_input("District")
market = st.text_input("Market")
commodity = st.text_input("Commodity")
variety = st.text_input("Variety")
grade = st.text_input("Grade")

# ---------- VOICE ----------
audio = st.audio_input("🎙 Speak commodity/price")

voice_text = ""
if audio:
    with open("temp.wav", "wb") as f:
        f.write(audio.read())

    client = get_client()
    voice_text = speech_to_text("temp.wav", client)
    st.success(f"Recognized: {voice_text}")

# ---------- BUTTON ----------
if st.button("Get Price Insight"):
    result, docs = rag_query(
        state, district, market, commodity, variety, grade, lang
    )

    st.subheader("📊 AI Insight")
    st.write(result)

    # ---------- GRAPH ----------
    fig = generate_price_trend(docs)
    if fig:
        st.pyplot(fig)
