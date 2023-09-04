import numpy as np
import PIL.Image
import PIL.ImageDraw

from doclean._compression import compress_images_in_pdf
from doclean._convert import convert
from doclean._whiten import adjust_levels

generator = np.random.default_rng(0)


def _generate_image(width: int, height: int) -> PIL.Image:
    # Generate noisy, very bright background.
    background = generator.integers(230, 256, size=(height, width, 3), dtype=np.uint8)
    image = PIL.Image.fromarray(background)

    # Prepare canvas.
    canvas = PIL.ImageDraw.Draw(image)

    # Write some text in the middle.
    canvas.text((width // 2, height // 2), "Hello, world!", fill=(0, 0, 0))

    return image


def test_whitening(tmp_path):
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.png"

    image = _generate_image(2480, 3508)
    image.save(input_path)

    adjust_levels(input_path, output_path)

    assert output_path.exists()


def test_conversion(tmp_path):
    input_dir_path = tmp_path / "input"
    input_dir_path.mkdir()
    pdf_file_path = tmp_path / "output.pdf"

    n_images = 2
    for i_image in range(n_images):
        image = _generate_image(2480, 3508)
        image.save(input_dir_path / f"image{i_image}.png")

    convert(input_dir_path, pdf_file_path)

    assert pdf_file_path.exists()


def test_compression(tmp_path):
    input_path = tmp_path / "input.pdf"
    output_path = tmp_path / "output.pdf"

    n_images = 2
    with PIL.Image.new("RGB", (2480, 3508)) as image:
        image.save(input_path, save_all=True, append_images=[image] * n_images)

    compress_images_in_pdf(input_path, output_path, scale_factor=0.5, quality=10)

    assert output_path.exists()
