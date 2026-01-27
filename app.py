import gradio as gr
import pandas as pd
import numpy as np
import pickle
import re
import speech_recognition as sr
from word2number import w2n

# ===============================
# LOAD MODEL & ENCODERS
# ===============================
with open("price_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("label_encoders.pkl", "rb") as f:
    label_encoders = pickle.load(f)

FEATURES = ['State', 'District', 'Market', 'Commodity', 'Variety', 'Grade']

# ===============================
# INDIAN NUMBER MAP (Hindi + Kannada)
# ===============================
INDIAN_NUMBER_MAP = {
    # Hindi
    "ek": 1, "do": 2, "teen": 3, "char": 4,
    "paanch": 5, "hazaar": 1000, "hazar": 1000,

    # Kannada
    "ondu": 1, "eradu": 2, "mooru": 3,
    "nalku": 4, "aidu": 5, "saavira": 1000
}

# ===============================
# PRICE EXTRACTION (ROBUST)
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

# ===============================
# VOICE TO TEXT
# ===============================
def speech_to_text(audio):
    if audio is None:
        return ""

    recognizer = sr.Recognizer()
    with sr.AudioFile(audio) as source:
        audio_data = recognizer.record(source)

    try:
        return recognizer.recognize_google(audio_data)
    except:
        return ""

# ===============================
# PRICE PREDICTION
# ===============================
def predict_price(state, district, market, commodity, variety, grade):
    input_data = {
        'State': state,
        'District': district,
        'Market': market,
        'Commodity': commodity,
        'Variety': variety,
        'Grade': grade
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
# NEGOTIATION LOGIC
# ===============================
def negotiate(audio, state, district, market, commodity, variety, grade):
    predicted_price = predict_price(
        state, district, market, commodity, variety, grade
    )

    if predicted_price is None:
        return "❌ Invalid input selection"

    spoken_text = speech_to_text(audio)
    offered = extract_price(spoken_text)

    if offered is None:
        return (
            "🎤 I couldn’t catch the price.\n"
            "Please say like:\n"
            "• I can sell for 2000\n"
            "• Do hazaar\n"
            "• Eradu saavira"
        )

    confidence = max(0, 100 - abs(predicted_price - offered) / predicted_price * 100)

    status = "✅ Fair Offer" if offered >= predicted_price * 0.95 else "⚠️ Low Offer"

    return (
        f"🗣 You said: {spoken_text}\n\n"
        f"💰 Your Offer: ₹{offered}\n"
        f"📊 Predicted Mandi Price: ₹{predicted_price}\n"
        f"{status}\n"
        f"🎯 Confidence Score: {round(confidence, 1)}%"
    )

# ===============================
# DROPDOWN VALUES
# ===============================
dropdowns = {
    col: sorted(label_encoders[col].classes_.tolist())
    for col in FEATURES
}

# ===============================
# GRADIO UI
# ===============================
with gr.Blocks(title="Multilingual Mandi Negotiation") as demo:
    gr.Markdown("## 🏪 Multilingual Mandi – Voice Negotiation App")
    gr.Markdown(
        "🎤 Speak naturally in **English / Hindi / Kannada**\n\n"
        "**Examples:**\n"
        "- I can sell for 2000\n"
        "- Do hazaar milega?\n"
        "- Eradu saavira kodtira?"
    )

    with gr.Row():
        state = gr.Dropdown(dropdowns['State'], label="State")
        district = gr.Dropdown(dropdowns['District'], label="District")

    with gr.Row():
        market = gr.Dropdown(dropdowns['Market'], label="Market")
        commodity = gr.Dropdown(dropdowns['Commodity'], label="Commodity")

    with gr.Row():
        variety = gr.Dropdown(dropdowns['Variety'], label="Variety")
        grade = gr.Dropdown(dropdowns['Grade'], label="Grade")

    audio = gr.Audio(type="filepath", label="🎤 Speak your offer")

    output = gr.Textbox(label="Negotiation Result", lines=8)

    btn = gr.Button("Negotiate")
    btn.click(
        negotiate,
        inputs=[audio, state, district, market, commodity, variety, grade],
        outputs=output
    )

demo.launch(share=True)
