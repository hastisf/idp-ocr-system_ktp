import json
from google import genai
from google.genai import types


def is_ktp(image_bytes: bytes, api_key: str) -> bool:
    """
    Classifies whether the uploaded image is an Indonesian KTP.
    Returns True if it is KTP, otherwise False.
    """

    try:
        client = genai.Client(api_key=api_key)

        prompt = """
Analyze this image carefully.

Determine whether this image is an Indonesian National Identity Card (KTP).

Respond ONLY with valid JSON.

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
            model="gemini-2.5-flash",
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

        result = json.loads(response.text)

        return result.get("is_ktp", False)

    except Exception as e:
        raise Exception(f"Gemini Classifier Error: {e}")
