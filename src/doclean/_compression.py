import PIL.ImageOps
from pypdf import PdfReader, PdfWriter


def compress_images_in_pdf(input_path, output_path, *, scale_factor, quality):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    for page in writer.pages:
        for img in page.images:
            image = PIL.ImageOps.scale(img.image, scale_factor)
            img.replace(image, quality=quality)

    with open(output_path, "wb") as f:
        writer.write(f)
