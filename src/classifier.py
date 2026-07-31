import json
from google import genai
from google.genai import types


def is_ktp(image_bytes: bytes, api_key: str) -> bool:
    """
    Classify whether the uploaded image is an Indonesian KTP.
    Returns True if KTP, otherwise False.
    """

    try:
        client = genai.Client(api_key=api_key)

        prompt = """
Analyze this image.

Determine whether this image is an Indonesian National Identity Card (KTP).

Return ONLY valid JSON.

Example:

{
  "is_ktp": true,
  "reason": "This is an Indonesian KTP."
}

or

{
  "is_ktp": false,
  "reason": "This is not an Indonesian KTP."
}
"""

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

        return result.get("is_ktp", False)

    except Exception as e:
        print(f"Gemini Classifier Error: {e}")
        return True
