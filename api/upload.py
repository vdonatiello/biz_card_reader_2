# File: /api/upload.py
import base64
import json
import os
import requests
from flask import Request, Response

def handler(request: Request) -> Response:
    try:
        data = request.get_json()
        image_data = data.get("image")

        if not image_data:
            return Response("Missing image data", status=400)

        # Decode the base64 image
        image_bytes = base64.b64decode(image_data.split(",")[-1])

        # Send to OpenAI
        import os
        openai_key = os.environ.get("OPENAI_API_KEY")

        headers = {
            "Authorization": f"Bearer {openai_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract name, company, phone, email, job title from this business card."},
                        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(image_bytes).decode()}}
                    ]
                }
            ],
            "max_tokens": 300
        }
        openai_response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        openai_response.raise_for_status()

        result_text = openai_response.json()['choices'][0]['message']['content']

        # Forward to Make webhook
        make_url = "https://hook.eu2.make.com/oz6cgrhqg8bctxvqhscaws053nery1mp"
        make_response = requests.post(make_url, json={"data": result_text})
        make_response.raise_for_status()

        return Response(json.dumps({"status": "success", "data": result_text}), status=200, mimetype='application/json')

    except Exception as e:
        return Response(json.dumps({"status": "error", "message": str(e)}), status=500, mimetype='application/json')
