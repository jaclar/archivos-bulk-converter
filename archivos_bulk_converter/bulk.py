import os
import click

from tqdm import tqdm

from services import (
    tif_to_pdf,
    ocr
)

import concurrent.futures

max_workers = 4

@click.command()
@click.option("--input", "-i", type=str, required=True, help="Input directory tree with *.tif files.")
@click.option("--output", "-o", type=str, required=True, help="Output directory, will be created if not present.")
@click.option("--watermark", "-w", default="./watermark.png", type=str, required=False, help="Path to watermark *.png file")
@click.option("--workers", default=4, type=int, required=False, help="Maximum amount of parallel workers")
@click.option("--pdf/--no-pdf", default=True, required=False, help="Toggle PDF generation")
@click.option("--ocr/--no-ocr", default=False, required=False, help="Toggles text recognition via OCR")
def cli(input: str, output: str, watermark:str, workers: int, pdf: bool, ocr: bool):
    tif_queue = getQueue(input, output)

    total_pages = 0
    pbar = tqdm(total=len(tif_queue))
    # Create a ProcessPoolExecutor
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        for pages in executor.map(process,
                                  [x[0] for x in tif_queue],
                                  [x[1] for x in tif_queue],
                                  [watermark]*len(tif_queue),
                                  [pdf]*len(tif_queue),
                                  [ocr]*len(tif_queue)):
            pbar.update(n=1)
            total_pages += pages
    pbar.close();
    print("Processed", total_pages, "pages from", len(tif_queue), "documents")

def process(input_dir: str, output_dir: str, watermark: str, enable_pdf: bool, enable_ocr: bool):
    if enable_pdf:
        pages = tif_to_pdf.in_memory(input_dir, output_dir, watermark)
    if enable_ocr:
        pages, conf = ocr.from_tif(input_dir, output_dir)
        with open('./scores.txt', "a") as txt:
            txt.write(str(conf) + " " + input_dir + "\n")
    return pages

def getQueue(input_dir, output_dir):
    tif_queue = []

    # Gather queue of tif folders to be converted
    # and create a parallel folder structure
    # rooted in `output_dir`j
    for x in os.walk(input_dir):
        dir = x[0]
        files = x[2]
        out_dir = dir.replace(input_dir, output_dir)

        if (os.path.basename(dir).startswith('.') or
            os.path.basename(dir).startswith('@') or
            os.path.basename(dir).endswith(' CD') or
            os.path.basename(dir).endswith('_TS')):
            # ignore hidden folders
            continue

        has_tif = any(".tif" in s for s in files)
        has_subfolder = any(not (d.startswith('.') or
                                 d.startswith('@') or
                                 d.endswith(' CD')) for d in x[1])

        if (has_tif and has_subfolder):
            print(dir, "has at least one tif and non-hidden subfolders - skipping")
        elif (has_tif):
            tif_queue.append((dir, os.path.dirname(out_dir)))
        else:
            try: # create output folder
                os.mkdir(out_dir)
            except FileExistsError:
                pass # ignore error if directory exists already

    return tif_queue
