import ast
import json

import polib
import requests

from constants import DEEPL_API_KEY, DEPL_BASE_URL


def translate(text, inspire_from_po):
    """
    If .po file is passed as a parameter then check if we have a translation in there.
    Otherwise, use DeepL.
    """
    if inspire_from_po:
        if translation := get_translation_from_po(text, inspire_from_po):
            return translation
    return translate_deepl(text)


def get_translation_from_po(text, inspire_from_po):
    """
    Try to get translation from .po file using polib
    """
    po_file = polib.pofile(inspire_from_po)
    for entry in po_file:
        if entry.msgstr and entry.msgstr == ast.literal_eval(text):
            print("   ↑ Existing in .po file")
            return f"'{entry.msgid}'"
    return None


def translate_deepl(text):
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
