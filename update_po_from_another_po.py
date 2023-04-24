# Go through the strings in a po file, that don't have msgstr, and try to find them from another po file

import argparse
import polib


def update_po_from_another_po(source, target):
    for target_entry in target:
        if not target_entry.msgstr:
            for source_entry in source:
                if target_entry.msgid == source_entry.msgid:
                    target_entry.msgstr = source_entry.msgstr

    target.save()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", "--source_po_file", default=None, help="The .po file to check for translations"
    )
    parser.add_argument(
        "-t", "--target_po_file", default=None, help="The .po file to update"
    )
    args = parser.parse_args()
    source = polib.pofile(args.source_po_file)
    target = polib.pofile(args.target_po_file)

    update_po_from_another_po(source, target)


if __name__ == "__main__":
    main()
