"""@author Jose Stovall | github.com/oitsjustjose"""

from typing import List

import zipfile

import os
import sys
import shutil
import json
import toml

THIS_DIR = "\\".join(os.path.realpath(__file__).split("\\")[:-1])
CLEANUP_CONF_PATH = os.path.join(THIS_DIR, ".." "configuration.json")
MMC_EXPORT_CONFIG_PATH = os.path.join(THIS_DIR, "config.toml")
PACK_UNZIPPED_PATH = os.path.join(THIS_DIR, "activepack")
PACK_ZIP_PATH = os.path.join(THIS_DIR, "activepack.zip")
RP_DIR = os.path.join(PACK_UNZIPPED_PATH, "minecraft", "resourcepacks")
TROUBLEMAKERS_PATH = os.path.join(THIS_DIR, "troublemakers")


def print(obj):
    """override"""
    log_nm_base = sys.argv[1].split("\\")[-1]
    with open(f"./{log_nm_base}.log", "a+", encoding="utf-8") as log_handle:
        log_handle.write(f"{str(obj)}\n")


def _clean_pack():
    """
    Removes client-only configs/files
    """
    with open(CLEANUP_CONF_PATH, "r", encoding="utf-8") as handle:
        config = json.loads(handle.read())

    for to_del in config["remove"]:
        fpath = os.path.join(
            PACK_UNZIPPED_PATH, "minecraft", to_del.replace("/", os.path.sep)
        )
        if not os.path.exists(fpath):
            continue
        if os.path.isdir(fpath):
            shutil.rmtree(fpath)
            print(f"Removed directory {fpath}")
        else:
            os.unlink(fpath)
            print(f"Removed file {fpath}")


def _get_modpack_outnames(join: bool = False) -> List[str]:
    """
    Gets the MR_{packname}.mrpack and CF_{packname}.zip names based off of the config.toml contents
    Args: join (bool) [False]: Whether to join them to the current dir or not
    Returns: Tuple[str, str]: The MR_ and CF_ paths (in that order)
    """
    with open(MMC_EXPORT_CONFIG_PATH, "r", encoding="utf-8") as handle:
        name = toml.loads(handle.read())["name"]
    if join:
        return [
            os.path.join(THIS_DIR, f"MR_{name}.mrpack"),
            os.path.join(THIS_DIR, f"CF_{name}.zip"),
        ]
    return [f"MR_{name}.mrpack", f"CF_{name}.zip"]


def __cleanup() -> None:
    """Cleans up output files"""
    os.unlink(MMC_EXPORT_CONFIG_PATH)
    os.unlink(PACK_ZIP_PATH)
    shutil.rmtree(PACK_UNZIPPED_PATH)
    shutil.rmtree(TROUBLEMAKERS_PATH)
    for file in os.listdir(THIS_DIR):
        if file.startswith("CF_") or file.startswith("MR_"):
            os.unlink(os.path.join(THIS_DIR, file))


def main() -> None:
    """
    The main run function.
    Args: None
    Returns: None
    Process Flow:
        1. Move file to this dir
        2. Unzip it, then:
            1. Clean up the client mods
            2. Grab the config.toml
            3. Find any exceptive files that are going to be a PITA and remove them (a. la. Witchery in the RP's dir)
        3. Re-zip
        4. mmc-export
        5. Move files from step 3 into output files
        6. Move output folders back to originating dir
    """
    if len(sys.argv) != 2:
        print("Missing 2nd parameter File")
        return

    if not os.path.exists(TROUBLEMAKERS_PATH):
        os.mkdir(TROUBLEMAKERS_PATH)

    # STEP 1: copy the modpack locally
    shutil.copy(sys.argv[1], PACK_ZIP_PATH)
    print("STEP 1: SUCCESS")

    # STEP 2: unzip the pack
    shutil.unpack_archive(PACK_ZIP_PATH, PACK_UNZIPPED_PATH, "zip")
    print("STEP 2: SUCCESS")

    # STEP 2.1: clean up client mods
    _clean_pack()
    print("STEP 2.1: SUCCESS")

    # STEP 2.2: grab the config.toml file
    config_toml_path = os.path.join(PACK_UNZIPPED_PATH, "config.toml")
    if os.path.exists(config_toml_path):
        shutil.move(config_toml_path, MMC_EXPORT_CONFIG_PATH)
    print("STEP 2.2: SUCCESS")

    # STEP 2.3: grab PITA resourcepacks files like Witchery's 1.7.10 jar
    if os.path.exists(RP_DIR):
        for rpname in os.listdir(RP_DIR):
            rppath = os.path.join(RP_DIR, rpname)
            if not os.path.isdir(rppath) and not rppath.endswith(".zip"):
                shutil.move(rppath, os.path.join(TROUBLEMAKERS_PATH, rpname))
                print(f"STEP 2.3: Potential Troublemaker Found & Relocated: {rpname}")
    else:
        print("No resourcepacks dir - skipping")

    # STEP 3: re-zip & cleanup
    shutil.make_archive(PACK_ZIP_PATH.replace(".zip", ""), "zip", PACK_UNZIPPED_PATH)
    shutil.rmtree(PACK_UNZIPPED_PATH)
    print("STEP 3: SUCCESS")

    # ---- ANY FURTHER REFERENCES TO PACK_UNZIPPED_PATH ARE BAD!! ---- #

    # STEP 4: MMC-EXPORT
    print("MMC-Exporter is running, please wait")
    status = os.system(
        " ".join(
            f"""
                mmc-export.exe
                -i "{PACK_ZIP_PATH}"
                -f Modrinth CurseForge
                -c "{MMC_EXPORT_CONFIG_PATH}"
                -o "{THIS_DIR}"
            """.split()
        )
    )

    if status != 0:
        print("Failed to convert MMC pack to Curse and/or Modrinth. See above log.")
        return

    print("STEP 4: SUCCESS")

    # STEP 5: Move Troublemakers back to inside each zip
    output_files = _get_modpack_outnames(join=True)
    for fname in output_files:
        with zipfile.ZipFile(os.path.join(THIS_DIR, fname), "a") as zipf:
            for filename in os.listdir(TROUBLEMAKERS_PATH):
                troublemaker_path = os.path.join(TROUBLEMAKERS_PATH, filename)
                zipf.write(troublemaker_path, f"overrides/resourcepacks/{filename}")
    print("STEP 5: SUCCESS")

    # STEP 6: Move finished pack files back to OG dir
    og_dirname = "\\".join(sys.argv[1].split("\\")[:-1])
    output_files = _get_modpack_outnames(join=False)
    for fname in output_files + ["bundled_links.md"]:
        shutil.move(os.path.join(THIS_DIR, fname), os.path.join(og_dirname, fname))

    print("STEP 6: SUCCESS")

    __cleanup()
    print("DONE")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        __cleanup()
        print(e)
