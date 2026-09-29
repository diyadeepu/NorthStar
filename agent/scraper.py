from datetime import datetime

def is_eligible(posting: dict, profile: dict) -> bool:
    # 1. Citizenship check
    if posting.get("requires_us_citizenship", False) and not profile["is_us_citizen"]:
        return False

    # 2. Window check (Open now through September 2028)
    deadline = posting.get("deadline", "2028-09-30")
    if deadline > profile["target_window_end"]:
        return False

    # 3. Minimum age check
    if profile["age"] < posting.get("min_age", 18):
        return False

    # 4. Major alignment check
    target_majors = posting.get("eligible_majors", [])
    if target_majors:
        matched_major = any(
            m.lower() in profile["major"].lower() or m.lower() in profile["minor"].lower()
            for m in target_majors
        )
        if not matched_major:
            return False

    return True