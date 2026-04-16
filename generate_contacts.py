import csv
import random

# Persona definitions
personas = [
    {"role": "Founder", "segment": "Decision Maker", "service_interest": "AI-assisted decision making"},
    {"role": "Strategy Lead", "segment": "Decision Maker", "service_interest": "Performance insights and recommendations"},
    {"role": "Creative Director", "segment": "Pressure Builder", "service_interest": "Generating social media content"},
    {"role": "Account Manager", "segment": "Pressure Builder", "service_interest": "Automating client communication"},
    {"role": "Freelancer", "segment": "Pressure Builder", "service_interest": "Automating repetitive operations"},
]

first_names = [
    "Alex", "Maya", "Jordan", "Priya", "Tom", "Luna", "Marcus", "Sofia",
    "Daniel", "Rachel", "James", "Nina", "Chris", "Zoe", "Ryan", "Aisha",
    "Kevin", "Elena", "Brian", "Fatima", "Tyler", "Chloe", "Andre", "Mia",
    "Jason", "Isabella", "Derek", "Yuki", "Patrick", "Leila", "Omar", "Hannah",
    "Victor", "Stella", "Nathan", "Aria", "Simon", "Diana", "Felix", "Clara"
]

last_names = [
    "Chen", "Rodriguez", "Park", "Patel", "Bradley", "Kim", "Webb", "Aldo",
    "Stone", "Mitchell", "Torres", "Singh", "Williams", "Brown", "Davis",
    "Martinez", "Johnson", "Lee", "Thompson", "White", "Harris", "Clark",
    "Lewis", "Walker", "Hall", "Allen", "Young", "King", "Wright", "Scott",
    "Green", "Baker", "Adams", "Nelson", "Carter", "Evans", "Turner", "Collins"
]

agencies = [
    "Pixel & Co", "Bold Studio", "The Forge Agency", "Spark Creative",
    "North Star Media", "Canvas Collective", "Echo Agency", "Prism Studios",
    "Velocity Creative", "Blueprint Agency", "Mosaic Media", "Apex Creative",
    "Orbit Studio", "Fusion Agency", "Horizon Creative", "Independent"
]

value_prop_affinity = {
    "Founder": ["Scalability", "Better Output"],
    "Strategy Lead": ["Scalability", "Better Output"],
    "Creative Director": ["Better Output", "Consistency"],
    "Account Manager": ["Time Back", "Consistency"],
    "Freelancer": ["Time Back", "Scalability"],
}

contacts = []
used_names = set()

while len(contacts) < 100:
    first = random.choice(first_names)
    last = random.choice(last_names)
    full_name = f"{first} {last}"
    
    if full_name in used_names:
        continue
    used_names.add(full_name)
    
    persona = random.choice(personas)
    agency = random.choice(agencies)
    email = f"{first.lower()}.{last.lower()}@{agency.lower().replace(' ', '').replace('&', 'and')}.com"
    value_prop = random.choice(value_prop_affinity[persona["role"]])
    
    contacts.append({
        "email": email,
        "firstname": first,
        "lastname": last,
        "company": agency,
        "jobtitle": persona["role"],
        "segment": persona["segment"],
        "service_interest": persona["service_interest"],
        "value_prop_affinity": value_prop,
        "lifecycle_stage": "lead"
    })

# Write CSV
with open("novamind_contacts.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=contacts[0].keys())
    writer.writeheader()
    writer.writerows(contacts)

print(f"Generated {len(contacts)} contacts → novamind_contacts.csv")

# Print breakdown
from collections import Counter
roles = Counter(c["jobtitle"] for c in contacts)
segments = Counter(c["segment"] for c in contacts)
print("\nRole breakdown:")
for role, count in roles.items():
    print(f"  {role}: {count}")
print("\nSegment breakdown:")
for seg, count in segments.items():
    print(f"  {seg}: {count}")