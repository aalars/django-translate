import json

import requests

from constants import DEEPL_API_KEY, DEPL_BASE_URL


def translate(text):
    url = DEPL_BASE_URL
    headers = {"Authorization": DEEPL_API_KEY}
    data = {
        "text": text,
        "target_lang": "EN",
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        response_dict = json.loads(response.content.decode())
        return response_dict["translations"][0]["text"]
    else:
        print(f"Translation failed: {response.content.decode()}")
        return text
