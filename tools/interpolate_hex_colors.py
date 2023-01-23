from colorsys import hls_to_rgb, rgb_to_hls

import numpy as np


def interpolateHexColors(start_hex, end_hex, n, power=1):
    """
    # This function interpolates any two hex color codes, and it returns a list of n linearly interpolated hex color
    codes.
    :param start_hex: string with the first hex color code
    :param end_hex: string with the last hex color code
    :param n: number of colors to interpolate, including the first and last ones
    :param power: integer indicating the power for the interpolation. E.g., 1 for 'linear',2 for 'quadratic'
    :returns: list of string with the interpolated hex color codes

    Example:
    interpolateHexColors('#000000', '#ffffff', 3)
    """
    if n <= 2:
        return [start_hex, end_hex]

    # convert hex color codes to RGB values
    start_rgb = tuple(int(start_hex[i : i + 2], 16) for i in (1, 3, 5))
    end_rgb = tuple(int(end_hex[i : i + 2], 16) for i in (1, 3, 5))

    # convert RGB values to HLS values
    start_hls = rgb_to_hls(*start_rgb)
    end_hls = rgb_to_hls(*end_rgb)

    # interpolate the H, L, and S values separately
    hue_interval = powspace(start_hls[0], end_hls[0], power=power, num=n)
    lightness_interval = powspace(start_hls[1], end_hls[1], power=power, num=n)
    saturation_interval = powspace(start_hls[2], end_hls[2], power=power, num=n)

    # generate the interpolated HLS color codes
    interpolated_hls = [
        (hue_interval[i], lightness_interval[i], saturation_interval[i])
        for i in range(0, n)
    ]

    # convert the interpolated HLS color codes back to RGB values
    interpolated_rgb = [hls_to_rgb(*hls) for hls in interpolated_hls]

    # convert the interpolated RGB color codes to hex color codes
    int_interpolated_rgb = []
    for rgb in interpolated_rgb:
        int_interpolated_rgb.append([int(c) for c in rgb])
    interpolated_hex = [
        "#{:02x}{:02x}{:02x}".format(*rgb) for rgb in int_interpolated_rgb
    ]
    return interpolated_hex


def powspace(start, stop, power, num):
    if start < 0 and stop < 0:
        start = np.power(-start, 1 / float(power))
        stop = np.power(-stop, 1 / float(power))
        return -np.power(np.linspace(start, stop, num=num), power)
    else:
        start = np.power(start, 1 / float(power))
        stop = np.power(stop, 1 / float(power))
        return np.power(np.linspace(start, stop, num=num), power)


if __name__ == "__main__":
    # Dark palette
    # interpolated_colors = interpolateHexColors("#EEF1F4", "#1B1D23", 10, 2)

    # Light palette
    interpolated_colors = interpolateHexColors("#EEF1F4", "#4b4f5a", 11, 1)

    # Print generated colors
    print(interpolated_colors)
