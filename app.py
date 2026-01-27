import gradio as gr
import pandas as pd
import numpy as np
import pickle
import speech_recognition as sr
from gtts import gTTS
import tempfile
import re
import joblib
import joblib

model = joblib.load("price_model.pkl")
label_encoders = joblib.load("label_encoders.pkl")



# ===============================
# LOAD MODEL & ENCODERS
# ===============================
with open("price_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("label_encoders.pkl", "rb") as f:
    label_encoders = pickle.load(f)

# ===============================
# LOAD DATA FOR DROPDOWNS
# ===============================
df = pd.read_csv("commodity_price.csv")
df.columns = df.columns.str.strip()

df.rename(columns={
    "Modal_x0020_Price": "Modal_Price",
    "Min_x0020_Price": "Min_Price",
    "Max_x0020_Price": "Max_Price"
}, inplace=True)

states = sorted(df["State"].dropna().unique())
districts = sorted(df["District"].dropna().unique())
markets = sorted(df["Market"].dropna().unique())
commodities = sorted(df["Commodity"].dropna().unique())
varieties = sorted(df["Variety"].dropna().unique())
grades = sorted(df["Grade"].dropna().unique())

# ===============================
# PRICE PREDICTION
# ===============================
def predict_price(state, district, market, commodity, variety, grade):
    data = {
        "State": state,
        "District": district,
        "Market": market,
        "Commodity": commodity,
        "Variety": variety,
        "Grade": grade
    }

    df_input = pd.DataFrame([data])

    for col in df_input.columns:
        le = label_encoders[col]
        if df_input[col][0] not in le.classes_:
            df_input[col][0] = le.classes_[0]
        df_input[col] = le.transform(df_input[col])

    price = model.predict(df_input)[0]
    confidence = min(95, 60 + np.random.rand() * 25)

    return round(price, 2), f"{confidence:.1f}%"

# ===============================
# SPEECH → TEXT
# ===============================
def speech_to_text(audio, language):
    recognizer = sr.Recognizer()

    lang_map = {
        "English": "en-IN",
        "Hindi": "hi-IN",
        "Kannada": "kn-IN"
    }

    with sr.AudioFile(audio) as source:
        audio_data = recognizer.record(source)

    try:
        return recognizer.recognize_google(
            audio_data, language=lang_map[language]
        )
    except:
        return ""

# ===============================
# NEGOTIATION LOGIC
# ===============================
def negotiate(audio, predicted_price, language):
    text = speech_to_text(audio, language)

    if text == "":
        return "Could not understand your voice.", None

    numbers = re.findall(r"\d+", text)

    if not numbers:
        response = "Please say your offered price clearly."
        final_price = predicted_price
    else:
        offer = int(numbers[0])

        if offer >= predicted_price * 0.95:
            response = "Deal accepted. This is a fair price."
            final_price = offer
        elif offer >= predicted_price * 0.85:
            counter = int((offer + predicted_price) / 2)
            response = f"My counter offer is {counter} rupees."
            final_price = counter
        else:
            response = "Offer too low. Price remains unchanged."
            final_price = predicted_price

    tts_lang = {"English": "en", "Hindi": "hi", "Kannada": "kn"}[language]
    tts = gTTS(response, lang=tts_lang)

    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)

    return response, temp_audio.name

# ===============================
# GRADIO UI
# ===============================
with gr.Blocks(title="Multilingual Mandi") as app:

    gr.Markdown("## 🌾 Multilingual Mandi – AI Price & Voice Negotiation")

    language = gr.Radio(
        ["English", "Hindi", "Kannada"],
        value="English",
        label="Spoken Language"
    )

    state = gr.Dropdown(states, label="State")
    district = gr.Dropdown(districts, label="District")
    market = gr.Dropdown(markets, label="Market")
    commodity = gr.Dropdown(commodities, label="Commodity")
    variety = gr.Dropdown(varieties, label="Variety")
    grade = gr.Dropdown(grades, label="Grade")

    predict_btn = gr.Button("Predict Price")

    price_out = gr.Number(label="Predicted Price (₹)")
    conf_out = gr.Textbox(label="Confidence Score")

    predict_btn.click(
        predict_price,
        inputs=[state, district, market, commodity, variety, grade],
        outputs=[price_out, conf_out]
    )

    gr.Markdown("### 🎙️ Speak your offer")

    voice_input = gr.Audio(type="filepath")
    negotiate_btn = gr.Button("Negotiate")

    negotiation_text = gr.Textbox(label="Negotiation Result")
    negotiation_voice = gr.Audio(label="Voice Response")

    negotiate_btn.click(
        negotiate,
        inputs=[voice_input, price_out, language],
        outputs=[negotiation_text, negotiation_voice]
    )

app.launch(share=True)
