"""Functions for running numpad files.

Importing this module will provide the following functions:
    import_npd   : Load the code found at the given file location, or in lib
                 | if not found.
    load_program : Load and parse a given file, importing any files in its
                 | first line.
    run          : Run the numpad code written at the file given by file_path.
"""

import os

from numpad import NumpadError, NullScope
from numpadparse import parser

VERBOSE = False


def import_npd(file_path):
    """Load the code found at the given file location, or in lib if not found.

    Parameters:
        file_path : str of the filename EXCLUDING THE EXTENSION.
                  | Folders can be included, but will be ignored in backup
                  | file search.

    Returns:
        Raw text of the found npd file.

    Raises an error if the file cannot be found.
    """
    if VERBOSE:
        print("Loading", file_path)

    if os.path.exists(f"{file_path}.npd"):
        with open(f"{file_path}.npd", 'r', encoding='utf-8') as file:
            text = file.read()
        return text

    if os.path.exists(f"{file_path}.txt"):
        with open(f"{file_path}.txt", 'r', encoding='utf-8') as file:
            text = file.read()
        return text

    file_name = os.path.basename(file_path)

    if os.path.exists(f"lib/{file_name}.npd"):
        with open(f"lib/{file_name}.npd", 'r', encoding='utf-8') as file:
            text = file.read()
        return text

    if os.path.exists(f"lib/{file_name}.txt"):
        with open(f"lib/{file_name}.txt", 'r', encoding='utf-8') as file:
            text = file.read()
        return text

    raise NumpadError(
        f"{file_name} could not be found. Import failed."
    )


def load_program(file_path):
    """Load and parse a given file, importing any files in its first line.

    Parameters:
        file_path   : str of the filename being accessed, WITHOUT EXTENSION.

    Returns:
        numpad.StatementBlock object that can be run, provided a Scope

    Raises an error if file_path cannot be found.
    """
    if not (os.path.exists(f"{file_path}.npd") or
            os.path.exists(f"{file_path}.txt")):
        raise NumpadError(
            f"{file_path} could not be found."
        )

    full_path = os.path.abspath(file_path)
    file_name = os.path.basename(file_path)
    folder = os.path.dirname(full_path)

    files = [file_name]
    texts = [None]
    i = 0

    while i < len(files):
        if texts[i]:
            text = texts[i]
        else:
            text = import_npd(os.path.join(folder, files[i]))

        imports, _ = text.split('\n', maxsplit=1)
        texts[i] = text
        d_i = 1

        if imports:
            for im_file in imports.split('.'):
                if im_file in files[:i]:
                    j = files.index(im_file)
                    files.append(im_file)
                    del files[j]
                    texts.append(texts[j])
                    del texts[j]
                    d_i -= 1
                else:
                    files.append(im_file)
                    texts.append(None)

        i += d_i

    final_text = "\n"
    for text in texts:
        final_text = text.split('\n', maxsplit=1)[1] + final_text
    
    if VERBOSE:
        print(final_text)

    program = parser.parse(final_text)
    return program


def run(file_path, param=None, param_delim=','):
    """Run the numpad code written at the file given by file_path.

    Parameters:
        file_path   : str of the filename being accessed, WITHOUT EXTENSION.
        param       : str containing integer parameters, separated by the
                    | param_delim
        param_delim : str used to separate the values in param.
                    | DEFAULT: ','

    Returns:
        The final value of the variable *00. Either an int or a list.

    Raises an error if file_path cannot be found.
    """
    program = load_program(file_path)

    if param:
        variables = {
            f"*0{i}": int(val)
            for i, val in enumerate(
                param.split(param_delim)
            )
        }
        if VERBOSE:
            print("Loaded parameters:", variables)
    else:
        variables = {}
        if VERBOSE:
            print("No parameters loaded.")

    scope = NullScope(variables)
    scope.set_value("*00", 0)

    program.run(scope)

    return scope.get_value("*00")
