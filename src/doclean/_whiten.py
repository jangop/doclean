import numpy as np
from loguru import logger
from PIL import Image


def adjust_levels(input_path, output_path):
    # Load the input image
    image = Image.open(input_path)

    if image is None:
        logger.critical(f"Cannot load image from `{input_path}`")
        raise RuntimeError("Could not load a required image")

    # Convert the image to grayscale
    gray_image = image.convert("L")
    pixel_values = np.array(gray_image)

    # Calculate histogram
    hist, _ = np.histogram(pixel_values, bins=256, range=(0, 256))

    # Calculate cumulative distribution function (CDF)
    cdf = hist.cumsum()
    cdf_normalized = cdf / cdf.max()

    # Find the threshold where CDF transitions from background to foreground
    lower_threshold = np.where(cdf_normalized > 0.01)[0][0]
    upper_threshold = np.where(cdf_normalized > 0.08)[0][0]

    # Clamp and rescale pixel values
    adjusted_pixel_values = np.clip(pixel_values, lower_threshold, upper_threshold)
    min_pixel_value = np.min(adjusted_pixel_values)
    max_pixel_value = np.max(adjusted_pixel_values)
    scaled_pixel_values = (
        (adjusted_pixel_values - min_pixel_value)
        / (max_pixel_value - min_pixel_value)
        * 255
    )
    adjusted_image = Image.fromarray(scaled_pixel_values.astype(np.uint8))

    # Save the processed image
    adjusted_image.save(output_path)
    logger.debug("Image processing complete")
    logger.debug(
        f"Lower threshold: {lower_threshold}; upper threshold: {upper_threshold}"
    )
    logger.debug(f"Adjusted image saved to `{output_path}`")
