import pytesseract
from PIL import Image
import io
import re
import os


# =========================================================
# TESSERACT CONFIGURATION
# =========================================================

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Tell pytesseract exactly where Tesseract is installed
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


# =========================================================
# CHECK TESSERACT
# =========================================================

def check_tesseract():
    """
    Check whether the Tesseract executable exists.
    """

    if not os.path.exists(TESSERACT_PATH):

        return {
            "installed": False,
            "message": (
                "Tesseract executable was not found at: "
                + TESSERACT_PATH
            )
        }

    try:

        version = pytesseract.get_tesseract_version()

        return {
            "installed": True,
            "version": str(version),
            "message": "Tesseract OCR is working correctly."
        }

    except Exception as e:

        return {
            "installed": False,
            "message": str(e)
        }


# =========================================================
# EXTRACT TEXT
# =========================================================

def extract_text(image_bytes):

    try:

        image = Image.open(
            io.BytesIO(image_bytes)
        )

        text = pytesseract.image_to_string(
            image
        )

        return text.strip()

    except Exception as e:

        return f"OCR Error: {str(e)}"


# =========================================================
# CHECK DOCUMENT TEXT
# =========================================================

def check_document_text(
    text,
    profile_name=""
):

    if not text or len(text.strip()) < 5:

        return {
            "valid": False,
            "message": "Very little or no text detected.",
            "name_found": False,
            "text_length": 0
        }

    text_lower = text.lower()

    cleaned_text = re.sub(
        r"\s+",
        " ",
        text_lower
    ).strip()

    name_found = False

    if profile_name:

        profile_words = (
            profile_name
            .lower()
            .split()
        )

        matches = 0

        for word in profile_words:

            if (
                len(word) >= 3
                and word in cleaned_text
            ):

                matches += 1

        required_matches = max(
            1,
            len(profile_words) // 2
        )

        if matches >= required_matches:

            name_found = True

    if profile_name and name_found:

        message = (
            "Document text detected and "
            "profile name appears in the document."
        )

    else:

        message = (
            "Document text detected. "
            "Manual verification may be required."
        )

    return {
        "valid": True,
        "message": message,
        "name_found": name_found,
        "text_length": len(text)
    }


# =========================================================
# COMPLETE DOCUMENT ANALYSIS
# =========================================================

def analyze_document(
    image_bytes,
    profile_name=""
):

    text = extract_text(
        image_bytes
    )

    result = check_document_text(
        text,
        profile_name
    )

    result["extracted_text"] = text

    return result