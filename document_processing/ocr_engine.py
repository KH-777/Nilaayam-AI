"""OCR engine for Nilaayam AI.

Provides image and PDF page OCR extraction with support for English and Tamil,
image preprocessing (binarization, sharpening, grayscale conversion, deskewing),
and graceful fallbacks when Tesseract is unavailable.
"""

import io
import logging
import os
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)

# Optional PIL imports
try:
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps
except ImportError:
    Image = None
    ImageEnhance = None
    ImageFilter = None
    ImageOps = None
    logger.warning("Pillow (PIL) is not installed. Image processing and OCR will be disabled.")

# Optional pytesseract imports
try:
    import pytesseract
    from pytesseract import Output
except ImportError:
    pytesseract = None
    Output = None
    logger.warning("pytesseract is not installed. OCR extraction will be disabled.")

# Optional PyMuPDF (fitz) imports
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None
    logger.warning("PyMuPDF (fitz) is not installed. PDF page rendering will be disabled.")


def _configure_tesseract_path() -> None:
    """Detect and set the Tesseract executable path if not found in PATH."""
    if pytesseract is None:
        return

    # Check if user/environment already specified a valid path
    current_cmd = getattr(pytesseract.pytesseract, "tesseract_cmd", "tesseract")
    if shutil.which(current_cmd) or os.path.isfile(current_cmd):
        return

    # Look for settings in backend config if available
    try:
        from backend.config import settings
        config_cmd = getattr(settings, "tesseract_cmd", "tesseract")
        if shutil.which(config_cmd) or os.path.isfile(config_cmd):
            pytesseract.pytesseract.tesseract_cmd = config_cmd
            return
    except Exception:
        pass

    # Windows common installation paths
    windows_candidates = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
    ]
    for candidate in windows_candidates:
        if os.path.isfile(candidate):
            pytesseract.pytesseract.tesseract_cmd = candidate
            logger.info("Found Tesseract binary at %s", candidate)
            return


_configure_tesseract_path()


def is_tesseract_available() -> bool:
    """Check if the Tesseract binary is runnable and whether Tamil language data is installed.

    Returns:
        bool: True if Tesseract executable is found and operational, False otherwise.
    """
    if pytesseract is None:
        logger.warning("pytesseract library is not installed.")
        return False

    _configure_tesseract_path()

    try:
        version = pytesseract.get_tesseract_version()
        logger.debug("Tesseract version %s detected.", version)
    except Exception as exc:
        logger.warning("Tesseract binary is not operational or not found on PATH: %s", exc)
        return False

    # Check available languages
    try:
        languages = pytesseract.get_languages()
        if "tam" not in languages:
            logger.warning(
                "Tamil language pack ('tam') is not installed in Tesseract. "
                "Available languages: %s. Falling back to English for Tamil texts.",
                languages,
            )
        else:
            logger.debug("Tesseract Tamil ('tam') language pack is available.")
    except Exception as exc:
        logger.warning("Could not query Tesseract languages: %s", exc)

    return True


def _compute_otsu_threshold(gray_img: "Image.Image") -> int:
    """Compute optimal binarization threshold using Otsu's method on a grayscale PIL Image."""
    hist = gray_img.histogram()
    total = sum(hist)
    if total == 0:
        return 128

    sum_all = sum(i * hist[i] for i in range(256))
    sum_b = 0
    w_b = 0
    max_var = 0.0
    threshold = 128

    for i in range(256):
        w_b += hist[i]
        if w_b == 0:
            continue
        w_f = total - w_b
        if w_f == 0:
            break

        sum_b += i * hist[i]
        m_b = sum_b / w_b
        m_f = (sum_all - sum_b) / w_f

        # Between-class variance
        var_between = float(w_b) * float(w_f) * ((m_b - m_f) ** 2)
        if var_between > max_var:
            max_var = var_between
            threshold = i

    return threshold


def preprocess_image(image: Any) -> Any:
    """Preprocess an image for OCR.

    Applies grayscale conversion, contrast enhancement, slight sharpening,
    and adaptive/Otsu binarization to maximize OCR accuracy.

    Args:
        image: A PIL Image object or a file path (str / Path).

    Returns:
        A preprocessed PIL Image object (or original if PIL is unavailable).
    """
    if Image is None:
        return image

    pil_img: Optional[Image.Image] = None
    if isinstance(image, (str, Path)):
        try:
            pil_img = Image.open(str(image))
        except Exception as exc:
            logger.error("Failed to open image from path '%s': %s", image, exc)
            return None
    elif isinstance(image, Image.Image):
        pil_img = image
    else:
        logger.warning("Unsupported image input type for preprocessing: %s", type(image))
        return image

    try:
        # Convert to RGB first if RGBA/Palette to avoid alpha transparency distortion
        if pil_img.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", pil_img.size, (255, 255, 255))
            if pil_img.mode == "P":
                pil_img = pil_img.convert("RGBA")
            if pil_img.mode in ("RGBA", "LA"):
                alpha = pil_img.split()[-1]
                background.paste(pil_img, mask=alpha)
                pil_img = background
            else:
                pil_img = pil_img.convert("RGB")

        # 1. Convert to Grayscale
        gray = pil_img.convert("L")

        # 2. Auto-contrast normalization
        if ImageOps:
            gray = ImageOps.autocontrast(gray, cutoff=1)

        # 3. Slight sharpening
        if ImageEnhance:
            sharpener = ImageEnhance.Sharpness(gray)
            gray = sharpener.enhance(1.6)
        elif ImageFilter:
            gray = gray.filter(ImageFilter.SHARPEN)

        # 4. Otsu Binarization / Threshold
        threshold = _compute_otsu_threshold(gray)
        # Apply threshold lookup table
        lut = [0 if i < threshold else 255 for i in range(256)]
        binary = gray.point(lut, mode="L")

        return binary

    except Exception as exc:
        logger.warning("Error during image preprocessing, using original image: %s", exc)
        return pil_img


def _detect_languages_in_text(text: str) -> str:
    """Detect presence of Tamil and English characters in extracted text."""
    has_tamil = bool(re.search(r"[\u0B80-\u0BFF]", text))
    has_english = bool(re.search(r"[A-Za-z]", text))

    if has_tamil and has_english:
        return "tam+eng"
    elif has_tamil:
        return "tam"
    elif has_english:
        return "eng"
    return "unknown"


def _resolve_languages(requested: str) -> str:
    """Check installed languages and fallback to English if Tamil is requested but missing."""
    if pytesseract is None:
        return "eng"

    try:
        available = pytesseract.get_languages()
    except Exception:
        available = ["eng"]

    req_parts = [p.strip() for p in requested.split("+") if p.strip()]
    supported_parts = [p for p in req_parts if p in available]

    if not supported_parts:
        if "eng" in available:
            return "eng"
        return available[0] if available else "eng"

    return "+".join(supported_parts)


def extract_text_from_image(
    image_path: Union[str, Path, Any],
    languages: str = "tam+eng",
) -> Dict[str, Any]:
    """Extract text, confidence, and metadata from an image using Tesseract OCR.

    Args:
        image_path: Path to the image file or a PIL Image instance.
        languages: Tesseract language string (defaults to 'tam+eng').

    Returns:
        Dict[str, Any]:
            - text (str): Extracted plain text.
            - confidence (float): Mean OCR confidence score between 0.0 and 1.0.
            - word_count (int): Number of words extracted.
            - language_detected (str): 'tam+eng', 'tam', 'eng', 'unknown', or 'none'.
    """
    default_result: Dict[str, Any] = {
        "text": "",
        "confidence": 0.0,
        "word_count": 0,
        "language_detected": "none",
    }

    if not is_tesseract_available() or Image is None:
        logger.warning("OCR extraction requested but Tesseract or Pillow is not available.")
        return default_result

    # Load PIL image if path given
    raw_img = image_path
    if isinstance(image_path, (str, Path)):
        if not os.path.exists(str(image_path)):
            logger.error("Image file does not exist: %s", image_path)
            return default_result
        try:
            raw_img = Image.open(str(image_path))
        except Exception as exc:
            logger.error("Failed to load image file '%s': %s", image_path, exc)
            return default_result

    # Preprocess image
    processed_img = preprocess_image(raw_img)
    if processed_img is None:
        return default_result

    # Resolve languages against installed language packs
    target_lang = _resolve_languages(languages)
    tess_config = "--oem 3 --psm 6"

    try:
        # 1. Extract detailed word data with confidence
        data: Dict[str, List[Any]] = pytesseract.image_to_data(
            processed_img,
            lang=target_lang,
            config=tess_config,
            output_type=Output.DICT,
        )

        # 2. Extract full text
        extracted_text = pytesseract.image_to_string(
            processed_img,
            lang=target_lang,
            config=tess_config,
        ).strip()

        # 3. Calculate mean word confidence
        conf_values = [
            float(c)
            for c in data.get("conf", [])
            if str(c).strip() and float(c) > 0
        ]
        if conf_values:
            overall_confidence = round(sum(conf_values) / (len(conf_values) * 100.0), 3)
            overall_confidence = max(0.0, min(1.0, overall_confidence))
        else:
            overall_confidence = 0.5 if extracted_text else 0.0

        words = [w for w in extracted_text.split() if w.strip()]
        detected_lang = _detect_languages_in_text(extracted_text)

        return {
            "text": extracted_text,
            "confidence": overall_confidence,
            "word_count": len(words),
            "language_detected": detected_lang,
        }

    except Exception as exc:
        logger.error("OCR execution failed for image: %s", exc)
        return default_result


def extract_text_from_pdf_page(
    pdf_path: str,
    page_num: int,
    languages: str = "tam+eng",
) -> Dict[str, Any]:
    """Render a single PDF page at 300 DPI and run OCR on the rendered image.

    Args:
        pdf_path: Path to the PDF file.
        page_num: 1-indexed page number.
        languages: Tesseract language string (e.g., 'tam+eng').

    Returns:
        Dict[str, Any]: Extracted OCR dictionary containing text, confidence,
        word_count, and language_detected.
    """
    default_result: Dict[str, Any] = {
        "text": "",
        "confidence": 0.0,
        "word_count": 0,
        "language_detected": "none",
    }

    if fitz is None:
        logger.warning("PyMuPDF (fitz) is required to render PDF pages for OCR.")
        return default_result

    if Image is None:
        logger.warning("Pillow (PIL) is required to process PDF images for OCR.")
        return default_result

    if not os.path.exists(pdf_path):
        logger.error("PDF file not found at %s", pdf_path)
        return default_result

    doc = None
    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)

        if page_num < 1 or page_num > total_pages:
            logger.error(
                "Invalid page_num %d for PDF '%s' (total pages: %d)",
                page_num,
                pdf_path,
                total_pages,
            )
            return default_result

        page = doc[page_num - 1]

        # 300 DPI rendering: zoom = 300 / 72 = 4.166667
        zoom = 300.0 / 72.0
        matrix = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=matrix, alpha=False)

        # Convert fitz pixmap to PIL Image
        img_bytes = pix.tobytes("png")
        pil_image = Image.open(io.BytesIO(img_bytes))

        # Run OCR on the PIL Image
        return extract_text_from_image(pil_image, languages=languages)

    except Exception as exc:
        logger.error(
            "Failed to render or OCR page %d of PDF '%s': %s",
            page_num,
            pdf_path,
            exc,
        )
        return default_result
    finally:
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass
