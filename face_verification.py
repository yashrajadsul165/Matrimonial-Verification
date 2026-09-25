import cv2
import numpy as np
from insightface.app import FaceAnalysis


# Load InsightFace model
face_app = FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"]
)

face_app.prepare(
    ctx_id=0,
    det_size=(640, 640)
)


def get_face_embedding(image):

    """
    Detect a face and generate its AI face embedding.
    """

    if image is None:
        return None

    faces = face_app.get(image)

    if len(faces) == 0:
        return None

    # Select the largest detected face
    face = max(
        faces,
        key=lambda x: (
            x.bbox[2] - x.bbox[0]
        ) * (
            x.bbox[3] - x.bbox[1]
        )
    )

    embedding = face.embedding

    # Normalize embedding
    embedding = embedding / np.linalg.norm(
        embedding
    )

    return embedding


def compare_faces(image1, image2):

    """
    Compare two faces using cosine similarity.
    Returns similarity percentage.
    """

    embedding1 = get_face_embedding(
        image1
    )

    embedding2 = get_face_embedding(
        image2
    )

    if embedding1 is None:
        return None, "No face detected in first image."

    if embedding2 is None:
        return None, "No face detected in second image."

    similarity = np.dot(
        embedding1,
        embedding2
    )

    # Convert similarity to percentage
    similarity_percentage = float(
        similarity * 100
    )

    similarity_percentage = max(
        0,
        min(
            100,
            similarity_percentage
        )
    )

    if similarity_percentage >= 70:

        result = "High face similarity"

    elif similarity_percentage >= 50:

        result = "Moderate face similarity"

    else:

        result = "Low face similarity"

    return (
        round(
            similarity_percentage,
            2
        ),
        result
    )