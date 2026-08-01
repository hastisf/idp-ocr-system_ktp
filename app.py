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

from PIL import Image

# Configuration
logo = Image.open("logo.png")

st.set_page_config(
    page_title="KTPVision AI",
    page_icon=logo,
    layout="centered",
)

# Initialize Database
init_db()

# Custom CSS for clean UI
st.markdown(
    """
    <style>
    .stApp {
    background-color: #F2EEFF;
    font-family: 'Inter', -apple-system, sans-serif;
    color: #1E293B;
}
    
    .brand-title {
        color: #312E81;
        font-weight: 700;
        font-size: 22px;
        margin-bottom: 20px;
    }
    
    .custom-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 24px rgba(99,102,241,.12);
        border: 1px solid #DDD6FE;
    }
    
    .ai-badge {
        background: #EDE9FE;
        color: #5B21B6;
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
        margin-top: 12px;
    }
    
    .info-box {
        background-color: #FAF9FF;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
        border: 1px solid #E9E5FF;
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
        color: #1E293B;
    }
    
    .sub-tag {
        color: #6366F1;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .footer-text {
        text-align: center;
        color: #94A3B8;
        font-size: 12px;
        margin-top: 30px;
        padding-bottom: 20px;
    }

    /* Styling Tombol Khusus */
    div[data-testid="stVerticalBlock"] div.stButton > button {
        border: 2px solid #FF4B4B !important;
        background-color: #2b1114 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        transition: all 0.3s ease !important;
    }

    div[data-testid="stVerticalBlock"] div.stButton > button:hover,
    div[data-testid="stVerticalBlock"] div.stButton > button:focus,
    div[data-testid="stVerticalBlock"] div.stButton > button:active {
        background-color: #ff4b4b !important;
        color: #ffffff !important;
        border-color: #ff4b4b !important;
        box-shadow: 0 0 8px rgba(255, 75, 75, 0.5) !important;
    }

    [data-testid="stFileUploaderDropzoneInstructions"] {
        display: none !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)

# Navigation
st.markdown(
    '<div class="brand-title">KTPVision AI</div>', unsafe_allow_html=True
)
tab_verif, tab_history = st.tabs(["Upload & Verification", "Database History"])

with tab_verif:
  # Header Card
  st.markdown(
      """
        <div class="custom-card">
            <div class="sub-tag">AI Identity Verification</div>
            <h1 style="font-size: 26px; margin: 6px 0 10px 0; color: #0F172A;">KTPVision <span style="color: #6366F1;">AI</span></h1>
            <p style="color: #475569; font-size: 14px; line-height: 1.5; margin: 0;">
                KTPVision AI is an intelligent document verification tool designed to automate Indonesian KTP processing. It instantly detects document validity, extracts key fields via Vision AI, performs data validation, and logs all entries securely.
            </p>
            <div class="ai-badge">AI Model: Gemini 3.5 Flash Lite</div>
        </div>
    """,
      unsafe_allow_html=True,
  )

  # Upload Document Section
  st.markdown(
      """
        <div style="margin-top: 15px; margin-bottom: 10px;">
            <div style="font-weight: 700; color: #1E293B; font-size: 15px;">Upload Document</div>
            <div style="color: #64748B; font-size: 12px; margin-top: 2px;">Format: PNG, JPG, JPEG. Max: 200MB.</div>
        </div>
    """,
      unsafe_allow_html=True,
  )

  uploaded_file = st.file_uploader(
      "Drop your KTP here or click to browse",
      type=["png", "jpg", "jpeg"],
      label_visibility="visible",
  )

  if uploaded_file:
    st.image(
        uploaded_file, caption="Selected Document", use_container_width=True
    )

  process_btn = st.button(
      "Process Document", type="primary", use_container_width=True
  )

  # Verification Result Section
  st.subheader("Verification Result")

  if process_btn:
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
            # 1. Classification
            is_ktp_doc = is_ktp(image_bytes, api_key)

            if not is_ktp_doc:
              st.error(
                  "Classification Failed: Uploaded document is NOT an"
                  " Indonesian KTP."
              )
            else:
              # 2. OCR Extraction
              ocr_data = extract_ktp_data(image_bytes, api_key)

              marital_map = {
                  "BELUM KAWIN": "SINGLE",
                  "KAWIN": "MARRIED",
                  "CERAI HIDUP": "DIVORCED",
                  "CERAI MATI": "WIDOWED",
              }
              if ocr_data.get("marital_status"):
                  marital = ocr_data["marital_status"].strip().upper()
                  ocr_data["marital_status"] = marital_map.get(
                      marital,
                      ocr_data["marital_status"],
                  )  

          
              # Translate occupation to English
              occupation_map = {
                  "BELUM/TIDAK BEKERJA": "UNEMPLOYED",
                  "MENGURUS RUMAH TANGGA": "HOMEMAKER",
                  "PELAJAR/MAHASISWA": "STUDENT",
                  "PELAJAR": "STUDENT",
                  "MAHASISWA": "STUDENT",
                  "PENSIUNAN": "RETIRED",
                  "PNS": "CIVIL SERVANT",
                  "PEGAWAI NEGERI": "CIVIL SERVANT",
                  "TNI": "MILITARY PERSONNEL",
                  "POLRI": "POLICE OFFICER",
                  "KARYAWAN SWASTA": "PRIVATE EMPLOYEE",
                  "PEGAWAI SWASTA": "PRIVATE EMPLOYEE",
                  "KARYAWAN BUMN": "STATE-OWNED ENTERPRISE EMPLOYEE",
                  "KARYAWAN BUMD": "REGIONAL GOVERNMENT ENTERPRISE EMPLOYEE",
                  "WIRASWASTA": "ENTREPRENEUR",
                  "PEDAGANG": "TRADER",
                  "PETANI": "FARMER",
                  "NELAYAN": "FISHERMAN",
                  "BURUH": "LABORER",
                  "BURUH HARIAN LEPAS": "DAILY LABORER",
                  "GURU": "TEACHER",
                  "DOSEN": "LECTURER",
                  "DOKTER": "DOCTOR",
                  "PERAWAT": "NURSE",
                  "BIDAN": "MIDWIFE",
                  "APOTEKER": "PHARMACIST",
                  "AKUNTAN": "ACCOUNTANT",
                  "ARSITEK": "ARCHITECT",
                  "PENGACARA": "LAWYER",
                  "NOTARIS": "NOTARY",
                  "HAKIM": "JUDGE",
                  "JAKSA": "PROSECUTOR",
                  "KONSULTAN": "CONSULTANT",
                  "PROGRAMMER": "PROGRAMMER",
                  "TEKNISI": "TECHNICIAN",
                  "MEKANIK": "MECHANIC",
                  "SOPIR": "DRIVER",
                  "PILOT": "PILOT",
                  "MASINIS": "TRAIN DRIVER",
                  "WARTAWAN": "JOURNALIST",
                  "SENIMAN": "ARTIST",
                  "PENELITI": "RESEARCHER",
                  "PEKERJA LEPAS": "FREELANCER",
              }

              if ocr_data.get("occupation"):
                occupation = ocr_data["occupation"].strip().upper()
                ocr_data["occupation"] = occupation_map.get(
                    occupation,
                    ocr_data["occupation"],
                )

              if (
                  ocr_data.get("expiry_date")
                  and ocr_data["expiry_date"].strip().upper() == "SEUMUR HIDUP"
              ):
                ocr_data["expiry_date"] = "LIFETIME"
                

              # 3. Validation
              nik = ocr_data.get("nik")
              gender = ocr_data.get("gender")
              val_status = validate_nik(nik, gender)

              elapsed_time = f"{round(time.time() - start_time, 2)}s"

              # 4. Database Storage
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

              # Overall Status Banner
              st.markdown(
                  f"""
                                <div class="custom-card" style="text-align: center; background-color: #EEF2FF; border-color: #C7D2FE;">
                                    <div style="font-size: 16px; font-weight: 700; color: #4338CA;">{val_status}</div>
                                    <div style="font-size: 12px; color: #6366F1; margin-top: 2px;">Overall Validation Status</div>
                                </div>
                            """,
                  unsafe_allow_html=True,
              )

              # Metric grid
              col1, col2 = st.columns(2)
              with col1:
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
              with col2:
                st.markdown(
                    '<div class="info-box"><div class="info-label">OCR'
                    ' Status</div><div'
                    ' class="info-value">Success</div></div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    '<div class="info-box"><div class="info-label">Database'
                    f' ID</div><div class="info-value">#{db_id}</div></div>',
                    unsafe_allow_html=True,
                )

              # Extracted Info list
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

# Footer
st.markdown(
    """
    <style>
    .footer-container {
        text-align: center;
        color: #64748B;
        font-size: 13px;
        margin-top: 40px;
        padding-top: 20px;
        padding-bottom: 20px;
        border-top: 1px solid #E2E8F0;
    }
    .footer-links a {
        color: #6366F1;
        text-decoration: none;
        font-weight: 600;
        margin: 0 10px;
    }
    .footer-links a:hover {
        text-decoration: underline;
    }
    </style>
    
    <div class="footer-container">
        <div>Hasti Sri Fatmawati | Data Analyst Portfolio</div>
        <div class="footer-links" style="margin-top: 8px;">
            <a href="https://www.linkedin.com/in/hasti-sri-fatmawati-361b49417/" target="_blank">LinkedIn</a> • 
            <a href="https://github.com/hastisf/" target="_blank">GitHub</a>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)
