"""
Usage:

python translate.py /path/to/your/django/project
"""

import os
import re
import sys
import requests
import json

DEEPL_API_KEY = ""

# Define the regular expression pattern for matching strings
pattern = r"(?<![_\.])[\"']((?:(?!(?<!\\)[\"']).)*)[\"'](?![_\w])"

if not DEEPL_API_KEY:
    print("Please set DEEPL_API_KEY environment variable.")
    sys.exit(1)


def translate(text):
    url = 'https://api-free.deepl.com/v2/translate'
    headers = {'Authorization': DEEPL_API_KEY}
    data = {
        'text': text,
        'target_lang': 'EN',
    }
    response = requests.post(url, headers=headers, data=data)
    print(response.status_code)
    if response.status_code == 200:
        response_dict = json.loads(response.content.decode())
        # print("translated_text")
        # print(text)
        # print(response_dict['translations'][0]['text'])
        return response_dict['translations'][0]['text']
    else:
        print(f"Translation failed: {response.content.decode()}")
        return text


def translate_directory(directory_):
    for root, dirs, files in os.walk(directory_):
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
                        # Call the translation function
                        translated_text = translate(match)
                        # Replace the original string with the translated string
                        content = content.replace(f'"{match}"', f'gettext("{translated_text}")')
                    # Return to the beginning of the file and write the modified content
                    f.seek(0)
                    f.write(content)
                    f.truncate()

# def translate_directory(directory_):
#     # Define the regular expression pattern to match translatable strings
#     pattern = re.compile(r"[_|gettext]\(['\"](.*?)['\"]\)")
#
#     # Find and replace Estonian strings in .py files
#     for root, dirs, files in os.walk(directory_):
#         print("-------------------------------")
#         print(root)
#         print(dirs)
#         print(files)
#         for file_ in files:
#             if file_.endswith(".py"):
#                 filepath = os.path.join(root, file_)
#                 with open(filepath, "r") as file_:
#                     print("-------------------------------")
#                     print("file")
#                     print(file_)
#                     contents = file_.read()
#                 for match in re.findall(pattern, contents):
#                     print("-------------------------------")
#                     print("match")
#                     print(match)
#                     # skip strings that look like variable names or are all caps
#                     # if match.isupper() or re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', match):
#                     if match.isupper() or not re.match(r'^(?=.*[^\W_])(?!.*_(?:[^\W_]*_)+[^\W_]*$)[^\W\d_]+(?:[^\W_]*[^\W\d_])?$', match):
#                         continue
#                     english = translate(match)
#                     # wrap the string with gettext() or gettext_lazy()
#                     if "lazy" in contents:
#                         replacement = f"gettext_lazy('{english}')"
#                     else:
#                         replacement = f"gettext('{english}')"
#                     # replace the Estonian string with English translation in the .py file
#                     # contents = contents.replace(f"'{match}'", replacement)
#                     contents = re.sub(f"'{match}'", replacement, contents)
#                 with open(filepath, "w") as file_:
#                     file_.write(contents)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <directory>")
        sys.exit(1)
    directory = sys.argv[1]
    translate_directory(directory)
