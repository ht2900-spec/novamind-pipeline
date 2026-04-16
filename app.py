import os
import json
import re
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ============================================
# BRAND BRIEF
# ============================================
BRAND_BRIEF = """
NOVAMIND BRAND BRIEF:
Core promise: "Your creative genius shouldn't be buried in task management. NovaMind handles the process so your team can forget about it."
Tone: Bold, Witty, Authoritative, Human, Energetic
Never use: corporate buzzwords, salesy language, passive tone, generic SaaS-speak
Always: speak peer-to-peer, lead with insight not promotion, respect the reader's craft
"""

# ============================================
# CONTENT MATRIX
# ============================================
CONTENT_MATRIX = {
    "Automating repetitive operations": {
        "best_value_props": ["Time Back", "Consistency"],
        "best_personas": ["Freelancer", "Designer", "Account Manager"]
    },
    "Generating automated briefs": {
        "best_value_props": ["Time Back", "Better Output"],
        "best_personas": ["Account Manager", "Creative Director"]
    },
    "Generating automated reports": {
        "best_value_props": ["Time Back", "Consistency"],
        "best_personas": ["Account Manager", "Analyst"]
    },
    "Generating social media content": {
        "best_value_props": ["Time Back", "Scalability"],
        "best_personas": ["Freelancer", "Creative Director"]
    },
    "Automating client communication": {
        "best_value_props": ["Time Back", "Consistency"],
        "best_personas": ["Account Manager", "Founder"]
    },
    "AI-assisted decision making": {
        "best_value_props": ["Better Output", "Scalability"],
        "best_personas": ["Founder", "Strategy Lead"]
    },
    "Risk detection and bottlenecks": {
        "best_value_props": ["Consistency", "Scalability"],
        "best_personas": ["Founder", "Strategy Lead"]
    },
    "Performance insights and recommendations": {
        "best_value_props": ["Better Output", "Scalability"],
        "best_personas": ["Founder", "Strategy Lead"]
    }
}

# ============================================
# MOCK CONTACTS
# ============================================
CONTACTS = [
    {"name": "Alex Chen", "role": "Founder", "agency": "Pixel & Co", "segment": "Decision Maker", "service_interest": "AI-assisted decision making"},
    {"name": "Rachel Stone", "role": "Founder", "agency": "Bold Studio", "segment": "Decision Maker", "service_interest": "Performance insights and recommendations"},
    {"name": "Daniel Park", "role": "Strategy Lead", "agency": "The Forge Agency", "segment": "Decision Maker", "service_interest": "Risk detection and bottlenecks"},
    {"name": "Maya Rodriguez", "role": "Creative Director", "agency": "Pixel & Co", "segment": "Pressure Builder", "service_interest": "Generating social media content"},
    {"name": "Tom Bradley", "role": "Account Manager", "agency": "Bold Studio", "segment": "Pressure Builder", "service_interest": "Automating client communication"},
    {"name": "Priya Patel", "role": "Account Manager", "agency": "The Forge Agency", "segment": "Pressure Builder", "service_interest": "Generating automated briefs"},
    {"name": "Luna Kim", "role": "Freelancer", "agency": "Independent", "segment": "Pressure Builder", "service_interest": "Automating repetitive operations"},
    {"name": "Marcus Webb", "role": "Freelancer", "agency": "Independent", "segment": "Pressure Builder", "service_interest": "Generating social media content"},
    {"name": "Sofia Aldo", "role": "Creative Director", "agency": "Independent", "segment": "Pressure Builder", "service_interest": "Generating automated briefs"},
]

# ============================================
# CONTENT GENERATION WITH FEEDBACK LOOP
# ============================================
def generate_content(topic, value_prop, segment):
    print(f"\nGenerating content for: {topic} | Value: {value_prop} | Segment: {segment}\n")

    # Load previous performance context
    feedback_context = ""
    if os.path.exists('segment_history.json'):
        with open('segment_history.json') as f:
            history = json.load(f)
        relevant = [c for c in history if c['topic'] == topic]
        if relevant:
            last = relevant[-1]
            dm_rate = last['dm_performance']['click_rate']
            pb_rate = last['pb_performance']['click_rate']
            dm_subj = last['dm_subject_style']
            pb_subj = last['pb_subject_style']
            feedback_context = f"""
PREVIOUS CAMPAIGN PERFORMANCE ON THIS TOPIC:
- Decision Makers: {dm_rate}% click rate using {dm_subj} subject lines
- Pressure Builders: {pb_rate}% click rate using {pb_subj} subject lines
- Apply these learnings: {'Pressure Builders outperformed — lean into their pain points more' if pb_rate > dm_rate else 'Decision Makers outperformed — emphasize ROI and strategic framing'}
"""

    prompt = f"""
{BRAND_BRIEF}
{feedback_context}
You are a content strategist for NovaMind.
Topic: {topic}
Value Proposition Focus: {value_prop}
Target Segment: {segment}

Segment context:
- Decision Maker: Founders, Strategy Leads. They have budget authority. Convince them with ROI and competitive advantage. Make them feel like leaders who make smart moves.
- Pressure Builder: Creative Directors, Account Managers, Freelancers. They feel daily pain. They don't sign the check but influence who does. Equip them to advocate internally. Make them feel understood and validated.

Return ONLY a valid JSON object:
{{
    "blog_title": "insight-led title, not salesy, makes the reader curious",
    "blog_outline": ["point 1", "point 2", "point 3", "point 4", "point 5"],
    "blog_draft": "500 word blog post in NovaMind brand voice",
    "newsletters": {{
        "decision_maker": {{
            "subject_clickbait": "curiosity-driven subject line",
            "subject_direct": "clear value subject line",
            "subject_insider": "industry insider subject line",
            "body": "150 word newsletter for Decision Makers, {value_prop} angle",
            "cta_action": "action-driven CTA",
            "cta_curiosity": "curiosity-driven CTA",
            "cta_social_proof": "social proof CTA"
        }},
        "pressure_builder": {{
            "subject_clickbait": "curiosity-driven subject line",
            "subject_direct": "clear value subject line",
            "subject_insider": "industry insider subject line",
            "body": "150 word newsletter for Pressure Builders, {value_prop} angle, make them feel understood",
            "cta_action": "action-driven CTA",
            "cta_curiosity": "curiosity-driven CTA",
            "cta_social_proof": "social proof CTA"
        }}
    }}
}}
"""

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        content = json.loads(match.group())
        return content
    else:
        raise ValueError("No valid JSON found in response")

# ============================================
# SAVE TO JSON
# ============================================
def save_content(topic, value_prop, segment, content):
    filename = f"content_{topic[:20].replace(' ', '_')}_{value_prop.replace(' ', '_')}_{segment.replace(' ', '_')}.json"
    with open(filename, 'w') as f:
        json.dump({
            "topic": topic,
            "value_prop": value_prop,
            "segment": segment,
            "content": content
        }, f, indent=2)
    print(f"Saved to {filename}")
    return filename

# ============================================
# TEST RUN
# ============================================
if __name__ == "__main__":
    result = generate_content(
        topic="Automating client communication",
        value_prop="Time Back",
        segment="Pressure Builder"
    )

    save_content("Automating client communication", "Time Back", "Pressure Builder", result)

    print("\nBLOG TITLE:", result["blog_title"])
    print("\n--- PRESSURE BUILDER NEWSLETTER ---")
    print("Clickbait:", result["newsletters"]["pressure_builder"]["subject_clickbait"])
    print("Direct:", result["newsletters"]["pressure_builder"]["subject_direct"])
    print("Insider:", result["newsletters"]["pressure_builder"]["subject_insider"])
    print("\nBody:", result["newsletters"]["pressure_builder"]["body"])
    print("\nCTA Action:", result["newsletters"]["pressure_builder"]["cta_action"])