import ast
import json

import polib
import requests

from constants import DEEPL_API_KEY, DEPL_BASE_URL


def translate(text, target_language, inspire_from_po):
    """
    If .po file is passed as a parameter then check if we have a translation in there.
    Otherwise, use DeepL.
    """
    if inspire_from_po:
        if translation := get_translation_from_po(text, inspire_from_po):
            return translation, "EN"
    return translate_deepl(text, target_language)


def get_translation_from_po(text, inspire_from_po):
    """
    Try to get translation from .po file using polib
    """
    po_file = polib.pofile(inspire_from_po)

    txt = ast.literal_eval(text) if ("'" and '"' in text[:2]) else text
    for entry in po_file:
        if entry.msgstr and entry.msgstr == txt:
            print("   ↑ Existing in .po file")
            return f"'{entry.msgid}'"
    return None


def translate_po_file(po_file, target_language):
    """
    Update the .po file with the translations when msgstr is empty
    """
    file = polib.pofile(po_file)
    for entry in file:
        # show progress in percentage
        print(f"{round((file.index(entry) / len(file)) * 100)}%", end="\r")
        if not entry.msgstr:
            entry.msgstr, _ = translate(entry.msgid, target_language, None)
    file.save()


def translate_deepl(text, target_lang):
    url = DEPL_BASE_URL
    headers = {"Authorization": DEEPL_API_KEY}
    data = {
        "text": text,
        "target_lang": target_lang,
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        response_dict = json.loads(response.content.decode())
        # Here we assume that target_lang is EN, so if the detected language is EN, then we translate again with
        # target_lang=ET
        if (
            response_dict["translations"][0]["detected_source_language"]
            == target_lang
            == "EN"
        ):
            return translate_deepl(text, "ET")

        return response_dict["translations"][0]["text"], target_lang
    else:
        print(f"Translation failed: {response.content.decode()}")
        return text, "initial"
