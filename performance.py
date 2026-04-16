import os
import json
import random
import anthropic
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ============================================
# PERFORMANCE SIMULATION
# Based on realistic engagement patterns
# ============================================

# Base rates by segment
BASE_RATES = {
    "Decision Maker": {"open": 0.35, "click": 0.12, "unsubscribe": 0.02},
    "Pressure Builder": {"open": 0.45, "click": 0.18, "unsubscribe": 0.01}
}

# Value prop multipliers
VALUE_PROP_MULTIPLIERS = {
    "Time Back":      {"Decision Maker": 0.85, "Pressure Builder": 1.25},
    "Consistency":    {"Decision Maker": 1.10, "Pressure Builder": 1.10},
    "Scalability":    {"Decision Maker": 1.30, "Pressure Builder": 0.90},
    "Better Output":  {"Decision Maker": 1.20, "Pressure Builder": 1.05}
}

# Subject line multipliers
SUBJECT_MULTIPLIERS = {
    "clickbait": {"Decision Maker": 0.90, "Pressure Builder": 1.20},
    "direct":    {"Decision Maker": 1.20, "Pressure Builder": 0.95},
    "insider":   {"Decision Maker": 1.15, "Pressure Builder": 1.15}
}

# Topic multipliers
TOPIC_MULTIPLIERS = {
    "Automating client communication":          {"Decision Maker": 1.10, "Pressure Builder": 1.30},
    "Automating repetitive operations":         {"Decision Maker": 0.90, "Pressure Builder": 1.20},
    "Generating automated briefs":              {"Decision Maker": 1.05, "Pressure Builder": 1.10},
    "Generating automated reports":             {"Decision Maker": 1.15, "Pressure Builder": 1.00},
    "Generating social media content":          {"Decision Maker": 0.85, "Pressure Builder": 1.25},
    "AI-assisted decision making":              {"Decision Maker": 1.35, "Pressure Builder": 0.85},
    "Risk detection and bottlenecks":           {"Decision Maker": 1.25, "Pressure Builder": 0.90},
    "Performance insights and recommendations": {"Decision Maker": 1.30, "Pressure Builder": 0.95}
}

def simulate_performance(topic, value_prop, segment, subject_style, contact_count):
    """Simulate realistic engagement metrics"""
    
    base = BASE_RATES[segment].copy()
    vp_mult = VALUE_PROP_MULTIPLIERS[value_prop][segment]
    subj_mult = SUBJECT_MULTIPLIERS[subject_style][segment]
    topic_mult = TOPIC_MULTIPLIERS.get(topic, {}).get(segment, 1.0)
    
    # Calculate rates with some randomness
    open_rate = min(base["open"] * vp_mult * subj_mult * topic_mult * random.uniform(0.9, 1.1), 0.95)
    click_rate = min(base["click"] * vp_mult * subj_mult * topic_mult * random.uniform(0.9, 1.1), open_rate)
    unsub_rate = max(base["unsubscribe"] * random.uniform(0.8, 1.2), 0.001)
    
    sent = contact_count
    opened = int(sent * open_rate)
    clicked = int(opened * (click_rate / open_rate))
    unsubscribed = int(sent * unsub_rate)
    converted = int(clicked * 0.15)
    cta_clicked = int(clicked * random.uniform(0.4, 0.7))
    
    return {
        "sent": sent,
        "opened": opened,
        "clicked": clicked,
        "unsubscribed": unsubscribed,
        "converted": converted,
        "cta_clicked": cta_clicked,
        "open_rate": round(open_rate * 100, 1),
        "click_rate": round(click_rate * 100, 1),
        "unsub_rate": round(unsub_rate * 100, 2),
        "conversion_rate": round((converted / sent) * 100, 1) if sent > 0 else 0,
        "cta_rate": round((cta_clicked / sent) * 100, 1) if sent > 0 else 0
    }

def build_matrix(campaigns):
    """Build the content matrix filled with performance data"""
    
    topics = list(TOPIC_MULTIPLIERS.keys())
    value_props = ["Time Back", "Consistency", "Scalability", "Better Output"]
    
    matrix = {}
    for topic in topics:
        matrix[topic] = {}
        for vp in value_props:
            relevant = [c for c in campaigns 
                       if c["topic"] == topic and c["value_prop"] == vp]
            if relevant:
                avg_click = sum(c["performance"]["click_rate"] for c in relevant) / len(relevant)
                matrix[topic][vp] = round(avg_click, 1)
            else:
                matrix[topic][vp] = "--"
    
    return matrix

def generate_ai_recommendations(campaigns, matrix):
    """Use Claude to analyze performance and recommend next steps"""
    
    print("\nGenerating AI recommendations...")
    
    # Find best performers
    best_campaigns = sorted(campaigns, key=lambda x: x["performance"]["click_rate"], reverse=True)[:3]
    worst_campaigns = sorted(campaigns, key=lambda x: x["performance"]["click_rate"])[:3]
    
    prompt = f"""
You are a marketing analyst for NovaMind.

Here are the top 3 performing campaigns:
{json.dumps([{
    "topic": c["topic"],
    "value_prop": c["value_prop"],
    "segment": c["segment"],
    "subject_style": c["subject_style"],
    "click_rate": c["performance"]["click_rate"]
} for c in best_campaigns], indent=2)}

Here are the 3 worst performing campaigns:
{json.dumps([{
    "topic": c["topic"],
    "value_prop": c["value_prop"],
    "segment": c["segment"],
    "subject_style": c["subject_style"],
    "click_rate": c["performance"]["click_rate"]
} for c in worst_campaigns], indent=2)}

Provide a brief, actionable analysis in JSON format:
{{
    "key_insight": "one sentence insight",
    "decision_maker_recommendation": "what content to send them next",
    "pressure_builder_recommendation": "what content to send them next",
    "next_topic": "recommended next blog topic",
    "next_value_prop": "recommended value prop to focus on",
    "subject_style_winner": "which subject style is working best and why"
}}

Return ONLY valid JSON.
"""
    
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    import re
    raw = message.content[0].text
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        return json.loads(match.group())
    return {}

def run_performance_analysis(contact_counts={"Decision Maker": 38, "Pressure Builder": 62}):
    """Run a full simulated campaign performance analysis"""
    
    topics = list(TOPIC_MULTIPLIERS.keys())
    value_props = ["Time Back", "Consistency", "Scalability", "Better Output"]
    subject_styles = ["clickbait", "direct", "insider"]
    segments = ["Decision Maker", "Pressure Builder"]
    
    campaigns = []
    
    # Simulate campaigns for each combination
    for topic in topics[:4]:  # Use 4 topics for demo
        for vp in value_props[:2]:  # Use 2 value props for demo
            for segment in segments:
                for style in subject_styles:
                    perf = simulate_performance(
                        topic=topic,
                        value_prop=vp,
                        segment=segment,
                        subject_style=style,
                        contact_count=contact_counts[segment]
                    )
                    campaigns.append({
                        "topic": topic,
                        "value_prop": vp,
                        "segment": segment,
                        "subject_style": style,
                        "performance": perf,
                        "date": datetime.now().strftime("%Y-%m-%d")
                    })
    
    # Build matrix
    matrix = build_matrix(campaigns)
    
    # Get AI recommendations
    recommendations = generate_ai_recommendations(campaigns, matrix)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"performance_{timestamp}.json"
    
    results = {
        "campaigns": campaigns,
        "matrix": matrix,
        "recommendations": recommendations,
        "generated_at": datetime.now().isoformat()
    }
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

# ============================================
# TEST RUN
# ============================================
if __name__ == "__main__":
    print("Running performance analysis...\n")
    results = run_performance_analysis()
    
    print("\n=== CONTENT MATRIX (Click Rates %) ===")
    print(f"{'Topic':<45}", end="")
    value_props = ["Time Back", "Consistency", "Scalability", "Better Output"]
    for vp in value_props:
        print(f"{vp:<16}", end="")
    print()
    print("-" * 110)
    
    for topic, vp_data in results["matrix"].items():
        print(f"{topic:<45}", end="")
        for vp in value_props:
            val = vp_data.get(vp, "--")
            print(f"{str(val):<16}", end="")
        print()
    
    print("\n=== AI RECOMMENDATIONS ===")
    rec = results["recommendations"]
    print(f"Key Insight: {rec.get('key_insight', '')}")
    print(f"Next Topic: {rec.get('next_topic', '')}")
    print(f"Next Value Prop: {rec.get('next_value_prop', '')}")
    print(f"Subject Style Winner: {rec.get('subject_style_winner', '')}")
    print(f"\nDecision Makers: {rec.get('decision_maker_recommendation', '')}")
    print(f"Pressure Builders: {rec.get('pressure_builder_recommendation', '')}")
    
    print(f"\nFull results saved to performance file")