# -*- coding: utf-8 -*-
"""
Module containing function to change icons color contained in
"icons" folder.
"""
import os
from typing import List

from PIL import Image


def changeIconsColor(
    folderInput: str = "icons",
    folderOutput: str = "iconsModified",
    rgbOld: List[int] = (0, 0, 0),
    rgbNew: List[int] = (255, 255, 255),
    maxAlpha: int = 210,
) -> bool:
    """
    function to remove icon prefix from all icons contained in "icons" folder.
    It also translates "-" into "_".

    :return: ``True`` if the operation is successful, ``False`` otherwise.
    """
    for count, filename in enumerate(os.listdir(folderInput)):
        im = Image.open(folderInput + "/" + filename)
        pixels = im.load()

        width, height = im.size
        for x in range(width):
            for y in range(height):
                r, g, b, a = pixels[x, y]
                if (r, g, b) == rgbOld:
                    pixels[x, y] = (rgbNew[0], rgbNew[1], rgbNew[2], min(maxAlpha, a))
        im.save(folderOutput + "/" + filename)

    return True


if __name__ == "__main__":
    ret = changeIconsColor(folderOutput="iconsModified")
    if ret:
        print("Icons color has changed.")
    else:
        print("Something went wrong during recoloring of icons.")
