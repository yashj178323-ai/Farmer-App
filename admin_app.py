import os
import io
import csv
import time
import hashlib
import sqlite3
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from db_manager import (
    DB_FILE,
    get_district_officer_contact,
    init_db,
    fetch_logs_filtered,
    fetch_metrics,
    fetch_open_grievance,
    resolve_grievance,
    verify_officer,
    update_officer_password,
    fetch_low_confidence_logs,
    fetch_kiosk_status,
    ticket_age_hours,
    fetch_distinct_languages,
    fetch_distinct_kiosks,
    fetch_avg_latency_ms,
    fetch_knowledge_gap_count,
)
from report_generator import generate_weekly_report_pdf

init_db()

st.set_page_config(
    page_title="Sahakar-Vaani | PACS Governance Administration",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# Theme / layout
# -----------------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Source+Serif+4:wght@600;700;800&display=swap');

:root {
    --navy: #102a43;
    --navy-2: #173b5e;
    --navy-3: #0b2035;
    --slate: #334e68;
    --muted: #627d98;
    --line: #d9e2ec;
    --surface: rgba(255,255,255,.95);
    --surface-strong: rgba(255,255,255,.985);
    --saffron: #e67e22;
    --green: #138808;
    --blue: #1769aa;
    --danger: #b42318;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ------------------------------------------------------------------
   FULL-SCREEN AGRICULTURAL BACKDROP
   Green crop-field imagery stays around the portal edges while the
   dashboard itself remains a solid white government workspace.
   ------------------------------------------------------------------ */
.stApp {
    min-height: 100vh !important;
    background: #dfe9df !important;
    position: relative !important;
}
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background-image:
        linear-gradient(90deg, rgba(10,48,22,.24) 0%, rgba(20,76,30,.08) 18%, rgba(255,255,255,.02) 50%, rgba(20,76,30,.08) 82%, rgba(10,48,22,.24) 100%),
        linear-gradient(180deg, rgba(255,255,255,.06) 0%, rgba(20,75,30,.05) 48%, rgba(8,48,18,.30) 100%),
        url("https://images.unsplash.com/photo-1716650205028-af3e1b453c3a?auto=format&fit=crop&fm=jpg&q=88&w=2400");
    background-size: cover;
    background-position: center center;
    background-repeat: no-repeat;
}

[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
main,
section.main {
    background: transparent !important;
}
[data-testid="stHeader"] {
    background: transparent !important;
    backdrop-filter: none !important;
    box-shadow: none !important;
    height: 0 !important;
    min-height: 0 !important;
}
[data-testid="stHeader"] > div {
    background: transparent !important;
}
[data-testid="stToolbar"],
.stAppDeployButton {
    display: none !important;
}

/* ------------------------------------------------------------------
   MAIN CONTENT — clean glass panels with stronger contrast
   ------------------------------------------------------------------ */
.block-container {
    width: min(1180px, calc(100vw - 32px)) !important;
    max-width: 1180px !important;
    margin: 14px auto 28px !important;
    padding: 18px 24px 44px !important;
    background: #ffffff !important;
    border: 1px solid #d8e1e8 !important;
    border-radius: 22px !important;
    box-shadow: 0 18px 46px rgba(8,34,52,.16) !important;
    backdrop-filter: none !important;
    box-sizing: border-box !important;
    position: relative !important;
    z-index: 2 !important;
}

/* The authentication page should sit directly on the crop-field backdrop.
   The authenticated dashboard keeps its centered white workspace. */
.block-container:has(.login-shell) {
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
    padding-top: 18px !important;
    padding-bottom: 34px !important;
}

/* Predictable spacing prevents Streamlit columns and cards from visually colliding. */
[data-testid="stHorizontalBlock"] {
    gap: 1rem !important;
    align-items: stretch !important;
    margin-bottom: 12px !important;
}
[data-testid="column"] {
    min-width: 0 !important;
}

.gov-ribbon {
    height: 6px;
    border-radius: 99px;
    margin: 0 0 14px 0;
    background: linear-gradient(90deg, #ff9933 0 33.33%, #ffffff 33.33% 66.66%, #138808 66.66% 100%);
    box-shadow: 0 2px 8px rgba(0,0,0,.12);
}

.gov-header {
    margin: 0 0 20px 0;
    padding: 0;
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
}
.gov-header-grid {
    display: flex;
    align-items: center;
    gap: 14px;
    min-width: 0;
}
.gov-emblem {
    flex: 0 0 auto;
    width: 64px;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255,255,255,.94);
    border: 1px solid #d7e0e8;
    border-radius: 14px;
    padding: 8px;
    box-shadow: 0 8px 22px rgba(16,42,67,.10);
}
.gov-emblem img {
    width: 48px;
    height: 48px;
    object-fit: contain;
    display: block;
}
.gov-title-panel {
    min-width: 0;
    flex: 1 1 auto;
    background: rgba(255,255,255,.96);
    border: 1px solid rgba(215,224,232,.96);
    border-radius: 15px;
    padding: 11px 16px 10px;
    box-shadow: 0 9px 24px rgba(16,42,67,.08);
}
.gov-kicker {
    color: #58708a !important;
    font-size: .68rem;
    font-weight: 800;
    letter-spacing: .12em;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.gov-title {
    color: #102a43 !important;
    font-family: 'Source Serif 4', serif !important;
    font-size: 1.55rem;
    line-height: 1.12;
    font-weight: 800;
}
.gov-subtitle {
    color: #526b84 !important;
    font-size: .78rem;
    margin-top: 3px;
    line-height: 1.35;
}
.gov-title-panel .tricolor-bar {
    width: 100%;
    height: 3px;
    margin-top: 8px;
    border-radius: 999px;
    background: linear-gradient(90deg, #ff9933 0 33.33%, #ffffff 33.33% 66.66%, #138808 66.66% 100%);
    border: 1px solid rgba(16,42,67,.08);
}
.secure-pill {
    flex: 0 0 auto;
    background: rgba(236,253,243,.96);
    color: #166534 !important;
    border: 1px solid #bbf7d0;
    border-radius: 999px;
    padding: 8px 11px;
    font-size: .67rem;
    font-weight: 800;
    white-space: nowrap;
    box-shadow: 0 6px 16px rgba(22,101,52,.07);
}

.page-title {
    font-family: 'Source Serif 4', serif !important;
    color: #102a43 !important;
    text-shadow: 0 2px 18px rgba(255,255,255,.75);
    font-size: 2rem;
    line-height: 1.1;
    font-weight: 800;
    margin: 8px 0 5px;
    padding-bottom: 2px;
}
.page-subtitle {
    color: #294b68 !important;
    font-weight: 600;
    text-shadow: 0 1px 10px rgba(255,255,255,.82);
    margin-bottom: 22px;
    line-height: 1.5;
}
.section-title {
    font-family: 'Source Serif 4', serif !important;
    color: #102a43 !important;
    font-size: 1.28rem;
    font-weight: 800;
    margin: 4px 0 10px;
}
.small-muted {
    color: #627d98 !important;
    font-size: .76rem;
}

.card {
    background: rgba(255,255,255,.955) !important;
    border: 1px solid rgba(255,255,255,.90) !important;
    border-radius: 17px !important;
    padding: 18px 18px 16px !important;
    box-shadow: 0 12px 30px rgba(7,30,49,.15) !important;
    margin: 0 0 18px 0 !important;
    backdrop-filter: blur(11px);
    overflow: hidden !important;
}
.card-soft { background: rgba(248,250,252,.93) !important; }
.card-accent { border-left: 5px solid var(--saffron) !important; }
.card-green { border-left: 5px solid var(--green) !important; }
.card-blue { border-left: 5px solid var(--blue) !important; }
.card-danger { border-left: 5px solid var(--danger) !important; }

.metric-card {
    background: rgba(255,255,255,.975) !important;
    border: 1px solid rgba(255,255,255,.96) !important;
    border-radius: 15px !important;
    padding: 15px 16px !important;
    min-height: 118px !important;
    height: 100% !important;
    box-sizing: border-box !important;
    box-shadow: 0 10px 26px rgba(7,30,49,.14) !important;
    transition: transform .18s ease, box-shadow .18s ease;
}
.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 18px 34px rgba(7,30,49,.22) !important;
}
.metric-label {
    color: #526b84 !important;
    font-size: .72rem !important;
    font-weight: 800 !important;
    text-transform: uppercase;
    letter-spacing: .055em;
}
.metric-value {
    color: #102a43 !important;
    font-size: 1.8rem !important;
    line-height: 1.15;
    font-weight: 800 !important;
    margin-top: 6px;
}
.metric-note {
    color: #627d98 !important;
    font-size: .73rem !important;
    margin-top: 5px;
}

[data-testid="stMetric"] {
    background: rgba(255,255,255,.97) !important;
    border: 1px solid rgba(255,255,255,.95) !important;
    border-radius: 14px !important;
    padding: 13px !important;
    box-shadow: 0 8px 22px rgba(7,30,49,.11) !important;
}
[data-testid="stMetricLabel"] p {
    color: #526b84 !important;
    font-weight: 700 !important;
}
[data-testid="stMetricValue"] {
    color: #102a43 !important;
    font-weight: 800 !important;
}

/* ------------------------------------------------------------------
   CUSTOM HAMBURGER NAVIGATION
   The native Streamlit sidebar is hidden. The portal uses a compact
   three-line menu in the header so the dashboard stays centered.
   ------------------------------------------------------------------ */
[data-testid="stSidebar"] {
    display: none !important;
}

.menu-popover {
    background: #102a43 !important;
    color: #fff !important;
    border-radius: 13px !important;
}

.menu-popover-title {
    color: #102a43 !important;
    font-family: 'Source Serif 4', serif !important;
    font-size: 1.12rem;
    font-weight: 800;
    margin-bottom: 2px;
}
.menu-popover-subtitle {
    color: #627d98 !important;
    font-size: .72rem;
    margin-bottom: 12px;
    line-height: 1.45;
}

[data-testid="stPopover"] > button {
    width: 48px !important;
    height: 48px !important;
    min-height: 48px !important;
    padding: 0 !important;
    border-radius: 13px !important;
    background: #102a43 !important;
    border: 1px solid #173b5e !important;
    color: #fff !important;
    box-shadow: 0 8px 20px rgba(16,42,67,.18) !important;
    font-size: 1.55rem !important;
    line-height: 1 !important;
}
[data-testid="stPopover"] > button:hover {
    background: #173b5e !important;
    border-color: #173b5e !important;
}

.menu-user {
    margin-top: 12px;
    padding: 10px 11px;
    border-radius: 11px;
    background: #f3f7fa;
    border: 1px solid #d9e2ec;
}
.menu-user-name { color:#102a43 !important; font-weight:800; font-size:.78rem; }
.menu-user-role { color:#627d98 !important; font-size:.66rem; margin-top:3px; }

/* Keep the popover navigation compact and readable. */
[data-testid="stPopover"] div[role="radiogroup"] {
    gap: 5px !important;
}
[data-testid="stPopover"] div[role="radiogroup"] label {
    background: #f8fafc !important;
    border: 1px solid #d9e2ec !important;
    border-radius: 9px !important;
    padding: 7px 9px !important;
    margin: 2px 0 !important;
}
[data-testid="stPopover"] div[role="radiogroup"] label:hover {
    background: #eef5fa !important;
    border-color: #b9cbe0 !important;
}
[data-testid="stPopover"] div[role="radiogroup"] label:has(input:checked) {
    background: #eaf2f8 !important;
    border-color: #9eb7cc !important;
    box-shadow: inset 4px 0 0 #ff9933 !important;
}
[data-testid="stPopover"] div[role="radiogroup"] label p {
    color: #102a43 !important;
    font-size: .76rem !important;
    font-weight: 700 !important;
}

/* ------------------------------------------------------------------
   STREAMLIT WIDGETS / TABLES — remove washed-out text and collisions
   ------------------------------------------------------------------ */
.stButton > button, .stDownloadButton > button {
    border-radius: 10px !important;
    font-weight: 700 !important;
    min-height: 40px !important;
    border: 1px solid #ccd7e3 !important;
    background: #fff !important;
    color: #102a43 !important;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: #9eb0c4 !important;
    background: #f8fafc !important;
}
button[kind="primary"] {
    background: #102a43 !important;
    color: #fff !important;
    border-color: #102a43 !important;
}

[data-testid="stDataFrame"] {
    background: rgba(255,255,255,.98) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    box-shadow: 0 7px 18px rgba(7,30,49,.10) !important;
}

div[data-baseweb="tab-list"] {
    gap: 5px;
    background: rgba(255,255,255,.70);
    padding: 5px;
    border-radius: 12px;
}
button[data-baseweb="tab"] { font-weight: 700 !important; }

.login-shell { max-width: 590px; margin: 6vh auto 0; position:relative; z-index:2; }
.login-card {
    background: rgba(255,255,255,.965) !important;
    border: 1px solid rgba(255,255,255,.92) !important;
    border-radius: 21px !important;
    padding: 31px !important;
    box-shadow: 0 22px 60px rgba(7,30,49,.22) !important;
    backdrop-filter: blur(13px);
}
.login-title {
    font-family: 'Source Serif 4', serif !important;
    color: #102a43 !important;
    font-size: 2rem;
    font-weight: 800;
}
.login-note { color:#526b84 !important; font-size:.88rem; line-height:1.55; }

.alert-box { border-radius:12px; padding:12px 14px; border:1px solid #fecaca; background:#fff7f7; color:#991b1b; font-weight:700; }
.info-box { border-radius:12px; padding:12px 14px; border:1px solid #bfdbfe; background:#eff6ff; color:#1e40af; font-weight:600; }

@media (min-width: 1400px) {
    .block-container {
        width: 1180px !important;
    }
}

/* Responsive cleanup */
@media (max-width: 900px) {
    .gov-header-grid {
        flex-wrap: wrap;
    }
    .gov-title-panel {
        flex: 1 1 calc(100% - 82px);
    }
    .secure-pill {
        margin-left: 78px;
    }
    .block-container { width: calc(100vw - 18px) !important; max-width: none !important; padding: .8rem .75rem 2.5rem !important; margin: 8px auto 1.5rem !important; border-radius: 18px !important; }
    [data-testid="stHorizontalBlock"] { gap: .65rem !important; }
    .gov-header-grid { align-items:flex-start; }
    .gov-title { font-size:1.35rem; }
    .secure-pill { display:none; }
}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def html_card(content, cls=""):
    st.markdown(f'<div class="card {cls}">{content}</div>', unsafe_allow_html=True)


def metric_card(label, value, note="", cls=""):
    st.markdown(
        f'<div class="metric-card {cls}"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',
        unsafe_allow_html=True,
    )


def safe_call(name, default=None, *args, **kwargs):
    """Call an existing db_manager helper without letting an optional widget crash the portal."""
    try:
        module = __import__("db_manager", fromlist=[name])
        fn = getattr(module, name)
        return fn(*args, **kwargs)
    except Exception:
        return default


def normalize_status(value):
    return str(value or "UNKNOWN").replace("_", " ").upper()


def make_download(data, label, filename, mime):
    if data is None:
        st.warning("No export data is currently available.")
        return
    st.download_button(label, data=data, file_name=filename, mime=mime, use_container_width=False)


# -----------------------------------------------------------------------------
# Authentication — authorized personnel only
# -----------------------------------------------------------------------------
# TEMPORARY BOOTSTRAP ACCOUNT
# Remove/replace these values before any real government deployment.
# The password is stored as a SHA-256 hash rather than plain text in the code.
TEMP_ADMIN_USERNAME = os.getenv("TEMP_ADMIN_USERNAME", "admin_pacs").strip()
TEMP_ADMIN_PASSWORD_SHA256 = os.getenv(
    "TEMP_ADMIN_PASSWORD_SHA256",
    "81b288c4eae1971245d697ec648ce3f7d6248da88c23f17e833ea3278d85c6c9",
).strip().lower()
TEMP_ADMIN_LABEL = "Temporary Bootstrap Officer"

# The actual temporary password for the default account is: Temp@2026!
# Keep this account only for initial testing and replace it with DB-backed
# officer authentication before production deployment.

def verify_admin_credentials(username, password):
    username = (username or "").strip()
    password = password or ""
    if not username or not password:
        return False

    # 1) Preferred project-native authentication.
    try:
        result = verify_officer(username, password)
        if isinstance(result, bool):
            if result:
                return True
        elif result is not None and bool(result):
            return True
    except TypeError:
        try:
            result = verify_officer(username=username, password=password)
            if isinstance(result, bool):
                if result:
                    return True
            elif result is not None and bool(result):
                return True
        except Exception:
            pass
    except Exception:
        pass

    # 2) Temporary bootstrap account for first-time local testing.
    # This is intentionally separate from the normal officer database.
    if username == TEMP_ADMIN_USERNAME:
        supplied_hash = hashlib.sha256(password.encode("utf-8")).hexdigest().lower()
        if supplied_hash == TEMP_ADMIN_PASSWORD_SHA256:
            return True

    # 3) Optional environment fallback for deployments that do not use the DB auth helper.
    env_user = os.getenv("ADMIN_USERNAME", "").strip()
    env_hash = os.getenv("ADMIN_PASSWORD_SHA256", "").strip().lower()
    if env_user and env_hash and username == env_user:
        return hashlib.sha256(password.encode("utf-8")).hexdigest().lower() == env_hash
    return False


if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False
if "admin_username" not in st.session_state:
    st.session_state.admin_username = ""
if "admin_auth_source" not in st.session_state:
    st.session_state.admin_auth_source = ""

if not st.session_state.admin_authenticated:
    st.markdown('<div class="gov-ribbon"></div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="login-shell">
          <div class="login-card">
            <div class="gov-kicker">PACS Governance Network</div>
            <div class="login-title">🏛️ Sahakar-Vaani Administration</div>
            <div class="login-note" style="margin-top:8px;">
              Restricted administrative console for authorised government and PACS officers.
              Operational telemetry, grievance records, policy indexing, reports and system controls
              are available only after successful officer authentication.
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    with st.form("admin_login", clear_on_submit=False):
        username = st.text_input("Officer ID / Username", placeholder="Enter authorised officer ID")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        submitted = st.form_submit_button("🔐 Sign in to secure portal", type="primary", use_container_width=True)
        if submitted:
            if verify_admin_credentials(username, password):
                st.session_state.admin_authenticated = True
                st.session_state.admin_username = username
                st.session_state.admin_auth_source = (
                    "temporary bootstrap" if username == TEMP_ADMIN_USERNAME else "authorised officer"
                )
                safe_call("log_admin_access_event", None, username)
                st.rerun()
            else:
                st.error("Authentication failed. Please use an authorised officer account.")
    st.info(
        f"Temporary testing account enabled: Officer ID `{TEMP_ADMIN_USERNAME}`. "
        "Use the temporary password supplied with this build. Replace this account before production use.",
        icon="🔐",
    )
    st.caption("Access is restricted to authorised personnel. Do not share credentials.")
    st.stop()

# -----------------------------------------------------------------------------
# Header / custom hamburger navigation
# -----------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="gov-header">
      <div class="gov-header-grid">
        <div class="gov-emblem">
          <img src="https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg" alt="Government of India emblem">
        </div>
        <div class="gov-title-panel">
          <div class="gov-kicker">PACS Governance Network • Administrative Console</div>
          <div class="gov-title">Sahakar-Vaani Government Operations Portal</div>
          <div class="gov-subtitle">Secure oversight of multilingual agricultural voice kiosks, grievances, policy knowledge and operational telemetry.</div>
          <div class="tricolor-bar"></div>
        </div>
        <div class="secure-pill">● AUTHENTICATED OFFICER</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# The hamburger is intentionally placed below the title row so it never pushes
# the dashboard outside the centered content width.
nav_left, nav_spacer = st.columns([0.08, 0.92], gap="small")
with nav_left:
    with st.popover("☰", help="Open portal features"):
        st.markdown('<div class="menu-popover-title">Portal features</div>', unsafe_allow_html=True)
        st.markdown('<div class="menu-popover-subtitle">Select an administrative area.</div>', unsafe_allow_html=True)
        menu = st.radio(
            "Portal navigation",
            [
                "Executive Overview",
                "Kiosk Operations",
                "Grievance & SLA",
                "Telemetry & Analytics",
                "Knowledge & Reports",
                "Security & Maintenance",
            ],
            key="portal_menu",
            label_visibility="collapsed",
        )
        st.markdown(
            f"""
            <div class="menu-user">
              <div class="menu-user-name">👤 {st.session_state.admin_username or 'Authorised Officer'}</div>
              <div class="menu-user-role">{TEMP_ADMIN_LABEL if st.session_state.admin_auth_source == 'temporary bootstrap' else 'Government / PACS Administrative Access'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🚪 Sign out", key="menu_sign_out", use_container_width=True):
            st.session_state.admin_authenticated = False
            st.session_state.admin_username = ""
            st.session_state.admin_auth_source = ""
            st.rerun()

# Log current session access without blocking the UI.
safe_call("log_admin_access_event", None, st.session_state.admin_username or "ADMIN")

# -----------------------------------------------------------------------------
# EXECUTIVE OVERVIEW
# -----------------------------------------------------------------------------
if menu == "Executive Overview":
    st.markdown('<div class="page-title">Executive Operations Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">National PACS kiosk network status, service quality and officer workload at a glance.</div>', unsafe_allow_html=True)

    daily = safe_call("fetch_daily_performance_summary", {
        "today_queries": 0, "avg_latency_ms": 0, "avg_confidence_pct": 0
    }) or {}
    active_nodes = safe_call("fetch_active_kiosk_nodes", []) or []
    escalated = safe_call("fetch_escalated_grievances", [], max_hours=48) or []
    gaps = safe_call("fetch_recent_knowledge_gaps", [], 5) or []
    sla = safe_call("fetch_grievance_sla_breakdown", {
        "under_24h": 0, "warning_24_48h": 0, "breached_48h": 0
    }) or {}

    total_nodes = len(active_nodes)
    online_nodes = sum(1 for row in active_nodes if len(row) >= 5 and str(row[4]).upper() in {"ONLINE", "ACTIVE"})
    online_text = f"{online_nodes}/{total_nodes} reported online" if total_nodes else "No kiosk heartbeat data"

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("Queries today", daily.get("today_queries", 0), "Current operating day", "card-blue")
    with c2: metric_card("Average latency", f"{daily.get('avg_latency_ms', 0)} ms", "Recorded kiosk response time", "card-accent")
    with c3: metric_card("RAG match quality", f"{daily.get('avg_confidence_pct', 0)}%", "Average grounding confidence", "card-green")
    with c4: metric_card("SLA breaches", sla.get("breached_48h", len(escalated)), "Open tickets older than 48 hours", "card-danger")

    # Full-width operational posture keeps all three signals aligned and
    # prevents nested Streamlit columns from creating uneven vertical blocks.
    html_card('<div class="section-title">Operational posture</div><div class="small-muted">Live signals from the kiosk and governance database.</div>', "card-blue")
    p1, p2, p3 = st.columns(3)
    with p1:
        metric_card("Kiosk nodes", total_nodes, "Registered / reporting nodes")
    with p2:
        metric_card("Online", online_nodes, online_text, "card-green")
    with p3:
        metric_card("Knowledge gaps", len(gaps), "Recent unresolved retrieval gaps", "card-accent")

    st.markdown('<div class="section-title">Officer attention queue</div>', unsafe_allow_html=True)
    if escalated:
        qcols = st.columns(2)
        for idx, (t_id, ts, k_id, ph, q, age) in enumerate(escalated[:6]):
            with qcols[idx % 2]:
                st.markdown(
                    f'<div class="card card-danger"><b>{t_id}</b> • {int(age)}h pending<br>'
                    f'<span class="small-muted">Kiosk {k_id} • {ph}</span><br>{str(q)[:120]}</div>',
                    unsafe_allow_html=True,
                )
    else:
        st.success("No grievance tickets currently beyond the 48-hour SLA threshold.")

    st.markdown('<div class="section-title">Kiosk network</div>', unsafe_allow_html=True)
    if active_nodes:
        rows = []
        for row in active_nodes:
            k_id, state, district, last_seen, status = row[:5]
            rows.append({"Kiosk": k_id, "State": state, "District": district, "Last seen": last_seen, "Status": status})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No kiosk heartbeat records are available yet.")

    st.markdown('<div class="section-title">Service mix today</div>', unsafe_allow_html=True)
    cat_stats = safe_call("fetch_today_category_breakdown", {}) or {}
    cols = st.columns(4)
    for col, label, key in zip(
        cols,
        ["KCC / Credit", "Crop insurance", "PACS bylaws", "General schemes"],
        ["LOAN_KCC", "CROP_INSURANCE", "PACS_BYLAWS", "GENERAL_SCHEMES"],
    ):
        with col:
            metric_card(label, cat_stats.get(key, 0), "Queries recorded today")

    st.markdown('<div class="section-title">Language usage</div>', unsafe_allow_html=True)
    lang_stats = safe_call("fetch_language_breakdown_stats", {}) or {}
    if lang_stats:
        df_lang = pd.DataFrame(list(lang_stats.items()), columns=["Language", "Queries"])
        st.bar_chart(df_lang.set_index("Language"), height=300)
    else:
        st.info("Language telemetry will appear after kiosk queries are recorded.")

# -----------------------------------------------------------------------------
# KIOSK OPERATIONS
# -----------------------------------------------------------------------------
elif menu == "Kiosk Operations":
    st.markdown('<div class="page-title">Kiosk Operations Centre</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Monitor terminal heartbeats, hardware resources, cache storage and broadcast controls.</div>', unsafe_allow_html=True)

    tabs = st.tabs(["Live fleet", "Hardware health", "Broadcast", "Storage & backups"])

    with tabs[0]:
        st.markdown('<div class="section-title">Registered PACS kiosk terminals</div>', unsafe_allow_html=True)
        active_nodes = safe_call("fetch_active_kiosk_nodes", []) or []
        if active_nodes:
            for start in range(0, len(active_nodes), 3):
                cols = st.columns(3)
                for col, row in zip(cols, active_nodes[start:start+3]):
                    k_id, state, district, last_seen, status = row[:5]
                    online = str(status).upper() in {"ONLINE", "ACTIVE"}
                    with col:
                        html_card(
                            f'<b>Kiosk {k_id}</b><br><span class="small-muted">{state} • {district}</span><br>'
                            f'<span class="status-pill {"status-online" if online else "status-offline"}">● {status}</span><br>'
                            f'<span class="small-muted">Last heartbeat: {last_seen}</span>',
                            "card-green" if online else "card-danger",
                        )
        else:
            st.info("No active kiosk heartbeats logged yet.")

        st.markdown('<div class="section-title">District telemetry explorer</div>', unsafe_allow_html=True)
        district = st.text_input("District name", value="Pune District", key="district_explorer")
        if st.button("Fetch district telemetry", key="fetch_district"):
            rows = safe_call("fetch_logs_by_district", [], district) or []
            if rows:
                df = pd.DataFrame(rows, columns=["Timestamp", "Kiosk", "Language", "Query", "Response"][:len(rows[0])])
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info(f"No query telemetry found for {district}.")

    with tabs[1]:
        st.markdown('<div class="section-title">Cluster subsystem diagnostics</div>', unsafe_allow_html=True)
        sys_h = safe_call("get_system_health", {}) or {}
        vec_h = safe_call("verify_vector_search_health", {}) or {}
        net_online = safe_call("is_internet_available", False)
        a, b, c = st.columns(3)
        with a: st.metric("SQLite telemetry DB", sys_h.get("db_status", "Unknown"), f"{sys_h.get('disk_free_gb', 0)} GB free")
        with b: st.metric("ChromaDB vector engine", vec_h.get("status", "Unknown"), f"{vec_h.get('collection_count', vec_h.get('collections', 0))} collections")
        with c: st.metric("Groq cloud link", "ONLINE" if net_online else "OFFLINE", "Fallback available")

        st.markdown('<div class="section-title">Hardware resource telemetry</div>', unsafe_allow_html=True)
        hw = safe_call("fetch_hardware_resource_telemetry", {}) or {}
        h1, h2, h3 = st.columns(3)
        with h1: st.metric("CPU", f"{hw.get('cpu_pct', 0)}%")
        with h2: st.metric("RAM", f"{hw.get('ram_pct', 0)}%")
        with h3: st.metric("Disk", f"{hw.get('disk_pct', 0)}%")
        if st.button("Run full diagnostic check"):
            health = safe_call("get_system_health", {}) or {}
            st.success(f"Diagnostic completed at {health.get('timestamp', datetime.now().isoformat())}.")
            st.json(health)

    with tabs[2]:
        st.markdown('<div class="section-title">Kiosk notice broadcast</div>', unsafe_allow_html=True)
        st.caption("Publish a controlled notice to kiosk terminals through the existing PACS broadcast mechanism.")
        notice = st.text_area("Announcement", height=100, placeholder="Enter the approved notice for kiosk screens…")
        if st.button("Publish notice to kiosk network", type="primary"):
            if notice.strip():
                ok = safe_call("set_pacs_broadcast_message", False, notice.strip())
                st.success("Broadcast notice updated across kiosk terminals." if ok is not False else "Broadcast notice submitted.")
            else:
                st.warning("Enter an announcement before publishing.")

    with tabs[3]:
        st.markdown('<div class="section-title">Storage and backup controls</div>', unsafe_allow_html=True)
        db_mb = safe_call("get_db_file_size_mb", 0) or 0
        cache_mb = safe_call("get_audio_cache_size", 0) or 0
        m1, m2 = st.columns(2)
        with m1: metric_card("Database size", f"{db_mb} MB", "SQLite telemetry database")
        with m2: metric_card("Audio cache", f"{cache_mb} MB", "Cached recordings and responses")

        if os.path.exists(DB_FILE):
            with open(DB_FILE, "rb") as db_f:
                st.download_button(
                    "📦 Download SQLite database backup",
                    data=db_f.read(),
                    file_name=f"sahakar_vaani_db_{datetime.now().strftime('%Y%m%d')}.db",
                    mime="application/x-sqlite3",
                )

        a, b, c = st.columns(3)
        with a:
            if st.button("Clear expired audio cache"):
                n = safe_call("cleanup_old_audio_cache", 0)
                st.success(f"Cleared {n} expired audio files.")
        with b:
            if st.button("Validate audio cache"):
                n = safe_call("validate_and_clean_audio_cache", 0)
                st.success(f"Removed {n} invalid audio files.")
        with c:
            if st.button("Optimize SQLite storage"):
                ok = safe_call("optimize_sqlite_database", False)
                st.success("SQLite storage optimized." if ok else "SQLite optimization could not be completed.")

        if st.button("Create compressed database backup (.db.gz)"):
            archive = safe_call("generate_compressed_db_backup", None)
            if archive:
                st.success(f"Backup created: {os.path.basename(archive)}")
            else:
                st.error("Backup could not be created.")

# -----------------------------------------------------------------------------
# GRIEVANCE & SLA
# -----------------------------------------------------------------------------
elif menu == "Grievance & SLA":
    st.markdown('<div class="page-title">Grievance Redressal & SLA Centre</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Review farmer grievances, assign action, track SLA ageing and maintain the resolution audit trail.</div>', unsafe_allow_html=True)

    tabs = st.tabs(["Open tickets", "SLA workload", "Ticket action", "Exports"])

    with tabs[0]:
        grievances = safe_call("fetch_all_grievances", pd.DataFrame())
        if not isinstance(grievances, pd.DataFrame):
            grievances = pd.DataFrame(grievances or [])
        if grievances.empty:
            st.info("No grievance records are currently available.")
        else:
            st.markdown('<div class="section-title">Active grievance register</div>', unsafe_allow_html=True)
            edited = st.data_editor(
                grievances,
                column_config={
                    "id": st.column_config.NumberColumn("ID", disabled=True),
                    "ticket_id": st.column_config.TextColumn("Ticket ID", disabled=True),
                    "phone": st.column_config.TextColumn("Farmer mobile"),
                    "query": st.column_config.TextColumn("Issue description"),
                    "status": st.column_config.SelectboxColumn("Status", options=["OPEN", "IN_PROGRESS", "RESOLVED", "REJECTED", "ESCALATED"], required=True),
                    "priority": st.column_config.SelectboxColumn("Priority", options=["LOW", "NORMAL", "HIGH", "CRITICAL"], required=True),
                },
                hide_index=True,
                num_rows="fixed",
                use_container_width=True,
            )
            if st.button("Save grievance changes", type="primary"):
                for _, row in edited.iterrows():
                    safe_call("update_grievance_status", None, row.get("ticket_id", row.get("id")), row.get("status", "OPEN"), row.get("priority", "NORMAL"))
                st.success("Grievance records updated.")
                st.rerun()

            st.markdown('<div class="section-title">Officer notification</div>', unsafe_allow_html=True)
            ticket_options = grievances["ticket_id"].tolist() if "ticket_id" in grievances.columns else grievances["id"].tolist()
            selected = st.selectbox("Ticket", ticket_options)
            phone = st.text_input("Officer mobile number")
            if st.button("Send officer alert"):
                safe_call("notify_pacs_officer", None, selected, phone, "Grievance requires officer action.")
                st.success(f"Notification dispatched for {selected}.")

    with tabs[1]:
        sla = safe_call("fetch_grievance_sla_breakdown", {"under_24h": 0, "warning_24_48h": 0, "breached_48h": 0}) or {}
        a, b, c = st.columns(3)
        with a: metric_card("Fresh", sla.get("under_24h", 0), "Under 24 hours")
        with b: metric_card("SLA warning", sla.get("warning_24_48h", 0), "24–48 hours")
        with c: metric_card("Overdue", sla.get("breached_48h", 0), "Over 48 hours", "card-danger")

        overdue = safe_call("fetch_escalated_grievances", [], max_hours=48) or []
        if overdue:
            st.error(f"{len(overdue)} ticket(s) have crossed the 48-hour SLA threshold.")
            for t_id, ts, k_id, ph, q, age in overdue:
                st.markdown(f'<div class="card card-danger"><b>{t_id}</b> • {int(age)} hours pending • Kiosk {k_id}<br>{q}</div>', unsafe_allow_html=True)
        else:
            st.success("No tickets are currently beyond the 48-hour SLA threshold.")

        avg_hours = safe_call("fetch_average_resolution_time_hours", 0) or 0
        st.metric("Average ticket resolution time", f"{avg_hours} hours")

    with tabs[2]:
        st.markdown('<div class="section-title">Ticket action controller</div>', unsafe_allow_html=True)
        t_id = st.text_input("Ticket ID", key="action_ticket")
        status = st.selectbox("New status", ["IN_PROGRESS", "RESOLVED", "REJECTED", "ESCALATED"])
        notes = st.text_area("Officer action notes / remarks")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Submit status update", type="primary"):
                if t_id.strip():
                    safe_call("update_grievance_status", None, t_id.strip(), status, notes)
                    st.success(f"Ticket {t_id} updated to {status}.")
                else:
                    st.warning("Enter a valid ticket ID.")
        with c2:
            if st.button("Elevate to HIGH priority"):
                if t_id.strip():
                    safe_call("escalate_grievance_priority", None, t_id.strip(), "HIGH")
                    st.success(f"Ticket {t_id} elevated to HIGH priority.")

        st.markdown('<div class="section-title">Ticket lifecycle history</div>', unsafe_allow_html=True)
        inspect = st.text_input("Ticket ID to inspect", key="timeline_ticket")
        if inspect:
            timeline = safe_call("fetch_ticket_history_timeline", [], inspect) or []
            if timeline:
                for ts, old_st, new_st, note in timeline:
                    st.markdown(f'<div class="card"><b>{ts}</b> • {old_st} → <b>{new_st}</b><br><span class="small-muted">{note}</span></div>', unsafe_allow_html=True)
            else:
                st.info("No lifecycle history found for this ticket.")

        st.markdown('<div class="section-title">Nodal officer assignment</div>', unsafe_allow_html=True)
        ac1, ac2 = st.columns(2)
        assign_ticket = ac1.text_input("Ticket ID to assign", key="assign_ticket")
        officer = ac2.selectbox("Nodal officer", ["Officer Deshmukh (Pune)", "Officer Patil (Shirur)", "Officer Shinde (Baramati)"])
        if st.button("Assign nodal officer"):
            if assign_ticket:
                safe_call("record_admin_audit_event", None, st.session_state.admin_username, "OFFICER_ASSIGNED", f"Assigned {assign_ticket} to {officer}")
                st.success(f"Ticket {assign_ticket} assigned to {officer}.")

    with tabs[3]:
        csv_data = safe_call("export_grievances_to_csv", None)
        make_download(csv_data, "📄 Download grievance register (.CSV)", "Sahakar_Vaani_Grievances.csv", "text/csv")
        if st.button("Bulk resolve all open tickets"):
            count = safe_call("bulk_resolve_open_grievances", 0)
            st.success(f"{count} open tickets were updated.")

# -----------------------------------------------------------------------------
# TELEMETRY & ANALYTICS
# -----------------------------------------------------------------------------
elif menu == "Telemetry & Analytics":
    st.markdown('<div class="page-title">Telemetry, Analytics & Audit</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Inspect query activity, latency, language distribution, trends and officer audit events.</div>', unsafe_allow_html=True)

    tabs = st.tabs(["Query logs", "Performance", "Languages & traffic", "Audit trail"])

    with tabs[0]:
        logs = safe_call("fetch_logs_filtered", None)
        if logs is None:
            logs = safe_call("fetch_low_confidence_logs", []) or []
        if isinstance(logs, pd.DataFrame):
            st.dataframe(logs, use_container_width=True, hide_index=True)
        elif logs:
            st.dataframe(pd.DataFrame(logs), use_container_width=True, hide_index=True)
        else:
            st.info("No query telemetry is currently available.")

        st.markdown('<div class="section-title">Knowledge gaps</div>', unsafe_allow_html=True)
        gaps = safe_call("fetch_unresolved_queries", []) or []
        if gaps:
            for ts, k_id, lang, q in gaps[:20]:
                st.warning(f"[{ts}] {k_id} • {lang} • {q}")
        else:
            st.success("No unresolved low-confidence queries are currently flagged.")

    with tabs[1]:
        daily = safe_call("fetch_daily_performance_summary", {"today_queries": 0, "avg_latency_ms": 0, "avg_confidence_pct": 0}) or {}
        a, b, c = st.columns(3)
        with a: st.metric("Queries today", daily.get("today_queries", 0))
        with b: st.metric("Average latency", f"{daily.get('avg_latency_ms', 0)} ms")
        with c: st.metric("RAG match quality", f"{daily.get('avg_confidence_pct', 0)}%")

        lang_data, latency_data = safe_call("fetch_analytics_summary", ([], [])) or ([], [])
        lcol, rcol = st.columns(2)
        with lcol:
            st.markdown('<div class="section-title">Queries by language</div>', unsafe_allow_html=True)
            if lang_data:
                st.dataframe(pd.DataFrame(lang_data, columns=["Language", "Queries"]), use_container_width=True, hide_index=True)
            else:
                st.info("No language telemetry recorded yet.")
        with rcol:
            st.markdown('<div class="section-title">Average response latency</div>', unsafe_allow_html=True)
            if latency_data:
                st.dataframe(pd.DataFrame(latency_data, columns=["Language", "Average ms"]), use_container_width=True, hide_index=True)
            else:
                st.info("Latency metrics will appear after the first recorded query.")

        top_kw = safe_call("fetch_top_query_keywords", [], 8) or []
        if top_kw:
            st.markdown('<div class="section-title">Trending inquiry keywords</div>', unsafe_allow_html=True)
            cols = st.columns(min(4, len(top_kw)))
            for i, (kw, count) in enumerate(top_kw):
                with cols[i % len(cols)]:
                    st.metric(f"#{i+1} {kw}", count)

    with tabs[2]:
        lang_stats = safe_call("fetch_language_demographics", {}) or {}
        if lang_stats:
            df = pd.DataFrame(list(lang_stats.items()), columns=["Language", "Share"])
            st.bar_chart(df.set_index("Language"), height=320)
        else:
            st.info("No language distribution data available.")

        peak = safe_call("fetch_peak_usage_hours", []) or []
        st.markdown('<div class="section-title">Peak kiosk traffic hours</div>', unsafe_allow_html=True)
        if peak:
            st.dataframe(pd.DataFrame(peak, columns=["Hour", "Queries"]), use_container_width=True, hide_index=True)
        else:
            st.info("Insufficient timestamp data for peak-hour analysis.")

        district = st.text_input("District filter", value="Pune District", key="telemetry_district")
        if st.button("Load district analytics"):
            rows = safe_call("fetch_logs_by_district", [], district) or []
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                st.info("No district records found.")

    with tabs[3]:
        audit_logs = safe_call("fetch_admin_audit_logs", []) or []
        if audit_logs:
            st.dataframe(pd.DataFrame(audit_logs, columns=["Timestamp", "Officer", "Action", "Details"]), use_container_width=True, hide_index=True)
        else:
            st.info("No administrative actions are recorded yet.")

        search_kw = st.text_input("Search audit logs", placeholder="Officer, action or ticket keyword…")
        if search_kw:
            matches = safe_call("search_admin_action_logs", [], search_kw) or []
            if matches:
                st.dataframe(pd.DataFrame(matches, columns=["Timestamp", "Officer", "Action", "Details"]), use_container_width=True, hide_index=True)
            else:
                st.info("No audit entries matched that search.")

        audit_csv = safe_call("export_admin_audit_logs_to_csv", None)
        make_download(audit_csv, "📜 Download admin audit log (.CSV)", f"Sahakar_Vaani_Admin_Audit_{datetime.now():%Y%m%d}.csv", "text/csv")

# -----------------------------------------------------------------------------
# KNOWLEDGE & REPORTS
# -----------------------------------------------------------------------------
elif menu == "Knowledge & Reports":
    st.markdown('<div class="page-title">Knowledge Base & Governance Reports</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Maintain policy indexing, inspect retrieval quality and generate official operational reports.</div>', unsafe_allow_html=True)

    tabs = st.tabs(["Knowledge base", "Vector inspection", "Reports & exports", "Ingestion history"])

    with tabs[0]:
        total_chunks = safe_call("get_total_indexed_chunks_count", 0) or 0
        gap_count = safe_call("fetch_knowledge_gap_count", 0) or 0
        a, b = st.columns(2)
        with a: metric_card("Active policy chunks", f"{total_chunks}", "Indexed in ChromaDB", "card-green")
        with b: metric_card("Knowledge gaps", f"{gap_count}", "Currently flagged retrieval gaps", "card-accent")

        st.markdown('<div class="section-title">Knowledge coverage gaps</div>', unsafe_allow_html=True)
        gaps = safe_call("fetch_recent_knowledge_gaps", [], 10) or []
        if gaps:
            for ts, k_id, lang, q, score in gaps:
                st.warning(f"[{ts}] {k_id} • {lang} • score {score} • {q}")
        else:
            st.success("No knowledge-base coverage gaps are currently flagged.")

        if st.button("Re-index policy vector store", type="primary"):
            try:
                from ingest import ingest_documents
                with st.spinner("Indexing policy documents from /data…"):
                    ingest_documents()
                st.success("Policy vector index updated successfully.")
            except Exception as exc:
                st.error(f"Indexing failed: {exc}")

    with tabs[1]:
        query = st.text_input("Test policy retrieval query", placeholder="Example: KCC interest subvention")
        if st.button("Run vector match test"):
            if not query.strip():
                st.warning("Enter a test query first.")
            else:
                try:
                    from rag_engine import load_vector_db
                    db = load_vector_db()
                    results = db.similarity_search_with_score(query.strip(), k=3)
                    if results:
                        for idx, (doc, score) in enumerate(results, 1):
                            src = os.path.basename(doc.metadata.get("source", "Unknown"))
                            st.markdown(f'<div class="card"><b>Match #{idx}</b> • Distance {round(score,3)} • Source {src}<br><span class="small-muted">{doc.page_content[:450]}</span></div>', unsafe_allow_html=True)
                    else:
                        st.info("No matching vector chunks were returned.")
                except Exception as exc:
                    st.error(f"Vector inspection failed: {exc}")

    with tabs[2]:
        st.markdown('<div class="section-title">Official weekly report</div>', unsafe_allow_html=True)
        if st.button("Generate weekly PDF report", type="primary"):
            try:
                report = generate_weekly_report_pdf()
                if isinstance(report, (bytes, bytearray)):
                    st.session_state.weekly_report = bytes(report)
                elif isinstance(report, str) and os.path.exists(report):
                    with open(report, "rb") as f:
                        st.session_state.weekly_report = f.read()
                else:
                    st.session_state.weekly_report = report
                st.success("Weekly governance report generated.")
            except Exception as exc:
                st.error(f"Report generation failed: {exc}")

        if st.session_state.get("weekly_report"):
            st.download_button(
                "⬇️ Download weekly PDF report",
                data=st.session_state.weekly_report,
                file_name=f"Sahakar_Vaani_Weekly_Report_{datetime.now():%Y%m%d}.pdf",
                mime="application/pdf",
            )

        st.markdown('<div class="section-title">Data exports</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            daily_csv = safe_call("export_today_telemetry_csv", None)
            make_download(daily_csv, "📊 Download today's query log", f"Sahakar_Vaani_Queries_{datetime.now():%Y%m%d}.csv", "text/csv")
        with c2:
            ingest_csv = safe_call("export_ingestion_logs_to_csv", None)
            make_download(ingest_csv, "📚 Download ingestion audit log", "Sahakar_Vaani_Ingestion_Audit.csv", "text/csv")

    with tabs[3]:
        history = safe_call("fetch_ingestion_logs", []) or []
        if history:
            st.dataframe(pd.DataFrame(history, columns=["Timestamp", "File", "Chunks", "Status"]), use_container_width=True, hide_index=True)
        else:
            st.info("No policy document ingestion events are recorded yet.")

# -----------------------------------------------------------------------------
# SECURITY & MAINTENANCE
# -----------------------------------------------------------------------------
elif menu == "Security & Maintenance":
    st.markdown('<div class="page-title">Security, Configuration & Maintenance</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Restricted controls for officer credentials, audit records, system configuration and database maintenance.</div>', unsafe_allow_html=True)

    tabs = st.tabs(["Officer security", "Database maintenance", "System configuration", "Audit & contacts"])

    with tabs[0]:
        html_card('<b>Restricted administrative control</b><br><span class="small-muted">Credential changes should be performed only by an authorised officer.</span>', "card-danger")
        st.text_input("Current officer username", value=st.session_state.admin_username, disabled=True)
        new_password = st.text_input("New password", type="password")
        confirm_password = st.text_input("Confirm new password", type="password")
        if st.button("Update officer password", type="primary"):
            if not new_password:
                st.warning("Enter a new password.")
            elif new_password != confirm_password:
                st.error("Password confirmation does not match.")
            else:
                try:
                    result = update_officer_password(st.session_state.admin_username, new_password)
                    st.success("Officer password updated successfully." if result is not False else "Password update could not be completed.")
                except TypeError:
                    try:
                        result = update_officer_password(st.session_state.admin_username, hashlib.sha256(new_password.encode()).hexdigest())
                        st.success("Officer password update submitted." if result is not False else "Password update could not be completed.")
                    except Exception as exc:
                        st.error(f"Password update failed: {exc}")
                except Exception as exc:
                    st.error(f"Password update failed: {exc}")

    with tabs[1]:
        st.markdown('<div class="section-title">Database and telemetry maintenance</div>', unsafe_allow_html=True)
        a, b = st.columns(2)
        with a:
            if st.button("Verify and repair DB schema"):
                safe_call("verify_and_repair_schema", None)
                st.success("Database schema verification completed.")
            if st.button("Reindex SQLite database"):
                ok = safe_call("reindex_sqlite_database", False)
                st.success("SQLite indexes rebuilt." if ok else "SQLite reindex could not be completed.")
        with b:
            if st.button("VACUUM SQLite database"):
                ok = safe_call("vacuum_sqlite_database", False)
                st.success("Unused SQLite storage reclaimed." if ok else "VACUUM could not be completed.")
            if st.button("Purge telemetry older than 30 days"):
                n = safe_call("purge_old_telemetry_logs", 0, 30)
                st.success(f"Purged {n} telemetry records.")

        if st.button("Archive telemetry older than 60 days"):
            n = safe_call("archive_old_telemetry_to_json", 0, 60)
            st.success(f"Archived {n} historical telemetry records.")

    with tabs[2]:
        st.markdown('<div class="section-title">Runtime configuration</div>', unsafe_allow_html=True)
        with st.expander("View environment configuration"):
            st.write(f"Database path: `{DB_FILE}`")
            st.write("Vector store: `ChromaDB (Local)`")
            st.write("TTS engine: `AI4Bharat / configured project engine`")
            st.write("LLM gateway: `Groq API`")
        force_offline = st.checkbox("Force offline mode", value=False)
        bypass_check = st.checkbox("Bypass amplitude / diagnostic check", value=False)
        timeout = st.number_input("Session timeout (seconds)", min_value=60, max_value=3600, value=300, step=30)
        st.caption(f"Current session override values: offline={force_offline}, bypass={bypass_check}, timeout={timeout}s")

        st.markdown('<div class="section-title">Manual officer action</div>', unsafe_allow_html=True)
        officer_id = st.text_input("Officer ID", value=st.session_state.admin_username)
        action = st.selectbox("Action type", ["TELEMETRY_REVIEW", "HARDWARE_MAINTENANCE", "MANUAL_CALL_MADE", "OTHER"])
        notes = st.text_area("Action details")
        if st.button("Record audit action"):
            if notes.strip():
                safe_call("record_admin_audit_event", None, officer_id, action, notes.strip())
                st.success("Audit action recorded.")
            else:
                st.warning("Enter action details before saving.")

    with tabs[3]:
        contact = safe_call("get_district_officer_contact", {}, "Pune District") or {}
        st.markdown('<div class="section-title">Regional escalation contact</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Nodal officer", contact.get("officer", "Not configured"))
        with c2: st.metric("Phone", contact.get("phone", "Not configured"))
        with c3: st.metric("Email", contact.get("email", "Not configured"))

        audit = safe_call("fetch_admin_audit_logs", []) or []
        st.markdown('<div class="section-title">Recent officer actions</div>', unsafe_allow_html=True)
        if audit:
            st.dataframe(pd.DataFrame(audit[:15], columns=["Timestamp", "Officer", "Action", "Details"]), use_container_width=True, hide_index=True)
        else:
            st.info("No officer actions are recorded yet.")

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div style="margin-top:30px;padding-top:15px;border-top:1px solid #dce4ed;color:#64748b;font-size:.72rem;display:flex;justify-content:space-between;gap:12px;">
      <span>Sahakar-Vaani • PACS Governance Administration</span>
      <span>Restricted system • Authorised personnel only</span>
    </div>
    """,
    unsafe_allow_html=True,
)
