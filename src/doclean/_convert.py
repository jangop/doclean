import datetime
import io
import subprocess
import tempfile
from contextlib import redirect_stderr
from pathlib import Path
from typing import Literal

import dateparser.search
import img2pdf
import ocrmypdf
from loguru import logger
from natsort import natsorted

from ._compression import compress_images_in_pdf, extract_images_from_pdf
from ._whiten import load_adjust_save


def _convert_image(image_path: Path, output_path: Path):
    # Call `doclean` with the image path and output path.
    # This will create a temporary directory and save the output PDF there.
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a temporary directory for the intermediate files.
        temp_dir = Path(temp_dir)

        # Clean/whiten the image.
        cleaned_image_path = (temp_dir / "cleaned").with_suffix(".png")
        logger.debug(f"Cleaning {image_path}...")
        load_adjust_save(image_path, cleaned_image_path)
        assert cleaned_image_path.exists()
        logger.debug(f"Cleaned image saved to {cleaned_image_path}.")

        # Call `unpaper`.
        unpapered_image_path = (temp_dir / "unpapered").with_suffix(".pbm")
        logger.debug(f"Unpapering {cleaned_image_path}...")
        subprocess.run(
            [
                "unpaper",
                "--no-deskew",
                str(cleaned_image_path),
                str(unpapered_image_path),
            ],
            check=True,
            capture_output=True,
        )
        assert unpapered_image_path.exists()
        logger.debug(f"Unpapered image saved to {unpapered_image_path}.")

        # Move to the output path.
        unpapered_image_path.rename(output_path)


def optimize_pack_ocr_save(
    input_dir_path: Path,
    pdf_file_path: Path,
    acceptable_extensions: tuple[str, ...] = (".png", ".jpg", ".jpeg", ".tiff", ".tif"),
    language: str = "deu",
    deskew: bool = True,
    output_type: Literal["pdf"] = "pdf",
):
    """Process image files and embed in a PDF."""
    if input_dir_path.is_file():
        temporary_image_directory = Path(tempfile.TemporaryDirectory().name)
        logger.debug(
            f"Extracting images from `{input_dir_path}` "
            f"into `{temporary_image_directory}`..."
        )
        extract_images_from_pdf(input_dir_path, temporary_image_directory)
        input_dir_path = temporary_image_directory

    # Collect images files according to the acceptable extensions.
    single_input_image_paths = natsorted(
        path
        for path in input_dir_path.iterdir()
        if path.suffix.lower() in acceptable_extensions
    )

    # Process each image file.
    with tempfile.TemporaryDirectory() as temporary_working_directory:
        n_images = len(single_input_image_paths)
        result_paths = []
        for i, image_path in enumerate(single_input_image_paths):
            output_path = (
                Path(temporary_working_directory) / f"{i:0{n_images // 10}}.pbm"
            )
            _convert_image(image_path, output_path)
            result_paths.append(output_path)

        # Use `img2pdf` to combine the images into a PDF.
        intermediate_path = Path(temporary_working_directory) / "intermediate.pdf"
        logger.debug(
            f"Combining {len(result_paths)} images "
            f"({result_paths}) into {intermediate_path}..."
        )
        with open(intermediate_path, "wb") as f:
            f.write(img2pdf.convert([str(result_path) for result_path in result_paths]))
        assert intermediate_path.exists()
        logger.debug(f"Intermediate PDF saved to {intermediate_path}.")

        # Use `ocrmypdf` to perform OCR on the PDF.
        logger.debug(f"Performing OCR on {intermediate_path}...")

        sink = io.StringIO()
        with redirect_stderr(sink):
            ocrmypdf.ocr(
                intermediate_path,
                pdf_file_path,
                language=language,
                deskew=deskew,
                output_type=output_type,
                jbig2_lossy=True,
                optimize=3,
                png_quality=1,
                keep_temporary_files=True,
            )
        ocrmypdf_stderr = sink.getvalue()

        # Determine ocrmypdf's temporary working directory.
        line_before_path = "Temporary working files retained at:"
        found_line_before_path = False
        for line in ocrmypdf_stderr.splitlines():
            if found_line_before_path:
                ocrmypdf_temporary_working_directory_path = Path(line)
                break
            if line == line_before_path:
                found_line_before_path = True
        else:
            raise ValueError(
                f"Could not find '{line_before_path}' "
                f"in ocrmypdf's stderr: {ocrmypdf_stderr}"
            )

        logger.debug(
            f"OCR complete. Temporary working directory: "
            f"`{ocrmypdf_temporary_working_directory_path}`"
        )

        # Compress the resulting PDF.
        compress_images_in_pdf(
            pdf_file_path, pdf_file_path, scale_factor=0.5, quality=25
        )

        # Open ocr results of first page and extract date.
        txt_file_paths = natsorted(
            ocrmypdf_temporary_working_directory_path.glob("*.txt")
        )
        with open(txt_file_paths[0]) as f:
            text = f.read()
        found_dates = dateparser.search.search_dates(
            text, languages=["de"], settings={"STRICT_PARSING": True}
        )
        if found_dates:
            # Pick the most recent date relative to today.
            found_dates = sorted(found_dates, key=lambda x: x[1].date())
            today = datetime.date.today()
            final_date = None
            for found_date in found_dates:
                logger.debug(f"Found date: {found_date}")
                if found_date[1].date() < today:
                    logger.debug(f"{found_date} ealier than today")
                    final_date = found_date
                else:
                    logger.debug(f"{found_date} later than today")
                    break
            if final_date:
                logger.debug(f"Final date: {final_date}")
                final_date = final_date[1].date()
                # Rename the PDF file to include the date.
                rename = False
                if rename:
                    pdf_file_path.rename(
                        pdf_file_path.with_name(
                            f"{pdf_file_path.stem}_"
                            f"{final_date}"
                            f"{pdf_file_path.suffix}"
                        )
                    )

        assert pdf_file_path.exists()
        logger.debug(f"Final PDF saved to {pdf_file_path}.")
