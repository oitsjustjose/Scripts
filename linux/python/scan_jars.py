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
    
    def __test(file_name: str) -> bool:
        """Tests to see if a given filename within the jar matches the provided args
        Uses regex matching if the regex flag is passed to the program

        Args:
            file_name (str): The name (full path) of the file within the jar
        """
        if args.regex:
            try:
                return re.compile(args.query).search(file_name) is not None
            except re.error as err:
                print(f"Regex Error! Invalid regular expression passed:\nFull Trace:\n{err}")
                sys.exit(1)
        else:
            return args.query in file_name

    with zipfile.ZipFile(jar_path, 'r') as jar:
        for file_name in jar.namelist():
            if __test(file_name):
                print(f"[{jar_path.relative_to(scan_dir)}] :: {file_name}")

def main(args) -> None:
    scan_dir = Path(args.dir).resolve()

    for root, _, files in os.walk(scan_dir):
        for file in list(filter(lambda x: x.endswith(".jar"), files)):
            scan_jar(Path(f"{root}/{file}").resolve(), args)
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Jar Scanner', description='Scans jars for a given file')
    parser.add_argument('query', help='The term (or regex) to search for within the filename')
    parser.add_argument('-d', '--dir', default=os.getcwd(), help='The directory to scan. Defaults to cwd')
    parser.add_argument('-r', '--regex', default=False, action='store_true', help='Parse and use regex any in your query.')
    args = parser.parse_args()
    main(args)
