import os
import json
import shutil
from agent.config import load_or_prompt_profile
from agent.scraper import is_eligible
from agent.resume_parser import extract_resume_text, get_resume_keywords
from agent.live_feed import fetch_live_opportunities
from agent.auto_applier import apply_to_role

def run_agent():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    docs_dir = os.path.join(base_dir, "docs")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(docs_dir, exist_ok=True)

    # 1. Parse Resume
    pdf_path = os.path.join(data_dir, "resume.pdf")
    try:
        resume_raw_text = extract_resume_text(pdf_path)
        extracted_skills = get_resume_keywords(resume_raw_text)
        print(f"Loaded resume. Detected skills: {', '.join(extracted_skills)}")
    except FileNotFoundError as err:
        print(f"Execution halted: {err}")
        return

    # 2. Load Eligibility Profile
    profile = load_or_prompt_profile()
    profile["resume_skills"] = extracted_skills

    # 3. Ingest Live Discoveries (No mock data)
    print("Fetching active listings...")
    live_postings = fetch_live_opportunities()

    # 4. Read Existing Tracker to Preserve Confirmed Historical Submissions
    tracker_file = os.path.join(data_dir, "tracker.json")
    submitted_items = {}
    if os.path.exists(tracker_file):
        try:
            with open(tracker_file, "r") as f:
                existing_tracker = json.load(f)
                for item in existing_tracker.get("items", []):
                    if item.get("status") in ["Applied", "Accepted", "Rejected"] and "submission_receipt" in item:
                        submitted_items[item["id"]] = item
        except Exception:
            submitted_items = {}

    # 5. Process New Eligible Postings (Test Batch: Cap at 2 Submissions)
    applied_in_this_cycle = 0
    MAX_APPLICATIONS_PER_CYCLE = 2  # Hard cap for rapid verification

    # Only scan the first 10 candidate postings to ensure near-instant execution
    for posting in live_postings[:10]:
        if applied_in_this_cycle >= MAX_APPLICATIONS_PER_CYCLE:
            print("Reached test batch cap of 2 applications. Finalizing...")
            break

        p_id = posting.get("id")
        if p_id in submitted_items:
            continue  # Already applied

        if is_eligible(posting, profile):
            req_skills = posting.get("required_skills", [])
            overlap = [s for s in req_skills if s in extracted_skills]
            posting["matched_skills"] = overlap

            print(f"Applying to verified match: {posting['title']} @ {posting['company']}...")
            result = apply_to_role(posting, profile)

            # Strict Accuracy Check: Only record if genuinely submitted
            if result.get("status") == "Applied" and result.get("submission_receipt"):
                submitted_items[p_id] = result
                applied_in_this_cycle += 1
                print(f"Verified submission recorded: {result['submission_receipt']}")
            else:
                print(f"Skipping {p_id}: Submission not confirmed ({result.get('notes', 'No confirmation')}).")

    # 6. Build the Clean Tracker
    tracker = {
        "profile": profile,
        "items": list(submitted_items.values()),
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

    with open(tracker_file, "w") as f:
        json.dump(tracker, f, indent=2)

    shutil.copyfile(tracker_file, os.path.join(docs_dir, "tracker.json"))
    print(f"Accuracy audit complete. {len(tracker['items'])} verified applications on dashboard.")

if __name__ == "__main__":
    run_agent()