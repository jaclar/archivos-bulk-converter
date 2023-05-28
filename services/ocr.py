from PIL import Image

import os

import pytesseract

def from_tif(input_dir, output_dir):
    txt_file_name = os.path.basename(input_dir) + ".txt"
    txt_path = os.path.join(output_dir, txt_file_name)

    # Get a list of all .tif files in the input directory
    filenames = [filename for filename in sorted(os.listdir(input_dir)) if filename.endswith('.tif')]

    with open(txt_path, "w") as txt:
        for filename in filenames:
            txt.write(filename + ":\n")
            txt.write(pytesseract.image_to_string(
                Image.open(os.path.join(input_dir, filename)),
                lang='spa') + "\n\n\n")
