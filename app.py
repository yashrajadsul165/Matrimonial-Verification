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
    init_database,
    authenticate_user,
    create_user,
    save_verification,
    get_all_verifications
)

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Matrimonial Verification System",
    page_icon="💍",
    layout="wide"
)

# =========================================================
# DATABASE
# =========================================================

init_database()

# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "logged_in": False,
    "username": "",
    "page": "🏠 Home",

    "profile_name": "",
    "profile_photo": None,
    "profile_photo_name": "",

    "face_score": None,
    "face_result": None,

    "deepfake_score": None,
    "deepfake_result": None,

    "liveness_score": None,
    "liveness_result": None,

    "document_result": None,
    "document_name_match": None,

    "feedback_score": None,
    "feedback_result": None,

    "verification_saved": False
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def reset_verification():
    st.session_state.profile_name = ""
    st.session_state.profile_photo = None
    st.session_state.profile_photo_name = ""

    st.session_state.face_score = None
    st.session_state.face_result = None

    st.session_state.deepfake_score = None
    st.session_state.deepfake_result = None

    st.session_state.liveness_score = None
    st.session_state.liveness_result = None

    st.session_state.document_result = None
    st.session_state.document_name_match = None

    st.session_state.feedback_score = None
    st.session_state.feedback_result = None

    st.session_state.verification_saved = False


def safe_number(value, default=0):
    try:
        if value is None:
            return default

        if isinstance(value, (int, float)):
            return value

        return float(value)

    except Exception:
        return default


def safe_result(result, default_message="Analysis completed."):
    if result is None:
        return default_message

    if isinstance(result, dict):
        return result

    return {
        "score": safe_number(result),
        "result": default_message,
        "message": default_message
    }


# =========================================================
# LOGIN PAGE
# =========================================================

def login_page():

    st.title("💍 Matrimonial Verification System")

    st.write(
        "Secure AI-powered matrimonial profile verification system."
    )

    tab1, tab2 = st.tabs(
        [
            "🔐 Login",
            "📝 Create Account"
        ]
    )

    # -----------------------------------------------------
    # LOGIN
    # -----------------------------------------------------

    with tab1:

        st.header("Login")

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
            "Login",
            type="primary",
            use_container_width=True
        ):

            if not username or not password:

                st.warning(
                    "Please enter username and password."
                )

            else:

                try:

                    result = authenticate_user(
                        username,
                        password
                    )

                    if result:

                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.page = "🏠 Home"

                        st.success(
                            "Login successful."
                        )

                        st.rerun()

                    else:

                        st.error(
                            "Invalid username or password."
                        )

                except Exception as e:

                    st.error(
                        f"Login error: {str(e)}"
                    )

    # -----------------------------------------------------
    # CREATE ACCOUNT
    # -----------------------------------------------------

    with tab2:

        st.header("Create Account")

        new_username = st.text_input(
            "Choose Username",
            key="new_username"
        )

        new_password = st.text_input(
            "Choose Password",
            type="password",
            key="new_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="confirm_password"
        )

        if st.button(
            "Create Account",
            type="primary",
            use_container_width=True
        ):

            if not new_username or not new_password:

                st.warning(
                    "Please enter username and password."
                )

            elif new_password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            else:

                try:

                    result = create_user(
                        new_username,
                        new_password
                    )

                    if result:

                        st.success(
                            "Account created successfully. "
                            "You can now login."
                        )

                    else:

                        st.error(
                            "Username may already exist."
                        )

                except Exception as e:

                    st.error(
                        f"Account creation error: {str(e)}"
                    )


# =========================================================
# MAIN APPLICATION
# =========================================================

if not st.session_state.logged_in:

    login_page()

    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("💍 Matrimonial")

    st.caption(
        f"Logged in as: {st.session_state.username}"
    )

    st.divider()

    pages = [
        "🏠 Home",
        "👤 Profile Verification",
        "🤖 AI Face Verification",
        "🖼️ Image Authenticity",
        "📷 Liveness Check",
        "📄 Document Verification",
        "💬 Feedback Analysis",
        "💞 Matching",
        "📊 Dashboard"
    ]

    selected_page = st.radio(
        "Navigation",
        pages,
        index=pages.index(
            st.session_state.page
        )
        if st.session_state.page in pages
        else 0
    )

    st.session_state.page = selected_page

    st.divider()

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False
        st.session_state.username = ""

        reset_verification()

        st.rerun()


# =========================================================
# PAGE VARIABLE
# =========================================================

page = st.session_state.page


# =========================================================
# HOME
# =========================================================

if page == "🏠 Home":

    st.title(
        "💍 Matrimonial Verification System"
    )

    st.subheader(
        "Secure AI-powered matrimonial profile verification system"
    )

    st.write(
        """
        This system helps verify matrimonial profiles using
        multiple AI and verification modules.
        """
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.info(
            """
            ### 👤 Profile Verification

            Upload and register the matrimonial profile.
            """
        )

    with col2:

        st.info(
            """
            ### 🤖 AI Verification

            Compare faces and analyze image authenticity.
            """
        )

    with col3:

        st.info(
            """
            ### 📄 Document Verification

            Verify uploaded documents using OCR.
            """
        )

    st.divider()

    st.subheader(
        "Verification Modules"
    )

    modules = [
        "👤 Profile Photo",
        "🤖 Face Verification",
        "🖼️ AI / Deepfake Detection",
        "📷 Liveness Detection",
        "📄 Document Verification",
        "💬 Feedback Analysis"
    ]

    for module in modules:

        st.write(
            f"• {module}"
        )


# =========================================================
# PROFILE VERIFICATION
# =========================================================

elif page == "👤 Profile Verification":

    st.header(
        "👤 Profile Verification"
    )

    st.write(
        "Create your matrimonial profile and upload a profile photo."
    )

    st.divider()

    profile_name = st.text_input(
        "Full Name",
        value=st.session_state.profile_name
    )

    uploaded_photo = st.file_uploader(
        "Upload your profile photo",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp",
            "bmp"
        ],
        key="profile_photo_uploader"
    )

    if uploaded_photo is not None:

        try:

            image_bytes = uploaded_photo.getvalue()

            image_array = np.frombuffer(
                image_bytes,
                dtype=np.uint8
            )

            image = cv2.imdecode(
                image_array,
                cv2.IMREAD_COLOR
            )

            if image is None:

                st.error(
                    "The uploaded file could not be read as an image."
                )

            else:

                st.session_state.profile_photo = image
                st.session_state.profile_photo_name = (
                    uploaded_photo.name
                )

                st.image(
                    image,
                    channels="BGR",
                    caption=uploaded_photo.name,
                    width=300
                )

                st.success(
                    "Photo uploaded successfully."
                )

        except Exception as e:

            st.error(
                f"Photo upload error: {str(e)}"
            )

    if st.button(
        "💾 Save Profile",
        type="primary"
    ):

        if not profile_name.strip():

            st.warning(
                "Please enter your full name."
            )

        elif st.session_state.profile_photo is None:

            st.warning(
                "Please upload a profile photo."
            )

        else:

            st.session_state.profile_name = (
                profile_name.strip()
            )

            st.success(
                "Profile saved successfully."
            )

            st.info(
                "You can now continue with the AI verification modules."
            )


# =========================================================
# AI FACE VERIFICATION
# =========================================================

elif page == "🤖 AI Face Verification":

    st.header(
        "🤖 AI Face Verification"
    )

    st.write(
        """
        Compare the registered profile photo with another
        verification photo.
        """
    )

    if st.session_state.profile_photo is None:

        st.warning(
            "Please complete Profile Verification first."
        )

    else:

        st.subheader(
            "Registered Profile Photo"
        )

        st.image(
            st.session_state.profile_photo,
            channels="BGR",
            width=300
        )

        verification_photo = st.file_uploader(
            "Upload verification/selfie photo",
            type=[
                "jpg",
                "jpeg",
                "png",
                "webp",
                "bmp"
            ],
            key="face_verification_uploader"
        )

        if verification_photo is not None:

            try:

                verify_bytes = (
                    verification_photo.getvalue()
                )

                verify_array = np.frombuffer(
                    verify_bytes,
                    dtype=np.uint8
                )

                verify_image = cv2.imdecode(
                    verify_array,
                    cv2.IMREAD_COLOR
                )

                if verify_image is None:

                    st.error(
                        "Unable to read verification image."
                    )

                else:

                    st.image(
                        verify_image,
                        channels="BGR",
                        caption=verification_photo.name,
                        width=300
                    )

                    if st.button(
                        "🔍 Compare Faces",
                        type="primary"
                    ):

                        try:

                            result = compare_faces(
                                st.session_state.profile_photo,
                                verify_image
                            )

                            result = safe_result(
                                result
                            )

                            score = result.get(
                                "score",
                                result.get(
                                    "similarity",
                                    result.get(
                                        "confidence",
                                        0
                                    )
                                )
                            )

                            score = safe_number(
                                score
                            )

                            if score <= 1:

                                score = score * 100

                            score = round(
                                min(
                                    max(
                                        score,
                                        0
                                    ),
                                    100
                                ),
                                2
                            )

                            st.session_state.face_score = score

                            result_text = result.get(
                                "result",
                                result.get(
                                    "message",
                                    "Face comparison completed."
                                )
                            )

                            st.session_state.face_result = (
                                result_text
                            )

                            st.metric(
                                "Face Similarity",
                                f"{score}%"
                            )

                            st.success(
                                result_text
                            )

                        except Exception as e:

                            st.error(
                                f"Face verification error: {str(e)}"
                            )

        except Exception as e:

            st.error(
                f"Image processing error: {str(e)}"
            )


# =========================================================
# IMAGE AUTHENTICITY
# =========================================================

elif page == "🖼️ Image Authenticity":

    st.header(
        "🖼️ Image Authenticity / Deepfake Detection"
    )

    st.write(
        """
        Analyze an image for possible manipulation,
        AI generation, or suspicious visual patterns.
        """
    )

    uploaded_image = st.file_uploader(
        "Upload image for authenticity analysis",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp",
            "bmp"
        ],
        key="deepfake_uploader"
    )

    if uploaded_image is not None:

        try:

            image_bytes = uploaded_image.getvalue()

            image_array = np.frombuffer(
                image_bytes,
                dtype=np.uint8
            )

            image = cv2.imdecode(
                image_array,
                cv2.IMREAD_COLOR
            )

            if image is None:

                st.error(
                    "Unable to read image."
                )

            else:

                st.image(
                    image,
                    channels="BGR",
                    caption=uploaded_image.name,
                    width=400
                )

                if st.button(
                    "🔍 Analyze Image",
                    type="primary"
                ):

                    try:

                        result = analyze_image(
                            image
                        )

                        result = safe_result(
                            result
                        )

                        score = result.get(
                            "score",
                            result.get(
                                "risk_score",
                                result.get(
                                    "confidence",
                                    0
                                )
                            )
                        )

                        score = safe_number(
                            score
                        )

                        if score <= 1:

                            score = score * 100

                        score = round(
                            min(
                                max(
                                    score,
                                    0
                                ),
                                100
                            ),
                            2
                        )

                        st.session_state.deepfake_score = score

                        result_text = result.get(
                            "result",
                            result.get(
                                "message",
                                "Image analysis completed."
                            )
                        )

                        st.session_state.deepfake_result = (
                            result_text
                        )

                        st.metric(
                            "Image Risk Score",
                            f"{score}/100"
                        )

                        st.info(
                            result_text
                        )

                    except Exception as e:

                        st.error(
                            f"Image analysis error: {str(e)}"
                        )

        except Exception as e:

            st.error(
                f"Image processing error: {str(e)}"
            )


# =========================================================
# LIVENESS
# =========================================================

elif page == "📷 Liveness Check":

    st.header(
        "📷 Liveness / Anti-Spoofing Check"
    )

    st.write(
        """
        Upload a verification image for the liveness analysis.
        """
    )

    liveness_photo = st.file_uploader(
        "Upload liveness image",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp",
            "bmp"
        ],
        key="liveness_uploader"
    )

    if liveness_photo is not None:

        try:

            image_bytes = liveness_photo.getvalue()

            image_array = np.frombuffer(
                image_bytes,
                dtype=np.uint8
            )

            image = cv2.imdecode(
                image_array,
                cv2.IMREAD_COLOR
            )

            if image is None:

                st.error(
                    "Unable to read image."
                )

            else:

                st.image(
                    image,
                    channels="BGR",
                    caption=liveness_photo.name,
                    width=400
                )

                if st.button(
                    "📷 Check Liveness",
                    type="primary"
                ):

                    try:

                        result = analyze_liveness(
                            image
                        )

                        result = safe_result(
                            result
                        )

                        score = result.get(
                            "score",
                            result.get(
                                "liveness_score",
                                result.get(
                                    "confidence",
                                    0
                                )
                            )
                        )

                        score = safe_number(
                            score
                        )

                        if score <= 1:

                            score = score * 100

                        score = round(
                            min(
                                max(
                                    score,
                                    0
                                ),
                                100
                            ),
                            2
                        )

                        st.session_state.liveness_score = score

                        result_text = result.get(
                            "result",
                            result.get(
                                "message",
                                "Liveness analysis completed."
                            )
                        )

                        st.session_state.liveness_result = (
                            result_text
                        )

                        st.metric(
                            "Liveness Score",
                            f"{score}/100"
                        )

                        st.success(
                            result_text
                        )

                    except Exception as e:

                        st.error(
                            f"Liveness error: {str(e)}"
                        )

        except Exception as e:

            st.error(
                f"Image processing error: {str(e)}"
            )


# =========================================================
# DOCUMENT VERIFICATION
# =========================================================

elif page == "📄 Document Verification":

    st.header(
        "📄 Document Verification"
    )

    st.write(
        """
        Upload an identity document and extract text using OCR.
        """
    )

    tesseract_status = check_tesseract()

    if tesseract_status.get(
        "installed",
        False
    ):

        st.success(
            "Tesseract OCR is available."
        )

    else:

        st.warning(
            "Tesseract OCR is not available."
        )

    document = st.file_uploader(
        "Upload document",
        type=[
            "jpg",
            "jpeg",
            "png",
            "pdf"
        ],
        key="document_uploader"
    )

    if document is not None:

        st.write(
            f"**Selected file:** {document.name}"
        )

        if st.button(
            "📄 Verify Document",
            type="primary"
        ):

            try:

                result = analyze_document(
                    document
                )

                result = safe_result(
                    result,
                    "Document analysis completed."
                )

                document_result = result.get(
                    "result",
                    result.get(
                        "message",
                        "Document analysis completed."
                    )
                )

                name_match = result.get(
                    "name_match",
                    result.get(
                        "document_name_match",
                        None
                    )
                )

                st.session_state.document_result = (
                    document_result
                )

                st.session_state.document_name_match = (
                    name_match
                )

                st.success(
                    document_result
                )

                if name_match is not None:

                    st.write(
                        "**Document Name Match:** "
                        + (
                            "Yes"
                            if name_match
                            else "No"
                        )
                    )

            except Exception as e:

                st.error(
                    f"Document verification error: {str(e)}"
                )


# =========================================================
# FEEDBACK ANALYSIS
# =========================================================

elif page == "💬 Feedback Analysis":

    st.header(
        "💬 Feedback Analysis"
    )

    feedback = st.text_area(
        "Enter user feedback",
        height=150
    )

    if st.button(
        "Analyze Feedback",
        type="primary"
    ):

        if not feedback.strip():

            st.warning(
                "Please enter feedback."
            )

        else:

            try:

                result = analyze_feedback(
                    feedback
                )

                result = safe_result(
                    result,
                    "Feedback analysis completed."
                )

                score = result.get(
                    "score",
                    result.get(
                        "feedback_score",
                        0
                    )
                )

                score = safe_number(
                    score
                )

                score = round(
                    min(
                        max(
                            score,
                            0
                        ),
                        100
                    ),
                    2
                )

                category = result.get(
                    "category",
                    result.get(
                        "result",
                        "General"
                    )
                )

                message = result.get(
                    "message",
                    "Feedback analysis completed."
                )

                st.session_state.feedback_score = score

                st.session_state.feedback_result = (
                    category
                )

                st.metric(
                    "Feedback Score",
                    f"{score}/100"
                )

                st.write(
                    f"**Category:** {category}"
                )

                st.write(
                    message
                )

            except Exception as e:

                st.error(
                    f"Feedback analysis error: {str(e)}"
                )


# =========================================================
# MATCHING
# =========================================================

elif page == "💞 Matching":

    st.header(
        "💞 Matrimonial Profile Matching"
    )

    st.info(
        """
        The verification modules provide evidence about
        profile authenticity. Compatibility should be based
        on user-selected preferences rather than the AI
        verification score.
        """
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

            try:

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

            except Exception as e:

                st.error(
                    f"Unable to save verification: {str(e)}"
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

    try:

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

    except Exception as e:

        st.warning(
            f"Unable to load saved records: {str(e)}"
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
