import argparse

import polib

from _translations import translations as t


def get_translations(translations):
    # Remove the extra quotes from the keys and values
    return {k.strip('"'): v.strip('"') for k, v in translations.items()}


# Update the .po file with the translations
def update_po_file(po_file):
    translations = get_translations(t)
    for entry in po_file:
        if entry.msgid in translations.values():
            # Get the corresponding key from the dictionary
            key = [k for k, v in translations.items() if v == entry.msgid][0]

            # Update the msgstr with the key from the dictionary
            entry.msgstr = key

    # Save the updated .po file
    po_file.save()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="Path to the .po file")
    args = parser.parse_args()
    po_file = polib.pofile(args.filepath)

    update_po_file(po_file)


if __name__ == "__main__":
    main()
