import os
from typing import Optional

import libcst as cst

from deepl_translate import translate


class UserFacingStringMatcher(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (cst.MetadataWrapper,)

    def __init__(self):
        super().__init__()
        self.matched_string = ""

    def visit_Str(self, node):
        print(node.value)
        if self.get_metadata(self, node).is_argument:
            # Ignore strings that are not arguments to functions
            return False
        if 'self.' in node.value:
            # Ignore strings that reference attributes, model fields, methods, etc
            return False
        self.matched_string = node.value


class ReplaceString(cst.CSTTransformer):
    def __init__(self, old_string: str, new_string: str):
        super().__init__()
        self.old_string = old_string
        self.new_string = new_string

    def leave_Call(self, original_node, updated_node):
        visitor = UserFacingStringMatcher()
        updated_node.visit(visitor)
        if not visitor.matched_string:
            return updated_node

        if len(updated_node.args) > 0:
            return cst.Call(func=(cst.Name(value='gettext')), args=[cst.Arg(cst.Str(updated_node.matched_string))])


def translate_file(file_path):
    with open(file_path, 'r') as f:
        source_code = f.read()

    module = cst.parse_module(source_code)
    matcher = UserFacingStringMatcher()
    module.visit(matcher)

    for node in matcher.matched_strings:
        # Translate the string and wrap it in either `gettext()` or `gettext_lazy()`
        translated_string = translate(node.value)
        if 'models.' in file_path:
            node.value = f'gettext_lazy("{translated_string}")'
        else:
            node.value = f'gettext("{translated_string}")'

    modified_source_code = module.code
    with open(file_path, 'w') as f:
        f.write(modified_source_code)


def translate_directory(directory_path):
    for dir_path, _, filenames in os.walk(directory_path):
        for filename in filenames:
            if filename.endswith('.py'):
                file_path = os.path.join(dir_path, filename)
                translate_file(file_path)


if __name__ == '__main__':
    translate_directory('/home/alar/workspaces/thorgate/vestman-vaheladu/vaheladu/storage')
