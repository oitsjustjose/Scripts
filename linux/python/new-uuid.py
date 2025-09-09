from argparse import ArgumentParser
from uuid import uuid4

from utils import copy_to_clipboard


def main(args):
    if args.copy_to_clipboard:
        copy_to_clipboard(str(uuid4()))
        print("Copied to clipboard!")
    else:
        print(str(uuid4()))


if __name__ == "__main__":
    parser = ArgumentParser(prog="new-uuid")
    parser.add_argument("-c", "--copy-to-clipboard", action="store_true")
    args = parser.parse_args()
    main(args)
