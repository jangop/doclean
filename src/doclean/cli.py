from pathlib import Path

import click
from loguru import logger

from . import adjust_levels, compress_images_in_pdf, convert

logger.enable("doclean")


@click.command()
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.argument("output_path", type=click.Path(path_type=Path))
@click.option("--scale-factor", type=float, default=0.5, help="Scale factor.")
@click.option("--quality", type=int, default=80, help="JPEG quality.")
def enter_image_compression_in_pdf(input_path, output_path, scale_factor, quality):
    compress_images_in_pdf(
        input_path, output_path, scale_factor=scale_factor, quality=quality
    )


@click.command()
@click.argument(
    "input_dir_path",
    type=click.Path(
        exists=True, readable=True, dir_okay=True, file_okay=False, path_type=Path
    ),
)
@click.argument("pdf_file_path", type=click.Path(writable=True, path_type=Path))
def enter_image2pdf_conversion(input_dir_path, pdf_file_path):
    convert(input_dir_path, pdf_file_path)


@click.command()
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.argument("output_path", type=click.Path(path_type=Path))
def enter_image_whitening(input_path, output_path):
    adjust_levels(input_path, output_path)
