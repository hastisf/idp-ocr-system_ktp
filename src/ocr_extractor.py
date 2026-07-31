import base64
import json
import requests


def extract_ktp_data(image_bytes: bytes, api_key: str) -> dict:
  """Extracts KTP fields using OpenRouter AI model with output in English."""
  headers = {
      "Authorization": f"Bearer {api_key}",
      "Content-Type": "application/json",
  }

  base64_image = base64.b64encode(image_bytes).decode("utf-8")

  prompt = """
    Extract all information from this Indonesian KTP image and return it strictly as a valid JSON object.
    Translate field names and values to clean, standard English.

    Required JSON Schema:
    {
      "province": "string or null",
      "regency_city": "string or null",
      "nik": "string or null",
      "name": "string or null",
      "place_and_date_of_birth": "string or null",
      "gender": "Male / Female or null",
      "blood_type": "string or null",
      "address": "string or null",
      "rt": "string or null",
      "rw": "string or null",
      "village_subdistrict": "string or null",
      "district": "string or null",
      "religion": "string or null",
      "marital_status": "Single / Married / Divorced or null",
      "occupation": "string or null",
      "nationality": "Indonesian / Foreigner or null",
      "expiry_date": "Lifetime / Date string or null"
    }

    Rules:
    1. Do NOT include markdown code fences like ```json ... ```. Return raw JSON string only.
    2. Ensure NIK contains digits only without spaces or dots.
    3. Standardize gender values to 'Male' or 'Female'.
    4. Standardize nationality values to 'Indonesian' or 'Foreigner'.
    """

  # Menggunakan model Gemini Flash gratis di OpenRouter yang sangat cepat & stabil untuk OCR
  payload = {
      "model": "google/gemini-2.5-flash:free",
      "messages": [{
          "role": "user",
          "content": [
              {"type": "text", "text": prompt},
              {
                  "type": "image_url",
                  "image_url": {
                      "url": f"data:image/jpeg;base64,{base64_image}"
                  },
              },
          ],
      }],
  }

response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers=headers,
    json=payload,
)
res_json = response.json()

# Pengecekan error
if "error" in res_json:
  error_msg = res_json["error"].get("message", "Unknown API error")
  raise Exception(f"OpenRouter API Error: {error_msg}")

if "choices" not in res_json or not res_json["choices"]:
  raise Exception(
      f"Gagal memproses gambar. Respon OpenRouter: {json.dumps(res_json)}"
  )

content = res_json["choices"][0]["message"]["content"].strip()

  # Cleaning markdown formatting
  if content.startswith("```"):
    content = content.split("```")[1]
    if content.startswith("json"):
      content = content[4:]

  return json.loads(content.strip())
