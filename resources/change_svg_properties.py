import logging
import os

from lxml import etree


def change_svg_properties(in_dir, out_dir, stroke_color, stroke_width):
    if not os.path.exists(out_dir):
        logging.info(f"Creating directory: {out_dir}")
        os.mkdir(out_dir)

    for f in os.listdir(in_dir):
        full_path = os.path.join(in_dir, f)
        print(in_dir + "/" + f)
        if f.endswith(".svg"):
            tree = etree.parse(full_path)
            root = tree.getroot()
            if root.get("stroke") is not stroke_color:
                logging.info(
                    f"Changing stroke color from {root.get('stroke')} to {stroke_color} in {f}"
                )
                root.set("stroke", stroke_color)

            if root.get("stroke-width") is not stroke_width:
                logging.info(
                    f"Changing stroke width from {root.get('stroke-width')} to {stroke_width} in {f}"
                )
                root.set("stroke-width", str(stroke_width))

            tree.write(os.path.join(out_dir, f))


if __name__ == "__main__":
    change_svg_properties("white_lucide", "red_lucide", "red", 1)
