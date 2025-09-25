"""@author Jose Stovall | github.com/oitsjustjose"""

import json
import os
import shutil
import sys
import zipfile
from pathlib import Path
from typing import List

import toml

THIS_DIR = Path(__file__).absolute().parent
CLEANUP_CONF_PATH = THIS_DIR.joinpath("..").joinpath("configuration.json").resolve()
MMC_EXPORT_CONFIG_PATH = THIS_DIR.joinpath("config.toml").resolve()
TROUBLEMAKERS_PATH = THIS_DIR.joinpath("troublemakers").resolve()
WORKING_FOLDER: Path = Path(".").resolve()  # Temp, gets resolved from sys.argv in main()

# Temporary variables that aren't actually persistent really
__TMP_PACK_UNZIPPED_PATH = THIS_DIR.joinpath("activepack").resolve()
__TMP_PACK_ZIP_PATH = THIS_DIR.joinpath("activepack.zip").resolve()
__TMP_RESPACK_DIR = __TMP_PACK_UNZIPPED_PATH.joinpath("minecraft").joinpath("resourcepacks").resolve()


def print(obj):
    """override"""
    # log_nm_base = sys.argv[1].split("\\")[-1]

    log_nm_base = Path()

    with open(f"./{log_nm_base}.log", "a+", encoding="utf-8") as log_handle:
        log_handle.write(f"{str(obj)}\n")


def _clean_pack():
    """
    Removes client-only configs/files
    """
    with open(CLEANUP_CONF_PATH, "r", encoding="utf-8") as handle:
        config = json.loads(handle.read())

    for to_del in config["remove"]:
        fpath = __TMP_PACK_UNZIPPED_PATH.joinpath("minecraft").joinpath(to_del)

        if not fpath.exists():
            continue

        if fpath.is_dir():
            shutil.rmtree(fpath)
            print(f"Removed directory {fpath}")
            continue

        fpath.unlink()
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
            str(THIS_DIR.joinpath(f"MR_{name}.mrpack")),
            str(THIS_DIR.joinpath(f"CF_{name}.zip")),
        ]
    return [f"MR_{name}.mrpack", f"CF_{name}.zip"]


def __cleanup() -> None:
    """Cleans up output files"""
    os.unlink(MMC_EXPORT_CONFIG_PATH)
    os.unlink(__TMP_PACK_ZIP_PATH)
    shutil.rmtree(__TMP_PACK_UNZIPPED_PATH)
    shutil.rmtree(TROUBLEMAKERS_PATH)
    for file in os.listdir(THIS_DIR):
        if file.startswith("CF_") or file.startswith("MR_"):
            THIS_DIR.joinpath(file).unlink()


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

    INPUT_FILE_PATH = Path(sys.argv[1]).resolve().parent
    if not TROUBLEMAKERS_PATH.exists():
        TROUBLEMAKERS_PATH.mkdir()

    # STEP 1: copy the modpack locally
    shutil.copy(INPUT_FILE_PATH.parent, __TMP_PACK_ZIP_PATH)
    print("STEP 1: SUCCESS")

    # STEP 2: unzip the pack
    shutil.unpack_archive(__TMP_PACK_ZIP_PATH, __TMP_PACK_UNZIPPED_PATH, "zip")
    print("STEP 2: SUCCESS")

    # STEP 2.1: clean up client mods
    _clean_pack()
    print("STEP 2.1: SUCCESS")

    # STEP 2.2: grab the config.toml file
    config_toml_path = __TMP_PACK_UNZIPPED_PATH.joinpath("config.toml")
    if config_toml_path.exists():
        shutil.move(config_toml_path, MMC_EXPORT_CONFIG_PATH)
    print("STEP 2.2: SUCCESS")

    # STEP 2.3: grab PITA resourcepacks files like Witchery's 1.7.10 jar
    if __TMP_RESPACK_DIR.exists() and __TMP_RESPACK_DIR.is_dir():
        for respack_path in __TMP_RESPACK_DIR.iterdir():
            if not respack_path.is_dir() and not respack_path.name.endswith(".zip"):
                shutil.move(respack_path, TROUBLEMAKERS_PATH.joinpath(respack_path.name))
                print(f"STEP 2.3: Potential Troublemaker Found & Relocated: {respack_path.name}")
    else:
        print("No resourcepacks dir - skipping")

    # STEP 3: re-zip & cleanup
    shutil.make_archive(str(__TMP_PACK_ZIP_PATH.with_suffix("")), "zip", __TMP_PACK_UNZIPPED_PATH)
    shutil.rmtree(__TMP_PACK_UNZIPPED_PATH)
    print("STEP 3: SUCCESS")

    # ---- ANY FURTHER REFERENCES TO PACK_UNZIPPED_PATH ARE BAD!! ---- #

    # STEP 4: MMC-EXPORT
    print("MMC-Exporter is running, please wait")
    status = os.system(
        " ".join(
            f"""
                mmc-export.exe
                -i "{__TMP_PACK_ZIP_PATH}"
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
        with zipfile.ZipFile(THIS_DIR.joinpath(fname), "a") as zipf:
            for file in TROUBLEMAKERS_PATH.iterdir():
                troublemaker_path = TROUBLEMAKERS_PATH.joinpath(file)
                zipf.write(troublemaker_path, f"overrides/resourcepacks/{file}")
    print("STEP 5: SUCCESS")

    # STEP 6: Move finished pack files back to OG dir
    output_files = _get_modpack_outnames(join=False)
    for fname in output_files + ["bundled_links.md"]:
        shutil.move(THIS_DIR.joinpath(fname), INPUT_FILE_PATH.parent.joinpath(fname))

    print("STEP 6: SUCCESS")

    __cleanup()
    print("DONE")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        __cleanup()
        print(e)
