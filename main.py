import argparse

import numpad
from numpadparse import parser

argu = argparse.ArgumentParser()
argu.add_argument('--file', required=True)
argu.add_argument('--param', default=None)
argu.add_argument('--verbose', action='store_true')

def load_text(text):

    imports, program = text.split('\n', maxsplit=1)

    if imports:
        for file in imports.split('/'):
            with open(f"{file}.npd", 'r', encoding='utf-8') as f:
                text = f.read()
                program = load_text(text) + program
    
    return program

def main(args):

    numpad.VERBOSE = args.verbose

    if args.param:
        variables = {
            f"*0{i}": int(val)
            for i, val in enumerate(
                args.param.split(',')
            )
        }
        if args.verbose:
            print("Loaded parameters:", variables)
    else:
        variables = {}
        if args.verbose:
            print("No parameters loaded.")

    with open(args.file, 'r', encoding='utf-8') as f:
        text = f.read()
        text = load_text(text) + '\n'
    
    if args.verbose:
        print(text)
    
    program = parser.parse(text)
    scope = numpad.NullScope(variables)
    scope.set_value("*00", 0)

    program.run(scope)

    print("Result:", scope.evaluate("*00"))

if __name__ == "__main__":
    args = argu.parse_args()
    main(args)