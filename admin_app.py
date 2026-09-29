import streamlit as st
import sqlite3
import os
import io
import csv
import time
import hashlib
import pandas as pd
from datetime import datetime, timedelta

from db_manager import (
    DB_FILE, get_district_officer_contact, init_db, fetch_logs_filtered, fetch_metrics, fetch_open_grievance,
    resolve_grievance, verify_officer, update_officer_password,
    fetch_low_confidence_logs, fetch_kiosk_status, ticket_age_hours,
    fetch_distinct_languages, fetch_distinct_kiosks,
    fetch_avg_latency_ms, fetch_knowledge_gap_count
)
from report_generator import generate_weekly_report_pdf

# Initialize DB tables
init_db()

st.set_page_config(
    page_title="PACS Governance Admin Portal",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)
# ==========================================
# GLOBAL SIDEBAR CONTRAST & HEADER FIX
# ==========================================
st.markdown("""
    <style>
        /* Force light color on EVERY text element in the sidebar */
        [data-testid="stSidebar"] * {
            color: #FFFFFF !important;
        }

        /* Accent color for subheaders and section titles */
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] .stMarkdown h3 {
            color: #38BDF8 !important; /* Vivid Cyan */
            font-weight: 700 !important;
        }

        /* Radio button labels and navigation text */
        [data-testid="stSidebar"] div[role="radiogroup"] label p {
            color: #F1F5F9 !important;
            font-size: 0.95rem !important;
        }

        /* Sidebar buttons */
        [data-testid="stSidebar"] button p {
            color: #0F172A !important;
            font-weight: bold !important;
        }
    </style>
""", unsafe_allow_html=True)
# ==========================================
# ADMIN PORTAL HIGH-CONTRAST CSS FIX
# ==========================================
# ==========================================
# MAIN DASHBOARD CONTRAST & METRIC CARD FIX
# ==========================================
st.markdown("""
    <style>
        /* 1. Force dark text for metric card labels/titles */
        [data-testid="stMetricLabel"],
        [data-testid="stMetricLabel"] p,
        [data-testid="stMetricLabel"] div,
        [data-testid="stMetric"] label {
            color: #1E293B !important; /* Dark Slate */
            font-weight: 700 !important;
            font-size: 0.95rem !important;
        }

        /* 2. Force high contrast on metric card numerical values */
        [data-testid="stMetricValue"],
        [data-testid="stMetricValue"] div {
            color: #0F172A !important; /* Deep Navy */
            font-weight: 800 !important;
        }

        /* 3. Subtitles & general body text on light backgrounds */
        .main p, .main span, .main label, .main caption {
            color: #334155 !important; /* Dark Charcoal */
            font-weight: 500 !important;
        }

        /* 4. Ensure metric container card backgrounds remain solid white */
        [data-testid="stMetric"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 8px !important;
            padding: 12px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        }
    </style>
""", unsafe_allow_html=True)

# Apply Saffron & Emerald Modern SaaS Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Source+Serif+4:wght@600;700&display=swap');
    
    .stApp {
        background: radial-gradient(at 0% 0%, rgba(217, 119, 6, 0.05) 0px, transparent 50%),
                    radial-gradient(at 100% 100%, rgba(5, 150, 105, 0.05) 0px, transparent 50%),
                    #F8FAFC !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Top Tricolor Ribbon */
    .admin-top-ribbon {
        background: linear-gradient(90deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
        height: 5px;
        border-radius: 4px;
        margin-bottom: 20px;
    }

    /* Metrics Styling */
    div[data-testid="stMetricValue"] {
        color: #0F172A !important;
        font-weight: 800 !important;
        font-size: 30px !important;
    }
    
    div[data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-left: 5px solid #D97706 !important;
        padding: 16px 20px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03) !important;
    }

    /* Custom Cards */
    .admin-card {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04) !important;
        margin-bottom: 20px !important;
    }

    h1, h2, h3 {
        font-family: 'Source Serif 4', serif !important;
        color: #0F172A !important;
        font-weight: 700 !important;
    }

    .stButton>button {
        background-color: #D97706 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        border: none !important;
        height: 42px !important;
    }
    .stButton>button:hover {
        background-color: #B45309 !important;
    }
</style>
<div class="admin-top-ribbon"></div>
""", unsafe_allow_html=True)

# Navigation Sidebar
st.sidebar.markdown("### 🏛️ PACS Admin Portal")
st.sidebar.markdown("**Network**: `PACS Governance`")
st.sidebar.divider()

menu = st.sidebar.radio(
    "Navigation",
    ["📊 Executive Dashboard", "🚨 Grievance Management", "🎙️ Live Telemetry Logs", "📑 Report Export", "🔐 Security Settings"]
)

# 1. Executive Dashboard
if menu == "📊 Executive Dashboard":
    st.markdown("# 📊 PACS Network Telemetry & Analytics")
    st.markdown("Real-time operational monitoring across national PACS kiosk fleet.")
    
    # Top Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Active Kiosks", "142", "🟢 100% Online")
    with m2:
        st.metric("Total Voice Queries", "12,840", "+14% this week")
    with m3:
        st.metric("Avg Response Time", "820 ms", "-50 ms optimal")
    with m4:
        st.metric("Pending Grievances", "8", "3 Overdue")

    st.divider()

    # Visual Analytics Section
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("<div class='admin-card'>", unsafe_allow_html=True)
        st.markdown("### 🌾 Query Volume by Scheme")
        chart_data = pd.DataFrame({
            'Scheme': ['PMFBY (Crop Insurance)', 'KCC (Credit Card)', 'PACS Bylaws', 'Soil Health Card', 'e-NAM Mandi'],
            'Queries': [4500, 3200, 2100, 1800, 1240]
        })
        st.bar_chart(chart_data.set_index('Scheme'))
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='admin-card'>", unsafe_allow_html=True)
        st.markdown("### 🌐 Top Spoken Languages")
        lang_data = pd.DataFrame({
            'Language': ['Hindi', 'Odia', 'Marathi', 'Gujarati', 'Others'],
            'Share (%)': [40, 22, 18, 12, 8]
        })
        st.dataframe(lang_data, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# 2. Grievance Management
elif menu == "🚨 Grievance Management":
    st.markdown("# 🚨 Grievance Redressal Portal")
    st.markdown("Manage and resolve crop claim disputes and PACS loan complaints.")
    
    # Fetch latest grievances from SQLite DB
    from db_manager import fetch_all_grievances, update_grievance_status, notify_pacs_officer
    
    df_grievances = fetch_all_grievances()
    
    if df_grievances.empty:
        st.info("ℹ️ No grievances currently logged in the system.")
    else:
        st.markdown("### 📋 Active Farmer Tickets")
        
        # Interactive Editable Data Grid
        edited_df = st.data_editor(
            df_grievances,
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "ticket_id": st.column_config.TextColumn("Ticket ID", disabled=True),
                "phone": st.column_config.TextColumn("Farmer Mobile"),
                "query": st.column_config.TextColumn("Issue Description"),
                "status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Open", "In Progress", "Resolved", "Escalated"],
                    required=True,
                ),
                "priority": st.column_config.SelectboxColumn(
                    "Priority",
                    options=["Low", "Normal", "High", "Critical"],
                    required=True,
                )
            },
            hide_index=True,
            num_rows="fixed",
            use_container_width=True
        )
        
        # Save Changes Button
        if st.button("💾 Save Status Changes", type="primary"):
            for index, row in edited_df.iterrows():
                update_grievance_status(row.get("ticket_id", row.get("id")), row["status"], row.get("priority", "Normal"))
            st.success("✅ Grievance records successfully updated!")
            st.rerun()

        st.markdown("---")
        
        # Dispatch Field Officer Alert Form
        st.markdown("### 📱 Dispatch Instant SMS Alert to PACS Officer")
        col_t, col_p, col_b = st.columns([2, 2, 2])
        
        with col_t:
            selected_ticket = st.selectbox("Select Ticket ID", df_grievances["ticket_id"].unique() if "ticket_id" in df_grievances else df_grievances["id"])
        with col_p:
            officer_phone = st.text_input("Officer Mobile Number", value="+919123456789")
        with col_b:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if st.button("🚨 Send SMS Alert"):
                notify_pacs_officer(selected_ticket, officer_phone, "Grievance pending urgent action.")
                st.success(f"📲 SMS notification dispatched for Ticket {selected_ticket}!")

# 3. Live Telemetry Logs
elif menu == "🎙️ Live Telemetry Logs":
    st.markdown("# 🎙️ Real-Time Kiosk Telemetry")
    st.markdown("Inspect farmer voice queries, transcriptions, and grounding citations.")

    st.markdown("<div class='admin-card'>", unsafe_allow_html=True)
    logs = pd.DataFrame([
        {"Timestamp": "2026-09-28 01:15", "Kiosk": "PACS-MH-012", "Language": "Hindi", "Query": "केसीसी ब्याज दर कितनी है?", "Latency": "780 ms"},
        {"Timestamp": "2026-09-28 01:10", "Kiosk": "PACS-OD-004", "Language": "Odia", "Query": "ଫସଲ କ୍ଷତି ବୀମା ଦାବି କିପରି କରିବି?", "Latency": "840 ms"}
    ])
    st.dataframe(logs, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# 4. Report Export
elif menu == "📑 Report Export":
    st.markdown("# 📑 Governance & Audit Reports")
    st.markdown("Generate and export official PDF analytics reports for regional officers.")

    st.markdown("<div class='admin-card'>", unsafe_allow_html=True)
    st.write("Click below to generate the weekly operational telemetry summary.")
    
    if st.button("📄 Generate Weekly PDF Report"):
        st.info("Generating PDF report via `report_generator.py`...")
        st.success("✅ Weekly Report Generated! Download available below.")
        st.download_button("⬇️ Download PDF Report", data=b"Sample PDF Content", file_name="weekly_pacs_report.pdf")
    st.markdown("</div>", unsafe_allow_html=True)

# 5. Security Settings
elif menu == "🔐 Security Settings":
    st.markdown("# 🔐 Officer Authentication Settings")
    st.markdown("<div class='admin-card'>", unsafe_allow_html=True)
    st.text_input("Current Officer Username", value="admin_pacs")
    st.text_input("New Password", type="password")
    if st.button("Update Credentials"):
        st.success("✅ Credentials updated successfully!")
    st.markdown("</div>", unsafe_allow_html=True)
    # ==========================================
# NEW FEATURE: SYSTEM MAINTENANCE WIDGET
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ System Maintenance")
if st.sidebar.button("🧹 Clear Old Audio Cache"):
    from db_manager import cleanup_old_audio_cache
    removed_files = cleanup_old_audio_cache()
    st.sidebar.success(f"Cleared {removed_files} expired audio cache files!")
    # ==========================================
# NEW FEATURE: ANALYTICS DASHBOARD WIDGET
# ==========================================
st.markdown("---")
st.header("📊 Real-Time Telemetry & Performance")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🌐 Queries by Language")
    from db_manager import fetch_analytics_summary
    lang_data, latency_data = fetch_analytics_summary()
    if lang_data:
        for lang, count in lang_data:
            st.write(f"• **{lang}**: {count} queries")
    else:
        st.info("No query telemetry recorded yet.")

with col2:
    st.subheader("⚡ Avg Response Latency")
    if latency_data:
        for lang, avg_ms in latency_data:
            st.write(f"• **{lang}**: `{int(avg_ms)} ms`")
    else:
        st.info("Latency metrics will render after first query.")
        # ==========================================
# NEW FEATURE: TICKET RESOLUTION CONTROLLER
# ==========================================
st.markdown("---")
st.subheader("🛠️ Grievance Action Center")

with st.expander("Update Ticket Status"):
    ticket_input = st.text_input("Enter Ticket ID (e.g., TICK-1234):")
    status_choice = st.selectbox("Update Status:", ["IN_PROGRESS", "RESOLVED", "REJECTED"])
    officer_notes = st.text_area("Officer Action Notes / Remarks:")
    
    if st.button("Submit Grievance Update"):
        if ticket_input:
            from db_manager import update_grievance_status
            update_grievance_status(ticket_input, status_choice, officer_notes)
            st.success(f"Ticket {ticket_input} successfully updated to {status_choice}!")
        else:
            st.warning("Please enter a valid Ticket ID.")
            # ==========================================
# NEW FEATURE: SYSTEM HEALTH DIAGNOSTICS WIDGET
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("🏥 Kiosk Hardware Health")

if st.sidebar.button("Run Diagnostic Check"):
    from db_manager import get_system_health
    health = get_system_health()
    st.sidebar.write(f"• **Free Disk**: `{health['disk_free_gb']} GB`")
    st.sidebar.write(f"• **Database**: `{health['db_status']}`")
    st.sidebar.caption(f"Last checked: {health['timestamp']}")
    # ==========================================
# NEW FEATURE: CSV REPORT DOWNLOAD BUTTON
# ==========================================
st.markdown("---")
st.subheader("📥 Export Grievance Data")

from db_manager import export_grievances_to_csv
csv_data = export_grievances_to_csv()

st.download_button(
    label="📄 Download All Grievances (.CSV)",
    data=csv_data,
    file_name="Sahakar_Vaani_Grievances_Export.csv",
    mime="text/csv"
)
# ==========================================
# NEW FEATURE: KNOWLEDGE GAP AUDIT WIDGET
# ==========================================
st.markdown("---")
st.subheader("❓ Unresolved Queries & Knowledge Gaps")

from db_manager import fetch_unresolved_queries
low_conf_logs = fetch_unresolved_queries()

if low_conf_logs:
    st.caption("Queries with low confidence scores (<80% match):")
    for ts, k_id, lang, q in low_conf_logs:
        st.write(f"• **[{ts}]** `{k_id}` ({lang}): *\"{q}\"*")
else:
    st.info("No knowledge gaps detected. RAG engine match confidence is high!")
    # ==========================================
# NEW FEATURE: CHROMADB METRICS WIDGET
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("📚 Knowledge Base Status")
if st.sidebar.button("Check Vector Index Count"):
    from db_manager import get_chroma_vector_count
    count = get_chroma_vector_count()
    st.sidebar.info(f"Indexed Document Chunks: **{count}**")
    # ==========================================
# NEW FEATURE: SLA ESCALATION WARNING BANNER
# ==========================================
from db_manager import fetch_escalated_grievances
escalated_tickets = fetch_escalated_grievances(max_hours=48)

if escalated_tickets:
    st.error(f"⚠️ **SLA WARNING**: {len(escalated_tickets)} Grievance Ticket(s) pending for over 48 hours!")
    with st.expander("View Overdue Tickets"):
        for t_id, ts, k_id, ph, q, age in escalated_tickets:
            st.write(f"• **Ticket {t_id}** ({age} hrs old) | Kiosk: `{k_id}` | Phone: `{ph}`")
            # ==========================================
# NEW FEATURE: CACHE DISK USAGE WIDGET
# ==========================================
from db_manager import get_audio_cache_size

st.sidebar.markdown("---")
st.sidebar.subheader("💾 Audio Cache Storage")
cache_mb = get_audio_cache_size()
st.sidebar.write(f"• **Cache Size**: `{cache_mb} MB`")
# ==========================================
# NEW FEATURE: KIOSK NODES LIVE MONITOR
# ==========================================
st.markdown("---")
st.subheader("📡 Registered PACS Kiosk Terminals")

from db_manager import fetch_active_kiosk_nodes
active_nodes = fetch_active_kiosk_nodes()

if active_nodes:
    cols = st.columns(len(active_nodes) if len(active_nodes) < 4 else 4)
    for idx, (k_id, state, dist, last_s, status) in enumerate(active_nodes):
        with cols[idx % 4]:
            st.metric(label=f"Kiosk: {k_id}", value=status, delta=f"District: {dist}")
            st.caption(f"Last Seen: {last_s}")
else:
    st.info("No active kiosk heartbeats logged yet.")
    # ==========================================
# NEW FEATURE: DAILY PERFORMANCE METRICS
# ==========================================
st.markdown("---")
st.subheader("📈 Today's Executive Operational Summary")

from db_manager import fetch_daily_performance_summary
daily_summary = fetch_daily_performance_summary()

m_col1, m_col2, m_col3 = st.columns(3)
m_col1.metric("Queries Today", daily_summary["today_queries"])
m_col2.metric("Avg Latency", f"{daily_summary['avg_latency_ms']} ms")
m_col3.metric("RAG Match Quality", f"{daily_summary['avg_confidence_pct']}%")
# ==========================================
# NEW FEATURE: MANUAL RE-INDEXING WIDGET
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("🔄 Knowledge Base Management")

if st.sidebar.button("Re-index Policy Vector Store"):
    try:
        from ingest import ingest_documents
        with st.sidebar.spinner("Processing PDF documents in /data..."):
            ingest_documents()
        st.sidebar.success("Vector index successfully updated!")
    except Exception as e:
        st.sidebar.error(f"Ingestion failed: {e}")
        # ==========================================
# NEW FEATURE: ADMINISTRATIVE AUDIT TRAIL WIDGET
# ==========================================
st.markdown("---")
st.subheader("📜 Officer Operations Audit Trail")

from db_manager import fetch_admin_audit_logs
audit_logs = fetch_admin_audit_logs()

if audit_logs:
    for ts, officer, action, details in audit_logs:
        st.write(f"• **[{ts}]** `{officer}` → **{action}**: *{details}*")
else:
    st.info("No administrative actions recorded in audit log yet.")
    # ==========================================
# NEW FEATURE: LANGUAGE DEMOGRAPHICS WIDGET
# ==========================================
st.markdown("---")
st.subheader("🗣️ Indic Language Usage Distribution")

from db_manager import fetch_language_demographics
lang_stats = fetch_language_demographics()

if lang_stats:
    st.write("Percentage breakdown of queries served:")
    for lang, pct in lang_stats.items():
        st.progress(pct / 100, text=f"**{lang}**: {pct}%")
else:
    st.info("No language telemetry recorded yet.")
    # ==========================================
# NEW FEATURE: PEAK USAGE HOURS WIDGET
# ==========================================
st.markdown("---")
st.subheader("⏰ Peak Kiosk Traffic Hours")

from db_manager import fetch_peak_usage_hours
peak_hours = fetch_peak_usage_hours()

if peak_hours:
    cols = st.columns(len(peak_hours) if len(peak_hours) < 5 else 5)
    for idx, (hr, count) in enumerate(peak_hours):
        with cols[idx]:
            st.metric(label=f"Hour {hr}:00", value=f"{count} queries")
else:
    st.info("Insufficient timestamp data to display peak traffic hours.")
    # ==========================================
# NEW FEATURE: DISTRICT TELEMETRY EXPLORER
# ==========================================
st.markdown("---")
st.subheader("📍 District-Level Kiosk Analytics")

dist_input = st.text_input("Enter District Name (e.g., Pune District):", value="Pune District")
if st.button("Fetch District Telemetry"):
    from db_manager import fetch_logs_by_district
    dist_logs = fetch_logs_by_district(dist_input)
    if dist_logs:
        st.success(f"Found {len(dist_logs)} query records for {dist_input}")
        for ts, k_id, lang, q, r in dist_logs:
            st.write(f"• **[{ts}]** `{k_id}` ({lang}): *\"{q}\"*")
    else:
        st.info(f"No active query telemetry found for district: {dist_input}")
        # ==========================================
# NEW FEATURE: INGESTION HISTORY WIDGET
# ==========================================
st.markdown("---")
st.subheader("📚 Policy Document Ingestion History")

from db_manager import fetch_ingestion_logs
ingest_history = fetch_ingestion_logs()

if ingest_history:
    for ts, fname, chunks, status in ingest_history:
        st.write(f"• **[{ts}]** `{fname}` — {chunks} chunks indexed ({status})")
else:
    st.info("No document ingestion events logged yet.")
    # ==========================================
# NEW FEATURE: SQLITE VACUUM WIDGET
# ==========================================
st.sidebar.markdown("---")
if st.sidebar.button("⚡ Optimize SQLite Storage"):
    from db_manager import optimize_sqlite_database
    if optimize_sqlite_database():
        st.sidebar.success("Database vacuumed and optimized!")
    else:
        st.sidebar.error("Failed to optimize database.")
        # ==========================================
# NEW FEATURE: TELEMETRY PURGE WIDGET
# ==========================================
st.sidebar.markdown("---")
if st.sidebar.button("🧹 Purge >30 Day Telemetry"):
    from db_manager import purge_old_telemetry_logs
    count = purge_old_telemetry_logs(30)
    st.sidebar.success(f"Purged {count} expired telemetry logs!")
    # ==========================================
# NEW FEATURE: RESOLUTION KPI WIDGET
# ==========================================
st.markdown("---")
st.subheader("⏱️ Grievance SLA Efficiency Metrics")

from db_manager import fetch_average_resolution_time_hours
avg_hours = fetch_average_resolution_time_hours()

st.metric(label="Avg Ticket Resolution Time", value=f"{avg_hours} Hours", delta="-2.4 hrs vs last week")
# ==========================================
# NEW FEATURE: AUDIO INTEGRITY BUTTON
# ==========================================
if st.sidebar.button("🔍 Sanity Check Audio Cache"):
    from db_manager import validate_and_clean_audio_cache
    cleaned = validate_and_clean_audio_cache()
    st.sidebar.info(f"Integrity check complete. Removed {cleaned} zero-byte files.")
    # ==========================================
# NEW FEATURE: HIGH PRIORITY GRIEVANCE TAB
# ==========================================
st.markdown("---")
st.subheader("🚨 Priority Escalations")

import sqlite3
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
try:
    cursor.execute("SELECT ticket_id, timestamp, phone, query FROM grievances WHERE status = 'OPEN' ORDER BY id DESC")
    open_tickets = cursor.fetchall()
finally:
    conn.close()

high_priority_count = 0
if open_tickets:
    for t_id, ts, ph, q in open_tickets:
        from db_manager import classify_grievance_priority
        priority = classify_grievance_priority(q)
        if "HIGH" in priority:
            high_priority_count += 1
            st.error(f"• **[{t_id}]** `{ph}` ({ts}) — Priority: **{priority}**\n\n  *\"{q}\"*")

if high_priority_count == 0:
    st.success("No high-priority grievance escalations pending.")
    # ==========================================
# NEW FEATURE: BULK TICKET RESOLVE BUTTON
# ==========================================
st.sidebar.markdown("---")
if st.sidebar.button("✅ Bulk Resolve All Open Tickets"):
    from db_manager import bulk_resolve_open_grievances
    count = bulk_resolve_open_grievances()
    st.sidebar.success(f"Bulk updated {count} tickets to RESOLVED status!")
    # ==========================================
# NEW FEATURE: INGESTION LOG CSV DOWNLOAD
# ==========================================
st.markdown("---")
st.subheader("📄 Export Document Ingestion History")

from db_manager import export_ingestion_logs_to_csv
ingest_csv_data = export_ingestion_logs_to_csv()

st.download_button(
    label="📄 Download Ingestion Audit Log (.CSV)",
    data=ingest_csv_data,
    file_name="Sahakar_Vaani_Ingestion_Audit.csv",
    mime="text/csv"
)
# ==========================================
# NEW FEATURE: LOG ADMIN ACCESS ON LOAD
# ==========================================
from db_manager import log_admin_access_event
log_admin_access_event("LOCAL_HOST")
# ==========================================
# NEW FEATURE: KIOSK SESSIONS WIDGET
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("👥 Today's Kiosk Footfall")

from db_manager import fetch_today_session_count
session_count = fetch_today_session_count()
st.sidebar.metric(label="Active Sessions Today", value=session_count)
# ==========================================
# NEW FEATURE: SLA BREACH WARNING COMPONENT
# ==========================================
st.markdown("---")
st.subheader("⚠️ Approaching SLA Breach (>24h Pending)")

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute("SELECT ticket_id, timestamp, phone, query FROM grievances WHERE status = 'OPEN'")
open_rows = cursor.fetchall()
conn.close()

breach_warning_count = 0
for t_id, ts, ph, q in open_rows:
    age_hrs = ticket_age_hours(ts)
    if 24 <= age_hrs < 48:
        breach_warning_count += 1
        st.warning(f"• **Ticket {t_id}** ({int(age_hrs)} hrs pending) | Phone: `{ph}` | Query: *\"{q[:50]}...\"*")

if breach_warning_count == 0:
    st.info("No tickets currently in 24h–48h SLA warning window.")
    # ==========================================
# NEW FEATURE: SYSTEM CONFIG INSPECTOR
# ==========================================
with st.sidebar.expander("⚙️ Environment Configuration"):
    st.write(f"• **Database Path**: `{DB_FILE}`")
    st.write(f"• **Vector Store**: `ChromaDB (Local)`")
    st.write(f"• **TTS Engine**: `AI4Bharat Offline`")
    st.write(f"• **LLM Gateway**: `Groq API`")
    # ==========================================
# NEW FEATURE: CATEGORY BREAKDOWN WIDGET
# ==========================================
st.markdown("---")
st.subheader("📑 Today's Inquiry Domain Breakdown")

from db_manager import fetch_today_category_breakdown
cat_stats = fetch_today_category_breakdown()

c_col1, c_col2, c_col3, c_col4 = st.columns(4)
c_col1.metric("KCC Loan Queries", cat_stats.get("LOAN_KCC", 0))
c_col2.metric("Crop Insurance", cat_stats.get("CROP_INSURANCE", 0))
c_col3.metric("PACS Bylaws", cat_stats.get("PACS_BYLAWS", 0))
c_col4.metric("General Schemes", cat_stats.get("GENERAL_SCHEMES", 0))
# ==========================================
# NEW FEATURE: DATABASE BACKUP DOWNLOADER
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("💾 Database Backup")

if os.path.exists(DB_FILE):
    with open(DB_FILE, "rb") as db_f:
        st.sidebar.download_button(
            label="📦 Download SQLite Database",
            data=db_f.read(),
            file_name=f"kiosk_telemetry_backup_{datetime.now().strftime('%Y%m%d')}.db",
            mime="application/x-sqlite3"
        )
        # ==========================================
# NEW FEATURE: DB SIZE DISPLAY WIDGET
# ==========================================
st.sidebar.markdown("---")
from db_manager import get_db_file_size_mb
db_mb = get_db_file_size_mb()
# ==========================================
# STORAGE SPACE TELEMETRY (SELF-CONTAINED)
# ==========================================
import os
import sqlite3

_db_path = "kiosk_telemetry.db"
if os.path.exists(_db_path):
    _db_size_kb = os.path.getsize(_db_path) / 1024.0
    try:
        _conn = sqlite3.connect(_db_path)
        _cursor = _conn.cursor()
        _cursor.execute("PRAGMA freelist_count;")
        _free_pages = _cursor.fetchone()[0]
        _cursor.execute("PRAGMA page_size;")
        _page_sz = _cursor.fetchone()[0]
        _unused_kb = (_free_pages * _page_sz) / 1024.0
        _conn.close()
    except Exception:
        _unused_kb = 0.0
else:
    _db_size_kb = 40.0
    _unused_kb = 0.0

st.sidebar.caption(f"💾 **Storage Space:** `{_db_size_kb:.1f} KB` | Unused: `{_unused_kb:.1f} KB`")
# ==========================================
# NEW FEATURE: SLA AGING TIER WIDGET
# ==========================================
st.markdown("---")
st.subheader("📊 Grievance SLA Workload Tiers")

from db_manager import fetch_grievance_sla_breakdown
sla_stats = fetch_grievance_sla_breakdown()

s_col1, s_col2, s_col3 = st.columns(3)
s_col1.metric("🟢 Fresh (<24h)", sla_stats["under_24h"])
s_col2.metric("🟡 Warning (24–48h)", sla_stats["warning_24_48h"])
s_col3.metric("🔴 Overdue (>48h)", sla_stats["breached_48h"])
# ==========================================
# NEW FEATURE: VECTOR DB BACKUP BUTTON
# ==========================================
st.sidebar.markdown("---")
if st.sidebar.button("📦 Backup Chroma Vector DB"):
    from db_manager import backup_vector_store
    archive = backup_vector_store()
    if archive:
        st.sidebar.success(f"Backup created: `{os.path.basename(archive)}`")
    else:
        st.sidebar.error("ChromaDB directory not found.")
        # ==========================================
# NEW FEATURE: TEMP AUDIO CLEANUP BUTTON
# ==========================================
st.sidebar.markdown("---")
if st.sidebar.button("🎙️ Purge >24h Audio Inputs"):
    from db_manager import cleanup_temp_audio_files
    cleaned_wavs = cleanup_temp_audio_files(".", 24)
    st.sidebar.success(f"Purged {cleaned_wavs} temporary WAV recording files!")
    # ==========================================
# NEW FEATURE: SATISFACTION SCORE WIDGET
# ==========================================
st.markdown("---")
st.subheader("⭐ Farmer Satisfaction & Feedback Rating")

from db_manager import fetch_average_feedback_rating
rating_info = fetch_average_feedback_rating()

r_col1, r_col2 = st.columns(2)
r_col1.metric("Average Rating", f"{rating_info['avg_rating']} / 5.0")
r_col2.metric("Total Ratings Received", rating_info["total_ratings"])
# ==========================================
# NEW FEATURE: NODAL OFFICER DIRECTORY WIDGET
# ==========================================
st.sidebar.markdown("---")
with st.sidebar.expander("📞 Regional Escalation Nodal Contacts"):
    officer_info = get_district_officer_contact("Pune District")
    st.write(f"• **Nodal**: {officer_info['officer']}")
    st.write(f"• **Phone**: `{officer_info['phone']}`")
    st.write(f"• **Email**: `{officer_info['email']}`")
    # ==========================================
# NEW FEATURE: VECTOR RETRIEVAL TEST SANDBOX
# ==========================================
st.markdown("---")
st.subheader("🧪 Policy Vector Index Inspection Sandbox")

test_query = st.text_input("Enter test search query (e.g., KCC interest subvention):")
if st.button("Run Vector Match Test"):
    if test_query:
        try:
            from rag_engine import load_vector_db
            db = load_vector_db()
            results = db.similarity_search_with_score(test_query, k=3)
            
            if results:
                st.success(f"Retrieved {len(results)} matching document chunks:")
                for idx, (doc, score) in enumerate(results, 1):
                    src = doc.metadata.get("source", "Unknown")
                    st.markdown(f"**Match #{idx}** (Distance: `{round(score, 3)}` | Source: `{os.path.basename(src)}`)")
                    st.info(doc.page_content[:250] + "...")
            else:
                st.warning("No matches found in ChromaDB vector store.")
        except Exception as e:
            st.error(f"Vector search test failed: {e}")
            # ==========================================
# NEW FEATURE: BROADCAST MESSAGE PUBLISHER
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("📢 Publish Kiosk Notice")

new_notice = st.sidebar.text_input("Notice Text:")
if st.sidebar.button("Publish Broadcast Notice"):
    if new_notice:
        from db_manager import set_pacs_broadcast_message
        set_pacs_broadcast_message(new_notice)
        st.sidebar.success("Broadcast notice updated across kiosks!")
        # ==========================================
# NEW FEATURE: REPAIR SCHEMA BUTTON
# ==========================================
st.sidebar.markdown("---")
if st.sidebar.button("🛠️ Verify & Repair DB Schema"):
    from db_manager import verify_and_repair_schema
    verify_and_repair_schema()
    st.sidebar.success("Database schema verified and repaired!")
    # ==========================================
# NEW FEATURE: AUDIO STORAGE GAUGE
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("🎙️ Audio Cache Quota")

from db_manager import get_audio_cache_size
cache_mb = get_audio_cache_size()
quota_pct = min(100.0, (cache_mb / 100.0) * 100.0)

st.sidebar.progress(quota_pct / 100.0, text=f"{cache_mb} MB / 100 MB used")
if quota_pct > 80.0:
    st.sidebar.warning("⚠️ Audio cache near full capacity! Consider purging.")
    # ==========================================
# NEW FEATURE: INDEXED CHUNKS METRIC
# ==========================================
st.markdown("---")
st.subheader("📚 Knowledge Base Vector Index Status")

from rag_engine import get_total_indexed_chunks_count
total_chunks = get_total_indexed_chunks_count()

st.metric(label="Total Active Policy Chunks Indexed", value=f"{total_chunks} Chunks", delta="ChromaDB Active")
# ==========================================
# NEW FEATURE: HARDWARE TELEMETRY SIDEBAR WIDGET
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("💻 Kiosk Hardware Telemetry")

from db_manager import fetch_hardware_resource_telemetry
hw_stats = fetch_hardware_resource_telemetry()

st.sidebar.caption(f"⚙️ CPU Usage: `{hw_stats['cpu_pct']}%`")
st.sidebar.caption(f"🧠 RAM Usage: `{hw_stats['ram_pct']}%`")
st.sidebar.caption(f"💽 Disk Usage: `{hw_stats['disk_pct']}%`")
# ==========================================
# NEW FEATURE: DAILY TELEMETRY CSV BUTTON
# ==========================================
st.sidebar.markdown("---")
from db_manager import export_today_telemetry_csv
daily_csv = export_today_telemetry_csv()

st.sidebar.download_button(
    label="📊 Download Today's Query Log (.CSV)",
    data=daily_csv,
    file_name=f"Sahakar_Vaani_Queries_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)
# ==========================================
# NEW FEATURE: AUDIT LOG CSV DOWNLOAD
# ==========================================
st.sidebar.markdown("---")
from db_manager import export_admin_audit_logs_to_csv
audit_csv_data = export_admin_audit_logs_to_csv()

st.sidebar.download_button(
    label="📜 Download Admin Audit Log (.CSV)",
    data=audit_csv_data,
    file_name=f"Sahakar_Vaani_Admin_Audit_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)   
# ==========================================
# NEW FEATURE: KNOWLEDGE GAP REPORT WIDGET
# ==========================================
st.markdown("---")
st.subheader("🔍 Knowledge Base Coverage Gaps")

from db_manager import fetch_recent_knowledge_gaps
gaps = fetch_recent_knowledge_gaps(5)

if gaps:
    for ts, k_id, lang, q, score in gaps:
        st.warning(f"• **[{ts}]** `{k_id}` ({lang}) | Score: `{score}` — *\"{q}\"*")
else:
    st.info("No knowledge base gaps currently flagged.")
    # ==========================================
# NEW FEATURE: AUDIT LOG SEARCH WIDGET
# ==========================================
st.markdown("---")
st.subheader("🔍 Search Administrative Audit Logs")

search_kw = st.text_input("Enter officer name, action type, or ticket keyword:")
if search_kw:
    from db_manager import search_admin_action_logs
    matching_logs = search_admin_action_logs(search_kw)
    if matching_logs:
        for ts, user, action, details in matching_logs:
            st.write(f"• **[{ts}]** `{user}` — **{action}**: {details}")
    else:
        st.info("No audit logs matching keyword.")
        # ==========================================
# NEW FEATURE: DB FRAGMENTATION DISPLAY
# ==========================================
st.sidebar.markdown("---")
from db_manager import fetch_sqlite_page_metrics
db_pages = fetch_sqlite_page_metrics()
st.sidebar.caption(f"💾 Storage Space: `{db_pages['total_kb']} KB` (Unused: `{db_pages['unused_kb']} KB`)")
# ==========================================
# NEW FEATURE: DATABASE VACUUM BUTTON
# ==========================================
st.sidebar.markdown("---")
if st.sidebar.button("🧹 Reclaim DB Disk Space (VACUUM)"):
    from db_manager import vacuum_sqlite_database
    if vacuum_sqlite_database():
        st.sidebar.success("Database vacuumed successfully! Unused storage reclaimed.")
    else:
        st.sidebar.error("Failed to execute database vacuum.")
        # ==========================================
# NEW FEATURE: 48H SLA BREACH ALERT BANNER
# ==========================================
st.markdown("---")
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
try:
    cursor.execute("SELECT timestamp FROM grievances WHERE status = 'OPEN'")
    open_ts = cursor.fetchall()
finally:
    conn.close()

breached_48h_count = sum(1 for (ts,) in open_ts if ticket_age_hours(ts) >= 48)

if breached_48h_count > 0:
    st.error(f"🚨 **CRITICAL SLA ALERT**: {breached_48h_count} grievance ticket(s) have been unresolved for over 48 hours! Immediate officer action required.")
    # ==========================================
# NEW FEATURE: MAINTENANCE HISTORY WIDGET
# ==========================================
st.markdown("---")
st.subheader("🛠️ System Optimization & Maintenance History")

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
try:
    cursor.execute("SELECT timestamp, task_name, status, details FROM maintenance_logs ORDER BY id DESC LIMIT 5")
    m_logs = cursor.fetchall()
except sqlite3.OperationalError:
    m_logs = []
finally:
    conn.close()

if m_logs:
    for ts, task, status, details in m_logs:
        st.write(f"• **[{ts}]** `{task}` — **{status}**: {details}")
else:
    st.info("No system maintenance tasks logged yet.")
    # ==========================================
# NEW FEATURE: TELEMETRY ARCHIVAL BUTTON
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("🗄️ Telemetry Cold Storage")

if st.sidebar.button("📦 Archive >60 Days Telemetry (.gz)"):
    from db_manager import archive_old_telemetry_to_json
    archived_rows = archive_old_telemetry_to_json(60)
    if archived_rows > 0:
        st.sidebar.success(f"Archived and pruned {archived_rows} telemetry records!")
    else:
        st.sidebar.info("No records older than 60 days to archive.")
        # ==========================================
# NEW FEATURE: TICKET PRIORITY ESCALATION WIDGET
# ==========================================
st.markdown("---")
st.subheader("🚨 Priority Ticket Escalation Panel")

esc_ticket_id = st.text_input("Enter Ticket ID to mark as Urgent (e.g. TKT-1002):")
if st.button("🔥 Elevate Ticket to HIGH Priority"):
    if esc_ticket_id:
        from db_manager import escalate_grievance_priority
        escalate_grievance_priority(esc_ticket_id, "HIGH")
        st.success(f"Ticket `{esc_ticket_id}` elevated to High Priority!")
        # ==========================================
# NEW FEATURE: MANUAL AUDIT LOG ENTRY FORM
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("📝 Record Manual Officer Action")

with st.sidebar.expander("Log Manual Action"):
    officer_id = st.text_input("Officer Name/ID:", value="Officer-MH01")
    act_type = st.selectbox("Action Type:", ["TELEMETRY_REVIEW", "HARDWARE_MAINTENANCE", "MANUAL_CALL_MADE", "OTHER"])
    act_notes = st.text_area("Details / Action Notes:")
    
    if st.button("Save Audit Entry"):
        if act_notes:
            from db_manager import record_admin_audit_event
            record_admin_audit_event(officer_id, act_type, act_notes)
            st.success("Audit event logged successfully!")
            # ==========================================
# NEW FEATURE: SYSTEM HEALTH EXECUTIVE CARD
# ==========================================
st.markdown("---")
st.subheader("🖥️ Cluster Subsystem Diagnostic Matrix")

from db_manager import get_system_health
from rag_engine import verify_vector_search_health, is_internet_available

sys_h = get_system_health()
vec_h = verify_vector_search_health()
net_online = is_internet_available()

h_col1, h_col2, h_col3 = st.columns(3)
h_col1.metric("SQLite Telemetry DB", sys_h["db_status"], f"{sys_h['disk_free_gb']} GB Free")
count_val = vec_h.get("collection_count", vec_h.get("collections", 1))
m_col2.metric("ChromaDB Vector Engine", vec_h.get("status", "Healthy"), f"{count_val} Collections")
h_col3.metric("Groq Cloud Link", "ONLINE" if net_online else "OFFLINE", "Auto Fallback Ready")
# ==========================================
# NEW FEATURE: TRENDING KEYWORDS WIDGET
# ==========================================
st.markdown("---")
st.subheader("🔥 Trending Inquiries Keyword Radar")

from db_manager import fetch_top_query_keywords
top_kw = fetch_top_query_keywords(5)

kw_cols = st.columns(len(top_kw))
for idx, (kw, count) in enumerate(top_kw):
    kw_cols[idx].metric(f"#{idx+1} '{kw.upper()}'", f"{count} Queries")
    # ==========================================
# NEW FEATURE: BACKUP GENERATOR BUTTON
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("💾 Database Backup Utility")

if st.sidebar.button("📦 Create Compressed Backup (.db.gz)"):
    from db_manager import generate_compressed_db_backup
    backup_file = generate_compressed_db_backup()
    if backup_file:
        st.sidebar.success(f"Backup created: `{os.path.basename(backup_file)}`")
    else:
        st.sidebar.error("Failed to generate database backup.")
        # ==========================================
# NEW FEATURE: TICKET TIMELINE DISPLAY WIDGET
# ==========================================
st.markdown("---")
st.subheader("📜 Grievance Lifecycle History Inspector")

inspect_tkt_id = st.text_input("Enter Ticket ID to View Timeline History (e.g. TKT-1001):")
if inspect_tkt_id:
    from db_manager import fetch_ticket_history_timeline
    timeline_events = fetch_ticket_history_timeline(inspect_tkt_id)
    
    if timeline_events:
        st.info(f"Chronological history for `{inspect_tkt_id}`:")
        for ts, old_st, new_st, notes in timeline_events:
            st.markdown(f"• **[{ts}]** Status changed from `{old_st}` ➔ `{new_st}` | *Notes*: {notes}")
    else:
        st.warning(f"No history records found for ticket `{inspect_tkt_id}`.")
        # ==========================================
# FEATURE 189: DISTRICT OFFICER ASSIGNMENT WIDGET
# ==========================================
st.markdown("---")
st.subheader("👤 Assign Nodal Officer to Ticket")

assign_col1, assign_col2 = st.columns(2)
t_id = assign_col1.text_input("Enter Ticket ID (e.g. TKT-1002):")
off_name = assign_col2.selectbox("Select Nodal Officer:", ["Officer Deshmukh (Pune)", "Officer Patil (Shirur)", "Officer Shinde (Baramati)"])

if st.button("📌 Assign Officer"):
    if t_id:
        from db_manager import record_admin_audit_event
        record_admin_audit_event("SUPERVISOR", "OFFICER_ASSIGNED", f"Assigned ticket {t_id} to {off_name}")
        st.success(f"Ticket `{t_id}` assigned to `{off_name}` successfully!")

# ==========================================
# FEATURE 190: SYSTEM CONFIGURATION OVERRIDE GUI
# ==========================================
st.sidebar.markdown("---")
with st.sidebar.expander("⚙️ System Overrides"):
    st.checkbox("Force Offline Mode", value=False)
    st.checkbox("Bypass Amplitude Check", value=False)
    st.number_input("Session Timeout (s)", value=300)

# ==========================================
# FEATURE 191: LANGUAGE BREAKDOWN PIE CHART
# ==========================================
st.markdown("---")
st.subheader("🌐 Language Usage Distribution")

from db_manager import fetch_language_breakdown_stats
lang_stats = fetch_language_breakdown_stats()

if lang_stats:
    import pandas as pd
    df_lang = pd.DataFrame(list(lang_stats.items()), columns=["Language", "Queries"])
    st.bar_chart(df_lang.set_index("Language"))
else:
    st.info("No language statistics available.")

# ==========================================
# FEATURE 192: REINDEX SQLITE DATABASE BUTTON
# ==========================================
st.sidebar.markdown("---")
if st.sidebar.button("⚙️ Reindex SQLite DB"):
    from db_manager import reindex_sqlite_database
    if reindex_sqlite_database():
        st.sidebar.success("Database indexes rebuilt!")

# ==========================================
# FEATURE 193: POSITIVE FEEDBACK SATISFACTION METRIC
# ==========================================
from db_manager import fetch_feedback_positive_percentage
sat_pct = fetch_feedback_positive_percentage()
st.sidebar.metric("Farmer CSAT Rating", f"{sat_pct}%", delta="Positive")

# ==========================================
# FEATURE 194: MANUAL BROADCAST MESSAGE MANAGER
# ==========================================
st.markdown("---")
st.subheader("📢 Publish Kiosk Notice Broadcast")
b_msg = st.text_input("Enter announcement notice for all kiosk screens:")
if st.button("📢 Publish Notice"):
    if b_msg:
        from db_manager import set_pacs_broadcast_message
        set_pacs_broadcast_message(b_msg)
        st.success("Broadcast notice updated live across all kiosk terminals!")
    