"""
Usage:

poetry run python translate.py /path/to/your/django/project
"""

import os
import re
import sys

from constants import DEEPL_API_KEY, IGNORE_WORDS, PATTERN
from deepl_translate import translate

if not DEEPL_API_KEY:
    print("Please set DEEPL_API_KEY environment variable.")
    sys.exit(1)


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
                        matches = re.findall(PATTERN, content)
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
