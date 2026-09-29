import os
import json
import resend
from datetime import datetime

TRACKER_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "tracker.json")
TARGET_EMAIL = "maildiyadeepu@gmail.com"

resend.api_key = os.environ.get("RESEND_API_KEY")

def send_digest():
    if not os.path.exists(TRACKER_PATH):
        print("Tracker file missing. Run main.py first.")
        return

    with open(TRACKER_PATH, "r") as f:
        tracker = json.load(f)

    items = tracker.get("items", [])
    now_str = datetime.now().strftime("%B %d, %Y - %I:%M %p")

    # Build the HTML status table
    table_rows = ""
    for item in items:
        status_color = "#0A8B8F"
        if item.get("status") == "Accepted":
            status_color = "#10B981"
        elif item.get("status") == "Rejected":
            status_color = "#EF4444"

        table_rows += f"""
        <tr style="border-bottom: 1px solid #D8ECE9;">
            <td style="padding: 10px 12px;"><strong>{item.get('title')}</strong><br><span style="color: #5E7A7D; font-size: 12px;">{item.get('company')}</span></td>
            <td style="padding: 10px 12px; text-transform: capitalize;">{item.get('category', '').replace('_', ' ')}</td>
            <td style="padding: 10px 12px;"><span style="color: {status_color}; font-weight: 600;">{item.get('status')}</span></td>
            <td style="padding: 10px 12px; font-size: 13px;">{item.get('notes', '—')}</td>
        </tr>
        """

    html_body = f"""
    <html>
    <body style="font-family: -apple-system, sans-serif; background-color: #FAFDFF; color: #1C3336; padding: 20px;">
        <div style="max-width: 650px; margin: 0 auto; background: #FFFFFF; border: 1px solid #D8ECE9; border-radius: 12px; padding: 24px;">
            <h2 style="color: #005A60; margin-top: 0;">NorthStar Application Update</h2>
            <p style="color: #5E7A7D; font-size: 14px;">Snapshot recorded at <strong>{now_str}</strong></p>
            <table style="width: 100%; border-collapse: collapse; margin-top: 16px; font-size: 14px; text-align: left;">
                <thead>
                    <tr style="background: #E0F9F6; color: #005A60;">
                        <th style="padding: 10px 12px;">Role</th>
                        <th style="padding: 10px 12px;">Category</th>
                        <th style="padding: 10px 12px;">Status</th>
                        <th style="padding: 10px 12px;">Notes</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

    try:
        response = resend.Emails.send({
            "from": "NorthStar <onboarding@resend.dev>",
            "to": TARGET_EMAIL,
            "subject": f"NorthStar Pipeline Update - {now_str}",
            "html": html_body
        })
        print(f"Update email delivered to {TARGET_EMAIL}. ID: {response['id']}")
    except Exception as e:
        print(f"Delivery failed: {e}")

if __name__ == "__main__":
    send_digest()