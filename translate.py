import argparse
import contextlib
import os
import re
from typing import Optional, Union

import libcst as cst

from constants import IGNORE_WORDS, PATTERN
from deepl_translate import translate


class FindUserFacingString(cst.CSTVisitor):
    def __init__(self):
        self.string = ""

    def visit_SimpleString(self, node: cst.SimpleString) -> Optional[bool]:
        if not node.value or node.value == '""' or node.value == "''":
            return False

        if node.value in IGNORE_WORDS:
            return False

        if re.match(PATTERN, node.value):
            self.string = node.value

        return False


class ReplaceString(cst.CSTTransformer):
    def leave_SimpleString(
        self, original_node: cst.SimpleString, updated_node: cst.SimpleString
    ) -> Union[cst.SimpleString, cst.Call]:
        visitor = FindUserFacingString()
        updated_node.visit(visitor)
        if visitor.string:
            translated_string = visitor.string
            return cst.Call(
                func=cst.Name("gettext"),
                args=[cst.Arg(cst.SimpleString(translated_string))],
            )
        return updated_node


def transform(source: str) -> str:
    module = cst.parse_module(source)
    module = module.visit(ReplaceString())
    return module.code


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="The directory to search for Python files")
    args = parser.parse_args()
    py_files = [
        os.path.join(root, name)
        for root, dirs, files in os.walk(args.directory)
        for name in files
        if name.endswith(".py") and "migrations" not in root
    ]

    for file in py_files:
        with open(file, "r+") as f:
            source_code = f.read()

            # Some strings cause the parser to fail
            with contextlib.suppress(AttributeError):
                transformed_code = transform(source_code)

                f.seek(0)
                f.write(transformed_code)
                f.truncate()


if __name__ == "__main__":
    main()
