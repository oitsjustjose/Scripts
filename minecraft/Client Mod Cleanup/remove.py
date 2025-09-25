"""
@author Jose Stovall | github.com/oitsjustjose
"""

import json
import os
import sys
from typing import List


THIS_DIR = "\\".join(os.path.realpath(__file__).split("\\")[:-1])


def __print(obj: any):
    with open(os.path.join(THIS_DIR, "log.txt"), "a+", encoding="utf-8") as fh:
        fh.write(f"{obj}\n")


print = __print


if len(sys.argv) != 2:
    print("Missing 2nd parameter <FOLDER>")
    sys.exit(1)

target_dir: str = sys.argv[1]
client_mods: List[str] = []

with open(os.path.join(THIS_DIR, "mods.json"), "r", encoding="utf-8") as fh:
    data = json.loads(fh.read())
    if "mods" not in data:
        print('Client mod JSON missing "mods" Array')
        sys.exit(1)
    client_mods = data["mods"]


for file_name in os.listdir(target_dir):
    for mod in client_mods:
        if mod.lower() in file_name.lower():
            os.unlink(os.path.join(target_dir, file_name))
            break
