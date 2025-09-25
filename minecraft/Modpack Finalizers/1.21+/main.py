"""@author Jose Stovall | github.com/oitsjustjose"""

import json
import os
import shutil
import sys
import zipfile
from dataclasses import dataclass
from typing import List

THIS_DIR = "\\".join(os.path.realpath(__file__).split("\\")[:-1])
IS_MODRINTH = sys.argv[1].endswith(".mrpack")

CONFIG_PATH = os.path.join(THIS_DIR, "..", "configuration.json")
PACK_UNZIP_PATH = os.path.join(THIS_DIR, "activepack")
PACK_ZIP_PATH = f"{PACK_UNZIP_PATH}.{'mrpack' if IS_MODRINTH else 'zip'}"


@dataclass
class ModpackInfo:
    name: str
    version: str


def print(obj) -> None:
    """Override the initial print so it goes to a logfile instead!"""
    log_nm_base = sys.argv[1].split("\\")[-1]
    with open(f"./{log_nm_base}.log", "a+", encoding="utf-8") as log_handle:
        log_handle.write(f"{str(obj)}\n")


def __cleanup() -> None:
    """File and dir cleanup for when the program exits"""
    # remove the copied zip file
    if os.path.exists(PACK_ZIP_PATH):
        os.unlink(PACK_ZIP_PATH)
    # remove any unzipped files
    if os.path.exists(PACK_UNZIP_PATH):
        shutil.rmtree(PACK_UNZIP_PATH)


def __get_pack_info() -> ModpackInfo:
    """
    Gets the modpack info based on the currently unzipped pack
    Returns None in the event of any failures
    """
    if not os.path.exists(PACK_UNZIP_PATH):
        print(
            f"[__get_pack_info]: Failed to get Modpack Info: {PACK_UNZIP_PATH} does not exist!"
        )
        return None

    manifest_path: str = None

    if IS_MODRINTH:
        manifest_path = os.path.join(PACK_UNZIP_PATH, "modrinth.index.json")
    else:
        manifest_path = os.path.join(PACK_UNZIP_PATH, "manifest.json")

    if not manifest_path:
        print(
            "[__get_pack_info]: Failed to get Modpack Info: could not find a valid manifest path!"
        )
        return None

    with open(manifest_path, "r") as handle:
        manifest = json.loads(handle.read())

    return ModpackInfo(
        manifest["name"], manifest["versionId" if IS_MODRINTH else "version"]
    )


def __patch_neo_curse() -> None:
    """
    Fixes an issue with CurseForge exports from Prism that makes them incompatible
    with the CurseForge launcher because CurseForge is fucking stupid
    """
    manifest_path = os.path.join(PACK_UNZIP_PATH, "manifest.json")

    if not os.path.exists(manifest_path):
        print(f"[__patch_neo_curse]: Failed to find manifest at {manifest_path}")
        return

    with open(manifest_path, "r") as handle:
        manifest = json.loads(handle.read())

    if "minecraft" not in manifest:
        print("[__patch_neo_curse]: Missing key \{minecraft\}")
        return

    if "modLoaders" not in manifest["minecraft"]:
        print("[__patch_neo_curse]: Missing key \{minecraft.modLoaders\}")
        return

    mc_version = manifest["minecraft"]["version"]
    if mc_version not in ["1.20.1"]:
        print(
            f"[__patch_neo_curse]: Minecraft {mc_version} does not need NeoForge cleanup (or if it does, clean up this script!)"
        )
        return

    for modloader in manifest["minecraft"]["modLoaders"]:
        if "neo" not in modloader["id"]:
            continue

        # Other versions might not need this patch, hard to say - 1.20.1 definitely does.
        if mc_version == "1.20.1":
            neo_version = modloader["id"].replace("neoforge-", "")
            modloader["id"] = f"neoforge-{mc_version}-{neo_version}"

    with open(manifest_path, "w") as handle:
        handle.write(json.dumps(manifest))


def main() -> None:
    """
    Processing flow (souper crude):

    1. Load the cleanup config
    2. Open the original zipped file
    3. Iterate through each cleanup config entry (don't forget to path prepend "overrides/"), deleting
    4. Re-zip if necessary?
    5. Profit?
    """

    if len(sys.argv) != 2:
        print("Missing 2nd parameter File")
        return

    # Copy the original file to ./activepack.[mrpack|zip]
    shutil.copy(sys.argv[1], PACK_ZIP_PATH)
    print("Copied pack to local dir")

    # Unzip the modpack -- .mrpacks are just glorified zip files too :)
    shutil.unpack_archive(PACK_ZIP_PATH, PACK_UNZIP_PATH, "zip")
    print("Unarchived pack successfully!")

    # Read in the config if it exists - if it doesn't, early exit
    if not os.path.exists(CONFIG_PATH):
        print(f"Failed to find configuration at {CONFIG_PATH}")
        __cleanup()
        return

    with open(CONFIG_PATH, "r") as handle:
        config = json.loads(handle.read())["remove"]

    # Prepend the "overrides/" path, remove all files necessary
    for target in [f"overrides/{x}" for x in config]:
        rm_path = os.path.join(PACK_UNZIP_PATH, target)
        if not os.path.exists(rm_path):
            continue

        if os.path.isdir(rm_path):
            shutil.rmtree(rm_path)
            print(f"Removed dir {rm_path}")
        else:
            os.unlink(rm_path)
            print(f"Removed file {rm_path}")

    # Fix CurseForge packs being pissed about NeoForge :V
    if not IS_MODRINTH:
        __patch_neo_curse()

    # Zip up the pack & cleanup the old working directory
    info = __get_pack_info()
    shutil.make_archive(
        os.path.join(THIS_DIR, f"{info.name} {info.version}"), "zip", PACK_UNZIP_PATH
    )
    shutil.rmtree(PACK_UNZIP_PATH)
    if IS_MODRINTH:
        os.rename(
            os.path.join(THIS_DIR, f"{info.name} {info.version}.zip"),
            os.path.join(THIS_DIR, f"{info.name} {info.version}.mrpack"),
        )

    # Rename .zip to .mrpack if it was a modrinth pack
    file_name = f"{info.name} {info.version}.{'mrpack' if IS_MODRINTH else 'zip'}"

    # Move the file back to where it should've started from
    og_dirname = "\\".join(sys.argv[1].split("\\")[:-1])
    shutil.move(os.path.join(THIS_DIR, file_name), os.path.join(og_dirname, file_name))
    print(
        f"Successfully processed & moved/replaced {'Modrinth' if IS_MODRINTH else 'CurseForge'} modpack"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        __cleanup()
        print(e)
