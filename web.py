from flask import Flask, render_template_string, request, jsonify
import json
import os
import sys
import random
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import generate_content, save_content
from hubspot import get_contacts_by_segment, log_campaign
from performance import run_performance_analysis, simulate_performance, TOPIC_MULTIPLIERS

app = Flask(__name__)

# ============================================
# CAMPAIGN HISTORY STORE
# ============================================
campaign_history = []
if os.path.exists('segment_history.json'):
    with open('segment_history.json') as f:
        campaign_history = json.load(f)

# ============================================
# BEHAVIOR SEGMENTS
# ============================================
BEHAVIOR_SEGMENTS = {
    "Time Back": "Efficiency Seeker",
    "Consistency": "Process Builder",
    "Scalability": "Growth Driver",
    "Better Output": "Quality Leader"
}

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NovaMind Content Pipeline</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0a0a0a; color: #fff; min-height: 100vh; }
        nav { display: flex; align-items: center; justify-content: space-between; padding: 20px 40px; border-bottom: 1px solid #222; background: #0a0a0a; position: sticky; top: 0; z-index: 100; }
        .logo { font-size: 22px; font-weight: 700; background: linear-gradient(135deg, #6366f1, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .nav-tabs { display: flex; gap: 8px; }
        .nav-tab { padding: 8px 20px; border-radius: 8px; border: none; background: transparent; color: #888; cursor: pointer; font-size: 14px; transition: all 0.2s; }
        .nav-tab.active, .nav-tab:hover { background: #1a1a1a; color: #fff; }
        .main { padding: 40px; max-width: 1400px; margin: 0 auto; }
        .page { display: none; }
        .page.active { display: block; }
        .card { background: #111; border: 1px solid #222; border-radius: 16px; padding: 28px; margin-bottom: 24px; }
        .card h2 { font-size: 18px; font-weight: 600; margin-bottom: 20px; color: #fff; }
        .card h3 { font-size: 15px; font-weight: 600; margin-bottom: 12px; color: #ccc; }
        .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }
        .form-group { display: flex; flex-direction: column; gap: 8px; }
        .form-group label { font-size: 13px; color: #888; }
        select, input { background: #1a1a1a; border: 1px solid #333; border-radius: 10px; padding: 12px 16px; color: #fff; font-size: 14px; outline: none; transition: border 0.2s; }
        select:focus, input:focus { border-color: #6366f1; }
        .btn { padding: 12px 28px; border-radius: 10px; border: none; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
        .btn-primary { background: linear-gradient(135deg, #6366f1, #a855f7); color: #fff; }
        .btn-primary:hover { opacity: 0.9; transform: translateY(-1px); }
        .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        .btn-secondary { background: #1a1a1a; color: #fff; border: 1px solid #333; }
        .btn-approve { background: #16a34a; color: #fff; }
        .btn-ab { background: #0369a1; color: #fff; }
        .tag { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 500; }
        .tag-purple { background: #3730a3; color: #a5b4fc; }
        .tag-green { background: #14532d; color: #86efac; }
        .tag-orange { background: #7c2d12; color: #fdba74; }
        .tag-blue { background: #1e3a5f; color: #93c5fd; }
        .tag-teal { background: #134e4a; color: #5eead4; }
        .subject-options { display: flex; flex-direction: column; gap: 8px; margin: 12px 0; }
        .subject-option { display: flex; align-items: center; gap: 12px; padding: 12px 16px; background: #1a1a1a; border: 1px solid #333; border-radius: 10px; cursor: pointer; transition: all 0.2s; }
        .subject-option:hover, .subject-option.selected { border-color: #6366f1; background: #1e1b4b; }
        .subject-option input { width: auto; padding: 0; }
        .subject-label { font-size: 11px; color: #888; width: 70px; flex-shrink: 0; }
        .newsletter-body { background: #1a1a1a; border: 1px solid #333; border-radius: 10px; padding: 16px; font-size: 14px; line-height: 1.6; color: #ccc; margin: 12px 0; min-height: 100px; white-space: pre-wrap; }
        .newsletter-body[contenteditable="true"] { border-color: #6366f1; outline: none; }
        .metrics-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; margin-bottom: 24px; }
        .metric-card { background: #111; border: 1px solid #222; border-radius: 12px; padding: 20px; text-align: center; }
        .metric-value { font-size: 28px; font-weight: 700; background: linear-gradient(135deg, #6366f1, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .metric-label { font-size: 13px; color: #888; margin-top: 4px; }
        .matrix-table { width: 100%; border-collapse: collapse; font-size: 13px; }
        .matrix-table th { padding: 12px 16px; text-align: left; color: #888; border-bottom: 1px solid #222; font-weight: 500; }
        .matrix-table td { padding: 12px 16px; border-bottom: 1px solid #1a1a1a; color: #ccc; }
        .matrix-table tr:hover td { background: #151515; }
        .matrix-value { font-weight: 600; color: #fff; }
        .matrix-high { color: #4ade80 !important; }
        .matrix-mid { color: #facc15 !important; }
        .matrix-low { color: #f87171 !important; }
        .recommendation-box { background: linear-gradient(135deg, #1e1b4b, #2e1065); border: 1px solid #4338ca; border-radius: 12px; padding: 20px; margin-bottom: 16px; }
        .recommendation-box h3 { color: #a5b4fc; margin-bottom: 8px; }
        .recommendation-box p { font-size: 14px; color: #c4b5fd; line-height: 1.6; }
        .loading { display: none; text-align: center; padding: 40px; color: #888; }
        .spinner { width: 40px; height: 40px; border: 3px solid #333; border-top-color: #6366f1; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 16px; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
        .three-col { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 24px; }
        .divider { height: 1px; background: #222; margin: 20px 0; }
        .alert { padding: 12px 16px; border-radius: 10px; margin-bottom: 16px; font-size: 14px; }
        .alert-success { background: #14532d; color: #86efac; border: 1px solid #16a34a; }
        .alert-error { background: #7f1d1d; color: #fca5a5; border: 1px solid #dc2626; }
        .segment-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
        .segment-bar-label { width: 160px; font-size: 13px; color: #888; }
        .segment-bar-track { flex: 1; height: 8px; background: #222; border-radius: 4px; overflow: hidden; }
        .segment-bar-fill { height: 100%; border-radius: 4px; background: linear-gradient(135deg, #6366f1, #a855f7); transition: width 0.5s ease; }
        .segment-bar-value { font-size: 13px; font-weight: 600; width: 50px; text-align: right; }
        .history-card { background: #111; border: 1px solid #222; border-radius: 12px; padding: 20px; margin-bottom: 16px; cursor: pointer; transition: all 0.2s; }
        .history-card:hover { border-color: #6366f1; }
        .history-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        .history-metrics { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; margin-top: 12px; }
        .history-metric { text-align: center; background: #1a1a1a; border-radius: 8px; padding: 8px; }
        .history-metric-value { font-size: 18px; font-weight: 700; color: #a5b4fc; }
        .history-metric-label { font-size: 10px; color: #888; margin-top: 2px; }
        .vs-bar { display: flex; gap: 16px; margin-top: 12px; }
        .vs-item { flex: 1; background: #1a1a1a; border-radius: 8px; padding: 12px; text-align: center; }
        .vs-value { font-size: 20px; font-weight: 700; }
        .vs-label { font-size: 11px; color: #888; margin-top: 4px; }
        .behavior-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 16px; }
        .behavior-card { background: #1a1a1a; border: 1px solid #333; border-radius: 12px; padding: 16px; text-align: center; }
        .behavior-count { font-size: 32px; font-weight: 700; background: linear-gradient(135deg, #6366f1, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .behavior-name { font-size: 13px; color: #ccc; margin-top: 4px; font-weight: 600; }
        .behavior-desc { font-size: 11px; color: #888; margin-top: 4px; }
        .ab-toggle { display: flex; gap: 8px; margin-bottom: 16px; }
        .ab-btn { padding: 8px 16px; border-radius: 8px; border: 1px solid #333; background: #1a1a1a; color: #888; cursor: pointer; font-size: 13px; transition: all 0.2s; }
        .ab-btn.active { background: #1e3a5f; border-color: #3b82f6; color: #93c5fd; }
        .ab-result { background: #0c1a2e; border: 1px solid #1e3a5f; border-radius: 10px; padding: 16px; margin-top: 12px; }
        .ab-winner { color: #4ade80; font-weight: 700; }
        textarea { background: #1a1a1a; border: 1px solid #333; border-radius: 10px; padding: 12px 16px; color: #fff; font-size: 14px; outline: none; width: 100%; resize: vertical; }
    </style>
</head>
<body>

<nav>
    <div class="logo">⚡ NovaMind</div>
    <div class="nav-tabs">
        <button class="nav-tab active" onclick="showPage('generate', this)">Generate</button>
        <button class="nav-tab" onclick="showPage('review', this)">Review & Approve</button>
        <button class="nav-tab" onclick="showPage('analytics', this)">Analytics</button>
        <button class="nav-tab" onclick="showPage('history', this)">Campaign History</button>
        <button class="nav-tab" onclick="showPage('segments', this)">Segments</button>
    </div>
</nav>

<div class="main">

    <!-- ===== PAGE 1: GENERATE ===== -->
    <div id="page-generate" class="page active">
        <div class="card">
            <h2>🎯 Content Campaign Generator</h2>
            <div class="form-grid">
                <div class="form-group">
                    <label>Topic</label>
                    <select id="topic">
                        <option>Automating client communication</option>
                        <option>Automating repetitive operations</option>
                        <option>Generating automated briefs</option>
                        <option>Generating automated reports</option>
                        <option>Generating social media content</option>
                        <option>AI-assisted decision making</option>
                        <option>Risk detection and bottlenecks</option>
                        <option>Performance insights and recommendations</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Value Proposition</label>
                    <select id="value_prop">
                        <option>Time Back</option>
                        <option>Consistency</option>
                        <option>Scalability</option>
                        <option>Better Output</option>
                    </select>
                </div>
            </div>
            <button class="btn btn-primary" id="generate-btn" onclick="generateContent()">
                Generate Campaign Content
            </button>
        </div>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Claude is generating your campaign content...</p>
        </div>

        <div id="generate-result" style="display:none">
            <div class="alert alert-success" id="generate-alert"></div>
            <div class="card">
                <h2>📝 Blog Post</h2>
                <h3 id="blog-title" style="font-size:20px; color:#fff; margin-bottom:16px;"></h3>
                <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:16px;" id="blog-outline"></div>
                <div class="newsletter-body" id="blog-draft"></div>
            </div>
            <button class="btn btn-primary" style="margin-bottom:24px;" onclick="showPage('review', document.querySelectorAll('.nav-tab')[1])">
                Review Newsletters →
            </button>
        </div>
    </div>

    <!-- ===== PAGE 2: REVIEW ===== -->
    <div id="page-review" class="page">
        <div id="no-content-msg" class="card" style="text-align:center; padding:60px;">
            <p style="color:#888;">Generate content first to review newsletters.</p>
            <button class="btn btn-secondary" style="margin-top:16px;" onclick="showPage('generate', document.querySelectorAll('.nav-tab')[0])">← Go Generate</button>
        </div>

        <div id="review-content" style="display:none;">

            <!-- A/B Toggle -->
            <div class="card">
                <h2>⚗️ Distribution Mode</h2>
                <div class="ab-toggle">
                    <button class="ab-btn active" id="manual-btn" onclick="setMode('manual')">✋ Manual Selection</button>
                    <button class="ab-btn" id="ab-btn" onclick="setMode('ab')">🔬 Auto A/B Test</button>
                </div>
                <p id="mode-desc" style="color:#888; font-size:13px;">You choose which subject line and CTA to send to each segment.</p>
            </div>

            <div class="two-col">
                <!-- Decision Maker -->
                <div class="card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                        <h2>Decision Maker Newsletter</h2>
                        <span class="tag tag-purple">38 contacts</span>
                    </div>
                    <h3>Choose Subject Line</h3>
                    <div class="subject-options" id="dm-subjects"></div>
                    <div class="divider"></div>
                    <h3>Newsletter Body <span style="font-size:11px; color:#888;">(editable)</span></h3>
                    <div class="newsletter-body" id="dm-body" contenteditable="true"></div>
                    <h3 style="margin-top:16px;">Choose CTA</h3>
                    <div class="subject-options" id="dm-ctas"></div>
                </div>

                <!-- Pressure Builder -->
                <div class="card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                        <h2>Pressure Builder Newsletter</h2>
                        <span class="tag tag-orange">62 contacts</span>
                    </div>
                    <h3>Choose Subject Line</h3>
                    <div class="subject-options" id="pb-subjects"></div>
                    <div class="divider"></div>
                    <h3>Newsletter Body <span style="font-size:11px; color:#888;">(editable)</span></h3>
                    <div class="newsletter-body" id="pb-body" contenteditable="true"></div>
                    <h3 style="margin-top:16px;">Choose CTA</h3>
                    <div class="subject-options" id="pb-ctas"></div>
                </div>
            </div>

            <div class="card" style="text-align:center;">
                <h2 style="margin-bottom:8px;">Ready to send?</h2>
                <p style="color:#888; margin-bottom:20px;">This will log the campaign to HubSpot and simulate sending to all 100 contacts.</p>
                <button class="btn btn-approve" id="approve-btn" onclick="approveCampaign()">
                    ✓ Approve & Send Campaign
                </button>
            </div>

            <div id="approve-result" style="display:none;">
                <div class="alert alert-success">✅ Campaign sent! Check Campaign History for results.</div>
                <button class="btn btn-primary" onclick="showPage('history', document.querySelectorAll('.nav-tab')[3]); loadHistory();">
                    View Campaign History →
                </button>
            </div>
        </div>
    </div>

    <!-- ===== PAGE 3: ANALYTICS ===== -->
    <div id="page-analytics" class="page">
        <button class="btn btn-primary" style="margin-bottom:24px;" onclick="loadAnalytics()">
            🔄 Run Performance Analysis
        </button>

        <div class="loading" id="analytics-loading">
            <div class="spinner"></div>
            <p>Analyzing campaign performance...</p>
        </div>

        <div id="analytics-content" style="display:none;">

            <!-- Funnel -->
            <div class="card">
                <h2>📊 Overall Campaign Funnel</h2>
                <div style="display:flex; gap:40px; align-items:flex-end; height:160px; padding:0 20px;">
                    <div style="flex:1; text-align:center;">
                        <div id="bar-sent" style="background:#6366f1; border-radius:8px 8px 0 0; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:13px; transition: height 0.5s;"></div>
                        <div style="font-size:11px; color:#888; margin-top:8px;">Sent</div>
                    </div>
                    <div style="flex:1; text-align:center;">
                        <div id="bar-opened" style="background:#8b5cf6; border-radius:8px 8px 0 0; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:13px; transition: height 0.5s;"></div>
                        <div style="font-size:11px; color:#888; margin-top:8px;">Opened</div>
                    </div>
                    <div style="flex:1; text-align:center;">
                        <div id="bar-clicked" style="background:#a855f7; border-radius:8px 8px 0 0; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:13px; transition: height 0.5s;"></div>
                        <div style="font-size:11px; color:#888; margin-top:8px;">Clicked</div>
                    </div>
                    <div style="flex:1; text-align:center;">
                        <div id="bar-cta" style="background:#c084fc; border-radius:8px 8px 0 0; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:13px; transition: height 0.5s;"></div>
                        <div style="font-size:11px; color:#888; margin-top:8px;">CTA Clicked</div>
                    </div>
                    <div style="flex:1; text-align:center;">
                        <div id="bar-converted" style="background:#e879f9; border-radius:8px 8px 0 0; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:13px; transition: height 0.5s;"></div>
                        <div style="font-size:11px; color:#888; margin-top:8px;">Converted</div>
                    </div>
                </div>
            </div>

            <!-- Segment + Subject -->
            <div class="two-col">
                <div class="card">
                    <h2>👥 Segment Performance</h2>
                    <div id="segment-bars"></div>
                </div>
                <div class="card">
                    <h2>🏆 Subject Style Performance</h2>
                    <div id="subject-winner"></div>
                </div>
            </div>

            <!-- CTA Performance -->
            <div class="card">
                <h2>🔗 CTA Style Performance</h2>
                <div id="cta-performance"></div>
            </div>

            <!-- Matrix -->
            <div class="card">
                <h2>📈 Content Matrix — Click Rates (%)</h2>
                <table class="matrix-table">
                    <thead>
                        <tr>
                            <th>Topic</th>
                            <th>Time Back</th>
                            <th>Consistency</th>
                            <th>Scalability</th>
                            <th>Better Output</th>
                        </tr>
                    </thead>
                    <tbody id="matrix-body"></tbody>
                </table>
            </div>

            <!-- AI Recommendations -->
            <div class="card">
                <h2>🤖 AI Recommendations</h2>
                <div class="recommendation-box">
                    <h3>Key Insight</h3>
                    <p id="rec-insight"></p>
                </div>
                <div class="two-col">
                    <div class="recommendation-box">
                        <h3>Next Topic</h3>
                        <p id="rec-topic"></p>
                    </div>
                    <div class="recommendation-box">
                        <h3>Next Value Prop</h3>
                        <p id="rec-vp"></p>
                    </div>
                </div>
                <div class="recommendation-box" style="margin-top:16px;">
                    <h3>Decision Makers</h3>
                    <p id="rec-dm"></p>
                </div>
                <div class="recommendation-box" style="margin-top:16px;">
                    <h3>Pressure Builders</h3>
                    <p id="rec-pb"></p>
                </div>
            </div>
        </div>
    </div>

    <!-- ===== PAGE 4: CAMPAIGN HISTORY ===== -->
    <div id="page-history" class="page">
        <div id="no-history-msg" class="card" style="text-align:center; padding:60px;">
            <p style="color:#888;">No campaigns sent yet. Generate and approve a campaign first!</p>
            <button class="btn btn-secondary" style="margin-top:16px;" onclick="showPage('generate', document.querySelectorAll('.nav-tab')[0])">← Go Generate</button>
        </div>

        <div id="history-content" style="display:none;">
            <div class="card">
                <h2>📬 Overall Performance So Far</h2>
                <div class="metrics-grid" id="overall-metrics"></div>
            </div>
            <div id="campaign-list"></div>
        </div>
    </div>

    <!-- ===== PAGE 5: SEGMENTS ===== -->
    <div id="page-segments" class="page">
        <div class="card">
            <h2>🧠 Behavior-Based Segmentation</h2>
            <p style="color:#888; font-size:14px; margin-bottom:20px;">After campaigns run, contacts are re-segmented based on what content they engaged with most — moving from role-based to behavior-based targeting.</p>

            <div class="two-col" style="margin-bottom:24px;">
                <div style="background:#1a1a1a; border-radius:12px; padding:20px;">
                    <h3 style="color:#888; margin-bottom:12px;">Stage 1 — Role Based</h3>
                    <div style="display:flex; flex-direction:column; gap:8px;">
                        <div class="tag tag-purple" style="display:block; text-align:center; padding:8px;">Decision Maker</div>
                        <div class="tag tag-orange" style="display:block; text-align:center; padding:8px;">Pressure Builder</div>
                    </div>
                </div>
                <div style="background:#1a1a1a; border-radius:12px; padding:20px;">
                    <h3 style="color:#888; margin-bottom:12px;">Stage 2 — Behavior Based</h3>
                    <div style="display:flex; flex-direction:column; gap:8px;">
                        <div class="tag tag-blue" style="display:block; text-align:center; padding:8px;">⚡ Efficiency Seeker</div>
                        <div class="tag tag-purple" style="display:block; text-align:center; padding:8px;">🔧 Process Builder</div>
                        <div class="tag tag-green" style="display:block; text-align:center; padding:8px;">🚀 Growth Driver</div>
                        <div class="tag tag-teal" style="display:block; text-align:center; padding:8px;">✨ Quality Leader</div>
                    </div>
                </div>
            </div>

            <button class="btn btn-primary" onclick="loadSegments()">Analyze Behavior Segments</button>
        </div>

        <div class="loading" id="segments-loading">
            <div class="spinner"></div>
            <p>Analyzing contact behavior...</p>
        </div>

        <div id="segments-content" style="display:none;">
            <div class="card">
                <h2>📊 Current Segment Distribution</h2>
                <div class="behavior-grid" id="behavior-grid"></div>
            </div>
            <div class="card">
                <h2>🎯 Segment Recommendations</h2>
                <div id="segment-recommendations"></div>
            </div>
        </div>
    </div>

</div>

<script>
let currentContent = null;
let distributionMode = 'manual';

function showPage(name, tabEl) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.getElementById('page-' + name).classList.add('active');
    if (tabEl) tabEl.classList.add('active');
}

function setMode(mode) {
    distributionMode = mode;
    document.getElementById('manual-btn').classList.toggle('active', mode === 'manual');
    document.getElementById('ab-btn').classList.toggle('active', mode === 'ab');
    document.getElementById('mode-desc').textContent = mode === 'manual'
        ? 'You choose which subject line and CTA to send to each segment.'
        : 'System automatically splits contacts across all subject/CTA combinations and picks the winner.';
}

async function generateContent() {
    const topic = document.getElementById('topic').value;
    const value_prop = document.getElementById('value_prop').value;
    document.getElementById('generate-btn').disabled = true;
    document.getElementById('loading').style.display = 'block';
    document.getElementById('generate-result').style.display = 'none';
    try {
        const res = await fetch('/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({topic, value_prop})
        });
        const data = await res.json();
        if (data.error) throw new Error(data.error);
        currentContent = data;
        displayGeneratedContent(data);
        populateReview(data);
    } catch(e) {
        alert('Error: ' + e.message);
    } finally {
        document.getElementById('generate-btn').disabled = false;
        document.getElementById('loading').style.display = 'none';
    }
}

function displayGeneratedContent(data) {
    document.getElementById('blog-title').textContent = data.content.blog_title;
    const outlineEl = document.getElementById('blog-outline');
    outlineEl.innerHTML = data.content.blog_outline.map(p => `<span class="tag tag-blue">${p}</span>`).join('');
    document.getElementById('blog-draft').textContent = data.content.blog_draft;
    document.getElementById('generate-alert').textContent = `✅ Content generated for "${data.topic}" — ${data.value_prop} angle`;
    document.getElementById('generate-result').style.display = 'block';
}

function populateReview(data) {
    const nl = data.content.newsletters;
    
    function renderOptions(containerId, options, groupName) {
        document.getElementById(containerId).innerHTML = options.map((s, i) => `
            <label class="subject-option ${i===0?'selected':''}">
                <input type="radio" name="${groupName}" value="${s.value}" ${i===0?'checked':''} onchange="this.closest('.subject-options').querySelectorAll('.subject-option').forEach(el=>el.classList.remove('selected')); this.closest('.subject-option').classList.add('selected')">
                <span class="subject-label">${s.label}</span>
                <span>${s.text}</span>
            </label>
        `).join('');
    }

    renderOptions('dm-subjects', [
        {label:'Clickbait', value:'clickbait', text: nl.decision_maker.subject_clickbait},
        {label:'Direct', value:'direct', text: nl.decision_maker.subject_direct},
        {label:'Insider', value:'insider', text: nl.decision_maker.subject_insider}
    ], 'dm-subject');

    renderOptions('pb-subjects', [
        {label:'Clickbait', value:'clickbait', text: nl.pressure_builder.subject_clickbait},
        {label:'Direct', value:'direct', text: nl.pressure_builder.subject_direct},
        {label:'Insider', value:'insider', text: nl.pressure_builder.subject_insider}
    ], 'pb-subject');

    renderOptions('dm-ctas', [
        {label:'Action', value:'action', text: nl.decision_maker.cta_action},
        {label:'Curiosity', value:'curiosity', text: nl.decision_maker.cta_curiosity},
        {label:'Social Proof', value:'social_proof', text: nl.decision_maker.cta_social_proof}
    ], 'dm-cta');

    renderOptions('pb-ctas', [
        {label:'Action', value:'action', text: nl.pressure_builder.cta_action},
        {label:'Curiosity', value:'curiosity', text: nl.pressure_builder.cta_curiosity},
        {label:'Social Proof', value:'social_proof', text: nl.pressure_builder.cta_social_proof}
    ], 'pb-cta');

    document.getElementById('dm-body').textContent = nl.decision_maker.body;
    document.getElementById('pb-body').textContent = nl.pressure_builder.body;
    document.getElementById('no-content-msg').style.display = 'none';
    document.getElementById('review-content').style.display = 'block';
}

async function approveCampaign() {
    if (!currentContent) return;
    document.getElementById('approve-btn').disabled = true;
    document.getElementById('approve-btn').textContent = 'Sending...';
    const dmSubject = document.querySelector('input[name="dm-subject"]:checked')?.value || 'direct';
    const pbSubject = document.querySelector('input[name="pb-subject"]:checked')?.value || 'clickbait';
    const dmCta = document.querySelector('input[name="dm-cta"]:checked')?.value || 'action';
    const pbCta = document.querySelector('input[name="pb-cta"]:checked')?.value || 'curiosity';
    try {
        const res = await fetch('/approve', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                topic: currentContent.topic,
                value_prop: currentContent.value_prop,
                dm_subject_style: dmSubject,
                pb_subject_style: pbSubject,
                dm_cta: dmCta,
                pb_cta: pbCta,
                mode: distributionMode
            })
        });
        const data = await res.json();
        if (data.success) {
            document.getElementById('approve-result').style.display = 'block';
        }
    } catch(e) {
        alert('Error: ' + e.message);
    } finally {
        document.getElementById('approve-btn').disabled = false;
        document.getElementById('approve-btn').textContent = '✓ Approve & Send Campaign';
    }
}

async function loadAnalytics() {
    document.getElementById('analytics-loading').style.display = 'block';
    document.getElementById('analytics-content').style.display = 'none';
    try {
        const res = await fetch('/analytics');
        const data = await res.json();
        displayAnalytics(data);
    } catch(e) {
        alert('Error loading analytics');
    } finally {
        document.getElementById('analytics-loading').style.display = 'none';
    }
}

function displayAnalytics(data) {
    const campaigns = data.campaigns || [];
    const totalSent = campaigns.reduce((s, c) => s + c.performance.sent, 0);
    const totalOpened = campaigns.reduce((s, c) => s + c.performance.opened, 0);
    const totalClicked = campaigns.reduce((s, c) => s + c.performance.clicked, 0);
    const totalCta = campaigns.reduce((s, c) => s + (c.performance.cta_clicked || 0), 0);
    const totalConverted = campaigns.reduce((s, c) => s + c.performance.converted, 0);
    const max = totalSent;

    [['sent',totalSent],['opened',totalOpened],['clicked',totalClicked],['cta',totalCta],['converted',totalConverted]].forEach(([key, val]) => {
        const el = document.getElementById('bar-' + key);
        const h = Math.max((val / max) * 130, 20);
        el.style.height = h + 'px';
        el.textContent = val.toLocaleString();
    });

    // Segment bars
    const dmC = campaigns.filter(c => c.segment === 'Decision Maker');
    const pbC = campaigns.filter(c => c.segment === 'Pressure Builder');
    const dmAvg = dmC.length ? (dmC.reduce((s,c) => s + c.performance.click_rate, 0) / dmC.length).toFixed(1) : 0;
    const pbAvg = pbC.length ? (pbC.reduce((s,c) => s + c.performance.click_rate, 0) / pbC.length).toFixed(1) : 0;
    document.getElementById('segment-bars').innerHTML = `
        <div class="segment-bar"><div class="segment-bar-label">Decision Makers</div><div class="segment-bar-track"><div class="segment-bar-fill" style="width:${dmAvg*2}%"></div></div><div class="segment-bar-value">${dmAvg}%</div></div>
        <div class="segment-bar"><div class="segment-bar-label">Pressure Builders</div><div class="segment-bar-track"><div class="segment-bar-fill" style="width:${pbAvg*2}%"></div></div><div class="segment-bar-value">${pbAvg}%</div></div>
    `;

    // Subject winner
    const stylePerf = {};
    campaigns.forEach(c => {
        if (!stylePerf[c.subject_style]) stylePerf[c.subject_style] = [];
        stylePerf[c.subject_style].push(c.performance.click_rate);
    });
    const styleAvgs = Object.entries(stylePerf).map(([style, rates]) => ({style, avg: (rates.reduce((a,b)=>a+b,0)/rates.length).toFixed(1)})).sort((a,b)=>b.avg-a.avg);
    document.getElementById('subject-winner').innerHTML = styleAvgs.map((s,i) => `
        <div class="segment-bar"><div class="segment-bar-label" style="text-transform:capitalize;">${s.style}</div><div class="segment-bar-track"><div class="segment-bar-fill" style="width:${s.avg*2}%; background:${i===0?'linear-gradient(135deg,#4ade80,#22c55e)':'linear-gradient(135deg,#6366f1,#a855f7)'}"></div></div><div class="segment-bar-value">${s.avg}%</div></div>
    `).join('');

    // CTA Performance
    const ctaPerf = {};
    campaigns.forEach(c => {
        const cta = c.cta_style || 'action';
        if (!ctaPerf[cta]) ctaPerf[cta] = [];
        ctaPerf[cta].push(c.performance.cta_rate || 0);
    });
    const ctaAvgs = Object.entries(ctaPerf).map(([cta, rates]) => ({cta, avg: (rates.reduce((a,b)=>a+b,0)/rates.length).toFixed(1)})).sort((a,b)=>b.avg-a.avg);
    document.getElementById('cta-performance').innerHTML = ctaAvgs.map((c,i) => `
        <div class="segment-bar"><div class="segment-bar-label" style="text-transform:capitalize;">${c.cta}</div><div class="segment-bar-track"><div class="segment-bar-fill" style="width:${c.avg*3}%; background:${i===0?'linear-gradient(135deg,#f59e0b,#ef4444)':'linear-gradient(135deg,#6366f1,#a855f7)'}"></div></div><div class="segment-bar-value">${c.avg}%</div></div>
    `).join('');

    // Matrix
    const matrix = data.matrix || {};
    const vps = ['Time Back', 'Consistency', 'Scalability', 'Better Output'];
    document.getElementById('matrix-body').innerHTML = Object.entries(matrix).map(([topic, vpData]) => `
        <tr><td>${topic}</td>${vps.map(vp => {
            const val = vpData[vp];
            if (val === '--') return '<td style="color:#555">—</td>';
            const cls = val >= 20 ? 'matrix-high' : val >= 15 ? 'matrix-mid' : 'matrix-low';
            return `<td class="matrix-value ${cls}">${val}%</td>`;
        }).join('')}</tr>
    `).join('');

    // Recommendations
    const rec = data.recommendations || {};
    document.getElementById('rec-insight').textContent = rec.key_insight || '';
    document.getElementById('rec-topic').textContent = rec.next_topic || '';
    document.getElementById('rec-vp').textContent = rec.next_value_prop || '';
    document.getElementById('rec-dm').textContent = rec.decision_maker_recommendation || '';
    document.getElementById('rec-pb').textContent = rec.pressure_builder_recommendation || '';
    document.getElementById('analytics-content').style.display = 'block';
}

async function loadHistory() {
    const res = await fetch('/history');
    const data = await res.json();
    if (!data.campaigns || data.campaigns.length === 0) {
        document.getElementById('no-history-msg').style.display = 'block';
        document.getElementById('history-content').style.display = 'none';
        return;
    }
    document.getElementById('no-history-msg').style.display = 'none';
    document.getElementById('history-content').style.display = 'block';

    // Overall metrics
    const campaigns = data.campaigns;
    const totalSent = campaigns.reduce((s,c) => s + c.dm_performance.sent + c.pb_performance.sent, 0);
    const totalOpened = campaigns.reduce((s,c) => s + c.dm_performance.opened + c.pb_performance.opened, 0);
    const totalClicked = campaigns.reduce((s,c) => s + c.dm_performance.clicked + c.pb_performance.clicked, 0);
    const totalCta = campaigns.reduce((s,c) => s + (c.dm_performance.cta_clicked||0) + (c.pb_performance.cta_clicked||0), 0);
    const totalConverted = campaigns.reduce((s,c) => s + c.dm_performance.converted + c.pb_performance.converted, 0);

    document.getElementById('overall-metrics').innerHTML = [
        {label:'Total Sent', value: totalSent.toLocaleString()},
        {label:'Total Opened', value: totalOpened.toLocaleString()},
        {label:'Total Clicked', value: totalClicked.toLocaleString()},
        {label:'CTA Clicked', value: totalCta.toLocaleString()},
        {label:'Converted', value: totalConverted.toLocaleString()}
    ].map(m => `<div class="metric-card"><div class="metric-value">${m.value}</div><div class="metric-label">${m.label}</div></div>`).join('');

    // Campaign list
    const avgOpenRate = totalSent > 0 ? ((totalOpened/totalSent)*100).toFixed(1) : 0;
    const avgClickRate = totalSent > 0 ? ((totalClicked/totalSent)*100).toFixed(1) : 0;

    document.getElementById('campaign-list').innerHTML = campaigns.map((c, i) => `
        <div class="history-card">
            <div class="history-card-header">
                <div>
                    <span style="font-weight:700; font-size:16px;">Campaign #${i+1}</span>
                    <span style="color:#888; font-size:13px; margin-left:12px;">${c.date}</span>
                </div>
                <div style="display:flex; gap:8px;">
                    <span class="tag tag-blue">${c.topic}</span>
                    <span class="tag tag-purple">${c.value_prop}</span>
                    ${c.mode === 'ab' ? '<span class="tag tag-green">A/B Test</span>' : ''}
                </div>
            </div>

            <div class="two-col" style="margin-bottom:12px;">
                <div>
                    <p style="font-size:12px; color:#888; margin-bottom:4px;">HOW IT WAS PERSONALIZED</p>
                    <p style="font-size:13px; color:#ccc;">Decision Makers received <strong style="color:#a5b4fc;">${c.dm_subject_style}</strong> subject + <strong style="color:#a5b4fc;">${c.dm_cta}</strong> CTA</p>
                    <p style="font-size:13px; color:#ccc;">Pressure Builders received <strong style="color:#fdba74;">${c.pb_subject_style}</strong> subject + <strong style="color:#fdba74;">${c.pb_cta}</strong> CTA</p>
                    <p style="font-size:12px; color:#888; margin-top:8px;">Behavior segment: <strong style="color:#5eead4;">${c.behavior_segment}</strong></p>
                </div>
                <div>
                    <p style="font-size:12px; color:#888; margin-bottom:4px;">THIS CAMPAIGN VS OVERALL AVERAGE</p>
                    <div class="vs-bar">
                        <div class="vs-item">
                            <div class="vs-value" style="color:${c.dm_performance.open_rate > avgOpenRate ? '#4ade80' : '#f87171'}">${c.dm_performance.open_rate}%</div>
                            <div class="vs-label">DM Open Rate</div>
                            <div style="font-size:10px; color:#888;">avg ${avgOpenRate}%</div>
                        </div>
                        <div class="vs-item">
                            <div class="vs-value" style="color:${c.pb_performance.open_rate > avgOpenRate ? '#4ade80' : '#f87171'}">${c.pb_performance.open_rate}%</div>
                            <div class="vs-label">PB Open Rate</div>
                            <div style="font-size:10px; color:#888;">avg ${avgOpenRate}%</div>
                        </div>
                        <div class="vs-item">
                            <div class="vs-value" style="color:${c.dm_performance.click_rate > avgClickRate ? '#4ade80' : '#f87171'}">${c.dm_performance.click_rate}%</div>
                            <div class="vs-label">DM Click Rate</div>
                            <div style="font-size:10px; color:#888;">avg ${avgClickRate}%</div>
                        </div>
                        <div class="vs-item">
                            <div class="vs-value" style="color:${c.pb_performance.click_rate > avgClickRate ? '#4ade80' : '#f87171'}">${c.pb_performance.click_rate}%</div>
                            <div class="vs-label">PB Click Rate</div>
                            <div style="font-size:10px; color:#888;">avg ${avgClickRate}%</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="history-metrics">
                <div class="history-metric"><div class="history-metric-value">${c.dm_performance.sent + c.pb_performance.sent}</div><div class="history-metric-label">Sent</div></div>
                <div class="history-metric"><div class="history-metric-value">${c.dm_performance.opened + c.pb_performance.opened}</div><div class="history-metric-label">Opened</div></div>
                <div class="history-metric"><div class="history-metric-value">${c.dm_performance.clicked + c.pb_performance.clicked}</div><div class="history-metric-label">Clicked</div></div>
                <div class="history-metric"><div class="history-metric-value">${(c.dm_performance.cta_clicked||0) + (c.pb_performance.cta_clicked||0)}</div><div class="history-metric-label">CTA Clicked</div></div>
                <div class="history-metric"><div class="history-metric-value">${c.dm_performance.converted + c.pb_performance.converted}</div><div class="history-metric-label">Converted</div></div>
            </div>
        </div>
    `).join('');
}

async function loadSegments() {
    document.getElementById('segments-loading').style.display = 'block';
    document.getElementById('segments-content').style.display = 'none';
    const res = await fetch('/segments');
    const data = await res.json();
    document.getElementById('segments-loading').style.display = 'none';

    const segments = [
        {name: 'Efficiency Seekers', key: 'Time Back', icon: '⚡', desc: 'Respond best to Time Back messaging', tag: 'tag-blue'},
        {name: 'Process Builders', key: 'Consistency', icon: '🔧', desc: 'Respond best to Consistency messaging', tag: 'tag-purple'},
        {name: 'Growth Drivers', key: 'Scalability', icon: '🚀', desc: 'Respond best to Scalability messaging', tag: 'tag-green'},
        {name: 'Quality Leaders', key: 'Better Output', icon: '✨', desc: 'Respond best to Better Output messaging', tag: 'tag-teal'}
    ];

    document.getElementById('behavior-grid').innerHTML = segments.map(s => `
        <div class="behavior-card">
            <div style="font-size:32px;">${s.icon}</div>
            <div class="behavior-count">${data.counts[s.key] || 0}</div>
            <div class="behavior-name">${s.name}</div>
            <div class="behavior-desc">${s.desc}</div>
        </div>
    `).join('');

    document.getElementById('segment-recommendations').innerHTML = segments.map(s => `
        <div class="recommendation-box" style="margin-bottom:12px;">
            <h3>${s.icon} ${s.name} (${data.counts[s.key] || 0} contacts)</h3>
            <p>${data.recommendations[s.key] || 'Run more campaigns to generate recommendations.'}</p>
        </div>
    `).join('');

    document.getElementById('segments-content').style.display = 'block';
}
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        topic = data['topic']
        value_prop = data['value_prop']
        content = generate_content(topic, value_prop, "both")
        filename = save_content(topic, value_prop, "both", content)
        return jsonify({'topic': topic, 'value_prop': value_prop, 'content': content, 'filename': filename})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/approve', methods=['POST'])
def approve():
    try:
        data = request.json
        topic = data['topic']
        value_prop = data['value_prop']
        dm_subject = data.get('dm_subject_style', 'direct')
        pb_subject = data.get('pb_subject_style', 'clickbait')
        dm_cta = data.get('dm_cta', 'action')
        pb_cta = data.get('pb_cta', 'curiosity')
        mode = data.get('mode', 'manual')

        # Simulate performance for both segments with actual choices
        dm_perf = simulate_performance(topic, value_prop, "Decision Maker", dm_subject, 38)
        pb_perf = simulate_performance(topic, value_prop, "Pressure Builder", pb_subject, 62)

        # Add CTA metrics
        dm_perf['cta_clicked'] = int(dm_perf['clicked'] * random.uniform(0.4, 0.7))
        pb_perf['cta_clicked'] = int(pb_perf['clicked'] * random.uniform(0.5, 0.8))
        dm_perf['cta_rate'] = round((dm_perf['cta_clicked'] / dm_perf['sent']) * 100, 1)
        pb_perf['cta_rate'] = round((pb_perf['cta_clicked'] / pb_perf['sent']) * 100, 1)

        # Determine behavior segment
        behavior_segment = BEHAVIOR_SEGMENTS.get(value_prop, "Efficiency Seeker")

        # Store in history
        campaign = {
            'topic': topic,
            'value_prop': value_prop,
            'dm_subject_style': dm_subject,
            'pb_subject_style': pb_subject,
            'dm_cta': dm_cta,
            'pb_cta': pb_cta,
            'mode': mode,
            'behavior_segment': behavior_segment,
            'dm_performance': dm_perf,
            'pb_performance': pb_perf,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        campaign_history.append(campaign)
        with open('segment_history.json', 'w') as f:
            json.dump(campaign_history, f, indent=2)

        # Log to HubSpot
        log_campaign(
            campaign_name=f"NovaMind — {topic}",
            topic=topic,
            value_prop=value_prop,
            segment="Both",
            contact_count=100
        )

        return jsonify({'success': True, 'campaign': campaign})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analytics')
def analytics():
    try:
        results = run_performance_analysis()
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history')
def history():
    return jsonify({'campaigns': campaign_history})

@app.route('/segments')
def segments():
    try:
        # Count contacts per behavior segment based on campaign history
        counts = {'Time Back': 0, 'Consistency': 0, 'Scalability': 0, 'Better Output': 0}
        recommendations = {}

        if campaign_history:
            for c in campaign_history:
                vp = c['value_prop']
                if vp in counts:
                    counts[vp] += 1

            # Generate recommendations per segment
            best_vp = max(campaign_history, key=lambda x: x['dm_performance']['click_rate'] + x['pb_performance']['click_rate'])
            for vp, name in BEHAVIOR_SEGMENTS.items():
                vp_campaigns = [c for c in campaign_history if c['value_prop'] == vp]
                if vp_campaigns:
                    avg_click = sum(c['dm_performance']['click_rate'] + c['pb_performance']['click_rate'] for c in vp_campaigns) / (len(vp_campaigns) * 2)
                    recommendations[vp] = f"Average click rate: {avg_click:.1f}%. {'Strong performer — double down.' if avg_click > 20 else 'Room to improve — try different topics.'}"
                else:
                    recommendations[vp] = "No campaigns run for this segment yet."
        else:
            # Default distribution from contacts
            counts = {'Time Back': 28, 'Consistency': 24, 'Scalability': 22, 'Better Output': 26}
            recommendations = {
                'Time Back': 'Projected 28 contacts. Best topics: Automating client communication, Repetitive operations.',
                'Consistency': 'Projected 24 contacts. Best topics: Generating automated reports, Workflow orchestration.',
                'Scalability': 'Projected 22 contacts. Best topics: AI-assisted decision making, Risk detection.',
                'Better Output': 'Projected 26 contacts. Best topics: Performance insights, Generating automated briefs.'
            }

        return jsonify({'counts': counts, 'recommendations': recommendations})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n🚀 NovaMind Pipeline running at http://127.0.0.1:5000\n")
    app.run(debug=True, port=5000)