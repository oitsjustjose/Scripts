from argparse import ArgumentParser
from random import randint
from uuid import uuid4
from utils import copy_to_clipboard

def generate_uuid(length: int, current="") -> str:
    if len(current) >= length:
        return current[:length]

    next = current + str(uuid4()).replace("-", "")
    return generate_uuid(length, current=next)


def generate(length: int, chars: str, current="") -> str:
    if len(current) >= length:
        return current[:length]

    next = current + chars[randint(0, (len(chars) - 1))]

    return generate(length, chars, current=next)


def main(args) -> None:
    num = int(args.num)
    if args.uuid_only:
        # Max recursion depth workaround
        rem, accumulator = num, ""
        while rem > 0:
            amt = min(128, rem)
            accumulator += generate_uuid(amt)
            rem -= amt

        if args.copy_to_clipboard:
            copy_to_clipboard(accumulator)
            print("Copied to clipboard!")
        else:
            print(accumulator)
    else:
        exclusions = list(map(lambda x: str(x).strip(), args.exclude_chars.split(",")))
        char_choices = "ABCDEFGHIJKLMONPQRSTUVWXYZabcdefghijklmonpqrstuvwxyz1234567890!@#$%^&*()-=_+[]{}\\|;:,<.>/?`~"

        for exclusion in exclusions:
            char_choices = char_choices.replace(exclusion, "")

        # Max recursion depth workaround
        rem, accumulator = num, ""
        while rem > 0:
            amt = min(128, rem)
            accumulator += generate(amt, char_choices)
            rem -= amt

        if args.copy_to_clipboard:
            copy_to_clipboard(accumulator)
            print("Copied to clipboard!")
        else:
            print(accumulator)


if __name__ == "__main__":
    parser = ArgumentParser(
        prog="Make Random",
        description="Creates a random GUID-like value of a provided length",
    )
    parser.add_argument("num")
    parser.add_argument("-u", "--uuid-only", action="store_true")
    parser.add_argument("-e", "--exclude-chars", default="")
    parser.add_argument("-c", "--copy-to-clipboard", action="store_true")

    args = parser.parse_args()
    main(args)
