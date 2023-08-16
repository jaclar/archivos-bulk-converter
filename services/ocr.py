from PIL import Image

import os
import re
import csv
from io import StringIO

import statistics

import pytesseract

def get_angle(image):
    try:
        output = pytesseract.image_to_osd(image, config="--psm 0")
        angle = int(re.search(r'Orientation in degrees: \d+', output).group().split(':')[-1].strip())
        confidence = float(re.search(r'Orientation confidence: \d+\.\d+', output).group().split(':')[-1].strip())
    except Exception as e:
        angle = 0.0
        confidence = 0.0
    return angle, confidence

def ocr_with_score(image):
    angle, confidence = get_angle(image)
    if (confidence > 2.0):
        image = image.rotate(angle, expand=True)

    f = StringIO(pytesseract.image_to_data(image, lang='spa'))
    reader = csv.DictReader(f, delimiter='\t', dialect='unix')
    string = ""
    conf = []
    for row in reader:
        confidence = float(row['conf'])
        if confidence > 0:
            conf.append(confidence)

        if row['text'] == '':
            string = string[slice(-1)] + '\n'
        else:
            string += row['text'] + ' '

    mean = 0.0
    if (len(conf) > 0):
        mean = statistics.fmean(conf)

    return string, mean

def from_tif(input_dir, output_dir):
    txt_file_name = os.path.basename(input_dir) + ".txt"
    txt_path = os.path.join(output_dir, txt_file_name)

    if os.path.isfile(txt_path): # skip OCR if output file exists already
        return 0, 0

    # Get a list of all .tif files in the input directory
    filenames = [filename for filename in sorted(os.listdir(input_dir)) if filename.endswith('.tif')]

    i = 1
    confidence = []
    with open(txt_path, "w") as txt:
        for filename in filenames:
            txt.write("Page " + str(i) + ":\n\n")
            text, conf = ocr_with_score(Image.open(os.path.join(input_dir, filename)))
            txt.write(text)
            confidence.append(conf)
            i += 1
    return len(filenames), statistics.fmean(confidence)
