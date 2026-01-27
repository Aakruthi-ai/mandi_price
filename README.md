# 🌾 Mandi Price Prediction & Negotiation App

An AI-powered web application that predicts **modal mandi prices** for agricultural commodities and helps farmers/traders **negotiate better prices** using machine learning, multilingual support, and voice input.

Built using **Python, Scikit-learn, Gradio**, and deployable on **Hugging Face Spaces**.
It includes dropdown menu of options for state, district, market,commodity,variety,grade from which user have to choose and can get its predicted price. It also includes a negotiation voice input for local vendors to know its negotiation price. 

---

## 🚀 Features

- 📈 **Price Prediction**
  - Predicts *Modal Price* of commodities using a trained Random Forest model
- 🌍 **Multilingual Support**
  - UI and dropdowns dynamically change based on selected language
  - Supports English, Hindi and Kannada (extensible)
- 🎙️ **Voice-driven Negotiation**
  - Users can speak their offered price
  - App evaluates and responds with negotiation advice
- 🤝 **Negotiation Assistant**
  - Compares offered price vs predicted market price
  - Suggests whether to accept, reject, or negotiate
- 📊 **Confidence Score**
  - Shows how confident the model is about the prediction
- 🧠 **Encoder-safe Inputs**
  - Prevents unseen-category errors during inference
- 🌐 **Web App Interface**
  - Built with Gradio
  - Ready for Hugging Face deployment

---


