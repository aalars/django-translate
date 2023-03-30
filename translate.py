import argparse
import ast
import os
import re
from typing import Optional, Union

import libcst as cst
from libcst._nodes.base import CSTValidationError

from constants import IGNORE_WORDS, PATTERN
from deepl_translate import translate

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
    def __init__(self, lazy: bool = False):
        super().__init__()
        self.lazy = lazy

    def leave_SimpleString(
        self, original_node: cst.SimpleString, updated_node: cst.SimpleString
    ) -> Union[cst.SimpleString, cst.Call]:
        visitor = FindUserFacingString()
        updated_node.visit(visitor)
        gettext = "gettext_lazy" if self.lazy else "gettext"
        if visitor.string:
            # Some strings cause the parser to fail
            translated_string = translate(visitor.string)
            TRANSLATIONS[visitor.string] = translated_string
            try:
                print(cst.ensure_type(updated_node, cst.SimpleString).value)
                return cst.Call(
                    func=cst.Name(gettext),
                    args=[cst.Arg(cst.SimpleString(translated_string))],
                )
            except CSTValidationError as e:
                print(f"problem with {visitor.string} -- {e}")
                return updated_node
        return updated_node


def transform(source: str, lazy: bool = False) -> str:
    module = cst.parse_module(source)
    try:
        module = module.visit(ReplaceStringWithGettext(lazy=lazy))
        return module.code
    except AttributeError as e:
        print(f"problem with source -- {e}")
        print("____________________________________________________")
        return source


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="The directory to search for Python files")
    args = parser.parse_args()
    py_files = []

    for root, dirs, files in os.walk(args.directory):
        py_files.extend(
            os.path.join(root, name)
            for name in files
            if name.endswith(".py") and "migrations" not in root
        )
    for file in py_files:
        print("")
        print("____________________________________________________")
        print(file)
        lazy = "models." in file or "models/" in file
        with open(file, "r+") as f:
            source_code = f.read()

            # Some strings cause the parser to fail
            transformed_code = transform(source_code, lazy=lazy)

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
