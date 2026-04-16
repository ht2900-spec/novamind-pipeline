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

## 🏗 Architecture