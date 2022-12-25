# -*- coding: utf-8 -*-
"""
Module containing function to format icons file contained in
"icons" folder.
"""
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def formatIconsFiles(folder: str, overwrite: bool = True) -> bool:
    """
    function to remove icon prefix from all icons contained in "icons" folder.
    It also translates "-" into "_".

    :param folder: folder containing icons
    :type folder: str
    :param overwrite: overwrite existing files, defaults to True
    :type overwrite: bool, optional
    :return: ``True`` if the operation is successful, ``False`` otherwise.
    """
    for count, filename in enumerate(os.listdir(folder)):
        modifiedFilename = filename.replace("icons8-", "")
        modifiedFilename = modifiedFilename.replace("-", "_")
        modifiedFilename = modifiedFilename.replace("_100", "")
        modifiedFilename = modifiedFilename.replace("_96", "")

        logger.debug(f"{count}: {filename} -> {modifiedFilename}")

        if filename != modifiedFilename:
            try:
                if overwrite and os.path.exists(os.path.join(folder, modifiedFilename)):
                    logger.info(f"Overwriting {modifiedFilename}.")
                    os.remove(folder + "/" + filename)
                os.rename(folder + "/" + filename, folder + "/" + modifiedFilename)
            except FileExistsError as e:
                logger.warning(f"File {modifiedFilename} already exists. Skipping.")

    return True


if __name__ == "__main__":
    ret = formatIconsFiles("icons")
    ret &= formatIconsFiles("iconsModified")
    if ret:
        logger.info("Formatting all icon files done.")
    else:
        logger.info("Something went wrong during renaming of icons.")
