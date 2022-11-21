# -*- coding: utf-8 -*-
"""
Module containing function to format icons file contained in
"icons" folder.
"""
import os


def formatIconsFiles() -> bool:
    """
    function to remove icon prefix from all icons contained in "icons" folder.
    It also translates "-" into "_".

    :return: ``True`` if the operation is successful, ``False`` otherwise.
    """
    for count, filename in enumerate(os.listdir("icons")):
        modifiedFilename = filename.replace("icons8-", "")
        modifiedFilename = modifiedFilename.replace("-", "_")
        print(f"{count}: {filename} -> {modifiedFilename}")

        os.rename("icons/" + filename, "icons/" + modifiedFilename)

    return True


if __name__ == "__main__":
    ret = formatIconsFiles()
    if ret:
        print("icon8 prefix has been removed from all icons.")
    else:
        print("Something went wrong during renaming of icons.")
