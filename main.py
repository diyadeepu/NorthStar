import os
import json
import shutil
from agent.config import load_or_prompt_profile
from agent.scraper import is_eligible
from agent.resume_parser import extract_resume_text, get_resume_keywords

SAMPLE_POSTINGS = [
    {
        "id": "INT-001",
        "category": "internship",
        "title": "Software Engineering Intern - Summer 2027",
        "company": "Tech Innovations Corp",
        "deadline": "2026-11-15",
        "min_age": 18,
        "requires_us_citizenship": True,
        "eligible_majors": ["Computer Science", "Electrical Engineering"],
        "required_skills": ["python", "git"],
        "status": "Applied",
        "notes": "First-round technical assessment sent"
    },
    {
        "id": "INT-002",
        "category": "internship",
        "title": "AI Product Management Intern",
        "company": "NextGen Systems",
        "deadline": "2027-01-10",
        "min_age": 18,
        "requires_us_citizenship": False,
        "eligible_majors": ["Computer Science", "Business"],
        "required_skills": ["product management", "ai"],
        "status": "Accepted",
        "notes": "Offer letter received"
    },
    {
        "id": "PT-101",
        "category": "part_time",
        "title": "Campus AI Academic Mentor",
        "company": "University Learning Center",
        "deadline": "2026-10-01",
        "min_age": 18,
        "requires_us_citizenship": False,
        "eligible_majors": ["Computer Science"],
        "required_skills": ["python"],
        "status": "Applied",
        "notes": "Interview scheduled"
    },
    {
        "id": "SCH-201",
        "category": "scholarship",
        "title": "Undergraduate Women in STEM Leadership Grant",
        "company": "Pacific Tech Foundation",
        "deadline": "2027-03-01",
        "min_age": 18,
        "requires_us_citizenship": True,
        "eligible_majors": ["Computer Science"],
        "required_skills": [],
        "status": "Rejected",
        "notes": "Competitive pool, re-apply in 2027"
    }
]

def run_agent():
    # 1. Ensure Directories Exist
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    docs_dir = os.path.join(base_dir, "docs")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(docs_dir, exist_ok=True)

    # 2. Extract and Parse resume.pdf
    pdf_path = os.path.join(data_dir, "resume.pdf")
    try:
        resume_raw_text = extract_resume_text(pdf_path)
        extracted_skills = get_resume_keywords(resume_raw_text)
        print(f"Successfully parsed resume.pdf. Identified skills: {', '.join(extracted_skills)}")
    except FileNotFoundError as err:
        print(f"Execution halted: {err}")
        return

    # 3. Load or Prompt User Eligibility Profile
    profile = load_or_prompt_profile()
    profile["resume_skills"] = extracted_skills

    # 4. Filter Postings Based on Eligibility & Matching
    eligible_items = []
    for posting in SAMPLE_POSTINGS:
        if is_eligible(posting, profile):
            # Check skill overlap if requirements are defined
            req_skills = posting.get("required_skills", [])
            overlap = [s for s in req_skills if s in extracted_skills]
            posting["matched_skills"] = overlap
            eligible_items.append(posting)

    # 5. Populate Tracker Data
    tracker_file = os.path.join(data_dir, "tracker.json")
    if os.path.exists(tracker_file):
        with open(tracker_file, "r") as f:
            tracker = json.load(f)
        tracker["profile"] = profile
        tracker["items"] = eligible_items
    else:
        tracker = {
            "profile": profile,
            "items": eligible_items,
            "upcoming_radar": [
                {
                    "title": "Machine Learning Engineer Internship (Summer 2028)",
                    "type": "Internship",
                    "open_date": "August 2027",
                    "target_skills": ["PyTorch", "Distributed Systems", "SQL"]
                },
                {
                    "title": "Technical Product Manager Apprentice",
                    "type": "Part-Time",
                    "open_date": "January 2027",
                    "target_skills": ["Product Roadmapping", "A/B Testing", "System Architecture"]
                }
            ]
        }

    # Save local database
    with open(tracker_file, "w") as f:
        json.dump(tracker, f, indent=2)

    # 6. Mirror to docs/ for GitHub Pages
    docs_tracker_file = os.path.join(docs_dir, "tracker.json")
    shutil.copyfile(tracker_file, docs_tracker_file)
    print(f"Sync complete. {len(eligible_items)} verified postings written to docs/tracker.json.")

if __name__ == "__main__":
    run_agent()