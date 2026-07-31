import base64
import json
from openai import OpenAI


def extract_ktp_data(image_bytes: bytes, api_key: str) -> dict:
    """Extracts KTP fields using OpenRouter API."""

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

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

    try:
        response = client.chat.completions.create(
            model="qwen/qwen2.5-vl-72b-instruct:free",
            messages=[
                {
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
                }
            ],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content.strip()
        return json.loads(content)

    except Exception as e:
        raise Exception(f"OpenRouter Error: {e}")
