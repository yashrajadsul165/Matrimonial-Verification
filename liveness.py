import cv2
import numpy as np


def detect_face(image):
    """
    Detect faces in an image.
    """

    if image is None:
        return 0

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades +
        "haarcascade_frontalface_default.xml"
    )

    faces = cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(80, 80)
    )

    return len(faces)


def analyze_liveness(image):
    """
    Basic liveness screening.

    This checks image presence and face detection.
    It is not a certified anti-spoofing system.
    """

    if image is None:
        return {
            "live": False,
            "score": 0,
            "message": "Invalid camera image."
        }

    face_count = detect_face(image)

    if face_count == 0:

        return {
            "live": False,
            "score": 0,
            "message": "No face detected."
        }

    if face_count > 1:

        return {
            "live": False,
            "score": 30,
            "message": "Multiple faces detected."
        }

    # Image quality measurements
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    brightness = float(
        np.mean(gray)
    )

    sharpness = float(
        cv2.Laplacian(
            gray,
            cv2.CV_64F
        ).var()
    )

    score = 70

    # Brightness check
    if 50 <= brightness <= 220:
        score += 10

    # Sharpness check
    if sharpness > 100:
        score += 10

    score = min(
        score,
        100
    )

    if score >= 80:

        message = (
            "Face detected with acceptable "
            "live-image quality."
        )

        live = True

    else:

        message = (
            "Face detected, but additional "
            "liveness verification is recommended."
        )

        live = False

    return {
        "live": live,
        "score": score,
        "message": message,
        "face_count": face_count,
        "brightness": round(
            brightness,
            2
        ),
        "sharpness": round(
            sharpness,
            2
        )
    }