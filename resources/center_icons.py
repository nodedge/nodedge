# -*- coding: utf-8 -*-
"""
Module containing function to change icons color contained in
"icons" folder.
"""
import logging
import os

from PIL import Image


def centerIcons(
    folderInput: str = "white_icons",
    folderOutput: str = "white_icons2",
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

        minX, minY = width + 1, height + 1
        maxX, maxY = 0, 0
        for x in range(width):
            for y in range(height):
                r, g, b, a = pixels[x, y]
                if a != 0:
                    minX = min(minX, x)
                    minY = min(minY, y)
                    maxX = max(maxX, x)
                    maxY = max(maxY, y)

        averageX = (minX + maxX) / 2
        averageY = (minY + maxY) / 2
        print(f"{filename}: {averageX}, {averageY}")
        distX = int(averageX - width / 2)
        distY = int(averageY - height / 2)
        print(distX, distY)
        # temp = [[]]
        try:
            for x in range(width):
                for y in range(height):
                    # if y < distY:
                    #     temp[x,y] = pixels[x, y]

                    if distY > 0:
                        if y < height - distY:
                            pixels[x, y] = pixels[x, y + distY]
                        else:
                            pixels[x, y] = (0, 0, 0, 0)
                    else:
                        if y > distY:
                            pixels[x, y] = pixels[x, y + distY]
                        else:
                            pixels[x, y] = (0, 0, 0, 0)
                    # if x < distX:
                    #     temp[x, y] = pixels[x, y]

            for x in range(width):
                for y in range(height):
                    if distX > 0:
                        if x < width - distX:
                            pixels[x, y] = pixels[x + distX, y]
                        else:
                            pixels[x, y] = (0, 0, 0, 0)
                    else:
                        if x > distX:
                            pixels[x, y] = pixels[x + distX, y]
                        else:
                            pixels[x, y] = (0, 0, 0, 0)
        except IndexError:
            logging.warning(f"IndexError: {filename}: {x}, {y}")
            continue

        # temp = pixels[0:distY, :]
        # pixels[0 : 100 - distY, :] = pixels[distY:100, :]
        # pixels[100 - distY : 100, :] = temp

        # print(minX, minY, maxX, maxY)
        im.save(folderOutput + "/" + filename)

    return True


if __name__ == "__main__":
    ret = centerIcons()
    if ret:
        print("Icons color has changed.")
    else:
        print("Something went wrong during recoloring of icons.")
