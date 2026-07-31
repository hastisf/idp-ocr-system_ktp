import base64
import json
import requests


def is_ktp(image_bytes: bytes, api_key: str) -> bool:
    """Classifies whether the uploaded image is an Indonesian KTP or not."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://streamlit.io",
        "X-Title": "IDP KTP App",
    }

    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    prompt = (
        "Analyze this image carefully. Is this image an Indonesian KTP (Kartu Tanda Penduduk) "
        "or a photo/scan of an Indonesian KTP? Respond with ONLY a JSON object: "
        '{"is_ktp": true, "reason": "short explanation"} or {"is_ktp": false, "reason": "short explanation"}. '
        "Do NOT include markdown formatting or extra text."
    )

    payload = {
        "model": "meta-llama/llama-3.2-11b-vision-instruct:free",
        "messages": [
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
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
        )
        res_json = response.json()

        if "error" in res_json:
            print(f"Classifier API Error: {res_json['error']}")
            return True  # Fallback: tetap izinkan jika API classifier error

        if "choices" not in res_json or not res_json["choices"]:
            print(f"Classifier invalid response: {res_json}")
            return True  # Fallback

        content = res_json["choices"][0]["message"]["content"].strip()

        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]

        result = json.loads(content.strip())
        return result.get("is_ktp", False)

    except Exception as e:
        print(f"Classifier exception: {e}")
        return True  # Fallback aman agar proses tetap berjalan
