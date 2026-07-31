import json
import sqlite3
import time
from datetime import datetime
import pandas as pd
import streamlit as st

from src.classifier import is_ktp
from src.database import init_db
from src.ocr_extractor import extract_ktp_data
from src.validator import validate_nik

# Configuration
st.set_page_config(page_title="KTPVision AI", layout="centered")

# Initialize Database
init_db()

# Custom CSS for Modern UI like VeriKTP
st.markdown(
    """
    <style>
    /* Background & Font */
    .stApp {
        background-color: #F8FAFC;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    .brand-title {
        color: #4F46E5;
        font-weight: 800;
        font-size: 24px;
        margin-bottom: 20px;
    }
    
    .custom-card {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        border: 1px solid #E2E8F0;
    }
    
    .ai-badge {
        background-color: #EFF6FF;
        color: #1D4ED8;
        padding: 8px 16px;
        border-radius: 10px;
        font-size: 13px;
        font-weight: 600;
        display: inline-block;
        margin-top: 14px;
        border: 1px solid #DBEAFE;
    }

    /* FIX TAB NAVIGATION (Jelas di HP & Desktop) */
    button[data-baseweb="tab"] {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #64748B !important;
        padding: 8px 16px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #FFFFFF !important;
        background-color: #2563EB !important;
        border-radius: 20px !important;
        font-weight: 700 !important;
    }

    /* BIKIN DROPZONE FILE UPLOADER PERSIS SEPERTI GAMBAR */
    div[data-testid="stFileUploader"] {
        width: 100%;
    }
    div[data-testid="stFileUploader"] label {
        font-size: 18px !important;
        font-weight: 700 !important;
        color: #1E293B !important;
        margin-bottom: 12px !important;
    }
    div[data-testid="stFileUploaderDropzone"] {
        border: 2px dashed #CBD5E1 !important;
        background-color: #FFFFFF !important;
        border-radius: 16px !important;
        padding: 30px 10px !important;
        text-align: center !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stFileUploaderDropzone"]:hover {
        border-color: #6366F1 !important;
        background-color: #F8FAFC !important;
    }

    /* Styling Teks Petunjuk Bawaan di Dalam Dropzone */
    [data-testid="stFileUploaderDropzoneInstructions"] {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #334155 !important;
    }

    /* Result Card Styles */
    .info-box {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 8px;
        border: 1px solid #E2E8F0;
    }
    .info-label {
        font-size: 11px;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 2px;
    }
    .info-value {
        font-size: 14px;
        font-weight: 600;
        color: #0F172A;
    }
    .sub-tag {
        color: #4F46E5;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Styling Tombol Process Document */
    div[data-testid="stVerticalBlock"] div.stButton > button {
        border: none !important;
        background-color: #2563EB !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        padding: 12px 20px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stVerticalBlock"] div.stButton > button:hover {
        background-color: #1D4ED8 !important;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3) !important;
    }

    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)

# Brand Header
st.markdown(
    '<div class="brand-title">KTPVision <span style="color:'
    ' #312E81;">AI</span></div>',
    unsafe_allow_html=True,
)

# Tabs Navigation
tab_verif, tab_history = st.tabs(["Upload & Verification", "Database History"])

with tab_verif:
  # Header Card
  st.markdown(
      """
        <div class="custom-card">
            <div class="sub-tag">AI Identity Verification</div>
            <h1 style="font-size: 28px; font-weight: 800; margin: 6px 0 10px 0; color: #0F172A;">
                KTPVision <span style="color: #4F46E5;">AI</span>
            </h1>
            <p style="color: #475569; font-size: 14px; line-height: 1.6; margin: 0;">
                KTPVision AI is an intelligent document verification tool designed to automate Indonesian KTP processing. It instantly detects document validity, extracts key fields via Vision AI, performs data validation, and logs all entries securely.
            </p>
            <div class="ai-badge">🤖 AI Model: Gemini 2.0 Flash</div>
        </div>
    """,
      unsafe_allow_html=True,
  )

  # Layout Grid untuk Desktop & HP
  col_upload, col_result = st.columns([1, 1], gap="large")

  with col_upload:
    # File Uploader Bawaan (Label jadi Judul, Kotaknya otomatis besar & responsive)
    uploaded_file = st.file_uploader(
        "Upload Document",
        type=["png", "jpg", "jpeg"],
        help="Format: PNG, JPG, JPEG. Max 200MB",
    )

    if uploaded_file:
      st.image(
          uploaded_file, caption="Selected Document", use_container_width=True
      )

    process_btn = st.button(
        "Process Document", type="primary", use_container_width=True
    )

  with col_result:
    st.subheader("Verification Result")

    if not process_btn and not uploaded_file:
      # Placeholder Tampilan Awal Sebelum di-Process
      st.markdown(
          """
            <div class="custom-card" style="text-align: center; background-color: #F8FAFC; padding: 40px 20px;">
                <div style="font-size: 24px; color: #94A3B8; font-weight: 700;">-</div>
                <div style="font-size: 13px; color: #64748B; margin-top: 4px;">Overall Validation Status</div>
            </div>
        """,
          unsafe_allow_html=True,
      )

    elif process_btn:
      if not uploaded_file:
        st.warning("Please upload a document image first.")
      else:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key:
          st.error("Missing GEMINI_API_KEY in Streamlit Secrets")
        else:
          image_bytes = uploaded_file.getvalue()
          start_time = time.time()

          with st.spinner("Processing document..."):
            try:
              is_ktp_doc = is_ktp(image_bytes, api_key)

              if not is_ktp_doc:
                st.error(
                    "Classification Failed: Uploaded document is NOT an"
                    " Indonesian KTP."
                )
              else:
                ocr_data = extract_ktp_data(image_bytes, api_key)
                nik = ocr_data.get("nik")
                gender = ocr_data.get("gender")
                val_status = validate_nik(nik, gender)
                elapsed_time = f"{round(time.time() - start_time, 2)}s"

                masked_nik = (
                    f"{nik[:6]}******{nik[-4:]}"
                    if nik and len(nik) == 16
                    else "INVALID"
                )
                name = ocr_data.get("name", "N/A")
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                conn = sqlite3.connect("ktp_ocr.db")
                cursor = conn.cursor()
                cursor.execute(
                    """
                                    INSERT INTO ktp_logs (waktu_upload, nik_masked, nama, jenis_dokumen, status_validasi, model_ai, raw_json)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                """,
                    (
                        current_time,
                        masked_nik,
                        name,
                        "Indonesian KTP",
                        val_status,
                        "Gemini 2.0 Flash",
                        json.dumps(ocr_data),
                    ),
                )
                db_id = cursor.lastrowid
                conn.commit()
                conn.close()

                # Status Banner
                st.markdown(
                    f"""
                                    <div class="custom-card" style="text-align: center; background-color: #EEF2FF; border-color: #C7D2FE;">
                                        <div style="font-size: 18px; font-weight: 700; color: #4338CA;">{val_status}</div>
                                        <div style="font-size: 12px; color: #6366F1; margin-top: 2px;">Overall Validation Status</div>
                                    </div>
                                """,
                    unsafe_allow_html=True,
                )

                # Grid Status
                c1, c2 = st.columns(2)
                with c1:
                  st.markdown(
                      '<div class="info-box"><div'
                      ' class="info-label">Classification</div><div'
                      ' class="info-value">Indonesian KTP</div></div>',
                      unsafe_allow_html=True,
                  )
                  st.markdown(
                      '<div class="info-box"><div class="info-label">Processing'
                      f' Time</div><div class="info-value">{elapsed_time}</div></div>',
                      unsafe_allow_html=True,
                  )
                with c2:
                  st.markdown(
                      '<div class="info-box"><div class="info-label">OCR'
                      ' Status</div><div'
                      ' class="info-value">Success</div></div>',
                      unsafe_allow_html=True,
                  )
                  st.markdown(
                      '<div class="info-box"><div'
                      ' class="info-label">Database ID</div><div'
                      f' class="info-value">#{db_id}</div></div>',
                      unsafe_allow_html=True,
                  )

                st.subheader("Extracted Information")
                fields = [
                    ("PROVINCE", ocr_data.get("province")),
                    ("REGENCY / CITY", ocr_data.get("regency_city")),
                    ("NIK", ocr_data.get("nik")),
                    ("NAME", ocr_data.get("name")),
                    ("BIRTH", ocr_data.get("place_and_date_of_birth")),
                    ("GENDER", ocr_data.get("gender")),
                    ("ADDRESS", ocr_data.get("address")),
                    (
                        "RT / RW",
                        (
                            f"{ocr_data.get('rt', '-')}"
                            f" / {ocr_data.get('rw', '-')}"
                        ),
                    ),
                    ("VILLAGE", ocr_data.get("village_subdistrict")),
                    ("DISTRICT", ocr_data.get("district")),
                    ("RELIGION", ocr_data.get("religion")),
                    ("MARITAL STATUS", ocr_data.get("marital_status")),
                    ("OCCUPATION", ocr_data.get("occupation")),
                    ("NATIONALITY", ocr_data.get("nationality")),
                    ("VALID UNTIL", ocr_data.get("expiry_date")),
                ]

                for label, val in fields:
                  display_val = val if val else "-"
                  st.markdown(
                      f"""
                                        <div class="info-box">
                                            <div class="info-label">{label}</div>
                                            <div class="info-value">{display_val}</div>
                                        </div>
                                    """,
                      unsafe_allow_html=True,
                  )

            except Exception as e:
              st.error(f"An error occurred during processing: {e}")

with tab_history:
  st.subheader("Processing History")
  conn = sqlite3.connect("ktp_ocr.db")
  try:
    df = pd.read_sql_query(
        """
            SELECT id AS "ID", waktu_upload AS "Timestamp", nik_masked AS "Masked NIK", 
                   nama AS "Name", status_validasi AS "Validation Status" 
            FROM ktp_logs ORDER BY id DESC
        """,
        conn,
    )
    conn.close()
    st.dataframe(df, use_container_width=True, hide_index=True)
  except Exception as e:
    st.error(f"Failed to fetch history: {e}")

# Footer Portfolio
st.markdown(
    """
    <div style="text-align: center; color: #64748B; font-size: 13px; margin-top: 50px; padding: 20px 0; border-top: 1px solid #E2E8F0;">
        <div>Hasti Sri Fatmawati | Data Analyst Portfolio</div>
        <div style="margin-top: 8px;">
            <a href="https://www.linkedin.com/in/hasti-sri-fatmawati-361b49417/" target="_blank" style="color: #4F46E5; text-decoration: none; font-weight: 600; margin-right: 10px;">LinkedIn</a> • 
            <a href="https://github.com/hastisf/" target="_blank" style="color: #4F46E5; text-decoration: none; font-weight: 600; margin-left: 10px;">GitHub</a>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)
