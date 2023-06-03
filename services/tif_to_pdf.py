from PIL import Image
import img2pdf

import os
import io
import subprocess
import concurrent.futures

def process_image(filename, input_dir, watermark):
    # Open the .tif image
    img = Image.open(os.path.join(input_dir, filename))

    # Convert the image to RGB (necessary for .jpeg format)
    img = img.convert('RGB')

    # Calculate the position to center the watermark
    position = ((img.width - watermark.width) // 2, (img.height - watermark.height) // 2)

    # Add the watermark
    img.paste(watermark, position, watermark)

    # Save the image as .jpeg to a BytesIO object with 30% quality
    jpeg_image = io.BytesIO()
    img.save(jpeg_image, format='JPEG', quality=30)

    # Reset the file pointer to the beginning of the stream
    jpeg_image.seek(0)

    return jpeg_image

def in_memory(input_dir, output_dir, watermark_path, max_workers=4):
    # Load the watermark image
    watermark = Image.open(watermark_path)

    pdf_file_name = os.path.basename(input_dir) + ".pdf"
    pdf_path = os.path.join(output_dir, pdf_file_name)

    if os.path.isfile(pdf_path): # skip pdf creation if output file exists already
        return 0

    # List to store the .jpeg images
    jpeg_images = []

    # Get a list of all .tif files in the input directory
    filenames = [filename for filename in sorted(os.listdir(input_dir)) if filename.endswith('.tif')]

    # Create a ProcessPoolExecutor
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Use the executor to map the process_image function to the filenames
        for jpeg_image in executor.map(process_image, filenames, [input_dir]*len(filenames), [watermark]*len(filenames)):
            jpeg_images.append(jpeg_image)

    # Convert all .jpeg images to a single .pdf file
    with open(pdf_path, 'wb') as f:
        imgs = []
        for jpeg_image in jpeg_images:
            jpeg_image.seek(0)
            imgs.append(jpeg_image.read())
        f.write(img2pdf.convert(*imgs))
    return len(jpeg_images)

def sh_script(input_dir, output_dir, watermark):
    script_path = "./tif_to_pdf.sh"
    parameters = [input_dir, output_dir, watermark]

    command = [script_path] + parameters

    try:
        subprocess.run(command, capture_output=True)
    except subprocess.CalledProcessError:
        print(item[0], "could not be converted")
