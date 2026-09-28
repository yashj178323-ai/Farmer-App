import hashlib
import html
import os
import streamlit as st

from rag_engine import (
    LANG_MAPPING,
    answer_farmer_query,
    generate_ai4bharat_voice,
    is_internet_available,
    transcribe_audio,
)
from db_manager import create_grievance, init_db, log_query, ping_kiosk
from locales import get_ui_translation

KIOSK_ID = "PACS-MH-012"
KIOSK_STATE = "Maharashtra"
KIOSK_DISTRICT = "Pune District"

st.set_page_config(
    page_title="Sahakar-Vaani | Farmer Kiosk",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_db()
ping_kiosk(KIOSK_ID, state=KIOSK_STATE, district=KIOSK_DISTRICT)

# -----------------------------------------------------------------------------
# UI CSS
# -----------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+Devanagari:wght@400;500;600;700;800&display=swap');

:root {
    --navy:#17324D;
    --muted:#536273;
    --saffron:#D68B3A;
    --green:#258653;
    --line:#D9E2EA;
}

html, body, [class*="css"] {
    font-family:'Inter','Noto Sans Devanagari',sans-serif;
}

/* Remove Streamlit's top rectangular header completely. */
[data-testid="stHeader"],
[data-testid="stToolbar"],
.stAppDeployButton {
    display:none !important;
    height:0 !important;
}

.stApp {
    min-height:100vh;
    background:
      linear-gradient(rgba(20,42,58,.40),rgba(20,42,58,.40)),
      url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1920&auto=format&fit=crop');
    background-size:cover;
    background-position:center;
    background-attachment:fixed;
}

.block-container {
    max-width:1180px !important;
    padding:22px 26px 42px 26px !important;
    margin-top:16px !important;
    margin-bottom:24px !important;
    background:#FFFFFF !important;
    border:1px solid #D7E0E8 !important;
    border-radius:20px !important;
    box-shadow:0 10px 35px rgba(0,0,0,.20) !important;
}

/* Every bordered Streamlit container is an opaque white card. */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background:#FFFFFF !important;
    border:1px solid #D7E0E8 !important;
    border-left:6px solid var(--saffron) !important;
    border-radius:16px !important;
    box-shadow:0 8px 24px rgba(0,0,0,.16) !important;
    padding:4px 4px 8px 4px !important;
    margin-bottom:16px !important;
}

/* Plain dynamic markdown text gets a white surface too. */
div[data-testid="stMarkdownContainer"] {
    color:#1F2D3D !important;
}
div[data-testid="stMarkdownContainer"] p,
div[data-testid="stMarkdownContainer"] li {
    color:#1F2D3D !important;
}

/* Main input controls are always white and high contrast. */
div[data-baseweb="select"] > div,
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stAudioInput"],
[data-testid="stFileUploaderDropzone"] {
    background:#FFFFFF !important;
    color:#17283A !important;
    border:1px solid #C9D5E0 !important;
    border-radius:10px !important;
}

[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder {
    color:#6B7785 !important;
    opacity:1 !important;
}

label, [data-testid="stWidgetLabel"] p {
    color:#26384A !important;
    font-weight:700 !important;
}

/* Opaque surfaces for all dynamic Streamlit messages and controls. */
[data-testid="stAlert"],
[data-testid="stNotification"],
[data-testid="stStatusWidget"],
[data-testid="stInfo"],
[data-testid="stSuccess"],
[data-testid="stWarning"],
[data-testid="stError"] {
    background:#FFFFFF !important;
    color:#1F2D3D !important;
    border-radius:11px !important;
}

[data-testid="stMarkdownContainer"] {
    background:transparent !important;
}

[data-testid="stVerticalBlock"] {
    color:#1F2D3D;
}

div[data-testid="stHorizontalBlock"] {
    background:transparent !important;
}

.stButton > button {
    min-height:44px !important;
    border-radius:10px !important;
    border:1px solid #C77F32 !important;
    background:#D99A5B !important;
    color:#FFFFFF !important;
    font-weight:800 !important;
}
.stButton > button:hover {
    background:#BD7835 !important;
    border-color:#BD7835 !important;
}

/* Hamburger button. */
.hamburger-row {
    margin-bottom:8px;
}

.menu-caption {
    color:#17324D !important;
    font-weight:800 !important;
    font-size:18px !important;
    padding-top:9px;
}

.hero-title {
    color:#17324D !important;
    font-size:31px !important;
    line-height:1.2 !important;
    font-weight:800 !important;
    margin:4px 0 !important;
}
.hero-subtitle {
    color:#405165 !important;
    font-size:16px !important;
    font-weight:700 !important;
    margin:0 !important;
}
.gov-tag {
    display:inline-block;
    background:#E4A15E;
    color:#FFFFFF !important;
    padding:6px 12px;
    border-radius:7px;
    font-size:12px;
    font-weight:800;
}
.section-title {
    color:#17324D !important;
    font-size:22px !important;
    font-weight:800 !important;
    margin:2px 0 10px 0 !important;
}
.card-label {
    color:#17324D !important;
    font-weight:800 !important;
    font-size:17px !important;
}
.info-box {
    background:#F4F8FC;
    border:1px solid #D5E0EA;
    border-radius:10px;
    padding:13px 15px;
    color:#1F2D3D !important;
    font-weight:700;
}
.query-box,
.answer-box,
.source-box,
.warning-box {
    background:#FFFFFF;
    border:1px solid #D5E0EA;
    border-radius:11px;
    padding:14px 16px;
    margin:9px 0;
    color:#1F2D3D !important;
}
.answer-box {
    background:#F7FFFA;
    border-left:5px solid #258653;
}
.source-box {
    background:#F6FAFE;
    border-left:5px solid #4B83B5;
}
.warning-box {
    background:#FFF9F0;
    border-left:5px solid #D68B3A;
}
.scheme-card {
    background:#F5F8FC;
    border:1px solid #D6E1EB;
    border-radius:12px;
    padding:14px;
    min-height:110px;
}
.scheme-card strong {
    display:block;
    color:#17324D !important;
    font-size:15px;
    margin-bottom:7px;
}
.scheme-card span {
    color:#536273 !important;
    font-size:13px;
    font-weight:600;
}

/* Metrics are also placed on solid white cards. */
[data-testid="stMetric"] {
    background:#FFFFFF !important;
    border:1px solid #D5E0EA !important;
    border-radius:11px !important;
    padding:10px 14px !important;
}
[data-testid="stMetricLabel"] p,
[data-testid="stMetricValue"] {
    color:#17324D !important;
}

[data-testid="stExpander"] {
    background:#FFFFFF !important;
    border:1px solid #D5E0EA !important;
    border-radius:11px !important;
}

[data-testid="stAudio"] {
    background:#FFFFFF !important;
    border:1px solid #D5E0EA !important;
    border-radius:11px !important;
    padding:8px !important;
}

.footer {
    background:#FFFFFF;
    border:1px solid #D7E0E8;
    border-radius:12px;
    padding:14px;
    text-align:center;
    color:#536273 !important;
    font-size:13px;
    font-weight:700;
    box-shadow:0 8px 24px rgba(0,0,0,.12);
}

[data-testid="stSidebar"] {
    background:#17283A !important;
}
[data-testid="stSidebar"] * {
    color:#F8FAFC !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color:#FFD39A !important;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Session state
# -----------------------------------------------------------------------------
defaults = {
    "selected_language": None,
    "last_audio_hash": None,
    "last_query": "",
    "last_response": "",
    "last_source": "",
    "last_context": [],
    "last_confidence": 0,
    "last_latency": 0,
    "last_audio_path": "",
    "text_scale": "Standard",
    "tts_slow": False,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

all_langs = list(LANG_MAPPING.keys())
if st.session_state.selected_language not in all_langs:
    st.session_state.selected_language = None

# -----------------------------------------------------------------------------
# Hamburger feature menu — replaces the old top rectangular area.
# -----------------------------------------------------------------------------
menu_col, title_col = st.columns([0.8, 8.2], gap="small")
with menu_col:
    with st.popover("☰", use_container_width=True):
        st.markdown("### Sahakar-Vaani Menu")
        st.caption("Open the kiosk features and controls from here.")

        current_index = (
            all_langs.index(st.session_state.selected_language)
            if st.session_state.selected_language in all_langs
            else 0
        )
        menu_language = st.selectbox(
            "Language",
            all_langs,
            index=current_index,
            key="menu_language_v3",
        )
        if st.button("🌐 Apply selected language", use_container_width=True):
            # Store exactly what the user selected. No preview-language state is used.
            st.session_state.selected_language = menu_language
            st.session_state.last_audio_hash = None
            st.rerun()

        st.markdown("---")
        st.markdown("**Features**")
        st.markdown("🎙️ Ask about government schemes")
        st.markdown("📖 View retrieved policy sources")
        st.markdown("🚨 Register a grievance")
        st.markdown("📞 Government helplines")

        st.markdown("---")
        st.markdown("**Display & voice**")
        st.session_state.text_scale = st.selectbox(
            "Text size",
            ["Standard", "Large", "Extra Large"],
            index=["Standard", "Large", "Extra Large"].index(st.session_state.text_scale),
            key="menu_text_scale",
        )
        speed = st.radio("Voice speed", ["Normal", "Slow"], index=1 if st.session_state.tts_slow else 0, key="menu_voice_speed")
        st.session_state.tts_slow = speed == "Slow"

        st.markdown("---")
        st.markdown("**Kiosk**")
        st.caption(f"Terminal: {KIOSK_ID}")
        st.caption(f"Location: {KIOSK_DISTRICT}, {KIOSK_STATE}")
        st.caption(f"Connection: {'Online' if is_internet_available() else 'Limited'}")

        if st.button("🔄 New session", use_container_width=True):
            lang = st.session_state.selected_language
            st.session_state.clear()
            for k, v in defaults.items():
                st.session_state[k] = v
            st.session_state.selected_language = lang
            st.rerun()

with title_col:
    st.markdown('<div class="menu-caption">🌾 Sahakar-Vaani • Farmer Assistance Kiosk</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Header card
# -----------------------------------------------------------------------------
with st.container(border=True):
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:20px;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg" style="width:72px;height:72px;object-fit:contain;">
            <div>
                <span class="gov-tag">{html.escape(get_ui_translation(st.session_state.selected_language or "English")['tag'])}</span>
                <div class="hero-title">🏛️ {html.escape(get_ui_translation(st.session_state.selected_language or "English")['title'])}</div>
                <div class="hero-subtitle">{html.escape(get_ui_translation(st.session_state.selected_language or "English")['subtitle'])}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# Language gate
# -----------------------------------------------------------------------------
if st.session_state.selected_language is None:
    gate_ui = get_ui_translation("English")
    with st.container(border=True):
        st.markdown(f'<div class="section-title">🌐 {html.escape(gate_ui["gate_title"])}</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">Select the exact language you will speak. '
            'The voice transcription, AI answer and voice playback will use this same language.</div>',
            unsafe_allow_html=True,
        )
        chosen = st.selectbox(
            gate_ui["gate_label"],
            all_langs,
            index=0,
            key="gate_language_v3",
        )
        if st.button(gate_ui["gate_btn"], type="primary", use_container_width=True):
            # Exact widget value -> exact application language.
            st.session_state.selected_language = chosen
            st.session_state.last_audio_hash = None
            st.rerun()
    st.stop()

active_lang = st.session_state.selected_language
T = get_ui_translation(active_lang)

# -----------------------------------------------------------------------------
# Active language and status
# -----------------------------------------------------------------------------
with st.container(border=True):
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown(f'<div class="info-box">🌐 {html.escape(T["active_lang"])} <b>{html.escape(active_lang)}</b></div>', unsafe_allow_html=True)
    with c2:
        if st.button("Change language", use_container_width=True):
            st.session_state.selected_language = None
            st.session_state.last_audio_hash = None
            st.session_state.last_query = ""
            st.session_state.last_response = ""
            st.session_state.last_source = ""
            st.session_state.last_context = []
            st.rerun()

# -----------------------------------------------------------------------------
# Policy schemes
# -----------------------------------------------------------------------------
with st.container(border=True):
    st.markdown(f'<div class="section-title">📚 {html.escape(T["schemes_header"])}</div>', unsafe_allow_html=True)
    cols = st.columns(5)
    schemes = [
        ("🌾 PMFBY", T["pmfby_sub"]),
        ("💳 KCC Card", T["kcc_sub"]),
        ("🏢 PACS Bylaws", T["pacs_sub"]),
        ("🧪 Soil Health", T["soil_sub"]),
        ("🛒 e-NAM", T["enam_sub"]),
    ]
    for col, (title, subtitle) in zip(cols, schemes):
        with col:
            st.markdown(f'<div class="scheme-card"><strong>{html.escape(title)}</strong><span>{html.escape(subtitle)}</span></div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Query console
# -----------------------------------------------------------------------------
with st.container(border=True):
    st.markdown(f'<div class="section-title">🎙️ {html.escape(T["audio_console_header"])}</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Ask one clear question about KCC, PMFBY, PACS bylaws, Soil Health Card or e-NAM. The answer is generated only from the policy documents indexed in this kiosk.</div>', unsafe_allow_html=True)

    audio_input = st.audio_input("🎙️ Record your question", key="farmer_audio_input_v2")

    typed_query = st.text_input(
        "Or type your question",
        placeholder="Example: Within how many hours must crop damage be reported under PMFBY?",
        key="typed_policy_question",
    )

    q1, q2, q3 = st.columns(3)
    preset_query = None
    with q1:
        if st.button(T["q1_btn"], use_container_width=True):
            preset_query = T["q1_text"]
    with q2:
        if st.button(T["q2_btn"], use_container_width=True):
            preset_query = T["q2_text"]
    with q3:
        if st.button(T["q3_btn"], use_container_width=True):
            preset_query = T["q3_text"]

    ask_typed = st.button("🔎 Ask this question", type="primary", use_container_width=True)

    final_query = None

    # Audio is processed exactly once per recording.
    if audio_input is not None:
        audio_bytes = audio_input.getvalue()
        audio_hash = hashlib.sha256(audio_bytes).hexdigest()
        if audio_hash != st.session_state.last_audio_hash:
            st.session_state.last_audio_hash = audio_hash
            with st.spinner("🎙️ Converting your speech to text..."):
                transcript = transcribe_audio(audio_bytes, language_name=active_lang)
            if transcript and not transcript.startswith(("Transcription Error", "Invalid")):
                final_query = transcript.strip()
            else:
                st.error(transcript or "Could not understand the recording.")

    if final_query is None and preset_query:
        final_query = preset_query
    if final_query is None and ask_typed and typed_query.strip():
        final_query = typed_query.strip()

    if final_query:
        st.session_state.last_query = final_query
        with st.spinner("🔎 Checking the verified policy documents..."):
            response_text, source_info, raw_context, confidence_score, latency_ms = answer_farmer_query(
                final_query,
                language_name=active_lang,
            )

        st.session_state.last_response = response_text
        st.session_state.last_source = source_info
        st.session_state.last_context = raw_context
        st.session_state.last_confidence = confidence_score
        st.session_state.last_latency = latency_ms

        st.markdown(
            f'<div class="query-box"><span class="card-label">🧑‍🌾 {html.escape(T["user_query_label"])}</span><br>{html.escape(final_query)}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="answer-box"><span class="card-label">🤖 {html.escape(T["ai_resp_label"])}</span><br>{html.escape(response_text)}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="source-box"><span class="card-label">📌 {html.escape(T["source_label"])}</span><br>{html.escape(source_info or "No verified source found.")}</div>',
            unsafe_allow_html=True,
        )

        if raw_context:
            with st.expander("📖 View the exact policy excerpts used for this answer"):
                for i, doc in enumerate(raw_context, 1):
                    src = html.escape(str(doc.get("source", "Unknown")))
                    page = doc.get("page")
                    page_text = f" • page {page}" if page else ""
                    st.markdown(f"**Source {i}: {src}{page_text}**")
                    st.write(doc.get("text", ""))

        with st.container(border=True):
            m1, m2, m3 = st.columns(3)
            m1.metric("Knowledge match", f"{confidence_score}%")
            m2.metric("Response time", f"{latency_ms} ms")
            m3.metric("Answer language", active_lang)

        with st.spinner("🔊 Preparing voice in the selected language..."):
            audio_path = generate_ai4bharat_voice(
                response_text,
                active_lang,
                slow=st.session_state.tts_slow,
            )
        if audio_path and os.path.exists(audio_path):
            st.audio(audio_path, format="audio/wav" if audio_path.endswith(".wav") else "audio/mp3", autoplay=True)
        else:
            st.markdown('<div class="warning-box">🔊 The text answer is ready, but voice playback could not be generated in the selected language.</div>', unsafe_allow_html=True)

        try:
            log_query(
                farmer_id="PACS_FARMER_GUEST",
                query_text=final_query,
                response_text=response_text,
                language=active_lang,
                confidence_score=confidence_score / 100.0,
                latency_ms=latency_ms,
            )
        except Exception as exc:
            print(f"Telemetry logging warning: {exc}")

# -----------------------------------------------------------------------------
# Grievance + helplines
# -----------------------------------------------------------------------------
with st.container(border=True):
    st.markdown("<div class='section-title'>🚨 Official Helpline & Grievance</div>", unsafe_allow_html=True)
    st.markdown('<div class="info-box">Kisan Call Center: <b>1800-180-1551</b> &nbsp; • &nbsp; PMFBY: <b>1800-200-5142</b> &nbsp; • &nbsp; PACS State Helpline: <b>1800-233-4567</b></div>', unsafe_allow_html=True)

    with st.expander("Register a grievance ticket"):
        phone = st.text_input("Mobile number", placeholder="Enter 10-digit mobile number", key="grievance_phone_v2")
        complaint = st.text_area("Complaint / issue", placeholder="Describe the issue clearly", key="grievance_text_v2")
        if st.button("Submit grievance ticket", type="primary", use_container_width=True):
            if phone.strip() and complaint.strip():
                ticket_id = create_grievance(KIOSK_ID, phone.strip(), complaint.strip())
                st.success(f"Ticket registered successfully: {ticket_id}")
            else:
                st.warning("Please provide both mobile number and complaint.")

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown("""
<div class="footer">
    Ministry of Cooperation • Primary Agricultural Credit Societies (PACS) Network<br>
    Sahakar-Vaani • Multilingual farmer assistance kiosk
</div>
""", unsafe_allow_html=True)
