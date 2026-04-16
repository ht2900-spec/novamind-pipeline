import os
import requests
from dotenv import load_dotenv

load_dotenv()

HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
BASE_URL = "https://api.hubapi.com"

HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_API_KEY}",
    "Content-Type": "application/json"
}

def get_contacts_by_segment(segment):
    """Fetch contacts from HubSpot filtered by segment"""
    print(f"\nFetching {segment} contacts from HubSpot...")
    
    url = f"{BASE_URL}/crm/v3/objects/contacts/search"
    
    payload = {
        "filterGroups": [{
            "filters": [{
                "propertyName": "segment",
                "operator": "EQ",
                "value": segment
            }]
        }],
        "properties": [
            "firstname", "lastname", "email", 
            "jobtitle", "segment", 
            "service_interest", "value_prop_affinity"
        ],
        "limit": 100
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        contacts = response.json()["results"]
        print(f"Found {len(contacts)} {segment} contacts")
        return contacts
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

def log_campaign(campaign_name, topic, value_prop, segment, contact_count):
    """Log campaign as a note in HubSpot"""
    print(f"\nLogging campaign: {campaign_name}")
    
    url = f"{BASE_URL}/crm/v3/objects/notes"
    
    payload = {
        "properties": {
            "hs_note_body": f"""
NOVAMIND CAMPAIGN LOG
Campaign: {campaign_name}
Topic: {topic}
Value Proposition: {value_prop}
Target Segment: {segment}
Contacts Reached: {contact_count}
Status: Sent
            """,
            "hs_timestamp": str(int(__import__('time').time() * 1000))
        }
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    
    if response.status_code == 201:
        print(f"Campaign logged successfully!")
        return response.json()["id"]
    else:
        print(f"Error logging: {response.status_code} - {response.text}")
        return None

# Test it
if __name__ == "__main__":
    # Test 1: Fetch Decision Makers
    decision_makers = get_contacts_by_segment("Decision Maker")
    if decision_makers:
        print("\nFirst Decision Maker:")
        props = decision_makers[0]["properties"]
        print(f"  {props['firstname']} {props['lastname']} — {props['jobtitle']}")
        print(f"  Segment: {props['segment']}")
        print(f"  Service Interest: {props['service_interest']}")
    
    # Test 2: Fetch Pressure Builders
    pressure_builders = get_contacts_by_segment("Pressure Builder")
    
    # Test 3: Log a campaign
    log_campaign(
        campaign_name="NovaMind Weekly #1",
        topic="Automating client communication",
        value_prop="Time Back",
        segment="Pressure Builder",
        contact_count=len(pressure_builders)
    )