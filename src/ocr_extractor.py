import json
from google import genai
from google.genai import types


def extract_ktp_data(image_bytes: bytes, api_key: str) -> dict:
    """
    Extract all fields from Indonesian KTP using Gemini Vision.
    """

    client = genai.Client(api_key=api_key)

    prompt = """
Extract all information from this Indonesian KTP image.

Return ONLY valid JSON.

Schema:

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

Rules:

- Do not explain.
- Do not use markdown.
- Return JSON only.
- NIK must contain digits only.
- Gender must be Male or Female.
- Nationality must be Indonesian or Foreigner.
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                prompt,
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type="image/jpeg",
                ),
            ],
            config={
                "response_mime_type": "application/json"
            },
        )

        return json.loads(response.text)

    except Exception as e:
        raise Exception(f"Gemini OCR Error: {e}")
