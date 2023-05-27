import os

from tqdm import tqdm

from convert import (
    sh_script,
    in_memory
)

import concurrent.futures

max_workers = 4

def start():
    print("Hello Poetry!")

    top = "../documents"
    output_dir = "../converted_documents_memory"

    tif_queue = []

    # Gather queue of tif folders to be converted
    # and create a parallel folder structure
    # rooted in `output_dir`
    for x in os.walk(top):
        dir = x[0]
        files = x[2]
        out_dir = dir.replace(top, output_dir)

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

    pbar = tqdm(total=len(tif_queue))
    # Create a ProcessPoolExecutor
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        for pdf in executor.map(in_memory, [x[0] for x in tif_queue], [x[1] for x in tif_queue], ["watermark.png"]*len(tif_queue)):
            pbar.update(n=1)
