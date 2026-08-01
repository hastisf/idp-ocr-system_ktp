<p align="center">
  <img src="logo.png" alt="KTPVision AI Logo" width="180">
</p>

<h1 align="center">KTPVision AI</h1>

<p align="center">
AI-powered Indonesian KTP verification system that classifies identity documents, extracts structured information using Google's Gemini Vision, validates NIK consistency, and securely stores verification history.
</p>

<p align="center">

**Live Demo:** https://idp-ocr-systemktp.streamlit.app/

</p>

---

## Features

- AI-based Indonesian KTP classification
- OCR information extraction using Gemini 3.5 Flash Lite
- Automatic NIK validation
- Structured information extraction
- SQLite database logging
- Verification history dashboard
- Responsive Streamlit interface

---

## Technology Stack

- Python
- Streamlit
- Google Gemini 3.5 Flash Lite
- SQLite
- Pandas
- Pillow

---

## Workflow

1. Upload an Indonesian KTP image.
2. AI classifies whether the document is a valid Indonesian KTP.
3. Gemini Vision extracts structured identity information.
4. NIK consistency is automatically validated.
5. Verification results are displayed.
6. Processing history is stored in SQLite.

---

## Extracted Information

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

## Installation

```bash
git clone https://github.com/hastisf/idp-ocr-system_ktp.git
cd idp-ocr-system_ktp
pip install -r requirements.txt
streamlit run app.py
```

Create a `.streamlit/secrets.toml` file:

```toml
GEMINI_API_KEY="YOUR_API_KEY"
```

---

## Author

**Hasti Sri Fatmawati**

- LinkedIn: https://www.linkedin.com/in/hasti-sri-fatmawati-361b49417/
- GitHub: https://github.com/hastisf
