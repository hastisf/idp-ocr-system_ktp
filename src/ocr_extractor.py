import io
import json
from google import genai
from PIL import Image


def extract_ktp_data(image_bytes: bytes, api_key: str) -> dict:
  """Extracts KTP fields using official new Google GenAI SDK."""
  # Client SDK baru dari Google
  client = genai.Client(api_key=api_key)

  image = Image.open(io.BytesIO(image_bytes))

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

  # Metode baru: client.models.generate_content
  response = client.models.generate_content(
      model="gemini-2.5-flash", contents=[image, prompt]
  )

  content = response.text.strip()

  if content.startswith("```"):
    content = content.split("```")[1]
    if content.startswith("json"):
      content = content[4:]

  return json.loads(content.strip())
