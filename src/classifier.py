import requests
import base64
import json

def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

def classify_ktp(image_bytes, api_key):
    # Membersihkan API Key dari spasi dan karakter non-ASCII
    clean_api_key = str(api_key).strip().encode('ascii', 'ignore').decode('ascii')
    base64_img = encode_image(image_bytes)
    
    headers = {
        "Authorization": f"Bearer {clean_api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = """
    Analyze this image carefully. Is this an Indonesian National Identity Card (KTP Indonesia)?
    Respond strictly in JSON with a single key 'is_ktp' which is true or false.
    Example: {"is_ktp": true}
    """
    
    payload = {
        "model": "google/gemini-2.0-flash-exp:free",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                ]
            }
        ],
        "response_format": {"type": "json_object"}
    }
    
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    return json.loads(response.json()['choices'][0]['message']['content'])