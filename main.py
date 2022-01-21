import argparse

import numpad
import numpadrun
from numpadparse import parser

argu = argparse.ArgumentParser()
argu.add_argument('--file', required=True)
argu.add_argument('--param', default=None)
argu.add_argument('--verbose', action='store_true')
argu.add_argument('--param_delim', default=',')

def main(args):

    numpad.VERBOSE = args.verbose
    numpadrun.VERBOSE = args.verbose

    final_value = numpadrun.run(
        args.file,
        args.param,
        args.param_delim
    )

    print("Result:", final_value)

if __name__ == "__main__":
    args = argu.parse_args()
    main(args)