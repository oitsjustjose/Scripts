import os
from platform import release, system
from subprocess import check_call
from sys import executable as python
from tempfile import mktemp

from requests import get as fetch


def copy_to_clipboard(val: str) -> bool:
    sys = system()
    copy_cmd = ""
    if sys == "Windows":
        copy_cmd = "clip.exe"
    elif sys == "macOS":
        copy_cmd = "pbcopy"
    elif sys == "Linux":
        if "WSL" in release():
            copy_cmd = "clip.exe"  # Windows native clip.exe still works in WSL
        else:
            copy_cmd = "xclip -selection clipboard"
    else:
        print(f"System {sys} is not supported - cannot copy to clipboard")
        return False

    tmp_path = mktemp()
    with open(tmp_path, "w", encoding="utf-8") as fh:
        fh.write(val.strip())

    try:
        ret_val = check_call(f"cat {str(tmp_path)} | {copy_cmd}", shell=True)
    finally:
        os.unlink(tmp_path)

    return ret_val == 0


def install_package(package_name: str) -> None:
    def _prereq() -> None:
        res = os.system(f"{python} -m pip")
        if res == 0:
            return

        data = fetch("https://bootstrap.pypa.io/get-pip.py")
        filename = mktemp()
        with open(filename, "w", encoding="utf-8") as fh:
            fh.write(data.text)

        os.system(f"{python} {filename}")
        os.unlink(filename)

    _prereq()
    os.system(f"{python} -m pip install {package_name}")
    print(f"Package {package_name} has been installed - please rerun this command!")
