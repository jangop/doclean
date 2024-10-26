from pathlib import Path

import PIL.ImageOps
from loguru import logger
from pypdf import PdfReader, PdfWriter


def compress_images_in_pdf(
    input_path: Path, output_path: Path, *, scale_factor: float, quality: int
):
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


def extract_images_from_pdf(input_path: Path, output_dir_path: Path):
    reader = PdfReader(input_path)
    output_dir_path.mkdir(parents=True, exist_ok=True)
    for page in reader.pages:
        for img in page.images:
            target_path = output_dir_path / f"{img.name}"
            img.image.save(target_path)
            logger.debug(f"Saved image to `{target_path}`")
