"""
Usage:

poetry run python translate.py /path/to/your/django/project
"""

import json
import os
import re
import sys

import requests

DEEPL_API_KEY = ""
IGNORE_WORDS = [
    "None",
    "True",
    "False",
    "Id",
    "UnitId",
    "ELVIS",
    "EVR",
    "ID",
    "FSC_COC",
    "FSC_COC/FM",
    "PEFC_COC",
    "FSC_FM",
    "FSC_CW/FM",
    "PEFC_FC",
    "PEFC_GFC",
    "FM/COC",
    "FSC 100%",
    "FSC Mix 10%",
    "FSC Mix 20%",
    "FSC Mix 30%",
    "FSC Mix 40%",
    "FSC Mix 50%",
    "FSC Mix 60%",
    "FSC Mix 70%",
    "FSC Mix 80%",
    "FSC Mix 90%",
    "FSC Mix Credit",
    "FSC Controlled Wood",
    "FSC Mix xx,x%",
    "PEFC Controlled Sources",
    "CompanyCertificate",
    "CompanyAssortment",
    "AssortmentMapping",
    "EE",
    "Thorgate",
    "Tallinn",
    "Harjumaa",
]

# Define the regular expression pattern for matching strings
pattern = r"""(?<![_\.])["']([A-Z][^"']*(?:(?!(?<!\\)["']).)*)["'](?![_\w])"""

if not DEEPL_API_KEY:
    print("Please set DEEPL_API_KEY environment variable.")
    sys.exit(1)


def translate(text):
    url = "https://api-free.deepl.com/v2/translate"
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


def translate_directory(directory_):
    for root, dirs, files in os.walk(directory_):
        if "migrations" not in root:
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    # Open the file for reading and writing
                    with open(filepath, "r+") as f:
                        # Read the entire file into memory
                        content = f.read()
                        # Use regex to find all strings that need to be translated
                        matches = re.findall(pattern, content)
                        for match in matches:
                            if match not in IGNORE_WORDS:
                                # Call the translation function
                                translated_text = translate(match)
                                # Replace the original string with the translated string
                                content = content.replace(
                                    f'"{match}"', f'gettext("{translated_text}")'
                                )
                        # Return to the beginning of the file and write the modified content
                        f.seek(0)
                        f.write(content)
                        f.truncate()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <directory>")
        sys.exit(1)
    directory = sys.argv[1]
    translate_directory(directory)
