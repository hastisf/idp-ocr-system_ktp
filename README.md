<h1>
  <img src="logo.png" alt="KTPVision AI Logo" width="42" align="center">
  KTPVision AI
</h1>

AI-powered Indonesian KTP verification system that automatically classifies Indonesian identity cards, extracts structured information using Google's Gemini Vision model, validates NIK consistency, and securely stores verification history in a local SQLite database.

## 🚀 Live Demo

**https://idp-ocr-systemktp.streamlit.app/**

---

## ✨ Features

- 🤖 AI-powered Indonesian KTP classification
- 📄 OCR-based identity information extraction using Gemini 3.5 Flash Lite
- ✅ Automatic NIK validation and consistency checking
- 🪪 Structured extraction of KTP identity fields
- 🗄️ SQLite database logging for verification history
- 📊 Interactive processing history dashboard
- 📱 Responsive Streamlit web interface

---

## 🛠️ Tech Stack

- Python
- Streamlit
- Google Gemini 3.5 Flash Lite
- SQLite
- Pandas
- Pillow

---

## 🔄 Workflow

1. Upload an Indonesian KTP image.
2. AI verifies whether the uploaded document is a valid Indonesian KTP.
3. Gemini Vision extracts structured identity information.
4. The extracted NIK is automatically validated.
5. Verification results are displayed.
6. Verification history is stored in the SQLite database.

---

## 📋 Extracted Information

- Province
- Regency / City
- NIK
- Name
- Place & Date of Birth
- Gender
- Address
- RT / RW
- Village
- District
- Religion
- Marital Status
- Occupation
- Nationality
- Valid Until

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/hastisf/idp-ocr-system_ktp.git
cd idp-ocr-system_ktp
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Create `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

Run the application:

```bash
streamlit run app.py
```

---

## 📂 Project Structure

```
.
├── app.py
├── logo.png
├── requirements.txt
├── src/
│   ├── classifier.py
│   ├── database.py
│   ├── ocr_extractor.py
│   └── validator.py
└── README.md
```

---

## 👩‍💻 Author

**Hasti Sri Fatmawati**

- 💼 LinkedIn: https://www.linkedin.com/in/hasti-sri-fatmawati-361b49417/
- 💻 GitHub: https://github.com/hastisf
