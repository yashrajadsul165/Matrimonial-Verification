import cv2
import numpy as np
from PIL import Image
import io


def analyze_image(image_bytes):
    """
    Analyze an uploaded image for basic AI/manipulation indicators.

    This is a screening system, not a definitive deepfake detector.
    """

    try:
        # Convert uploaded bytes to image
        pil_image = Image.open(
            io.BytesIO(image_bytes)
        ).convert("RGB")

        image = np.array(pil_image)

        # RGB -> BGR for OpenCV
        image = cv2.cvtColor(
            image,
            cv2.COLOR_RGB2BGR
        )

        # -------------------------------------------------
        # 1. Image quality analysis
        # -------------------------------------------------

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        # Sharpness
        sharpness = cv2.Laplacian(
            gray,
            cv2.CV_64F
        ).var()

        # -------------------------------------------------
        # 2. Noise analysis
        # -------------------------------------------------

        noise = cv2.GaussianBlur(
            gray,
            (3, 3),
            0
        )

        noise_difference = cv2.absdiff(
            gray,
            noise
        )

        noise_level = float(
            np.mean(noise_difference)
        )

        # -------------------------------------------------
        # 3. Image dimensions
        # -------------------------------------------------

        height, width = gray.shape

        # -------------------------------------------------
        # 4. JPEG compression analysis
        # -------------------------------------------------

        compression_score = 0

        if image_bytes[:2] == b"\xff\xd8":

            compression_score = 1

        # -------------------------------------------------
        # 5. Calculate screening risk
        # -------------------------------------------------

        risk_score = 0

        # Very low noise can sometimes occur in
        # heavily generated/processed images.
        if noise_level < 2:

            risk_score += 25

        elif noise_level < 4:

            risk_score += 10

        # Extremely high sharpness can indicate
        # aggressive enhancement/processing.
        if sharpness > 2500:

            risk_score += 20

        elif sharpness > 1500:

            risk_score += 10

        # Very small images provide less evidence.
        if width < 300 or height < 300:

            risk_score += 10

        # Keep score between 0 and 100
        risk_score = max(
            0,
            min(
                100,
                risk_score
            )
        )

        # -------------------------------------------------
        # Result
        # -------------------------------------------------

        if risk_score >= 60:

            result = "High manipulation/AI-image risk"

        elif risk_score >= 30:

            result = "Moderate manipulation/AI-image risk"

        else:

            result = "Low manipulation/AI-image risk"

        return {
            "risk_score": risk_score,
            "result": result,
            "sharpness": round(
                float(sharpness),
                2
            ),
            "noise_level": round(
                noise_level,
                2
            ),
            "width": width,
            "height": height,
            "jpeg_detected": bool(
                compression_score
            )
        }

    except Exception as e:

        return {
            "error": str(e)
        }