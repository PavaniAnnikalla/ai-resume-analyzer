"""
AI Resume Analyzer — Premium Edition
======================================
Startup SaaS-grade UI with full analysis functionality:
  • PDF text extraction (PyPDF2)
  • Skill detection from predefined list
  • ATS score (rule-based, /100)
  • Best-fit role suggestion
  • Sidebar navigation
  • Glassmorphism dark theme

Run:  streamlit run app.py
"""

import streamlit as st
import PyPDF2
import io
import re
import math

# ── Must be first Streamlit call ──
st.set_page_config(
    page_title="ResumeIQ · AI Resume Analyzer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════
#  GLOBAL CSS  — Refined dark luxury with amber/gold accents
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500&family=Lato:wght@300;400;700&display=swap');

/* ── Root variables ── */
:root {
    --bg-base:      #080b12;
    --bg-surface:   #0d1117;
    --bg-card:      rgba(255,255,255,0.035);
    --border:       rgba(255,255,255,0.07);
    --border-glow:  rgba(251,191,36,0.25);
    --gold:         #fbbf24;
    --gold-light:   #fde68a;
    --gold-dim:     rgba(251,191,36,0.15);
    --teal:         #2dd4bf;
    --rose:         #fb7185;
    --text-primary: #f0f4f8;
    --text-muted:   #64748b;
    --text-sub:     #94a3b8;
    --radius-lg:    18px;
    --radius-md:    12px;
    --radius-sm:    8px;
    --shadow-glow:  0 0 40px rgba(251,191,36,0.08);
    --shadow-card:  0 8px 32px rgba(0,0,0,0.4);
}

/* ── Base reset ── */
html, body, [class*="css"] {
    font-family: 'Lato', sans-serif;
    color: var(--text-primary);
}

/* ── App background with subtle grid ── */
.stApp {
    background-color: var(--bg-base);
    background-image:
        linear-gradient(rgba(251,191,36,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(251,191,36,0.03) 1px, transparent 1px);
    background-size: 48px 48px;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--bg-surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 2rem;
}

/* ── Main content padding ── */
.block-container {
    padding: 2rem 2.5rem 4rem !important;
    max-width: 1080px;
}

/* ── Headings ── */
h1,h2,h3,h4,h5 {
    font-family: 'Syne', sans-serif !important;
    color: var(--text-primary) !important;
}

/* ── Logo in sidebar ── */
.sidebar-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0 1.2rem 2rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
}
.sidebar-logo-icon {
    width: 36px; height: 36px;
    background: var(--gold);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    box-shadow: 0 0 16px rgba(251,191,36,0.4);
}
.sidebar-logo-text {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.15rem;
    color: var(--text-primary);
    letter-spacing: -0.02em;
}
.sidebar-logo-text span { color: var(--gold); }

/* ── Sidebar nav item ── */
.nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0.6rem 1.2rem;
    border-radius: var(--radius-sm);
    margin: 0.15rem 0.5rem;
    cursor: pointer;
    color: var(--text-sub);
    font-size: 0.88rem;
    font-weight: 500;
    transition: all 0.2s;
}
.nav-item.active {
    background: var(--gold-dim);
    color: var(--gold);
    border: 1px solid var(--border-glow);
}
.nav-badge {
    margin-left: auto;
    background: var(--gold-dim);
    color: var(--gold);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    padding: 1px 7px;
    border-radius: 99px;
    border: 1px solid var(--border-glow);
}

/* ── Page header ── */
.page-header {
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
}
.page-header-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 0.4rem;
}
.page-header-title {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: var(--text-primary);
    margin: 0;
    line-height: 1.15;
}
.page-header-sub {
    color: var(--text-muted);
    font-size: 0.9rem;
    margin-top: 0.4rem;
    font-weight: 300;
}

/* ── Glass card ── */
.g-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.2rem;
    backdrop-filter: blur(12px);
    box-shadow: var(--shadow-card);
    transition: border-color 0.3s;
}
.g-card:hover { border-color: rgba(255,255,255,0.12); }
.g-card-accent {
    border-color: var(--border-glow);
    box-shadow: var(--shadow-card), var(--shadow-glow);
}

/* ── Card label ── */
.card-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 6px;
}
.card-label::before {
    content: '';
    display: inline-block;
    width: 14px; height: 2px;
    background: var(--gold);
    border-radius: 2px;
}

/* ── Metric card row ── */
.metric-row { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.2rem; }
.metric-card {
    flex: 1; min-width: 140px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1.1rem 1.3rem;
    position: relative;
    overflow: hidden;
}
.metric-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--gold);
    border-radius: 2px 2px 0 0;
}
.metric-card.teal::after { background: var(--teal); }
.metric-card.rose::after  { background: var(--rose); }
.metric-val {
    font-family: 'Syne', sans-serif;
    font-size: 1.9rem;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1;
    margin-bottom: 0.3rem;
}
.metric-lbl {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ── SVG gauge — rendered inline ── */
.gauge-wrap {
    display: flex;
    align-items: center;
    gap: 2.5rem;
    flex-wrap: wrap;
    padding: 0.5rem 0;
}
.gauge-meta h2 {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.6rem !important;
    margin: 0 0 0.3rem !important;
}
.gauge-meta p { color: var(--text-sub); font-size: 0.88rem; margin: 0; }

/* ── Skill chip ── */
.chip-group { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.4rem; }
.chip {
    font-size: 0.78rem;
    font-weight: 600;
    padding: 0.28rem 0.75rem;
    border-radius: 999px;
    letter-spacing: 0.02em;
}
.chip-gold  { background: rgba(251,191,36,0.12); color: #fbbf24; border: 1px solid rgba(251,191,36,0.3); }
.chip-teal  { background: rgba(45,212,191,0.10); color: #2dd4bf; border: 1px solid rgba(45,212,191,0.25); }
.chip-rose  { background: rgba(251,113,133,0.10); color: #fb7185; border: 1px solid rgba(251,113,133,0.25); }
.chip-slate { background: rgba(148,163,184,0.08); color: #94a3b8; border: 1px solid rgba(148,163,184,0.2); }

/* ── Role bar ── */
.role-bar-row {
    display: flex; align-items: center; gap: 0.8rem;
    margin-bottom: 0.7rem;
}
.role-bar-label {
    width: 160px; flex-shrink: 0;
    font-size: 0.82rem; color: var(--text-sub);
    font-weight: 500;
}
.role-bar-track {
    flex: 1; height: 8px;
    background: rgba(255,255,255,0.05);
    border-radius: 99px; overflow: hidden;
}
.role-bar-fill {
    height: 100%; border-radius: 99px;
    background: linear-gradient(90deg, var(--gold), #f59e0b);
    transition: width 0.6s cubic-bezier(.4,0,.2,1);
}
.role-bar-fill.best {
    background: linear-gradient(90deg, var(--teal), #059669);
    box-shadow: 0 0 12px rgba(45,212,191,0.4);
}
.role-bar-score {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: var(--text-muted);
    width: 28px; text-align: right;
}

/* ── Role badge ── */
.role-badge-wrap { margin: 0.8rem 0 1.2rem; }
.role-badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: linear-gradient(135deg, rgba(45,212,191,0.15), rgba(251,191,36,0.1));
    border: 1px solid rgba(45,212,191,0.35);
    color: var(--teal);
    font-family: 'Syne', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    padding: 0.55rem 1.3rem;
    border-radius: 999px;
    box-shadow: 0 0 24px rgba(45,212,191,0.15);
}

/* ── Tip card ── */
.tip-card {
    display: flex; align-items: flex-start; gap: 0.8rem;
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
}
.tip-icon { font-size: 0.9rem; margin-top: 1px; flex-shrink: 0; }
.tip-text { font-size: 0.85rem; color: var(--text-sub); line-height: 1.5; }

/* ── Upload zone ── */
[data-testid="stFileUploader"] {
    background: rgba(251,191,36,0.03) !important;
    border: 1.5px dashed rgba(251,191,36,0.25) !important;
    border-radius: var(--radius-md) !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(251,191,36,0.5) !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

/* ── Progress bar override ── */
.stProgress > div > div {
    background: linear-gradient(90deg, var(--gold), #f59e0b) !important;
    border-radius: 99px !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: #1e2a3a; border-radius: 99px; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  DATA — Skills & Roles
# ═══════════════════════════════════════════════════════════
SKILL_CATEGORIES = {
    "Programming": [
        "python","java","javascript","typescript","c++","c#","r","scala",
        "go","rust","swift","kotlin","php","ruby","matlab",
    ],
    "Web & Frontend": [
        "html","css","react","angular","vue","bootstrap","tailwind",
        "jquery","next.js","gatsby","webpack","sass","node.js","express",
    ],
    "Data & ML": [
        "machine learning","deep learning","nlp","computer vision",
        "tensorflow","pytorch","keras","scikit-learn","pandas","numpy",
        "matplotlib","seaborn","tableau","power bi","data analysis",
        "data visualization","statistics","neural network","regression",
        "classification","clustering","feature engineering",
    ],
    "Databases": [
        "sql","mysql","postgresql","mongodb","sqlite","redis",
        "cassandra","oracle","nosql","firebase",
    ],
    "Cloud & DevOps": [
        "aws","azure","gcp","docker","kubernetes","terraform",
        "ci/cd","jenkins","github actions","linux","bash",
        "cloudformation","lambda","ec2","s3",
    ],
    "Tools": [
        "git","github","jira","agile","scrum","rest api","graphql",
        "microservices","hadoop","spark","kafka","excel","figma",
    ],
}

ALL_SKILLS = {s for skills in SKILL_CATEGORIES.values() for s in skills}

CHIP_COLORS = ["chip-gold","chip-teal","chip-rose","chip-slate"]

ROLES = {
    "Data Analyst":      {"icon":"📊","required":["sql","excel","data analysis","python","statistics"],
                          "bonus":["tableau","power bi","pandas","numpy","data visualization","matplotlib","seaborn","r"],
                          "desc":"Turns raw data into business intelligence using querying & visualization."},
    "ML Intern":         {"icon":"🤖","required":["machine learning","python","scikit-learn"],
                          "bonus":["tensorflow","pytorch","keras","deep learning","nlp","numpy","pandas"],
                          "desc":"Builds and experiments with ML models under senior guidance."},
    "Software Engineer": {"icon":"💻","required":["python","java","git","sql"],
                          "bonus":["c++","rest api","microservices","docker","agile","jira","github","scrum"],
                          "desc":"Designs, builds, and maintains scalable software systems."},
    "Web Developer":     {"icon":"🌐","required":["html","css","javascript"],
                          "bonus":["react","angular","vue","node.js","next.js","typescript","bootstrap","tailwind"],
                          "desc":"Creates responsive, user-friendly web applications."},
    "Cloud Intern":      {"icon":"☁️","required":["aws","azure","gcp","linux"],
                          "bonus":["docker","kubernetes","terraform","bash","ci/cd","github actions","ec2","s3"],
                          "desc":"Assists in deploying and managing cloud infrastructure."},
}

RESUME_SECTIONS = [
    "experience","education","skills","projects","certifications",
    "summary","objective","achievements","publications","volunteer",
    "internship","work history","profile",
]


# ═══════════════════════════════════════════════════════════
#  CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════
def extract_text(file) -> str:
    text = ""
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        for page in reader.pages:
            t = page.extract_text()
            if t: text += t + "\n"
    except Exception as e:
        st.error(f"PDF read error: {e}")
    return text


def detect_skills(text: str) -> dict:
    low = text.lower()
    return {cat: [s for s in skills if re.search(r'\b'+re.escape(s)+r'\b', low)]
            for cat, skills in SKILL_CATEGORIES.items()
            if any(re.search(r'\b'+re.escape(s)+r'\b', low) for s in skills)}


def ats_score(text: str, skills: dict) -> tuple:
    score = 0; tips = []; low = text.lower()
    # Skills (50)
    total = sum(len(v) for v in skills.values())
    score += min(total * 3, 50)
    tips.append(("✦", f"{total} skills detected across your resume." if total >= 5
                 else "Add more technical skills to boost your ATS ranking."))
    # Length (15)
    wc = len(text.split())
    if wc >= 400:   score += 15; tips.append(("✦", f"Good resume length ({wc:,} words)."))
    elif wc >= 200: score += 8;  tips.append(("△", "Expand descriptions to 400+ words."))
    else:            tips.append(("⚠", "Resume is very short — add more detail."))
    # Sections (20)
    found = [s for s in RESUME_SECTIONS if s in low]
    score += min(len(found)*3, 20)
    missing = [s.title() for s in RESUME_SECTIONS if s not in low][:3]
    if missing: tips.append(("△", f"Consider adding: {', '.join(missing)}."))
    else:       tips.append(("✦", "All key resume sections present."))
    # Contact (10)
    has_email = bool(re.search(r'[\w.+-]+@[\w-]+\.[a-z]{2,}', low))
    has_phone = bool(re.search(r'(\+?\d[\d\s\-().]{7,}\d)', text))
    has_li    = "linkedin" in low
    score += (5 if has_email else 0)+(3 if has_phone else 0)+(2 if has_li else 0)
    if not has_email: tips.append(("⚠", "Email not detected — make sure it's visible."))
    if not has_li:    tips.append(("△", "Add your LinkedIn URL for recruiter credibility."))
    # Quantified (5)
    if re.search(r'\d+\s*(%|percent|x|times|users|customers|projects)', low):
        score += 5; tips.append(("✦", "Quantified achievements detected — great signal!"))
    else:
        tips.append(("△", "Add measurable results e.g. 'Improved speed by 30%'."))
    return min(score, 100), tips


def suggest_role(skills: dict) -> tuple:
    flat = {s for v in skills.values() for s in v}
    scores = {r: sum(1 for s in m["required"] if s in flat)*3 +
                 sum(1 for s in m["bonus"]    if s in flat)
              for r, m in ROLES.items()}
    best = max(scores, key=scores.get)
    return best, ROLES[best], scores


def gauge_svg(score: int) -> str:
    """Return an SVG arc gauge for the ATS score."""
    radius = 70; cx = cy = 90; stroke = 12
    circumference = math.pi * radius          # half-circle
    filled = circumference * (score / 100)

    if score >= 75:   color = "#2dd4bf"; label_color = "#2dd4bf"
    elif score >= 50: color = "#fbbf24"; label_color = "#fbbf24"
    else:             color = "#fb7185"; label_color = "#fb7185"

    grade = "Excellent" if score >= 75 else ("Good" if score >= 50 else ("Fair" if score >= 30 else "Needs Work"))

    return f"""
    <svg viewBox="0 0 180 110" width="220" height="140" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="{color}" stop-opacity="0.6"/>
          <stop offset="100%" stop-color="{color}"/>
        </linearGradient>
      </defs>
      <!-- Track arc -->
      <path d="M {cx-radius},{cy} A {radius},{radius} 0 0,1 {cx+radius},{cy}"
            fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="{stroke}"
            stroke-linecap="round"/>
      <!-- Filled arc -->
      <path d="M {cx-radius},{cy} A {radius},{radius} 0 0,1 {cx+radius},{cy}"
            fill="none" stroke="url(#g1)" stroke-width="{stroke}"
            stroke-linecap="round"
            stroke-dasharray="{filled:.1f} {circumference:.1f}"
            stroke-dashoffset="0"/>
      <!-- Score text -->
      <text x="{cx}" y="{cy-8}" text-anchor="middle"
            font-family="Syne,sans-serif" font-size="28" font-weight="800"
            fill="{label_color}">{score}</text>
      <text x="{cx}" y="{cy+12}" text-anchor="middle"
            font-family="IBM Plex Mono,monospace" font-size="9"
            fill="rgba(255,255,255,0.35)" letter-spacing="2">/ 100</text>
      <text x="{cx}" y="{cy+30}" text-anchor="middle"
            font-family="Syne,sans-serif" font-size="11" font-weight="600"
            fill="{label_color}" opacity="0.85">{grade}</text>
    </svg>"""


# ═══════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">⚡</div>
        <div class="sidebar-logo-text">Resume<span>IQ</span></div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["🏠  Dashboard", "📊  ATS Score", "🔑  Skills", "🎯  Role Match", "💡  Tips"],
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="padding: 1rem 1.2rem; background: rgba(251,191,36,0.06);
         border: 1px solid rgba(251,191,36,0.2); border-radius: 12px; margin: 0 0.5rem;">
        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.6rem;
             letter-spacing:0.12em; color:#fbbf24; margin-bottom:0.5rem;">HOW IT WORKS</div>
        <div style="font-size:0.78rem; color:#64748b; line-height:1.7;">
            1. Upload your PDF resume<br>
            2. AI extracts & analyzes text<br>
            3. Get your ATS score + tips<br>
            4. Discover your best-fit role
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="padding: 0 1.2rem; font-size: 0.72rem; color: #334155; line-height:1.6;">
        No data stored · Runs locally<br>
        Built with Python + Streamlit
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  PAGE HEADER
# ═══════════════════════════════════════════════════════════
st.markdown("""
<div class="page-header">
    <div class="page-header-eyebrow">AI-Powered · Rule-Based · Instant</div>
    <div class="page-header-title">Resume Analyzer</div>
    <div class="page-header-sub">Upload your PDF resume and get a detailed ATS breakdown in seconds.</div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  UPLOAD CARD
# ═══════════════════════════════════════════════════════════
st.markdown('<div class="g-card g-card-accent">', unsafe_allow_html=True)
st.markdown('<div class="card-label">Upload Resume</div>', unsafe_allow_html=True)
uploaded = st.file_uploader("Drop your PDF here or click to browse",
                             type=["pdf"], label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  ANALYSIS
# ═══════════════════════════════════════════════════════════
if uploaded:
    with st.spinner("Analyzing your resume…"):
        text = extract_text(uploaded)

    if not text.strip():
        st.error("⚠️ Could not extract text. Ensure your PDF is not a scanned image.")
        st.stop()

    skills   = detect_skills(text)
    score, tips = ats_score(text, skills)
    role, role_meta, role_scores = suggest_role(skills)
    total_skills = sum(len(v) for v in skills.values())
    word_count   = len(text.split())
    sections_hit = sum(1 for s in RESUME_SECTIONS if s in text.lower())

    # ── Quick metrics ──
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="metric-val">{score}</div>
            <div class="metric-lbl">ATS Score</div>
        </div>
        <div class="metric-card teal">
            <div class="metric-val">{total_skills}</div>
            <div class="metric-lbl">Skills Found</div>
        </div>
        <div class="metric-card rose">
            <div class="metric-val">{word_count:,}</div>
            <div class="metric-lbl">Word Count</div>
        </div>
        <div class="metric-card">
            <div class="metric-val">{sections_hit}</div>
            <div class="metric-lbl">Sections</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Determine active section from sidebar ──
    show_all = "Dashboard" in page

    # ═══ ATS SCORE GAUGE ═══
    if show_all or "ATS" in page:
        st.markdown('<div class="g-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-label">ATS Score Breakdown</div>', unsafe_allow_html=True)

        col_gauge, col_info = st.columns([1, 2], gap="large")
        with col_gauge:
            st.markdown(gauge_svg(score), unsafe_allow_html=True)

        with col_info:
            st.markdown(f"""
            <div style="padding-top:0.5rem;">
                <div style="font-family:'IBM Plex Mono',monospace; font-size:0.65rem;
                     letter-spacing:0.14em; color:#64748b; text-transform:uppercase;
                     margin-bottom:0.4rem;">Score interpretation</div>
                <div style="display:flex; flex-direction:column; gap:0.5rem; margin-top:0.6rem;">
                    {"".join([
                        f'<div style="display:flex;align-items:center;gap:0.6rem;">'
                        f'<div style="width:8px;height:8px;border-radius:50%;background:{"#2dd4bf" if t>=75 else "#fbbf24" if t>=50 else "#fb7185"};flex-shrink:0;"></div>'
                        f'<span style="font-size:0.8rem;color:#94a3b8;">'
                        f'{"75–100 · Excellent — ATS-ready" if t==75 else "50–74 · Good — minor improvements needed" if t==50 else "30–49 · Fair — needs more detail" if t==30 else "0–29 · Needs significant work"}</span></div>'
                        for t in [75, 50, 30, 0]
                    ])}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        # Sub-score breakdown
        score_items = [
            ("Skills Coverage",     min(total_skills*3, 50), 50),
            ("Resume Length",       15 if word_count>=400 else (8 if word_count>=200 else 0), 15),
            ("Section Keywords",    min(sections_hit*3, 20), 20),
            ("Contact Info",        10 if re.search(r'[\w.+-]+@[\w-]+\.[a-z]{2,}', text.lower()) else 5, 10),
            ("Quantified Impact",   5 if re.search(r'\d+\s*(%|percent|x|times|users)', text.lower()) else 0, 5),
        ]
        for label, val, mx in score_items:
            pct = val / mx if mx else 0
            st.markdown(f"""
            <div class="role-bar-row">
                <div class="role-bar-label">{label}</div>
                <div class="role-bar-track">
                    <div class="role-bar-fill" style="width:{pct*100:.0f}%"></div>
                </div>
                <div class="role-bar-score">{val}/{mx}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ═══ SKILLS ═══
    if show_all or "Skill" in page:
        st.markdown('<div class="g-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-label">Detected Skills</div>', unsafe_allow_html=True)

        if skills:
            for i, (cat, items) in enumerate(skills.items()):
                color = CHIP_COLORS[i % len(CHIP_COLORS)]
                st.markdown(f"""
                <div style="margin-bottom:1rem;">
                    <div style="font-family:'IBM Plex Mono',monospace; font-size:0.7rem;
                         color:#475569; letter-spacing:0.08em; margin-bottom:0.4rem;
                         text-transform:uppercase;">{cat}</div>
                    <div class="chip-group">
                        {"".join(f'<span class="chip {color}">{s}</span>' for s in items)}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No skills detected. Try a richer, text-based PDF resume.")

        st.markdown('</div>', unsafe_allow_html=True)

    # ═══ ROLE MATCH ═══
    if show_all or "Role" in page:
        st.markdown('<div class="g-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-label">Best-Fit Role</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="role-badge-wrap">
            <div class="role-badge">{role_meta['icon']}&nbsp; {role}</div>
        </div>
        <p style="color:#64748b; font-size:0.85rem; margin-bottom:1.4rem;">{role_meta['desc']}</p>
        """, unsafe_allow_html=True)

        max_s = max(role_scores.values()) or 1
        for r, s in sorted(role_scores.items(), key=lambda x: -x[1]):
            is_best = r == role
            pct = s / max_s * 100
            icon = ROLES[r]["icon"]
            st.markdown(f"""
            <div class="role-bar-row">
                <div class="role-bar-label" style="{'color:#2dd4bf;font-weight:700;' if is_best else ''}">
                    {icon} {r}
                </div>
                <div class="role-bar-track">
                    <div class="role-bar-fill {'best' if is_best else ''}" style="width:{pct:.0f}%"></div>
                </div>
                <div class="role-bar-score">{s}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ═══ TIPS ═══
    if show_all or "Tip" in page:
        st.markdown('<div class="g-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-label">Improvement Tips</div>', unsafe_allow_html=True)

        icon_map = {"✦": "✦", "△": "▲", "⚠": "⚠️"}
        for icon, tip in tips:
            border = ("rgba(45,212,191,0.2)" if icon=="✦"
                      else "rgba(251,191,36,0.2)" if icon=="△"
                      else "rgba(251,113,133,0.2)")
            st.markdown(f"""
            <div class="tip-card" style="border-left: 3px solid {border};">
                <div class="tip-icon">{icon}</div>
                <div class="tip-text">{tip}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Raw text expander ──
    with st.expander("🔍  View Extracted Resume Text"):
        st.markdown(f"""
        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.75rem;
             color:#475569; line-height:1.8; white-space:pre-wrap;
             max-height:320px; overflow-y:auto; padding:0.5rem;">
{text[:4000]}{"..." if len(text)>4000 else ""}
        </div>
        """, unsafe_allow_html=True)

else:
    # ── Empty state ──
    st.markdown("""
    <div style="text-align:center; padding:5rem 2rem;">
        <div style="font-size:3rem; margin-bottom:1.2rem; opacity:0.4;">⚡</div>
        <div style="font-family:'Syne',sans-serif; font-size:1.1rem;
             color:#334155; font-weight:600; margin-bottom:0.4rem;">
            Ready to analyze your resume
        </div>
        <div style="font-size:0.85rem; color:#1e2a3a;">
            Upload a text-based PDF above to get started
        </div>
    </div>
    """, unsafe_allow_html=True)