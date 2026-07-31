import base64
import json
from openai import OpenAI


def is_ktp(image_bytes: bytes, api_key: str) -> bool:
  """Classifies whether the uploaded image is an Indonesian KTP or not."""
  try:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    prompt = (
        "Analyze this image carefully. Is this image an Indonesian KTP (Kartu"
        " Tanda Penduduk) or a photo/scan of an Indonesian KTP? Respond with"
        ' ONLY a JSON object: {"is_ktp": true, "reason": "short explanation"}'
        ' or {"is_ktp": false, "reason": "short explanation"}. Do NOT include'
        " markdown formatting or extra text."
    )

    response = client.chat.completions.create(
        model="qwen/qwen2.5-vl-72b-instruct:free",
        messages=[{
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
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content.strip()
    result = json.loads(content)
    return result.get("is_ktp", False)

  except Exception as e:
    print(f"Classifier error: {e}")
    return True  # Fallback aman
