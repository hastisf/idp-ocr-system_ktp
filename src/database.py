import sqlite3

def init_db():
    conn = sqlite3.connect("ktp_ocr.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ktp_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            waktu_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            nik_masked TEXT,
            nama TEXT,
            jenis_dokumen TEXT,
            status_validasi TEXT,
            model_ai TEXT,
            raw_json TEXT
        )
    """)
    conn.commit()
    conn.close()