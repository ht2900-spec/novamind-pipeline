# ⚡ NovaMind AI Marketing Pipeline

An AI-powered marketing content pipeline that generates, segments, distributes, and optimizes blog and newsletter content for NovaMind — a fictional AI automation startup for small creative agencies.

## 🎯 What It Does

This system takes a blog topic from input to newsletter distribution and performance analysis in one automated pipeline:

1. **Generate** — Claude AI writes a blog post + segmented newsletters based on topic, value proposition, and audience
2. **Review & Approve** — Human-in-the-loop gate to edit content, select subject lines and CTAs before sending
3. **Distribute** — Campaigns logged to HubSpot CRM, contacts segmented by role and behavior
4. **Analyze** — Performance matrix tracks what content works for which audience
5. **Optimize** — AI recommendations inform the next campaign using previous results

---

## 🧠 Strategic Design Decisions

### Two-Stage Segmentation
Most marketing tools segment by job title. This pipeline segments in two stages:

**Stage 1 — Role Based:**
- Decision Makers (Founders, Strategy Leads) — have budget authority, respond to ROI and competitive advantage messaging
- Pressure Builders (Creative Directors, Account Managers, Freelancers) — feel daily pain, don't sign the check but influence who does

**Stage 2 — Behavior Based (after engagement data):**
- ⚡ Efficiency Seekers — respond to Time Back messaging
- 🔧 Process Builders — respond to Consistency messaging  
- 🚀 Growth Drivers — respond to Scalability messaging
- ✨ Quality Leaders — respond to Better Output messaging

### Content Matrix
Content is generated at the intersection of **topic × value proposition**, not just by persona. The same topic ("Automating client communication") generates completely different content depending on whether the angle is Time Back, Consistency, Scalability, or Better Output.

### Brand Voice
NovaMind's tone: **Bold, Witty, Authoritative, Human, Energetic**

Core promise: *"Your creative genius shouldn't be buried in task management. NovaMind handles the process so your team can forget about it."*

### Feedback Loop
After each campaign, performance data is stored and injected into the next generation prompt — so Claude writes smarter content each round based on what actually performed.

---

## 🏗 Architecture & Flow

```
INPUT: Topic + Value Proposition
            │
            ▼
    Claude Sonnet 4.5
    Generates:
    - Blog post (500 words)
    - Decision Maker newsletter
    - Pressure Builder newsletter
    - 3 subject line options each
    - 3 CTA options each
            │
            ▼
    HUMAN REVIEW GATE
    - Edit newsletter body
    - Select subject line style
    - Select CTA style
    - Choose Manual or A/B mode
            │
            ▼
    HUBSPOT CRM API
    - 100 segmented contacts
    - Campaign logged with topic,
      date, segment, value prop
            │
            ▼
    PERFORMANCE SIMULATION
    Rates calculated using:
    segment x value prop x
    subject style x topic
            │
            ▼
    ANALYTICS DASHBOARD
    - Funnel metrics
    - Content matrix
    - Segment comparison
    - CTA performance
            │
            ▼
    AI RECOMMENDATIONS
    Feeds back into next
    content generation prompt
```

## 👥 Two-Stage Segmentation

```
Stage 1 Role-Based        Stage 2 Behavior-Based
──────────────────        ──────────────────────
Decision Maker      →     Efficiency Seeker
Founders, Strategy        Time Back messaging

Pressure Builder    →     Process Builder
CDs, AMs, Freelance       Consistency messaging

                          Growth Driver
                          Scalability messaging

                          Quality Leader
                          Better Output messaging
```

## 🛠 Tools & Models

| Component | Tool | Detail |
|-----------|------|--------|
| AI Model | Anthropic Claude | claude-sonnet-4-5 |
| Web Framework | Flask | 3.1.3 |
| CRM | HubSpot | Private App API v3 |
| HTTP Client | Requests | 2.33.1 |
| Environment | python-dotenv | 1.2.2 |

## ⚠️ Assumptions & Limitations

- **Email sending is simulated** — HubSpot Marketing Email requires a paid tier. In production this would connect to HubSpot's Marketing API, Mailchimp, or SendGrid
- **Performance data is simulated** — engagement rates are calculated using realistic multipliers based on segment type, value proposition, topic affinity, and subject line style. Not random numbers — logic-driven simulation
- **Contact list is mock data** — 100 contacts generated programmatically to reflect realistic agency role distribution across 5 roles and 2 segments
- **Campaign history persists locally** — stored in `segment_history.json`. In production this would live in a database
- **Behavior segments are projections** — Stage 2 segmentation becomes data-backed after 10+ campaigns. Initial distribution is projected from contact value prop affinities