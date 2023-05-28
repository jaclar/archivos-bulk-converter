import os
import click

from tqdm import tqdm

from convert import (
    sh_script,
    in_memory
)

import concurrent.futures

max_workers = 4

@click.command()
@click.option("--input", "-i", type=str, required=True, help="Input directory tree with *.tif files.")
@click.option("--output", "-o", type=str, required=True, help="Output directory, will be created if not present.")
@click.option("--watermark", "-w", default="./watermark.png", type=str, required=False, help="Path to watermark *.png file")
@click.option("--workers", default=4, type=int, required=False, help="Maximum amount of parallel workers")
def cli(input: str, output: str, watermark:str, workers: int):
    tif_queue = getQueue(input, output)

    pbar = tqdm(total=len(tif_queue))
    # Create a ProcessPoolExecutor
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        for pdf in executor.map(in_memory, [x[0] for x in tif_queue], [x[1] for x in tif_queue], [watermark]*len(tif_queue)):
            pbar.update(n=1)


def getQueue(input_dir, output_dir):
    tif_queue = []

    # Gather queue of tif folders to be converted
    # and create a parallel folder structure
    # rooted in `output_dir`j
    for x in os.walk(input_dir):
        dir = x[0]
        files = x[2]
        out_dir = dir.replace(input_dir, output_dir)

        has_tif = any(".tif" in s for s in files)

        if (has_tif and len(x[1]) > 0):
            print(dir, "has at least one tif and subfolders - skipping")
        elif (has_tif):
            tif_queue.append((dir, os.path.dirname(out_dir)))
        else:
            try: # create output folder
                os.mkdir(out_dir)
            except FileExistsError:
                pass # ignore error if directory exists already

    return tif_queue
