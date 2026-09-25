import streamlit as st
import cv2
import numpy as np
import os
import json
from PIL import Image
from datetime import datetime
import hashlib


# =========================================================
# OPTIONAL OCR
# =========================================================

try:
    import pytesseract

    TESSERACT_AVAILABLE = True

    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

except Exception:
    TESSERACT_AVAILABLE = False


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Matrimonial Verification System",
    page_icon="💍",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================

st.title(
    "AI-Powered Matrimonial Photo Authenticity and Identity Verification System"
)

st.write(
    "AI-powered prototype for matrimonial profile verification, "
    "document checking, profile matching, feedback and recommendations."
)


# =========================================================
# FOLDERS
# =========================================================

os.makedirs("uploads", exist_ok=True)
os.makedirs("documents", exist_ok=True)
os.makedirs("reports", exist_ok=True)


# =========================================================
# SESSION STATE
# =========================================================

default_values = {

    "photo_verified": False,

    "photo_score": 0,

    "authenticity_score": 0,

    "document_verified": False,

    "document_text": "",

    "face_match_score": 0,

    "liveness_verified": False,

    "compatibility_score": 0,

    "selected_profile": None,

    "search_results": [],

    "verification_history": [],

    "liveness_active": False,

    "background_completed": False,

    "behavior_score": 0,

    "feedback_score": 0,

    "verification_gate_passed": False,

    "final_report": ""
}


for key, value in default_values.items():

    if key not in st.session_state:

        st.session_state[key] = value


# =========================================================
# HELPER FUNCTION
# =========================================================

def save_json(filename, data):

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


def load_json(filename):

    if os.path.exists(filename):

        try:

            with open(
                filename,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(file)

        except Exception:

            return []

    return []


# =========================================================
# USER PROFILE
# =========================================================

st.header("1. User Profile")

name = st.text_input(
    "Enter your name"
)

age = st.number_input(
    "Age",
    min_value=18,
    max_value=100,
    value=23
)

gender = st.selectbox(
    "Gender",
    [
        "Male",
        "Female",
        "Other"
    ]
)

location = st.text_input(
    "Location"
)

education = st.text_input(
    "Education"
)

profession = st.text_input(
    "Profession"
)

interests = st.text_input(
    "Interests",
    placeholder="Travel, Music, Reading"
)


# =========================================================
# MATCH PREFERENCES
# =========================================================

st.header("2. Match Preferences")

preferred_age = st.slider(
    "Preferred Age",
    18,
    60,
    (21, 30)
)

preferred_location = st.text_input(
    "Preferred Location"
)

preferred_education = st.text_input(
    "Preferred Education"
)

preferred_profession = st.text_input(
    "Preferred Profession"
)

preferred_interests = st.text_input(
    "Preferred Interests"
)


# =========================================================
# PROFILE PHOTO
# =========================================================

st.header("3. Profile Photo Verification")

photo = st.file_uploader(
    "Upload your profile photo",
    type=["jpg", "jpeg", "png"],
    key="profile_photo"
)


if photo:

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

    if image is not None:

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades
            + "haarcascade_frontalface_default.xml"
        )

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5
        )

        for (
            x,
            y,
            w,
            h
        ) in faces:

            cv2.rectangle(
                image,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

        image_rgb = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        st.image(
            image_rgb,
            caption="Face Detection Result",
            width=450
        )

        if len(faces) == 1:

            st.success(
                "One face detected."
            )

            height, width = image.shape[:2]

            sharpness = cv2.Laplacian(
                gray,
                cv2.CV_64F
            ).var()

            # Resolution score
            if width >= 300 and height >= 300:

                resolution_score = 50

            else:

                resolution_score = 20

            # Sharpness score
            if sharpness >= 100:

                sharpness_score = 50

            else:

                sharpness_score = 20

            photo_score = (
                resolution_score
                + sharpness_score
            )

            st.session_state.photo_score = photo_score

            st.progress(
                photo_score / 100
            )

            st.write(
                f"Photo Quality Score: {photo_score}%"
            )

            if photo_score >= 70:

                st.session_state.photo_verified = True

                st.success(
                    "Photo quality verification passed."
                )

            else:

                st.session_state.photo_verified = False

                st.warning(
                    "Photo quality needs improvement."
                )

        elif len(faces) > 1:

            st.session_state.photo_verified = False

            st.warning(
                "Multiple faces detected. "
                "Please upload a single-person profile photo."
            )

        else:

            st.session_state.photo_verified = False

            st.warning(
                "No face detected."
            )

    else:

        st.error(
            "Unable to read the image."
        )


# =========================================================
# STEP 38
# PHOTO AUTHENTICITY ANALYSIS
# =========================================================

st.header("4. Photo Authenticity Analysis")

st.write(
    "This prototype checks basic image properties that may indicate "
    "whether a profile image needs additional review."
)

if photo and st.session_state.photo_verified:

    if st.button(
        "🔍 Analyze Photo Authenticity",
        key="authenticity_button"
    ):

        image_array = np.asarray(
            bytearray(
                photo.getvalue()
            ),
            dtype=np.uint8
        )

        authenticity_image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        if authenticity_image is not None:

            height, width = authenticity_image.shape[:2]

            gray_auth = cv2.cvtColor(
                authenticity_image,
                cv2.COLOR_BGR2GRAY
            )

            sharpness = cv2.Laplacian(
                gray_auth,
                cv2.CV_64F
            ).var()

            file_size_kb = (
                photo.size / 1024
            )

            authenticity_score = 0

            # Resolution
            if width >= 500 and height >= 500:

                authenticity_score += 30

            elif width >= 300 and height >= 300:

                authenticity_score += 20

            # Image sharpness
            if sharpness >= 150:

                authenticity_score += 30

            elif sharpness >= 70:

                authenticity_score += 20

            # File size
            if file_size_kb >= 50:

                authenticity_score += 20

            # Face presence
            if st.session_state.photo_verified:

                authenticity_score += 20

            st.session_state.authenticity_score = (
                authenticity_score
            )

            st.progress(
                authenticity_score / 100
            )

            st.write(
                f"Basic Authenticity Analysis Score: "
                f"{authenticity_score}%"
            )

            if authenticity_score >= 70:

                st.success(
                    "Image passed the basic authenticity screening."
                )

            else:

                st.warning(
                    "Image should receive additional review."
                )

            st.caption(
                "This is a prototype screening score. "
                "It does not prove that an image is genuine or AI-free."
            )


# =========================================================
# DOCUMENT VERIFICATION
# =========================================================

st.header("5. Document Verification")

document = st.file_uploader(
    "Upload Identity Document",
    type=["jpg", "jpeg", "png"],
    key="identity_document"
)


if document:

    document_path = os.path.join(
        "documents",
        document.name
    )

    with open(
        document_path,
        "wb"
    ) as file:

        file.write(
            document.getbuffer()
        )

    document_image = Image.open(
        document
    )

    st.image(
        document_image,
        caption="Uploaded Identity Document",
        width=500
    )

    if st.button(
        "Verify Document",
        key="verify_document"
    ):

        st.session_state.document_verified = True

        st.success(
            "Document uploaded and basic verification completed."
        )

        if TESSERACT_AVAILABLE:

            try:

                extracted_text = pytesseract.image_to_string(
                    document_image
                )

                st.session_state.document_text = (
                    extracted_text
                )

                if extracted_text.strip():

                    st.text_area(
                        "Extracted Document Information",
                        extracted_text,
                        height=200
                    )

                else:

                    st.warning(
                        "No readable text detected."
                    )

            except Exception as error:

                st.warning(
                    f"OCR error: {error}"
                )

        else:

            st.info(
                "Tesseract OCR is not installed. "
                "Basic document upload still works."
            )

        st.caption(
            "Document upload/OCR does not by itself prove legal document authenticity."
        )


# =========================================================
# STEP 39
# DOCUMENT INFORMATION
# =========================================================

st.header("6. Document Information")

if st.session_state.document_text.strip():

    document_text_lower = (
        st.session_state.document_text.lower()
    )

    detected_fields = []

    keywords = {

        "Name": ["name", "surname"],

        "Date": [
            "date",
            "dob",
            "birth"
        ],

        "Address": [
            "address",
            "residential"
        ],

        "ID": [
            "id",
            "identity",
            "number"
        ]
    }

    for field, words in keywords.items():

        for word in words:

            if word in document_text_lower:

                detected_fields.append(
                    field
                )

                break

    if detected_fields:

        st.write(
            "Possible information categories detected:"
        )

        for field in detected_fields:

            st.write(
                f"✓ {field}"
            )

    else:

        st.info(
            "No standard information categories detected."
        )

else:

    st.info(
        "Upload and process a document to see extracted information."
    )


# =========================================================
# FACE MATCH
# =========================================================

st.header("7. Face Match Verification")

verification_photo = st.file_uploader(
    "Upload second verification photo",
    type=["jpg", "jpeg", "png"],
    key="verification_photo"
)


if verification_photo and photo:

    if st.button(
        "Compare Faces",
        key="compare_faces"
    ):

        first_bytes = np.asarray(
            bytearray(
                photo.getvalue()
            ),
            dtype=np.uint8
        )

        second_bytes = np.asarray(
            bytearray(
                verification_photo.getvalue()
            ),
            dtype=np.uint8
        )

        first_image = cv2.imdecode(
            first_bytes,
            cv2.IMREAD_GRAYSCALE
        )

        second_image = cv2.imdecode(
            second_bytes,
            cv2.IMREAD_GRAYSCALE
        )

        if (
            first_image is not None
            and second_image is not None
        ):

            first_image = cv2.resize(
                first_image,
                (200, 200)
            )

            second_image = cv2.resize(
                second_image,
                (200, 200)
            )

            difference = cv2.absdiff(
                first_image,
                second_image
            )

            mean_difference = np.mean(
                difference
            )

            similarity = max(
                0,
                100 - mean_difference
            )

            similarity = round(
                similarity,
                2
            )

            st.session_state.face_match_score = (
                similarity
            )

            st.progress(
                similarity / 100
            )

            st.write(
                f"Basic Image Similarity: {similarity}%"
            )

            if similarity >= 70:

                st.success(
                    "Basic image match passed."
                )

            else:

                st.warning(
                    "Low image similarity."
                )

            st.caption(
                "Prototype similarity check only. "
                "Later this can be replaced by ArcFace/InsightFace."
            )


# =========================================================
# LIVENESS
# =========================================================

st.header("8. Basic Liveness Verification")

if not st.session_state.liveness_active:

    if st.button(
        "▶ Start Liveness Verification",
        key="start_liveness"
    ):

        st.session_state.liveness_active = True

        st.rerun()


if st.session_state.liveness_active:

    st.info(
        "Camera verification is active."
    )

    camera_image = st.camera_input(
        "Take a live verification photo",
        key="liveness_camera"
    )

    if st.button(
        "⏹ Stop Liveness Verification",
        key="stop_liveness"
    ):

        st.session_state.liveness_active = False

        st.session_state.liveness_verified = False

        st.rerun()

    if camera_image:

        camera_bytes = np.asarray(
            bytearray(
                camera_image.getvalue()
            ),
            dtype=np.uint8
        )

        camera_frame = cv2.imdecode(
            camera_bytes,
            cv2.IMREAD_COLOR
        )

        if camera_frame is not None:

            camera_gray = cv2.cvtColor(
                camera_frame,
                cv2.COLOR_BGR2GRAY
            )

            cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades
                + "haarcascade_frontalface_default.xml"
            )

            live_faces = cascade.detectMultiScale(
                camera_gray,
                scaleFactor=1.1,
                minNeighbors=5
            )

            if len(live_faces) == 1:

                st.session_state.liveness_verified = True

                st.success(
                    "Live face detected."
                )

            elif len(live_faces) > 1:

                st.session_state.liveness_verified = False

                st.warning(
                    "Multiple faces detected."
                )

            else:

                st.session_state.liveness_verified = False

                st.warning(
                    "No face detected."
                )


# =========================================================
# STEP 40
# BACKGROUND INFORMATION
# =========================================================

st.header("9. Background Information")

st.info(
    "This section uses information voluntarily provided by the profile owner "
    "or verified through appropriate authorized sources. "
    "It does not perform a secret investigation."
)

employment_status = st.selectbox(
    "Employment Status",
    [
        "Not Provided",
        "Employed",
        "Self Employed",
        "Student",
        "Other"
    ]
)

years_experience = st.number_input(
    "Years of Experience",
    min_value=0,
    max_value=50,
    value=0
)

city_history = st.text_input(
    "Current/Previous City Information"
)

education_verified = st.checkbox(
    "Education information provided for verification"
)

employment_verified = st.checkbox(
    "Employment information provided for verification"
)

reference_available = st.checkbox(
    "Reference/contact information voluntarily provided"
)

if st.button(
    "Save Background Information",
    key="save_background"
):

    st.session_state.background_completed = True

    st.success(
        "Background information saved for this prototype profile."
    )


# =========================================================
# STEP 41
# BEHAVIORAL PROFILE
# =========================================================

st.header("10. Behavioral Profile")

st.write(
    "Behavioral information is based on self-description and feedback. "
    "It should not be treated as a psychological diagnosis."
)

communication = st.slider(
    "Communication Preference",
    1,
    5,
    3
)

respectfulness = st.slider(
    "Respectfulness",
    1,
    5,
    3
)

reliability = st.slider(
    "Reliability",
    1,
    5,
    3
)

social_nature = st.slider(
    "Social Nature",
    1,
    5,
    3
)

family_orientation = st.slider(
    "Family Orientation",
    1,
    5,
    3
)

behavior_score = round(
    (
        communication
        + respectfulness
        + reliability
        + social_nature
        + family_orientation
    ) / 25 * 100,
    2
)

st.session_state.behavior_score = behavior_score

st.progress(
    behavior_score / 100
)

st.write(
    f"Self/feedback-based behavioral profile score: "
    f"{behavior_score}%"
)

st.caption(
    "This score represents the entered questionnaire values only; "
    "it is not an objective measurement of personality."
)


# =========================================================
# SAMPLE PROFILES
# =========================================================

profiles = [

    {
        "name": "Priya",
        "age": 24,
        "gender": "Female",
        "location": "Pune",
        "education": "B.Tech",
        "profession": "Software Engineer",
        "interests": "Travel, Music, Reading",
        "about": "Interested in technology, travel and reading."
    },

    {
        "name": "Sneha",
        "age": 26,
        "gender": "Female",
        "location": "Mumbai",
        "education": "MBA",
        "profession": "Business Analyst",
        "interests": "Travel, Movies, Music",
        "about": "Enjoys travelling, movies and music."
    },

    {
        "name": "Anjali",
        "age": 23,
        "gender": "Female",
        "location": "Pune",
        "education": "B.E",
        "profession": "Data Analyst",
        "interests": "Technology, Reading, Travel",
        "about": "Interested in data, technology and travel."
    },

    {
        "name": "Neha",
        "age": 27,
        "gender": "Female",
        "location": "Nashik",
        "education": "MCA",
        "profession": "Software Developer",
        "interests": "Technology, Travel, Music",
        "about": "Enjoys technology and travelling."
    }
]


# =========================================================
# COMPATIBILITY FUNCTION
# =========================================================

def calculate_compatibility(
    user_location,
    user_education,
    user_profession,
    user_interests,
    profile
):

    score = 0

    reasons = []

    if (
        profile["age"]
        >= preferred_age[0]
        and
        profile["age"]
        <= preferred_age[1]
    ):

        score += 25

        reasons.append(
            "Age matches preferred range"
        )

    if user_location.strip():

        if (
            user_location.lower()
            ==
            profile["location"].lower()
        ):

            score += 20

            reasons.append(
                "Same location"
            )

    if user_education.strip():

        if (
            user_education.lower()
            in
            profile["education"].lower()
        ):

            score += 15

            reasons.append(
                "Education compatibility"
            )

    if user_profession.strip():

        if (
            user_profession.lower()
            in
            profile["profession"].lower()
        ):

            score += 15

            reasons.append(
                "Profession compatibility"
            )

    user_interest_list = [
        item.strip().lower()
        for item in user_interests.split(",")
        if item.strip()
    ]

    profile_interest_list = [
        item.strip().lower()
        for item in profile["interests"].split(",")
        if item.strip()
    ]

    common = set(
        user_interest_list
    ).intersection(
        set(profile_interest_list)
    )

    if len(common) > 0:

        interest_score = min(
            25,
            len(common) * 10
        )

        score += interest_score

        reasons.append(
            "Common interests: "
            + ", ".join(common)
        )

    return score, reasons


# =========================================================
# PROFILE SEARCH
# =========================================================

st.header("11. Profile Search")

search_age = st.slider(
    "Search Age",
    18,
    60,
    (21, 30),
    key="search_age"
)

search_location = st.text_input(
    "Search Location",
    key="search_location"
)

search_education = st.text_input(
    "Search Education",
    key="search_education"
)

search_profession = st.text_input(
    "Search Profession",
    key="search_profession"
)


if st.button(
    "🔎 Search Profiles",
    key="search_profiles"
):

    results = []

    for profile in profiles:

        age_match = (
            search_age[0]
            <= profile["age"]
            <= search_age[1]
        )

        location_match = True

        if search_location.strip():

            location_match = (
                search_location.lower()
                in profile["location"].lower()
            )

        education_match = True

        if search_education.strip():

            education_match = (
                search_education.lower()
                in profile["education"].lower()
            )

        profession_match = True

        if search_profession.strip():

            profession_match = (
                search_profession.lower()
                in profile["profession"].lower()
            )

        if (
            age_match
            and location_match
            and education_match
            and profession_match
        ):

            results.append(profile)

    st.session_state.search_results = results


# =========================================================
# PROFILE DETAILS
# =========================================================

st.header("12. Profile Details")

if len(
    st.session_state.search_results
) > 0:

    selected_name = st.selectbox(
        "Select Profile",
        [
            item["name"]
            for item in st.session_state.search_results
        ]
    )

    selected_profile = next(
        item
        for item in profiles
        if item["name"] == selected_name
    )

    st.session_state.selected_profile = (
        selected_profile
    )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            selected_profile["name"]
        )

        st.write(
            f"Age: {selected_profile['age']}"
        )

        st.write(
            f"Gender: {selected_profile['gender']}"
        )

        st.write(
            f"Location: {selected_profile['location']}"
        )

    with col2:

        st.write(
            f"Education: {selected_profile['education']}"
        )

        st.write(
            f"Profession: {selected_profile['profession']}"
        )

        st.write(
            f"Interests: {selected_profile['interests']}"
        )

    st.write(
        f"About: {selected_profile['about']}"
    )

else:

    st.info(
        "Search for profiles first."
    )


# =========================================================
# STEP 42
# BEHAVIORAL FEEDBACK
# =========================================================

st.header("13. Real User Feedback")

feedback_file = "feedback.json"

feedback_data = load_json(
    feedback_file
)

feedback_person = st.selectbox(
    "Select Profile",
    [
        profile["name"]
        for profile in profiles
    ],
    key="feedback_person"
)

feedback_rating = st.slider(
    "Experience Rating",
    1,
    5,
    5,
    key="feedback_rating"
)

feedback_text = st.text_area(
    "Share your experience",
    placeholder=(
        "Example: I interacted with this person and "
        "found the communication respectful."
    )
)


if st.button(
    "Submit Feedback",
    key="submit_feedback"
):

    if feedback_text.strip():

        new_feedback = {

            "profile": feedback_person,

            "rating": feedback_rating,

            "feedback": feedback_text,

            "date": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }

        feedback_data.append(
            new_feedback
        )

        save_json(
            feedback_file,
            feedback_data
        )

        st.success(
            "Feedback saved successfully."
        )

    else:

        st.warning(
            "Please enter feedback."
        )


# =========================================================
# FEEDBACK SUMMARY
# =========================================================

st.header("14. Feedback Summary")

selected_feedback = [
    item
    for item in feedback_data
    if (
        st.session_state.selected_profile
        and
        item["profile"]
        ==
        st.session_state.selected_profile["name"]
    )
]


if selected_feedback:

    average_feedback = sum(
        item["rating"]
        for item in selected_feedback
    ) / len(selected_feedback)

    st.session_state.feedback_score = round(
        average_feedback / 5 * 100,
        2
    )

    st.write(
        f"Average Feedback Rating: "
        f"{average_feedback:.1f}/5"
    )

    st.progress(
        average_feedback / 5
    )

    for item in selected_feedback:

        st.write(
            f"⭐ {item['rating']}/5"
        )

        st.write(
            item["feedback"]
        )

        st.caption(
            item["date"]
        )

else:

    st.info(
        "No feedback available for the selected profile."
    )


# =========================================================
# STEP 43
# VERIFICATION GATE
# =========================================================

st.header("15. Verification Before Matching")

st.write(
    "The system checks whether enough verification information "
    "is available before presenting the final recommendation."
)

verification_points = 0

if st.session_state.photo_verified:

    verification_points += 20

if st.session_state.authenticity_score >= 60:

    verification_points += 20

if st.session_state.document_verified:

    verification_points += 20

if st.session_state.liveness_verified:

    verification_points += 20

if st.session_state.background_completed:

    verification_points += 20


st.progress(
    verification_points / 100
)

st.write(
    f"Verification Readiness: "
    f"{verification_points}%"
)


if verification_points >= 60:

    st.session_state.verification_gate_passed = True

    st.success(
        "✅ Verification requirements are sufficiently completed "
        "for this prototype."
    )

else:

    st.session_state.verification_gate_passed = False

    st.warning(
        "⚠️ Complete more verification steps before relying "
        "on the matching result."
    )


# =========================================================
# STEP 44
# ADVANCED RECOMMENDATION
# =========================================================

st.header("16. AI-Based Profile Recommendation")

recommendations = []

for profile in profiles:

    compatibility, reasons = calculate_compatibility(
        location,
        education,
        profession,
        interests,
        profile
    )

    recommendations.append(
        {
            "profile": profile,
            "score": compatibility,
            "reasons": reasons
        }
    )


recommendations.sort(
    key=lambda x: x["score"],
    reverse=True
)


if st.session_state.verification_gate_passed:

    st.success(
        "Profile recommendations are available."
    )

    for item in recommendations:

        profile = item["profile"]

        score = item["score"]

        reasons = item["reasons"]

        with st.expander(
            f"💍 {profile['name']} — "
            f"{score}% compatibility"
        ):

            st.write(
                f"Age: {profile['age']}"
            )

            st.write(
                f"Location: {profile['location']}"
            )

            st.write(
                f"Education: {profile['education']}"
            )

            st.write(
                f"Profession: {profile['profession']}"
            )

            st.write(
                f"Interests: {profile['interests']}"
            )

            st.write(
                "Why this profile was suggested:"
            )

            if reasons:

                for reason in reasons:

                    st.write(
                        f"✓ {reason}"
                    )

            else:

                st.write(
                    "Limited matching information."
                )

else:

    st.info(
        "Complete the verification steps above "
        "before using the final recommendation."
    )


# =========================================================
# STEP 45
# FINAL COMPREHENSIVE REPORT
# =========================================================

st.header("17. Final Verification & Matching Report")

if st.button(
    "📋 Generate Final Report",
    key="generate_report"
):

    report_name = (
        name
        if name.strip()
        else "Not Provided"
    )

    report = f"""
MATRIMONIAL VERIFICATION SYSTEM
================================

USER PROFILE
------------
Name: {report_name}
Age: {age}
Gender: {gender}
Location: {location}
Education: {education}
Profession: {profession}
Interests: {interests}

PHOTO VERIFICATION
------------------
Photo Quality Score: {st.session_state.photo_score}%
Authenticity Screening Score: {st.session_state.authenticity_score}%
Face Match Score: {st.session_state.face_match_score}%
Liveness Verified: {st.session_state.liveness_verified}

DOCUMENT VERIFICATION
---------------------
Document Uploaded: {st.session_state.document_verified}

BACKGROUND INFORMATION
----------------------
Background Information Completed: {st.session_state.background_completed}
Employment Status: {employment_status}
Years of Experience: {years_experience}
Education Information Provided: {education_verified}
Employment Information Provided: {employment_verified}
Reference Information Provided: {reference_available}

BEHAVIORAL PROFILE
------------------
Behavioral Questionnaire Score: {st.session_state.behavior_score}%

MATCHING
--------
Compatibility Score: {st.session_state.compatibility_score}%

FEEDBACK
--------
Feedback Score: {st.session_state.feedback_score}%

VERIFICATION READINESS
----------------------
Verification Readiness: {verification_points}%
Verification Gate Passed: {st.session_state.verification_gate_passed}

REPORT GENERATED
----------------
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

NOTE
----
This is a college-project prototype.
The verification and matching results should not be treated
as definitive proof of identity, character, compatibility,
or suitability.
"""

    st.session_state.final_report = report

    st.text_area(
        "Final Report",
        report,
        height=600
    )


# =========================================================
# STEP 46
# DOWNLOAD REPORT
# =========================================================

st.header("18. Download Report")

if st.session_state.final_report:

    report_filename = (
        "matrimonial_verification_report.txt"
    )

    st.download_button(
        label="⬇️ Download Verification Report",
        data=st.session_state.final_report,
        file_name=report_filename,
        mime="text/plain"
    )

else:

    st.info(
        "Generate the final report first."
    )


# =========================================================
# STEP 47
# DASHBOARD
# =========================================================

st.header("19. Project Dashboard")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Photo Score",
        f"{st.session_state.photo_score}%"
    )

with col2:

    st.metric(
        "Authenticity",
        f"{st.session_state.authenticity_score}%"
    )

with col3:

    st.metric(
        "Face Match",
        f"{st.session_state.face_match_score}%"
    )

with col4:

    st.metric(
        "Compatibility",
        f"{st.session_state.compatibility_score}%"
    )


st.write("---")


# =========================================================
# VERIFICATION BADGE
# =========================================================

st.header("20. Profile Verification Badge")

if verification_points >= 80:

    st.success(
        "🟢 HIGH VERIFICATION COMPLETION"
    )

elif verification_points >= 60:

    st.warning(
        "🟡 PARTIAL VERIFICATION COMPLETION"
    )

else:

    st.info(
        "🔴 VERIFICATION INCOMPLETE"
    )


# =========================================================
# PROJECT STATUS
# =========================================================

st.header("21. Project Module Status")

modules = {

    "Profile Information": bool(name.strip()),

    "Photo Verification": (
        st.session_state.photo_verified
    ),

    "Photo Authenticity Screening": (
        st.session_state.authenticity_score > 0
    ),

    "Document Verification": (
        st.session_state.document_verified
    ),

    "Face Match": (
        st.session_state.face_match_score > 0
    ),

    "Liveness": (
        st.session_state.liveness_verified
    ),

    "Background Information": (
        st.session_state.background_completed
    ),

    "Behavioral Model": (
        st.session_state.behavior_score > 0
    ),

    "Feedback System": (
        len(feedback_data) > 0
    ),

    "Profile Matching": (
        len(recommendations) > 0
    ),

    "Final Report": (
        bool(st.session_state.final_report)
    )
}


for module, status in modules.items():

    if status:

        st.write(
            f"✅ {module}"
        )

    else:

        st.write(
            f"⏳ {module}"
        )


# =========================================================
# FINAL NOTE
# =========================================================

st.write("---")

st.info(
    "This application is a college-project prototype. "
    "Some modules currently use rule-based or basic computer-vision "
    "methods. Production deployment would require stronger biometric "
    "verification, AI-generated-image detection, anti-spoofing, "
    "secure document verification, privacy controls, consent and "
    "appropriate data protection."
)