import argparse
import os
import re
import sys
import zipfile

from pathlib import Path


def scan_jar(jar_path: Path, args) -> None:
    """Opens the jar at jar_path and iterates over all files within,
    determining if the file name matches

    Args:
        jar_path (Path): The absolute path, resolved, to the Jar file
        args (Namespace): The program's args from argparse
    """

    scan_dir = Path(args.dir).resolve()

    def __test(scan_target: str) -> bool:
        """Scans the scan_target to see if it contains the queries from the parsed args.
            If the args instruct us to use regex, compile the regex and attempt to use it

        Args:
            scan_target (str): The text to scan for - can be a filename or file contents

        Returns:
            bool: True if the scan_target contains the query or regex
        """
        if args.regex:
            try:
                return re.compile(args.query).search(scan_target) is not None
            except re.error as err:
                print(
                    f"Regex Error! Invalid regular expression passed:\nFull Trace:\n{err}"
                )
                sys.exit(1)
        else:
            return args.query in scan_target

    with zipfile.ZipFile(jar_path, "r") as jar:
        for file_name in jar.namelist():
            if args.deep:  # Perform a deep scan of the jar itself
                with jar.open(file_name) as file:
                    try:
                        if __test(file.read().decode()):
                            print(f"[{jar_path.relative_to(scan_dir)}] :: {file_name}")
                    except UnicodeDecodeError:
                        pass  # This just means the file was a binary / non-text file

            elif __test(file_name):
                print(f"[{jar_path.relative_to(scan_dir)}] :: {file_name}")


def main(args) -> None:
    scan_dir = Path(args.dir).resolve()

    for root, _, files in os.walk(scan_dir):
        for file in list(filter(lambda x: x.endswith(".jar"), files)):
            scan_jar(Path(f"{root}/{file}").resolve(), args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Jar Scanner", description="Scans jars for a given file"
    )
    parser.add_argument(
        "query", help="The term (or regex) to search for within the filename"
    )
    parser.add_argument(
        "-d",
        "--dir",
        default=os.getcwd(),
        help="The directory to scan. Defaults to cwd",
    )
    parser.add_argument(
        "-r",
        "--regex",
        default=False,
        action="store_true",
        help="Parse and use regex any in your query.",
    )
    parser.add_argument(
        "-D",
        "--deep",
        default=False,
        action="store_true",
        help="Rather than searching the file *name* for the given term (or regex), searches the contents of files instead",
    )
    args = parser.parse_args()
    main(args)
