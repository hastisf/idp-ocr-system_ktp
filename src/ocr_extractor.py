import json
from google import genai
from google.genai import types


def extract_ktp_data(image_bytes: bytes, api_key: str) -> dict:
    """
    Extract all fields from an Indonesian KTP using Gemini Vision.
    Returns a dictionary.
    """

    client = genai.Client(api_key=api_key)

    prompt = """
Extract all information from this Indonesian KTP image.

Return ONLY valid JSON.

Use this exact schema:

{
  "province": null,
  "regency_city": null,
  "nik": null,
  "name": null,
  "place_and_date_of_birth": null,
  "gender": null,
  "blood_type": null,
  "address": null,
  "rt": null,
  "rw": null,
  "village_subdistrict": null,
  "district": null,
  "religion": null,
  "marital_status": null,
  "occupation": null,
  "nationality": null,
  "expiry_date": null
}

Rules & Specific Field Instructions:
- "province": Extract the text right after "PROVINSI" from the header (e.g. "JAWA BARAT" or "DKI JAKARTA").
- "regency_city": Extract the text right after "KABUPATEN" or "KOTA" from the header (e.g. "KOTA BANDUNG" or "JAKARTA SELATAN").
- NIK must contain digits only without spaces or dots.
- Gender must be Male or Female.
- Nationality must be Indonesian or Foreigner.
- Return JSON only, no markdown formatting, no explanations.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=[
                prompt,
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type="image/jpeg",
                ),
            ],
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
            ),
        )

        result = json.loads(response.text)

        return result

    except Exception as e:
        raise Exception(f"Gemini OCR Error: {e}")
