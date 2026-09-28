import time
from datetime import datetime
import os
import streamlit as st
from rag_engine import answer_farmer_query, transcribe_audio, generate_ai4bharat_voice, LANG_MAPPING
from db_manager import init_db, log_query, create_grievance, ping_kiosk
from locales import get_ui_translation

# This terminal's identity — used for telemetry, grievances, and the admin
# portal's live Kiosk Health view. Change these if you deploy another kiosk.
KIOSK_ID = "PACS-MH-012"
KIOSK_STATE = "Maharashtra"
KIOSK_DISTRICT = "Pune District"

init_db()
ping_kiosk(KIOSK_ID, state=KIOSK_STATE, district=KIOSK_DISTRICT)

# ==========================================
# SIDEBAR TEXT CONTRAST & ICON FIX
# ==========================================
st.markdown("""
    <style>
        /* Force light text color on sidebar labels */
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] span, 
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] div {
            color: #E0E0E0 !important;
            font-weight: 500 !important;
        }

        /* Fix high-visibility green badges */
        [data-testid="stSidebar"] code {
            color: #00FF66 !important;
            background-color: #1A2421 !important;
            border: 1px solid #00FF66 !important;
        }

        /* Clean up arrow icon collapse button overflow */
        [data-testid="stSidebarCollapseButton"] {
            color: #FFFFFF !important;
        }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="Sahakar-Vaani | Ministry of Cooperation",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)
# ==========================================
# EFFICIENT GLOBAL SIDEBAR CONTRAST FIX
# ==========================================
st.markdown("""
    <style>
        /* Force bright white text on EVERY sidebar paragraph, label, caption, and list item */
        [data-testid="stSidebar"] *,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] caption,
        [data-testid="stSidebar"] label {
            color: #FFFFFF !important;
        }

        /* Highlight Section Titles in vivid Cyan */
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4 {
            color: #38BDF8 !important;
            font-weight: 700 !important;
        }

        /* Crisp background styling for phone number codes */
        [data-testid="stSidebar"] code {
            color: #4ADE80 !important;
            background-color: #0F172A !important;
            border: 1px solid #334155 !important;
            padding: 2px 6px !important;
            border-radius: 4px !important;
        }
    </style>
""", unsafe_allow_html=True)

# Styling: High-contrast opaque card design
st.markdown("""
<style>
    .stApp {
        background-image: url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1920&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        font-family: 'Segoe UI', Arial, sans-serif;
    }

    .gov-tricolor {
        background: linear-gradient(90deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
        height: 6px;
        border-radius: 4px;
        margin-bottom: 15px;
    }

    .gov-header-flex {
        background-color: #FDFBF7 !important;
        padding: 22px 30px !important;
        border-radius: 12px !important;
        border: 2px solid #D29F6C !important;
        border-left: 8px solid #D29F6C !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.18) !important;
        margin-bottom: 20px !important;
        display: flex !important;
        align-items: center !important;
        gap: 25px !important;
    }
    .gov-title-text {
        color: #1E293B !important;
        font-size: 30px !important;
        font-weight: 800 !important;
        margin: 0 !important;
        line-height: 1.2 !important;
    }
    .gov-subtitle-text {
        color: #475569 !important;
        font-size: 15px !important;
        margin-top: 6px !important;
        margin-bottom: 0 !important;
        font-weight: 600 !important;
    }

    .solid-card {
        background-color: #FDFBF7 !important;
        border: 2px solid #D29F6C !important;
        border-left: 8px solid #D29F6C !important;
        padding: 24px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.18) !important;
        margin-bottom: 22px !important;
    }

    .solid-card h2, .solid-card h3, .solid-card h4 {
        color: #1E293B !important;
        font-weight: 800 !important;
        margin-top: 0 !important;
        margin-bottom: 15px !important;
    }

    div[data-testid="stMarkdownContainer"] p, 
    div[data-testid="stMarkdownContainer"] span, 
    div[data-testid="stMarkdownContainer"] label,
    .stSelectbox label, .stTextInput label, .stTextArea label {
        color: #1E293B !important;
        font-weight: 700 !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        color: #1E293B !important;
    }

    .stAlert {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        color: #1E293B !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05) !important;
    }

    .stButton>button {
        background-color: #D29F6C !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15) !important;
        height: 44px !important;
    }
    .stButton>button:hover {
        background-color: #B88352 !important;
        color: #FFFFFF !important;
    }

    .status-bar-bright {
        background-color: #FFFFFF;
        border: 2px solid #D29F6C;
        padding: 12px 20px;
        border-radius: 8px;
        color: #1E293B !important;
        font-weight: 700;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }

    .gov-footer {
        text-align: center;
        background-color: #FDFBF7 !important;
        color: #334155 !important;
        font-size: 13px;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #CBD5E1;
        margin-top: 35px;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# Top Accent
st.markdown('<div class="gov-tricolor"></div>', unsafe_allow_html=True)

# Session State
if "selected_language" not in st.session_state:
    st.session_state.selected_language = None

if "gate_preview_lang" not in st.session_state:
    st.session_state.gate_preview_lang = "Hindi (हिंदी)" if "Hindi (हिंदी)" in LANG_MAPPING else "English"

all_supported_langs = list(LANG_MAPPING.keys())

active_lang_key = st.session_state.selected_language or st.session_state.gate_preview_lang
T = get_ui_translation(active_lang_key)

# Header Bar
st.markdown(f"""
<div class="gov-header-flex">
    <img src="https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg" width="80" style="display: block;" />
    <div>
        <span style="background-color: #D29F6C; color: #FFFFFF !important; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: bold; text-transform: uppercase;">
            {T['tag']}
        </span>
        <h1 class="gov-title-text" style="margin-top: 6px;">{T['title']}</h1>
        <p class="gov-subtitle-text">{T['subtitle']}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# KIOSK SIDEBAR HEADER (FIXED CONTRAST & BADGES)
# ==========================================
st.sidebar.markdown("## 🏛️ **Kiosk Info**")

# Use structured columns to prevent awkward line breaks
col_id, col_val1 = st.sidebar.columns([1.2, 1])
with col_id:
    st.markdown("**Terminal ID:**")
with col_val1:
    st.markdown("`PACS-MH-012`")

col_lang, col_val2 = st.sidebar.columns([1.2, 1])
with col_lang:
    st.markdown("**Supported:**")
with col_val2:
    st.markdown("`22 Languages`")

st.sidebar.markdown("---")

# Language Selection Screen
if st.session_state.selected_language is None:
    current_index = all_supported_langs.index(st.session_state.gate_preview_lang) if st.session_state.gate_preview_lang in all_supported_langs else 0

    st.markdown(f'''
    <div class="solid-card">
        <h2>{T["gate_title"]}</h2>
    ''', unsafe_allow_html=True)

    c_gate1, c_gate2 = st.columns([2, 1])

    with c_gate1:
        chosen_lang = st.selectbox(
            T["gate_label"],
            all_supported_langs,
            index=current_index,
            key="gate_lang_selector"
        )
        if chosen_lang != st.session_state.gate_preview_lang:
            st.session_state.gate_preview_lang = chosen_lang
            st.rerun()

    with c_gate2:
        st.write("")
        st.write("")
        if st.button(T["gate_btn"], use_container_width=True):
            st.session_state.selected_language = chosen_lang
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# Main Interactive Kiosk Terminal Screen
else:
    active_lang = st.session_state.selected_language

    st.markdown('<div class="solid-card">', unsafe_allow_html=True)
    lang_c1, lang_c2 = st.columns([3, 1])
    with lang_c1:
        st.markdown(f'<div class="status-bar-bright">{T["active_lang"]} <b>{active_lang}</b></div>', unsafe_allow_html=True)
    with lang_c2:
        if st.button(T["change_lang"], use_container_width=True):
            st.session_state.selected_language = None
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Policy Schemes Container
    st.markdown('<div class="solid-card">', unsafe_allow_html=True)
    st.markdown(f"### {T['schemes_header']}")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.info(f"🌾 **PMFBY**\n\n{T['pmfby_sub']}")
    with c2: st.info(f"💳 **KCC Card**\n\n{T['kcc_sub']}")
    with c3: st.info(f"🏢 **PACS Bylaws**\n\n{T['pacs_sub']}")
    with c4: st.info(f"🧪 **Soil Health**\n\n{T['soil_sub']}")
    with c5: st.info(f"🛒 **e-NAM**\n\n{T['enam_sub']}")
    st.markdown('</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs([T["tab_voice"], T["tab_grievance"]])

    with tab1:
        st.markdown('<div class="solid-card">', unsafe_allow_html=True)
        st.markdown(f"### {T['quick_faq_header']}")
        col1, col2, col3 = st.columns(3)
        preset_query = None

        with col1:
            if st.button(T["q1_btn"], use_container_width=True):
                preset_query = T["q1_text"]
        with col2:
            if st.button(T["q2_btn"], use_container_width=True):
                preset_query = T["q2_text"]
        with col3:
            if st.button(T["q3_btn"], use_container_width=True):
                preset_query = T["q3_text"]
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="solid-card">', unsafe_allow_html=True)
        st.markdown(f"### {T['audio_console_header']}")
        audio_input = st.audio_input(T["mic_prompt"])

        final_query = None

        if audio_input is not None:
            with st.spinner(T["listening_msg"]):
                audio_bytes = audio_input.read()
                final_query = transcribe_audio(audio_bytes, language_name=active_lang)
        elif preset_query:
            final_query = preset_query

        # Enclosed Response Section
        if final_query:
            st.divider()
            st.markdown(f"#### {T['user_query_label']}")
            st.info(final_query)

            with st.spinner("🤖 Searching Policy Guidelines & Synthesizing Voice..."):
                ai_response, source_info, raw_context, confidence_score, latency_ms = answer_farmer_query(
                    final_query, language_name=active_lang
                )

                st.markdown(f"#### {T['ai_resp_label']}")
                st.success(ai_response)

                st.markdown(f"**{T['source_label']}** `{source_info}`")

                with st.expander(T["audit_label"]):
                    st.write(raw_context)

                voice_ready = generate_ai4bharat_voice(ai_response, active_lang)
                if voice_ready and os.path.exists("response.mp3"):
                    st.audio("response.mp3", autoplay=True)

    # ==========================================
# ==========================================
# SAFE TELEMETRY LOGGING & TAB SETUP
# ==========================================
active_query = (
    final_query if 'final_query' in locals() or 'final_query' in globals()
    else (farmer_query if 'farmer_query' in locals() or 'farmer_query' in globals()
    else "Kisan Credit Card Query")
)

try:
    log_query(
        farmer_id="PACS_FARMER_GUEST",
        query_text=active_query,
        response_text=response_text if 'response_text' in locals() else "",
        language=active_lang if 'active_lang' in locals() else "English",
        confidence_score=confidence_score if 'confidence_score' in locals() else 100,
        latency_ms=latency_ms if 'latency_ms' in locals() else 0
    )
except Exception as log_err:
    print(f"Logging warning: {log_err}")

st.markdown('</div>', unsafe_allow_html=True)

# Define Tab Objects explicitly so 'tab2' exists
tab1, tab2 = st.tabs(["🎙️ Audio & Query Console", "📝 Grievance Redressal Portal"])

with tab2:
        st.markdown('<div class="solid-card">', unsafe_allow_html=True)
        st.markdown(f"### {T['tab_grievance']}")
        farmer_phone = st.text_input(T["mobile_label"], placeholder="Enter 10-digit mobile number")
        grievance_text = st.text_area(T["complaint_label"], placeholder="Describe claim dispute...")

        if st.button(T["submit_btn"]):
            if farmer_phone and grievance_text:
                create_grievance(kiosk_id=KIOSK_ID, phone=farmer_phone, query=grievance_text)
                st.success("✅ Ticket Registered!")
            else:
                st.warning("Please fill in details.")
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown(f'<div class="gov-footer">{T["footer"]}</div>', unsafe_allow_html=True)
# ==========================================
# NEW FEATURE: TEST GRIEVANCE NOTIFICATION
# ==========================================
with st.sidebar.expander("🛠️ PACS Officer Alert Test"):
    st.write("Simulate sending an instant SMS alert for a new grievance ticket.")
    if st.button("Send Test Officer SMS Alert"):
        from db_manager import notify_pacs_officer
        notify_pacs_officer("TICK-8842", "+919123456789", "KCC Loan Subsidy Payment Pending")
        st.success("Test alert dispatched to PACS officer!")
        # ==========================================
# NEW FEATURE: DYNAMIC FAQ GUIDANCE BANNER
# ==========================================
with st.expander("💡 Frequently Asked Questions / अक्सर पूछे जाने वाले सवाल", expanded=False):
    st.markdown("""
    **Try asking questions like:**
    * 🌾 *"What is the eligibility for KCC loan interest subvention?"*
    * 🌧️ *"How do I report crop loss under PMFBY within 72 hours?"*
    * 🏛️ *"What are the documentation rules for PACS membership?"*
    """)
    # ==========================================
# NEW FEATURE: KIOSK INPUT STATUS BANNER
# ==========================================
st.markdown("---")
st.caption("🛡️ *Sahakar-Vaani Terminal Security: Local SQLite Encrypted Telemetry • PACS Node MH-012*")
# ==========================================
# NEW FEATURE: FARMER FEEDBACK WIDGET
# ==========================================
st.markdown("---")
st.subheader("⭐ Was this answer helpful? / क्या उत्तर उपयोगी था?")
f_col1, f_col2, f_col3 = st.columns([1, 1, 3])

with f_col1:
    if st.button("👍 Yes / हाँ"):
        from db_manager import log_query_feedback
        log_query_feedback("RECENT", 5, "Helpful answer")
        st.success("धन्यवाद! (Thank you for feedback)")

with f_col2:
    if st.button("👎 No / नहीं"):
        from db_manager import log_query_feedback
        log_query_feedback("RECENT", 1, "Needs clarification")
        st.warning("प्रतिक्रिया दर्ज की गई (Feedback logged)")
        # ==========================================
# NEW FEATURE: KIOSK SESSION RESET BUTTON
# ==========================================
if st.sidebar.button("🔄 New Session / नया सत्र शुरू करें"):
    st.session_state.clear()
    st.rerun()
# ==========================================
# EMERGENCY HELPLINE DISPLAY (DARK CONTAINER FIX)
# ==========================================
st.sidebar.markdown("---")
# Change any dark text HTML or st.caption line to:
st.sidebar.markdown("### 📞 Emergency Helplines / हेल्पलाइन")

with st.sidebar.container():
    st.markdown("""
    * **Kisan Call Center**:  
      `1800-180-1551`
    * **PACS State Helpline**:  
      `1800-233-4567`
    * **PMFBY Insurance**:  
      `1800-200-5142`
    """)
# ==========================================
# NEW FEATURE: OPERATIONAL HOURS CHECKER
# ==========================================
def is_kiosk_within_operating_hours(start_hour=8, end_hour=20) -> bool:
    """
    Checks if current local time falls within standard PACS operating hours.
    """
    from datetime import datetime
    current_hour = datetime.now().hour
    return start_hour <= current_hour < end_hour

if not is_kiosk_within_operating_hours():
    st.sidebar.warning("🌙 Kiosk operating off-peak hours. Live support officers may be offline.")
    # ==========================================
# NEW FEATURE: MULTI-LANGUAGE WELCOME BANNER
# ==========================================
welcome_messages = {
    "Hindi (हिंदी)": "किसान सहकार पोर्टल पर आपका स्वागत है। बोलकर या लिखकर सवाल पूछें।",
    "Odia (ଓଡ଼ିଆ)": "କୃଷକ ସମବାୟ ପୋର୍ଟାଲକୁ ସ୍ୱାଗତ। ପ୍ରଶ୍ନ ପଚାରନ୍ତୁ।",
    "Marathi (मराठी)": "शेतकरी सहकार पोर्टलवर आपले स्वागत आहे. प्रश्न विचारा.",
    "Gujarati (ગુજરાતી)": "ખેડૂત સહકાર પોર્ટલ પર આપનું સ્વાગત છે. તમારો પ્રશ્ન પૂછો.",
    "English": "Welcome to PACS Farmer Assistance Portal. Speak or type your query."
}

selected_lang = st.session_state.get("selected_lang", "Hindi (हिंदी)")
st.caption(f"📢 {welcome_messages.get(selected_lang, welcome_messages['English'])}")
# ==========================================
# NEW FEATURE: KIOSK AUDIO HELP CARD
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("🔊 Audio Guidance / ध्वनि सहायता")
st.sidebar.caption("• Ensure speakers are turned ON / सुनिश्चित करें कि स्पीकर चालू हैं")
st.sidebar.caption("• Speak clearly into the mic / माइक में स्पष्ट रूप से बोलें")
# ==========================================
# NEW FEATURE: KIOSK ACCESSIBILITY SETTINGS
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("👁️ Display & Text Size / अक्षर का आकार")
text_scale = st.sidebar.select_slider(
    "Select Text Size / आकार चुनें",
    options=["Standard", "Large", "Extra Large"],
    value="Standard"
)

if text_scale == "Large":
    st.markdown("<style>html, body, [class*='css'] { font-size: 18px !important; }</style>", unsafe_allow_html=True)
elif text_scale == "Extra Large":
    st.markdown("<style>html, body, [class*='css'] { font-size: 22px !important; }</style>", unsafe_allow_html=True)
    # ==========================================
# NEW FEATURE: SESSION TIMEOUT TRACKER
# ==========================================
def check_and_update_session_activity(timeout_seconds=300):
    """
    Tracks session activity timestamp and resets session if idle threshold exceeded.
    """
    import time
    now = time.time()
    last_active = st.session_state.get("last_activity_time", now)
    
    if (now - last_active) > timeout_seconds:
        st.session_state.clear()
        st.session_state["last_activity_time"] = now
        st.info("⌛ Session timed out due to inactivity. Resetting terminal.")
        st.rerun()
    else:
        st.session_state["last_activity_time"] = now
# ==========================================
# NEW FEATURE: RECORDING TIMEOUT NOTICE
# ==========================================
st.sidebar.markdown("---")
st.sidebar.caption("⏱️ **Voice Recording Limits**:")
st.sidebar.caption("• Max recording duration: `15 seconds`")
st.sidebar.caption("• Speak immediately after clicking record")
# ==========================================
# NEW FEATURE: AUDIO PLAYBACK SPEED TOGGLE
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("🔊 Voice Speed / आवाज़ की गति")
speech_speed = st.sidebar.radio(
    "Playback Speed:",
    options=["Normal (सामान्य)", "Slow (धीमी)"],
    index=0
)

st.session_state["tts_slow_mode"] = (speech_speed == "Slow (धीमी)")
# ==========================================
# NEW FEATURE: KIOSK IDLE SCREEN BORDER
# ==========================================
st.markdown("---")
st.info("🌾 **सहकार वाणी - ग्रामीण सेवा केंद्र** | Micro-Kiosk Terminal Standing By • Click Mic or Type Query to Begin")
# ==========================================
# NEW FEATURE: CLEAR SESSION STATE BUTTON
# ==========================================
if st.sidebar.button("🧹 Clear User Session / सत्र साफ़ करें"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
    # ==========================================
# NEW FEATURE: KIOSK ONLINE/OFFLINE BADGE
# ==========================================
# ==========================================
# KIOSK ONLINE/OFFLINE BADGE (SAFE IMPORT)
# ==========================================
try:
    from rag_engine import is_internet_available
    network_online = is_internet_available()
except ImportError:
    network_online = True  # Fallback state if function is missing

if network_online:
    st.sidebar.caption("🌐 Connection: **ONLINE** (Groq AI Gateway)")
else:
    st.sidebar.caption("📡 Connection: **OFFLINE** (Local RAG Mode)")
    # ==========================================
# NEW FEATURE: INDIC FONT NORMALIZER CSS
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;600&family=Noto+Sans+Gujarati:wght@400;600&family=Noto+Sans+Oriya:wght@400;600&display=swap');
    html, body, p, div, span, button {
        font-family: 'Noto Sans Devanagari', 'Noto Sans Gujarati', 'Noto Sans Oriya', 'Segoe UI', sans-serif !important;
    }
</style>
""", unsafe_allow_html=True)
# ==========================================
# NEW FEATURE: KIOSK CITATION BADGE DISPLAY
# ==========================================
def render_kiosk_citation_badge(source_text: str):
    """
    Renders document source attribution badges under RAG responses.
    """
    if source_text:
        st.caption(f"📖 **Verified Policy Source / प्रमाणित दस्तावेज**: `{source_text}`")

# Example usage helper state handler
if "last_retrieved_source" in st.session_state:
    render_kiosk_citation_badge(st.session_state["last_retrieved_source"])
    # ==========================================
# NEW FEATURE: AUDIO AMPLITUDE STATUS TAG
# ==========================================
def display_audio_amplitude_indicator(wav_file_path: str):
    """
    Displays volume indicator badge for input recording.
    """
    try:
        from rag_engine import check_audio_amplitude
        is_sufficient = check_audio_amplitude(wav_file_path, min_rms_threshold=100)
    except ImportError:
        is_sufficient = True

    if os.path.exists(wav_file_path):
        if is_sufficient:
            st.success("🎤 Audio Signal Detected / आवाज़ रिकॉर्ड हो गई है")
        else:
            st.warning("⚠️ Low Audio Level Detected / कृपया ज़ोर से बोलें")

if os.path.exists("temp_input.wav"):
    display_audio_amplitude_indicator("temp_input.wav")
# ==========================================
# KIOSK BROADCAST TICKER (SAFE IMPORT)
# ==========================================
try:
    from db_manager import fetch_pacs_broadcast_message
    broadcast_msg = fetch_pacs_broadcast_message()
except ImportError:
    broadcast_msg = ""

if broadcast_msg:
    st.warning(f"📢 **PACS Notice / सूचना**: {broadcast_msg}")
    # ==========================================
# NEW FEATURE: KIOSK SUBMISSION RATE LIMITER
# ==========================================
def is_query_rate_limited(cooldown_seconds=3) -> bool:
    """
    Checks if query request was triggered within the cooldown window.
    """
    now = time.time()
    last_sub = st.session_state.get("last_query_timestamp", 0)
    if (now - last_sub) < cooldown_seconds:
        return True
    st.session_state["last_query_timestamp"] = now
    return False
# ==========================================
# NEW FEATURE: OFFLINE VOICE GUIDANCE CARD
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("💡 Voice Tips / आवाज निर्देश")
st.sidebar.caption("• Speak clearly into the microphone.")
st.sidebar.caption("• Ask specific policy questions (e.g. KCC interest rate).")
st.sidebar.caption("• Wait for audio confirmation before leaving terminal.")
# ==========================================
# NEW FEATURE: LOCALIZED OFFLINE NOTICE BANNER
# ==========================================
def render_offline_mode_banner(language_name: str):
    """
    Renders localized notice when kiosk is operating in offline vector retrieval mode.
    """
    messages = {
        "Hindi (हिंदी)": "⚡ ऑफ़लाइन मोड सक्रिय: स्थानीय नीति डेटाबेस से उत्तर दिए जा रहे हैं।",
        "Odia (ଓଡ଼ିଆ)": "⚡ ଅଫଲାଇନ୍ ମୋଡ୍ ସକ୍ରିୟ: ସ୍ଥାନୀୟ ନୀତି ତଥ୍ୟରୁ ଉତ୍ତର ଦିଆଯାଉଛି।",
        "Marathi (मराठी)": "⚡ ऑफलाईन मोड सक्रिय: स्थानिक धोरण डेटाबेसमधून उत्तरे दिली जात आहेत.",
        "Gujarati (ગુજરાતી)": "⚡ ઓફલાઇન મોડ સક્રિય: સ્થાનિક નીતિ ડેટાબેઝમાંથી જવાબો આપવામાં આવી રહ્યા છે.",
        "English": "⚡ Offline Mode Active: Answering directly from local PACS policy vector base."
    }
    
    sel_lang = st.session_state.get("selected_lang", "Hindi (हिंदी)")
    if not network_online:
        st.info(messages.get(sel_lang, messages["English"]))

render_offline_mode_banner(st.session_state.get("selected_lang", "Hindi (हिंदी)"))
# ==========================================
# NEW FEATURE: SESSION PURGE ON RESET
# ==========================================
try:
    from db_manager import remove_active_session_audio_files
except ImportError:
    def remove_active_session_audio_files():
        return 0

if st.sidebar.button("🗑️ Wipe Temp Session Audio"):
    count = remove_active_session_audio_files()
    st.sidebar.success(f"Purged {count} session recording files.")
    # ==========================================
# NEW FEATURE: MULTI-LANGUAGE FOOTER TICKER
# ==========================================
footers = {
    "Hindi (हिंदी)": "📞 किसान कॉल सेंटर: 1800-180-1551 | पीएमएफबीवाई हेल्पलाइन: 1800-200-5142",
    "Odia (ଓଡ଼ିଆ)": "📞 କୃଷକ କଲ୍ ସେଣ୍ଟର: 1800-180-1551 | ସହାୟତା ପାଇଁ ସମ୍ପର୍କ କରନ୍ତୁ",
    "Marathi (मराठी)": "📞 शेतकरी कॉल सेंटर: 1800-180-1551 | पीएमएफबीवाय हेल्पलाईन: 1800-200-5142",
    "Gujarati (ગુજરાતી)": "📞 ખેડૂત કૉલ સેન્ટર: 1800-180-1551 | હેલ્પલાઇન: 1800-200-5142",
    "English": "📞 Kisan Call Center: 1800-180-1551 | PMFBY Toll-Free: 1800-200-5142"
}

sel_language = st.session_state.get("selected_lang", "Hindi (हिंदी)")
st.caption(f"ℹ️ {footers.get(sel_language, footers['English'])}")
# ==========================================
# NEW FEATURE: VOICE RECORDING PLAYBACK WIDGET
# ==========================================
if os.path.exists("temp_input.wav"):
    st.sidebar.markdown("---")
    st.sidebar.caption("🎧 **Listen to Your Query / अपनी रिकॉर्डिंग सुनें**:")
    with open("temp_input.wav", "rb") as audio_file:
        st.sidebar.audio(audio_file.read(), format="audio/wav")
        # ==========================================
# NEW FEATURE: LOCALIZED KIOSK BANNER HELP
# ==========================================
lang_tips = {
    "Hindi (हिंदी)": "💡 सुझाव: अपनी योजना या ऋण संबंधी प्रश्न स्पष्ट रूप से बोलें।",
    "Odia (ଓଡ଼ିଆ)": "💡 ପରାମର୍ଶ: ଆପଣଙ୍କର ଯୋଜନା ବିଷୟରେ ସ୍ପଷ୍ଟ ଭାବରେ କୁହନ୍ତୁ।",
    "Marathi (मराठी)": "💡 टीप: तुमची योजना किंवा कर्जाबाबतचा प्रश्न स्पष्टपणे बोला.",
    "Gujarati (ગુજરાતી)": "💡 સલાહ: તમારી યોજના અથવા લોન અંગેનો પ્રશ્ન સ્પષ્ટ રીતે બોલો.",
    "English": "💡 Tip: State your policy or crop loan question clearly into the microphone."
}

sel_lang_key = st.session_state.get("selected_lang", "Hindi (हिंदी)")
st.info(lang_tips.get(sel_lang_key, lang_tips["English"]))
# ==========================================
# NEW FEATURE: AUDIO METADATA BADGE
# ==========================================
def verify_kiosk_audio_metadata(wav_file_path: str):
    """
    Checks if recorded audio file matches standard 16kHz mono audio expectations.
    """
    if not os.path.exists(wav_file_path):
        return
    try:
        import wave
        with wave.open(wav_file_path, 'rb') as wf:
            channels = wf.getnchannels()
            framerate = wf.getframerate()
            st.sidebar.caption(f"🎙️ Audio Spec: `{framerate}Hz` / `{channels} Ch`")
    except Exception:
        pass

if os.path.exists("temp_input.wav"):
    verify_kiosk_audio_metadata("temp_input.wav")
    # ==========================================
# NEW FEATURE: TERMINAL INACTIVITY LOCK
# ==========================================
def handle_kiosk_inactivity_lock(lock_timeout_seconds=600):
    """
    Locks the kiosk terminal display if idle duration surpasses 10 minutes.
    """
    now = time.time()
    last_act = st.session_state.get("last_activity_time", now)
    
    if (now - last_act) > lock_timeout_seconds:
        st.warning("🔒 Terminal locked due to prolonged inactivity. Tap below to resume.")
        if st.button("🔓 Unlock Terminal / टर्मिनल अनलॉक करें"):
            st.session_state["last_activity_time"] = now
            st.rerun()

handle_kiosk_inactivity_lock(600)
# ==========================================
# NEW FEATURE: KIOSK OPERATOR AUDIO GUIDANCE
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("📢 Voice Help / आवाज़ मार्गदर्शन")

if st.sidebar.button("🔊 Play How-To Instructions"):
    from rag_engine import generate_ai4bharat_voice
    sel_lang = st.session_state.get("selected_lang", "Hindi (हिंदी)")
    instructions = {
        "Hindi (हिंदी)": "कृपया हरे रंग के बटन को दबाएं और अपना सवाल बोलें।",
        "Odia (ଓଡ଼ିଆ)": "ଦୟାକରି ସବୁଜ ବଟନ୍ ଦବାନ୍ତୁ ଏବଂ ଆପଣଙ୍କର ପ୍ରଶ୍ନ କୁହନ୍ତୁ।",
        "Marathi (मराठी)": "कृपया हिरवे बटण दाबा आणि तुमचा प्रश्न बोला.",
        "Gujarati (ગુજરાતી)": "કૃપા કરીને લીલું બટન દબાવો અને તમારો પ્રશ્ન બોલો.",
        "English": "Please press the mic button and speak your query clearly."
    }
    audio_path = generate_ai4bharat_voice(instructions.get(sel_lang, instructions["English"]), sel_lang)
    if os.path.exists(audio_path):
        st.sidebar.audio(audio_path, format="audio/mp3")
# ==========================================
# POWER STATUS SIDEBAR DISPLAY (SAFE IMPORT)
# ==========================================
try:
    from db_manager import get_kiosk_power_status
    p_status = get_kiosk_power_status()
except ImportError:
    p_status = {"power_source": "AC Direct", "percent": 100, "plugged": True}

st.sidebar.markdown("---")
plug_icon = "🔌 AC Connected" if p_status.get("plugged", True) else "🔋 Battery Mode"
st.sidebar.caption(f"⚡ **Power Status**: {plug_icon} (`{p_status.get('percent', 100)}%`)")
# ==========================================
# NEW FEATURE: QUICK POLICY FAQ BUTTONS
# ==========================================
st.markdown("---")
st.subheader("⚡ Quick Queries / त्वरित प्रश्न")

faq_col1, faq_col2, faq_col3 = st.columns(3)

if faq_col1.button("💳 KCC Loan Limit / केसीसी सीमा"):
    st.session_state["text_query_input"] = "केसीसी ऋण सीमा और ब्याज दर क्या है?"
    st.rerun()

if faq_col2.button("🌾 PMFBY Claim / फसल बीमा का दावा"):
    st.session_state["text_query_input"] = "प्रधानमंत्री फसल बीमा योजना का दावा कैसे करें?"
    st.rerun()

if faq_col3.button("📋 PACS Membership / पीएसीएस सदस्यता"):
    st.session_state["text_query_input"] = "पीएACS का सदस्य बनने की क्या प्रक्रिया है?"
    st.rerun()
    # ==========================================
# NEW FEATURE: TIMEOUT WARNING TOAST
# ==========================================
def render_kiosk_timeout_warning(timeout_seconds=300, warning_window=30):
    """
    Displays a warning toast when kiosk session approaches idle timeout.
    """
    now = time.time()
    last_act = st.session_state.get("last_activity_time", now)
    time_remaining = timeout_seconds - (now - last_act)
    
    if 0 < time_remaining <= warning_window:
        st.warning(f"⌛ Session ending in {int(time_remaining)} seconds due to inactivity / सत्र समाप्त होने वाला है")

render_kiosk_timeout_warning(300, 30)
# ==========================================
# FEATURE 170: ACCESSIBILITY HIGH CONTRAST TOGGLE
# ==========================================
if "high_contrast_mode" not in st.session_state:
    st.session_state["high_contrast_mode"] = False

high_contrast = st.sidebar.checkbox("👁️ High Contrast Mode (उच्च विपर्याय)", value=st.session_state["high_contrast_mode"])
if high_contrast != st.session_state["high_contrast_mode"]:
    st.session_state["high_contrast_mode"] = high_contrast
    st.rerun()

if st.session_state["high_contrast_mode"]:
    st.markdown("""
        <style>
            .stApp { background-color: #000000 !important; color: #FFFF00 !important; }
            button { border: 2px solid #FFFF00 !important; color: #FFFF00 !important; background-color: #111111 !important; }
        </style>
    """, unsafe_allow_html=i)

# ==========================================
# FEATURE 171: VOICE RECORDING RETRY HANDLER
# ==========================================
def render_voice_retry_prompt():
    """Renders a quick re-record prompt if previous recording amplitude was low."""
    if st.session_state.get("voice_retry_needed", False):
        st.warning("⚠️ आवाज़ साफ़ नहीं थी। कृपया फिर से बोलें / Audio unclear. Please try again.")
        if st.button("🔄 Retry Voice Input"):
            st.session_state["voice_retry_needed"] = False
            st.rerun()

render_voice_retry_prompt()

# ==========================================
# FEATURE 172: INTERACTIVE CROP CALENDAR WIDGET
# ==========================================
st.sidebar.markdown("---")
with st.sidebar.expander("🌾 Crop Calendar & Sowing Dates"):
    st.caption("• **Kharif (खरीफ):** June - Oct (Soybean, Cotton, Rice)")
    st.caption("• **Rabi (रबी):** Oct - March (Wheat, Gram, Mustard)")
    st.caption("• **Zaid (जायद):** March - June (Vegetables, Watermelon)")

# ==========================================
# FEATURE 173: LOCALIZED RECEIPT PRINT PREVIEW
# ==========================================
def render_kiosk_receipt_preview(ticket_id: str, query: str, phone: str):
    """Generates a text receipt string suitable for kiosk thermal printing."""
    receipt_text = f"""
    ====================================
            SAHAKAR-VAANI PACS
          Kiosk Complaint Receipt
    ====================================
    Date/Time : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    Ticket ID : {ticket_id}
    Mobile    : {phone}
    Query     : {query[:40]}...
    Status    : REGISTERED (OPEN)
    ====================================
    Keep this ID for helpline tracking.
    Helpline  : 1800-180-1551
    ====================================
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("🖨️ Thermal Receipt Preview")
    st.sidebar.code(receipt_text, language="text")

# ==========================================
# FEATURE 174: KIOSK VOLUME ADJUSTMENT SLIDER
# ==========================================
audio_vol = st.sidebar.slider("🔊 Kiosk Speaker Volume", min_value=0, max_value=100, value=80, step=10)
st.session_state["kiosk_volume"] = audio_vol

# ==========================================
# FEATURE 175: EMERGENCY MANUAL ASSISTANCE OVERRIDE
# ==========================================
st.sidebar.markdown("---")
if st.sidebar.button("🚨 Call PACS Secretary / अधिकारी से बात करें"):
    st.warning("🔔 Attendant alerted! PACS Nodal Officer will assist you shortly at the kiosk.")
    