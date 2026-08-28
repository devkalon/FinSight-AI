import io
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from typing import Tuple, Union

class ImagePreprocessor:
    """
    Financial document and receipt image preprocessor.
    Enhances contrast, normalizes orientation, reduces noise, and scales for optimal OCR accuracy.
    """

    @staticmethod
    def preprocess(image_input: Union[str, bytes, Image.Image]) -> Image.Image:
        """
        Runs a multi-stage preprocessing pipeline on the input image.
        Returns a clean, high-contrast PIL Image ready for OCR extraction.
        """
        # 1. Load image
        if isinstance(image_input, str):
            image = Image.open(image_input)
        elif isinstance(image_input, bytes):
            image = Image.open(io.BytesIO(image_input))
        elif isinstance(image_input, Image.Image):
            image = image_input.copy()
        else:
            raise ValueError("Unsupported image input type")

        # 2. Correct EXIF orientation if present
        try:
            image = ImageOps.exif_transpose(image)
        except Exception:
            pass

        # 3. Convert to RGB / Grayscale
        if image.mode != 'RGB' and image.mode != 'L':
            image = image.convert('RGB')

        # 4. Scale image to optimal DPI/resolution range
        width, height = image.size
        # If too small (e.g. low-res receipt screenshot), upscale with LANCZOS
        if width < 1000 or height < 1000:
            scale = max(1000 / width, 1000 / height, 1.5)
            new_size = (int(width * scale), int(height * scale))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        # If excessively large (> 3500px), downscale to avoid memory pressure
        elif width > 3500 or height > 3500:
            scale = min(3500 / width, 3500 / height)
            new_size = (int(width * scale), int(height * scale))
            image = image.resize(new_size, Image.Resampling.BILINEAR)

        # 5. Grayscale conversion for text contrast
        gray = image.convert('L')

        # 6. Enhance Contrast
        contrast_enhancer = ImageEnhance.Contrast(gray)
        enhanced_contrast = contrast_enhancer.enhance(1.8)

        # 7. Enhance Sharpness
        sharpness_enhancer = ImageEnhance.Sharpness(enhanced_contrast)
        sharp_image = sharpness_enhancer.enhance(1.5)

        # 8. Subtle median filter to remove salt-and-pepper noise
        denoised = sharp_image.filter(ImageFilter.MedianFilter(size=3))

        return denoised

image_preprocessor = ImagePreprocessor()
