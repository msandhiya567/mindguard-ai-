"""
MindGuard AI - Recommendation Service
========================================
Simple rule-based recommendations based on assessment answers and the
predicted risk level. These are general digital well-being suggestions,
NOT medical treatment advice.
"""


def generate_recommendations(answer: dict, risk_level: str) -> list[dict]:
    """
    answer: dict with AssessmentAnswer fields
    risk_level: "Low" / "Medium" / "High"

    Returns a list of {"category": ..., "text": ...} dicts.
    """
    recs = []

    # --- Usage-based ---
    if answer["avg_daily_usage_hours"] >= 6:
        recs.append({
            "category": "usage",
            "text": "Your daily social media usage is quite high. Try setting app "
                    "time limits and taking short screen breaks every hour.",
        })
    elif answer["avg_daily_usage_hours"] >= 3:
        recs.append({
            "category": "usage",
            "text": "Consider tracking your daily usage for a week to build "
                    "awareness of your habits.",
        })

    # --- Sleep-based ---
    if answer["sleep_hours_per_night"] < 6:
        recs.append({
            "category": "sleep",
            "text": "Your sleep hours are on the lower side. Try setting a "
                    "consistent bedtime and avoiding screens 30 minutes before sleep.",
        })

    # --- Academic impact ---
    if answer["affects_academic_performance"].strip().lower() == "yes":
        recs.append({
            "category": "academic",
            "text": "Since social media is affecting your academic performance, "
                    "try using focus/distraction-blocking apps during study hours.",
        })

    # --- Conflicts ---
    if answer["conflicts_over_social_media"] >= 3:
        recs.append({
            "category": "relationships",
            "text": "You've reported frequent conflicts related to social media. "
                    "Consider setting healthier boundaries around usage in relationships.",
        })

    # --- Mental health score (assume lower = worse, adjust if your scale is reversed) ---
    if answer["mental_health_score"] <= 4:
        recs.append({
            "category": "mental_health",
            "text": "Your self-reported mental health score is on the lower side. "
                    "Consider talking to a counselor or trusted person about how you're feeling.",
        })

    # --- General fallback based on risk level ---
    if risk_level == "High" and not recs:
        recs.append({
            "category": "general",
            "text": "Your overall risk signal is high. Consider a digital detox "
                    "day this week and reflect on your social media habits.",
        })
    elif risk_level == "Low":
        recs.append({
            "category": "general",
            "text": "Your digital well-being signal looks healthy. Keep maintaining "
                    "your current balance of usage, sleep, and offline activities.",
        })

    return recs