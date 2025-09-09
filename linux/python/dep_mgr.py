# https://bootstrap.pypa.io/get-pip.py

import os
import sys
import tempfile

import requests

PYTHON = sys.executable


def _prereq() -> None:
    res = os.system(f"{PYTHON} -m pip")
    if res == 0:
        return

    data = requests.get("https://bootstrap.pypa.io/get-pip.py")
    filename = tempfile.mktemp()
    with open(filename, "w", encoding="utf-8") as fh:
        fh.write(data.text)

    os.system(f"{PYTHON} {filename}")
    os.unlink(filename)


def install_package(package_name: str) -> None:
    _prereq()
    os.system(f"{PYTHON} -m pip install {package_name}")
    print(f"Package {package_name} has been installed - please rerun this command!")
