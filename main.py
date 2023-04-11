import argparse
import ast
import logging
import os
import re
from typing import Optional, Union

import libcst as cst
from libcst._nodes.base import CSTValidationError

from constants import IGNORE_WORDS, PATTERN
from translate import translate, translate_po_file

TRANSLATIONS = {}


class FindUserFacingString(cst.CSTVisitor):
    def __init__(self):
        self.string = ""

    def visit_SimpleString(self, node: cst.SimpleString) -> Optional[bool]:
        stripped = ast.literal_eval(node.value)

        if not node.value or not stripped or node.value == '""' or node.value == "''":
            return False

        if stripped in IGNORE_WORDS:
            return False

        if not re.match(PATTERN, node.value):
            return False

        self.string = node.value

        return False


class ReplaceStringWithGettext(cst.CSTTransformer):
    def __init__(
        self,
        lazy: bool = False,
        inspire_from_po: Union[str, bool] = False,
        target_language: str = "EN",
    ):
        super().__init__()
        self.lazy = lazy
        self.inspire_from_po = inspire_from_po
        self.target_language = target_language

    def leave_SimpleString(
        self, original_node: cst.SimpleString, updated_node: cst.SimpleString
    ) -> Union[cst.SimpleString, cst.Call]:
        visitor = FindUserFacingString()
        updated_node.visit(visitor)
        gettext = "gettext_lazy" if self.lazy else "gettext"
        if visitor.string:
            # Some strings cause the parser to fail
            translated_string, language = translate(
                visitor.string, self.target_language, self.inspire_from_po
            )
            TRANSLATIONS[visitor.string] = translated_string

            # We do not want to translate string in py files that are already EN
            # TODO: Put into variable
            if language == "ET":
                translated_string = visitor.string

            try:
                print(cst.ensure_type(updated_node, cst.SimpleString).value)
                return cst.Call(
                    func=cst.Name(gettext),
                    args=[cst.Arg(cst.SimpleString(translated_string))],
                )
            except CSTValidationError as e:
                logging.error("Problem with %s", visitor.string, e, exc_info=False)
                return updated_node
        return updated_node


def transform(
    source: str,
    target_language: str,
    lazy: bool = False,
    inspire_from_po: Union[str, bool] = False,
) -> str:
    module = cst.parse_module(source)
    try:
        module = module.visit(
            ReplaceStringWithGettext(
                lazy=lazy,
                inspire_from_po=inspire_from_po,
                target_language=target_language,
            )
        )
        return module.code
    except AttributeError as e:
        logging.error("Problem with source, fix this manually", e, exc_info=False)
        return source


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--directory",
        dest="directory",
        help="The directory to search for Python files",
    )
    parser.add_argument(
        "-p", "--po_file", default=None, help="The .po file to inspire from"
    )
    parser.add_argument(
        "-l", "--language", default="EN", help="Translation target language"
    )
    parser.add_argument(
        "-to",
        "--translate_only",
        default=False,
        help="Translates only the given po file",
        action=argparse.BooleanOptionalAction,
    )

    args = parser.parse_args()
    py_files = []

    if args.translate_only:
        if not args.po_file:
            raise ValueError("You must provide a po file to translate")

        translate_po_file(args.po_file, args.language)
        return

    for root, dirs, files in os.walk(args.directory):
        py_files.extend(
            os.path.join(root, name)
            for name in files
            if name.endswith(".py") and "migrations" not in root
        )
    for file in py_files:
        print("")
        print("-" * 80)
        print(file)
        print("-" * 80)
        lazy = "models." in file or "models/" in file
        with open(file, "r+") as f:
            source_code = f.read()

            # Some strings cause the parser to fail
            transformed_code = transform(
                source_code,
                target_language=args.language,
                lazy=lazy,
                inspire_from_po=args.po_file,
            )

            f.seek(0)
            f.write(transformed_code)
            f.truncate()

            # Write translations to file
            translations_file = "_translations.py"
            if not os.path.exists(translations_file):
                with open(translations_file, "w") as trans_file:
                    trans_file.write("# Translations\n")
            with open(translations_file, "w") as trans_file:
                trans_file.write(f"translations = {TRANSLATIONS}\n")


if __name__ == "__main__":
    main()
