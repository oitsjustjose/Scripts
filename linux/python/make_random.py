from uuid import uuid4
from argparse import ArgumentParser

def generate(length: int, current = ""):
    if len(current) >= length:
        return current[:length]
    
    next = current + str(uuid4()).replace("-", "")
    return generate(length, current = next)

def main(num: int) -> None:
    print(generate(num))

if __name__ == "__main__":
    parser = ArgumentParser(prog="Make Random", description="Creates a random GUID-like value of a provided length")
    parser.add_argument('num')

    args = parser.parse_args()
    main(int(args.num))
    
