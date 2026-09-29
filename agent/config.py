import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "profile.json")

def load_or_prompt_profile() -> dict:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)

    print("=== Complete Your Profile & Eligibility ===")
    profile = {
        "full_name": input("Full Name: ").strip(),
        "is_us_citizen": input("Are you a US Citizen/Permanent Resident? (yes/no): ").strip().lower() == "yes",
        "age": int(input("Age: ").strip() or "20"),
        "major": input("Major (e.g., Computer Science): ").strip(),
        "minor": input("Minor (e.g., Business): ").strip(),
        "expected_graduation": input("Expected Graduation (YYYY-MM, e.g., 2028-06): ").strip(),
        "target_window_end": "2028-09-30",
        "keywords": ["python", "ai", "product management", "software engineer", "data"]
    }

    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(profile, f, indent=2)
    return profile