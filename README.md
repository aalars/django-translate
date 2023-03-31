Few helpers that somewhat automate the process of translating a Python (Django) project.

On high level the process is (with some manual steps in between)
- Extract the strings to be translated from the code
- Get the translations from .po file or translate the strings using DeepL Translate API
- Replace the strings in the code with the translated strings wrapped in `gettext()` or `gettext_lazy()` function
- Save the translations into a dictionary in the `_translations.py` file
- Translate the strings in the .po files using the dictionary

## main.py

Uses `libcst` to parse the Python code and extract the strings to be translated. 

These strings will be translated to English using DeepL Translate API and replaced with the translated strings in the code.

`gettext_lazy()` is only used if the path has `models.` or `models/` in it. 

Migration files are ignored (checks if `migrations` is in path).

Translations will be saved into a dictionary in the `_translations.py` file in the format:

```python
translations = {
    '"Puidu tüübid"': '"Types of wood"',
}
```

## update_po.py

Uses `polib` to parse the .po files and replace the strings with the translated strings from the `_translations.py` file.

## Guide

### Prerequisites

1. Clone the repo
2. Run `poetry install` to install the dependencies
3. Create yourself a DeepL API key and save it in the `DEEPL_API_KEY` environment variable

### Remove potential issues

Run the command for the first time, check logs for errors, revert those changes and fix the errors manually. 
Commit fixes. Use optional parameter `-p` with path to a `.po` file to first find for translations in tha file.

```bash
poetry run python main.py -d path/to/your/directory -p path/to/your/po/file
```

Why? Because `libcst` doesn't handle some strings well, and our code is not so good either. 
Also, our code does not detect if the string is already in a gettext function.

### Add ignore words, improve pattern

If there are some repeating strings that don't need to be translated, add them to the `IGNORE_WORDS` list in the `constants.py` file.

If you want then you can also improve the `PATTERN` regex in the `constants.py` file.

### Run the script for last time

When you are somewhat happy with the results, run the command last time. Manually go over the changes and fix any errors, 
keeping the translations in the dictionary in sync with the changes. Run `poetry run black .` to format the dictionary.

### Replace strings in .po files

Run the command below. This takes the values from the dictionary in the `_translations.py` file and replaces the strings in the .po files. 
Manually go over the changes to make sure everything is good to go.

```bash
poetry run python update_po.py path/to/your/po/file
```

## TODO

- [ ] Make it recognize and ignore if the string is already in a gettext function
- [ ] Better logic to detect if gettext or gettext_lazy should be used
- [ ] Would be better if EN strings were keys in the dictionary
- [ ] Possibly can skip the _translations.py file and just use the .po files
- [ ] Add tests
- [ ] Add possibility of a dry run -- gettext linter?
- [ ] Add imports
- [ ] Replace _() with respective gettext function
- [ ] Do not save translations in the dictionary with double quotes, use `ast.literal_eval(string)`
