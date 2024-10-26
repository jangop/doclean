from pathlib import Path

import click
from loguru import logger

from . import compress_images_in_pdf, load_adjust_save, optimize_pack_ocr_save

logger.enable("doclean")


@click.group()
def cli():
    """Document cleaning and processing tools.

    This tool provides various utilities for cleaning and processing documents:

    \b
    - Image whitening (doclean whiten)
    - PDF image compression (doclean compress)
    - Image to PDF conversion with OCR (doclean convert)
    """
    pass


@cli.command(name="whiten")
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.argument("output_path", type=click.Path(path_type=Path))
def enter_image_whitening(input_path, output_path):
    """Clean and whiten a scanned document image.

    This command processes a scanned document image by adjusting its levels
    to produce a cleaner, more readable result with a white background.

    \b
    INPUT_PATH: Path to the input image file
    OUTPUT_PATH: Path where the processed image will be saved
    """
    load_adjust_save(input_path, output_path)


@cli.command(name="compress")
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.argument("output_path", type=click.Path(path_type=Path))
@click.option(
    "--scale-factor",
    type=click.FloatRange(min=0.1, max=1.0),
    default=0.5,
    help="Scale factor for image resizing (should be between 0.1 and 1.0).",
    show_default=True,
)
@click.option(
    "--quality",
    type=click.IntRange(1, 100),
    default=80,
    help="JPEG quality (should be between 1 and 100).",
    show_default=True,
)
def enter_image_compression_in_pdf(input_path, output_path, scale_factor, quality):
    """Compress images within a PDF file.

    This command reduces the size of a PDF by compressing and optionally
    resizing the images it contains while maintaining readability.

    \b
    INPUT_PATH: Path to the input PDF file
    OUTPUT_PATH: Path where the compressed PDF will be saved
    """
    compress_images_in_pdf(
        input_path, output_path, scale_factor=scale_factor, quality=quality
    )


@cli.command(name="convert")
@click.argument(
    "input_dir_path",
    type=click.Path(
        exists=True, readable=True, dir_okay=True, file_okay=True, path_type=Path
    ),
)
@click.argument("pdf_file_path", type=click.Path(writable=True, path_type=Path))
@click.option(
    "--lang",
    default="deu",
    help="OCR language (e.g., 'eng' for English, 'deu' for German).",
    show_default=True,
)
@click.option(
    "--deskew/--no-deskew",
    default=True,
    help="Enable/disable automatic page deskewing.",
    show_default=True,
)
@click.option(
    "--rename/--no-rename",
    default=False,
    help="Automatically rename the output PDF with the detected date.",
    show_default=True,
)
def enter_image2pdf_conversion(input_dir_path, pdf_file_path, lang, deskew, rename):
    """Convert images to a searchable PDF.

    This command processes either a directory of images or a PDF file, cleaning the
    images and combining them into a single searchable PDF with OCR text recognition.
    If --rename is specified and a date is found in the first page, the output file
    will be renamed to include that date.

    \b
    INPUT_DIR_PATH: Directory containing image files or a PDF file
    PDF_FILE_PATH: Path where the final PDF will be saved
    """
    optimize_pack_ocr_save(
        input_dir_path,
        pdf_file_path,
        language=lang,
        deskew=deskew,
        rename=rename,
    )
