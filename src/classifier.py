import json
import io
from PIL import Image
import google.generativeai as genai


def is_ktp(image_bytes: bytes, api_key: str) -> bool:
  """Classifies whether the uploaded image is an Indonesian KTP or not."""
  try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    image = Image.open(io.BytesIO(image_bytes))

    prompt = (
        "Analyze this image carefully. Is this image an Indonesian KTP (Kartu"
        " Tanda Penduduk) or a photo/scan of an Indonesian KTP? Respond with"
        ' ONLY a JSON object: {"is_ktp": true, "reason": "short explanation"}'
        ' or {"is_ktp": false, "reason": "short explanation"}. Do NOT include'
        " markdown formatting or extra text."
    )

    response = model.generate_content([prompt, image])
    content = response.text.strip()

    if content.startswith("```"):
      content = content.split("```")[1]
      if content.startswith("json"):
        content = content[4:]

    result = json.loads(content.strip())
    return result.get("is_ktp", False)

  except Exception as e:
    print(f"Classifier error: {e}")
    return True  # Fallback aman
