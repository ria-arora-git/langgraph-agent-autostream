import json
import datetime
from typing import Optional


_captured_leads = []


def mock_lead_capture(name: str, email: str, platform: str) -> dict:
    if not name or not email or not platform:
        return {
            "status": "error",
            "message": "All fields (name, email, platform) are required."
        }

    if "@" not in email or "." not in email.split("@")[-1]:
        return {
            "status": "error",
            "message": f"Invalid email address: {email}"
        }

    lead_id = f"LEAD-{len(_captured_leads) + 1001}"
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"

    lead = {
        "lead_id": lead_id,
        "name": name,
        "email": email,
        "platform": platform,
        "captured_at": timestamp,
        "product": "AutoStream",
        "plan_interest": "Pro"
    }

    _captured_leads.append(lead)

    print(f"\n{'='*55}")
    print(f"  ✅  Lead captured successfully!")
    print(f"  Name     : {name}")
    print(f"  Email    : {email}")
    print(f"  Platform : {platform}")
    print(f"  Lead ID  : {lead_id}")
    print(f"  Time     : {timestamp}")
    print(f"{'='*55}\n")

    return {
        "status": "success",
        "lead_id": lead_id,
        "message": f"Lead {name} captured successfully with ID {lead_id}.",
        "data": lead
    }


def get_all_leads() -> list:
    return _captured_leads