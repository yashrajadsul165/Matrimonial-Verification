import streamlit as st
import cv2
import numpy as np
import os
from datetime import datetime

# =========================================================
# PROJECT MODULES
# =========================================================

from face_verification import compare_faces
from deepfake_detection import analyze_image
from liveness import analyze_liveness
from document_verification import (
    analyze_document,
    check_tesseract
)
from behavior_model import analyze_feedback
from database import (
    create_database,
    save_verification,
    get_all_verifications
)
from auth import (
    create_auth_database,
    create_user,
    login_user
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Matrimonial Verification System",
    page_icon="💍",
    layout="wide"
)


# =========================================================
# CREATE REQUIRED DATABASES
# =========================================================

create_database()
create_auth_database()


# =========================================================
# CREATE FOLDERS
# =========================================================

os.makedirs(
    "uploads",
    exist_ok=True
)

os.makedirs(
    "verification_photos",
    exist_ok=True
)


# =========================================================
# SESSION VARIABLES
# =========================================================

session_defaults = {

    "logged_in": False,

    "username": "",

    "profile_name": "",

    "profile_photo": None,

    "profile_photo_name": "",

    "verification_photo": None,

    "face_score": None,

    "face_result": "",

    "deepfake_score": None,

    "deepfake_result": "",

    "deepfake_details": None,

    "liveness_score": None,

    "liveness_result": "",

    "document_result": "",

    "document_name_match": False,

    "document_text": "",

    "feedback_score": None,

    "feedback_result": "",

    "verification_saved": False,

    "liveness_started": False
}


for key, value in session_defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value


# =========================================================
# LOGIN / REGISTRATION PAGE
# =========================================================

if not st.session_state.logged_in:

    st.title(
        "💍 Matrimonial Verification System"
    )

    st.write(
        "Secure AI-powered matrimonial "
        "profile verification system."
    )

    st.divider()

    login_tab, register_tab = st.tabs(
        [
            "🔐 Login",
            "📝 Create Account"
        ]
    )

    # -----------------------------------------------------
    # LOGIN
    # -----------------------------------------------------

    with login_tab:

        st.subheader(
            "Login"
        )

        username = st.text_input(
            "Username",
            key="login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "🔐 Login",
            type="primary"
        ):

            if not username or not password:

                st.warning(
                    "Please enter username and password."
                )

            else:

                if login_user(
                    username,
                    password
                ):

                    st.session_state.logged_in = True
                    st.session_state.username = username

                    st.success(
                        "Login successful!"
                    )

                    st.rerun()

                else:

                    st.error(
                        "Invalid username or password."
                    )

    # -----------------------------------------------------
    # REGISTRATION
    # -----------------------------------------------------

    with register_tab:

        st.subheader(
            "Create New Account"
        )

        new_username = st.text_input(
            "Create username",
            key="register_username"
        )

        new_password = st.text_input(
            "Create password",
            type="password",
            key="register_password"
        )

        confirm_password = st.text_input(
            "Confirm password",
            type="password",
            key="confirm_password"
        )

        if st.button(
            "📝 Create Account"
        ):

            if not new_username or not new_password:

                st.warning(
                    "Please enter username and password."
                )

            elif new_password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            elif len(new_password) < 8:

                st.warning(
                    "Password must contain at least 8 characters."
                )

            else:

                success, message = create_user(
                    new_username,
                    new_password
                )

                if success:

                    st.success(
                        message +
                        " You can now login."
                    )

                else:

                    st.error(
                        message
                    )

    st.stop()


# =========================================================
# HEADER
# =========================================================

st.title(
    "💍 AI-Powered Matrimonial Photo Authenticity "
    "and Identity Verification System"
)

st.write(
    "AI-based profile verification, identity verification, "
    "photo authenticity screening and matrimonial verification."
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title(
    "🔐 Verification System"
)

st.sidebar.success(
    f"Logged in as: {st.session_state.username}"
)

page = st.sidebar.radio(
    "Select Module",
    [
        "🏠 Home",
        "👤 Profile Verification",
        "🤖 AI Face Verification",
        "🖼️ Deepfake Detection",
        "📷 Liveness Verification",
        "📄 Document Verification",
        "💬 Feedback Analysis",
        "💞 Matching",
        "📊 Dashboard"
    ]
)

st.sidebar.divider()

if st.sidebar.button(
    "🚪 Logout"
):

    st.session_state.logged_in = False
    st.session_state.username = ""

    st.rerun()


# =========================================================
# HOME
# =========================================================

if page == "🏠 Home":

    st.header(
        "🏠 Welcome to the Verification System"
    )

    st.write(
        "This system provides multiple verification "
        "layers for matrimonial profiles."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.info(
            "👤 Profile\n\n"
            "Register and verify the user's profile photo."
        )

    with col2:

        st.info(
            "🤖 AI Verification\n\n"
            "Compare profile and verification faces."
        )

    with col3:

        st.info(
            "🛡️ Authenticity\n\n"
            "Screen photos, liveness and documents."
        )

    st.divider()

    st.subheader(
        "Verification Pipeline"
    )

    st.write(
        """
        1. 👤 Profile Registration
        2. 🤖 AI Face Verification
        3. 🖼️ Image Authenticity Screening
        4. 📷 Liveness Verification
        5. 📄 Document Verification
        6. 💬 Feedback Analysis
        7. 🗄️ Database Storage
        8. 📊 Verification Dashboard
        """
    )


# =========================================================
# PROFILE VERIFICATION
# =========================================================

elif page == "👤 Profile Verification":

    st.header(
        "👤 Profile Verification"
    )

    name = st.text_input(
        "Enter your name",
        value=st.session_state.profile_name
    )

    photo = st.file_uploader(
        "Upload your profile photo",
        type=[
            "jpg",
            "jpeg",
            "png"
        ],
        key="profile_upload"
    )

    if photo is not None:

        image_bytes = np.asarray(
            bytearray(
                photo.getvalue()
            ),
            dtype=np.uint8
        )

        image = cv2.imdecode(
            image_bytes,
            cv2.IMREAD_COLOR
        )

        if image is None:

            st.error(
                "Unable to read the uploaded image."
            )

        else:

            gray = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2GRAY
            )

            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades +
                "haarcascade_frontalface_default.xml"
            )

            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5
            )

            display_image = image.copy()

            for (
                x,
                y,
                w,
                h
            ) in faces:

                cv2.rectangle(
                    display_image,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

            display_image = cv2.cvtColor(
                display_image,
                cv2.COLOR_BGR2RGB
            )

            st.image(
                display_image,
                caption="Profile Photo Face Detection",
                width=450
            )

            if len(faces) > 0:

                st.success(
                    f"Face detected: {len(faces)}"
                )

                if name.strip() == "":

                    st.warning(
                        "Please enter your name."
                    )

                else:

                    if st.button(
                        "💾 Save Profile",
                        type="primary"
                    ):

                        file_path = os.path.join(
                            "uploads",
                            photo.name
                        )

                        with open(
                            file_path,
                            "wb"
                        ) as file:

                            file.write(
                                photo.getbuffer()
                            )

                        st.session_state.profile_name = name
                        st.session_state.profile_photo = image
                        st.session_state.profile_photo_name = photo.name

                        st.success(
                            "Profile photo saved successfully!"
                        )

                        st.info(
                            "Your profile is ready for AI verification."
                        )

            else:

                st.warning(
                    "No face detected. "
                    "Please upload a clear face photo."
                )


# =========================================================
# AI FACE VERIFICATION
# =========================================================

elif page == "🤖 AI Face Verification":

    st.header(
        "🤖 Real AI Identity Verification"
    )

    if st.session_state.profile_photo is None:

        st.warning(
            "First complete Profile Verification."
        )

    else:

        st.success(
            f"Profile loaded: "
            f"{st.session_state.profile_name}"
        )

        verification_photo = st.file_uploader(
            "Upload verification photo",
            type=[
                "jpg",
                "jpeg",
                "png"
            ],
            key="verification_upload"
        )

        if verification_photo is not None:

            image_bytes = np.asarray(
                bytearray(
                    verification_photo.getvalue()
                ),
                dtype=np.uint8
            )

            verification_image = cv2.imdecode(
                image_bytes,
                cv2.IMREAD_COLOR
            )

            if verification_image is None:

                st.error(
                    "Unable to read verification image."
                )

            else:

                display_image = cv2.cvtColor(
                    verification_image,
                    cv2.COLOR_BGR2RGB
                )

                st.image(
                    display_image,
                    caption="Verification Photo",
                    width=450
                )

                if st.button(
                    "🔍 Start AI Face Verification",
                    type="primary"
                ):

                    with st.spinner(
                        "AI is comparing the faces..."
                    ):

                        score, result = compare_faces(
                            st.session_state.profile_photo,
                            verification_image
                        )

                    if score is None:

                        st.error(
                            result
                        )

                    else:

                        st.session_state.face_score = score
                        st.session_state.face_result = result
                        st.session_state.verification_photo = verification_image

                        st.subheader(
                            "AI Verification Result"
                        )

                        st.metric(
                            "Face Similarity",
                            f"{score}%"
                        )

                        if score >= 70:

                            st.success(
                                "✅ High face similarity detected."
                            )

                        elif score >= 50:

                            st.warning(
                                "⚠️ Moderate face similarity."
                            )

                        else:

                            st.error(
                                "❌ Low face similarity."
                            )

                        st.write(
                            f"Result: {result}"
                        )


# =========================================================
# DEEPFAKE DETECTION
# =========================================================

elif page == "🖼️ Deepfake Detection":

    st.header(
        "🖼️ AI-Generated / Manipulated Image Screening"
    )

    st.info(
        "This is a screening layer based on image characteristics. "
        "It should not be treated as proof that an image is fake."
    )

    if st.session_state.profile_photo is None:

        st.warning(
            "First upload a profile photo."
        )

    else:

        image_file = st.file_uploader(
            "Upload image to screen",
            type=[
                "jpg",
                "jpeg",
                "png"
            ],
            key="deepfake_upload"
        )

        if image_file is not None:

            st.image(
                image_file,
                caption="Image for Authenticity Screening",
                width=450
            )

            if st.button(
                "🔎 Analyze Image",
                type="primary"
            ):

                with st.spinner(
                    "Analyzing image characteristics..."
                ):

                    result = analyze_image(
                        image_file.getvalue()
                    )

                if "error" in result:

                    st.error(
                        result["error"]
                    )

                else:

                    st.session_state.deepfake_score = result[
                        "risk_score"
                    ]

                    st.session_state.deepfake_result = result[
                        "result"
                    ]

                    st.session_state.deepfake_details = result

                    st.metric(
                        "Screening Risk Score",
                        f"{result['risk_score']}/100"
                    )

                    st.write(
                        f"**Result:** {result['result']}"
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.write(
                            f"Sharpness: "
                            f"{result['sharpness']}"
                        )

                    with col2:

                        st.write(
                            f"Noise level: "
                            f"{result['noise_level']}"
                        )

                    with col3:

                        st.write(
                            f"Resolution: "
                            f"{result['width']} × "
                            f"{result['height']}"
                        )


# =========================================================
# LIVENESS
# =========================================================

elif page == "📷 Liveness Verification":

    st.header(
        "📷 Liveness / Anti-Spoofing"
    )

    st.warning(
        "Current version performs basic live-image screening. "
        "A production system should use a dedicated anti-spoofing model."
    )

    if not st.session_state.liveness_started:

        if st.button(
            "▶️ Start Camera",
            type="primary"
        ):

            st.session_state.liveness_started = True

            st.rerun()

    else:

        camera_photo = st.camera_input(
            "Take a live verification photo"
        )

        if camera_photo is not None:

            camera_bytes = np.asarray(
                bytearray(
                    camera_photo.getvalue()
                ),
                dtype=np.uint8
            )

            camera_image = cv2.imdecode(
                camera_bytes,
                cv2.IMREAD_COLOR
            )

            if camera_image is not None:

                result = analyze_liveness(
                    camera_image
                )

                st.session_state.liveness_score = result.get(
                    "score",
                    0
                )

                st.session_state.liveness_result = result.get(
                    "message",
                    ""
                )

                st.metric(
                    "Liveness Score",
                    f"{result.get('score', 0)}/100"
                )

                if result.get(
                    "live",
                    False
                ):

                    st.success(
                        "✅ " +
                        result.get(
                            "message",
                            "Live image detected."
                        )
                    )

                else:

                    st.warning(
                        "⚠️ " +
                        result.get(
                            "message",
                            "Additional verification recommended."
                        )
                    )

        if st.button(
            "⏹️ Stop Camera"
        ):

            st.session_state.liveness_started = False

            st.rerun()


# =========================================================
# DOCUMENT VERIFICATION
# =========================================================

elif page == "📄 Document Verification":

    st.header(
        "📄 Document Verification"
    )

    st.write(
        "Upload a document image for OCR-based text extraction "
        "and basic profile-name consistency checking."
    )

    tesseract_status = check_tesseract()

    if not tesseract_status["installed"]:

        st.error(
            "Tesseract OCR is not available."
        )

        st.code(
            tesseract_status["message"]
        )

    else:

        st.success(
            "Tesseract OCR is ready."
        )

        if not st.session_state.profile_name:

            st.warning(
                "Complete Profile Verification first."
            )

        document_file = st.file_uploader(
            "Upload document image",
            type=[
                "jpg",
                "jpeg",
                "png"
            ],
            key="document_upload"
        )

        if document_file is not None:

            st.image(
                document_file,
                caption="Uploaded Document",
                width=500
            )

            if st.button(
                "📄 Verify Document",
                type="primary"
            ):

                with st.spinner(
                    "Reading document..."
                ):

                    result = analyze_document(
                        document_file.getvalue(),
                        st.session_state.profile_name
                    )

                st.session_state.document_result = result.get(
                    "message",
                    ""
                )

                st.session_state.document_name_match = result.get(
                    "name_found",
                    False
                )

                st.session_state.document_text = result.get(
                    "extracted_text",
                    ""
                )

                if result.get(
                    "valid",
                    False
                ):

                    st.success(
                        result["message"]
                    )

                else:

                    st.warning(
                        result["message"]
                    )

                st.subheader(
                    "Extracted Text"
                )

                st.text_area(
                    "OCR Result",
                    result.get(
                        "extracted_text",
                        ""
                    ),
                    height=250
                )


# =========================================================
# FEEDBACK ANALYSIS
# =========================================================

elif page == "💬 Feedback Analysis":

    st.header(
        "💬 Behavioral / Feedback Analysis"
    )

    st.info(
        "This is a simple feedback-screening model. "
        "It does not determine personality, character or intent."
    )

    feedback = st.text_area(
        "Enter feedback or verification comments",
        height=150
    )

    if st.button(
        "🔎 Analyze Feedback",
        type="primary"
    ):

        if not feedback.strip():

            st.warning(
                "Please enter some feedback."
            )

        else:

            result = analyze_feedback(
                feedback
            )

            st.session_state.feedback_score = result[
                "score"
            ]

            st.session_state.feedback_result = result[
                "category"
            ]

            st.metric(
                "Feedback Score",
                f"{result['score']}/100"
            )

            st.write(
                f"**Category:** {result['category']}"
            )

            st.write(
                result["message"]
            )


# =========================================================
# MATCHING
# =========================================================

elif page == "💞 Matching":

    st.header(
        "💞 Matrimonial Profile Matching"
    )

    st.info(
        "The verification modules provide evidence about "
        "profile authenticity. Compatibility should be based "
        "on user-selected preferences rather than the AI "
        "verification score."
    )

    if st.session_state.profile_name:

        st.write(
            f"**Current Profile:** "
            f"{st.session_state.profile_name}"
        )

    else:

        st.warning(
            "No profile registered yet."
        )

    st.subheader(
        "Verification Summary"
    )

    if st.session_state.face_score is not None:

        st.write(
            f"🤖 Face Similarity: "
            f"{st.session_state.face_score}%"
        )

    if st.session_state.deepfake_score is not None:

        st.write(
            f"🖼️ Image Screening Risk: "
            f"{st.session_state.deepfake_score}/100"
        )

    if st.session_state.liveness_score is not None:

        st.write(
            f"📷 Liveness Score: "
            f"{st.session_state.liveness_score}/100"
        )


# =========================================================
# DASHBOARD
# =========================================================

elif page == "📊 Dashboard":

    st.header(
        "📊 Verification Dashboard"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Profile",
            "Completed"
            if st.session_state.profile_photo is not None
            else "Pending"
        )

    with col2:

        st.metric(
            "AI Face",
            "Completed"
            if st.session_state.face_score is not None
            else "Pending"
        )

    with col3:

        st.metric(
            "Liveness",
            "Completed"
            if st.session_state.liveness_score is not None
            else "Pending"
        )

    with col4:

        st.metric(
            "Document",
            "Completed"
            if st.session_state.document_result
            else "Pending"
        )

    st.divider()

    st.subheader(
        "Current Verification"
    )

    if st.session_state.profile_name:

        st.write(
            f"👤 **Name:** "
            f"{st.session_state.profile_name}"
        )

    if st.session_state.face_score is not None:

        st.write(
            f"🤖 **Face Similarity:** "
            f"{st.session_state.face_score}%"
        )

        st.write(
            f"**Face Result:** "
            f"{st.session_state.face_result}"
        )

    if st.session_state.deepfake_score is not None:

        st.write(
            f"🖼️ **Image Risk Score:** "
            f"{st.session_state.deepfake_score}/100"
        )

        st.write(
            f"**Image Result:** "
            f"{st.session_state.deepfake_result}"
        )

    if st.session_state.liveness_score is not None:

        st.write(
            f"📷 **Liveness Score:** "
            f"{st.session_state.liveness_score}/100"
        )

        st.write(
            f"**Liveness Result:** "
            f"{st.session_state.liveness_result}"
        )

    if st.session_state.document_result:

        st.write(
            f"📄 **Document:** "
            f"{st.session_state.document_result}"
        )

        st.write(
            f"**Document Name Match:** "
            f"{'Yes' if st.session_state.document_name_match else 'No'}"
        )

    if st.session_state.feedback_score is not None:

        st.write(
            f"💬 **Feedback Score:** "
            f"{st.session_state.feedback_score}/100"
        )

        st.write(
            f"**Feedback:** "
            f"{st.session_state.feedback_result}"
        )

    st.divider()

    # -----------------------------------------------------
    # SAVE COMPLETE VERIFICATION
    # -----------------------------------------------------

    st.subheader(
        "💾 Save Verification Record"
    )

    if st.session_state.profile_name:

        if st.button(
            "💾 Save Complete Verification",
            type="primary"
        ):

            record_id = save_verification(

                name=st.session_state.profile_name,

                photo_name=st.session_state.profile_photo_name,

                face_similarity=st.session_state.face_score,

                face_result=st.session_state.face_result,

                deepfake_score=st.session_state.deepfake_score,

                deepfake_result=st.session_state.deepfake_result,

                liveness_score=st.session_state.liveness_score,

                liveness_result=st.session_state.liveness_result,

                document_result=st.session_state.document_result,

                document_name_match=st.session_state.document_name_match,

                feedback_score=st.session_state.feedback_score,

                feedback_result=st.session_state.feedback_result
            )

            st.session_state.verification_saved = True

            st.success(
                f"Verification saved successfully. "
                f"Record ID: {record_id}"
            )

    else:

        st.info(
            "Complete Profile Verification first."
        )

    # -----------------------------------------------------
    # DATABASE RECORDS
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "🗄️ Saved Verification Records"
    )

    records = get_all_verifications()

    if records:

        for record in records:

            with st.expander(
                f"Record #{record['id']} — "
                f"{record['name']} — "
                f"{record['created_at']}"
            ):

                st.write(
                    f"**Name:** {record['name']}"
                )

                st.write(
                    f"**Face Similarity:** "
                    f"{record['face_similarity']}"
                )

                st.write(
                    f"**Face Result:** "
                    f"{record['face_result']}"
                )

                st.write(
                    f"**Deepfake Risk:** "
                    f"{record['deepfake_score']}"
                )

                st.write(
                    f"**Deepfake Result:** "
                    f"{record['deepfake_result']}"
                )

                st.write(
                    f"**Liveness Score:** "
                    f"{record['liveness_score']}"
                )

                st.write(
                    f"**Liveness Result:** "
                    f"{record['liveness_result']}"
                )

                st.write(
                    f"**Document:** "
                    f"{record['document_result']}"
                )

                st.write(
                    f"**Document Name Match:** "
                    f"{'Yes' if record['document_name_match'] else 'No'}"
                )

                st.write(
                    f"**Feedback Score:** "
                    f"{record['feedback_score']}"
                )

                st.write(
                    f"**Feedback:** "
                    f"{record['feedback_result']}"
                )

    else:

        st.info(
            "No verification records saved yet."
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "AI-Powered Matrimonial Photo Authenticity "
    "and Identity Verification System"
)

st.caption(
    "System time: "
    + datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )
)