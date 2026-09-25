import re


# =========================================================
# BEHAVIOR / FEEDBACK ANALYSIS
# =========================================================

def analyze_feedback(feedback_text):
    """
    Basic behavioral and feedback analysis.

    This is a simple rule-based screening component.
    It does NOT diagnose personality or intent.
    """

    if not feedback_text:

        return {
            "score": 50,
            "category": "No feedback",
            "positive_points": 0,
            "negative_points": 0,
            "message": "No feedback provided."
        }

    text = feedback_text.lower().strip()

    # Remove extra spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    positive_words = [
        "good",
        "great",
        "honest",
        "respect",
        "respectful",
        "kind",
        "friendly",
        "helpful",
        "clear",
        "polite",
        "positive",
        "genuine",
        "trust",
        "trusted",
        "reliable"
    ]

    negative_words = [
        "fake",
        "fraud",
        "scam",
        "rude",
        "abusive",
        "harassment",
        "cheat",
        "cheating",
        "dishonest",
        "threat",
        "threatening",
        "suspicious",
        "misleading",
        "problem",
        "bad"
    ]

    positive_points = 0
    negative_points = 0

    for word in positive_words:

        if word in text:

            positive_points += 1

    for word in negative_words:

        if word in text:

            negative_points += 1

    # Starting neutral score
    score = 50

    score += positive_points * 5
    score -= negative_points * 8

    # Keep score between 0 and 100
    score = max(
        0,
        min(
            100,
            score
        )
    )

    if score >= 70:

        category = "Positive feedback"

    elif score >= 40:

        category = "Neutral / mixed feedback"

    else:

        category = "Negative feedback"

    message = (
        "Feedback analyzed using basic "
        "keyword-based screening."
    )

    return {
        "score": score,
        "category": category,
        "positive_points": positive_points,
        "negative_points": negative_points,
        "message": message
    }


# =========================================================
# USER FEEDBACK SUMMARY
# =========================================================

def create_feedback_summary(
    feedback_list
):
    """
    Analyze multiple feedback entries.
    """

    if not feedback_list:

        return {
            "total_feedback": 0,
            "average_score": 0,
            "summary": "No feedback available."
        }

    results = []

    for feedback in feedback_list:

        result = analyze_feedback(
            feedback
        )

        results.append(
            result
        )

    total_score = sum(
        item["score"]
        for item in results
    )

    average_score = (
        total_score /
        len(results)
    )

    if average_score >= 70:

        summary = "Overall feedback is mostly positive."

    elif average_score >= 40:

        summary = "Overall feedback is mixed or neutral."

    else:

        summary = "Overall feedback contains negative indicators."

    return {
        "total_feedback": len(results),
        "average_score": round(
            average_score,
            2
        ),
        "summary": summary,
        "results": results
    }