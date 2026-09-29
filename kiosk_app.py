import hashlib
import html
import os
import streamlit as st
import streamlit.components.v1 as components

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
    background:transparent !important;
    border:none !important;
    border-radius:0 !important;
    box-shadow:none !important;
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

/* Individual dynamic cards stay solid; the farm image remains visible around them. */
.query-box, .answer-box, .source-box, .info-box, .warning-box, .scheme-card {
    background:#FFFFFF !important;
    color:#1F2D3D !important;
    border:1px solid #D7E0E8 !important;
    border-radius:12px !important;
    padding:14px 16px !important;
    box-shadow:0 3px 12px rgba(0,0,0,.10) !important;
}
.query-box { border-left:5px solid #D68B3A !important; }
.answer-box { border-left:5px solid #258653 !important; }
.source-box { border-left:5px solid #4B83B5 !important; }
.warning-box { border-left:5px solid #D68B3A !important; }
.scheme-card { min-height:72px !important; text-align:left !important; }
.scheme-card strong, .scheme-card span { display:block !important; color:#1F2D3D !important; }
.scheme-card span { margin-top:8px !important; color:#536273 !important; }
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
# UI translation
# -----------------------------------------------------------------------------
UI_BASE = {
    "tag":"Government of India • Ministry of Cooperation",
    "title":"Sahakar-Vaani | Farmer Assistance Kiosk",
    "subtitle":"Voice-first, policy-grounded assistance for farmers",
    "menu_title":"Sahakar-Vaani Menu",
    "menu_caption":"Open kiosk features and settings.",
    "language":"Language",
    "apply_language":"🌐 Apply selected language",
    "features":"Features",
    "feature_questions":"🎙️ Ask about government schemes",
    "feature_sources":"📖 View retrieved policy sources",
    "feature_grievance":"🚨 Register a grievance",
    "feature_helplines":"📞 Government helplines",
    "display_voice":"Display & voice",
    "text_size":"Text size",
    "standard":"Standard",
    "large":"Large",
    "extra_large":"Extra Large",
    "voice_speed":"Voice speed",
    "normal":"Normal",
    "slow":"Slow",
    "kiosk":"Kiosk",
    "new_session":"New session",
    "connection":"Connection",
    "gate_title":"Choose your language",
    "gate_label":"Select language",
    "gate_btn":"Continue",
    "gate_info":"Select the exact language you will speak. The voice transcription, AI answer and voice playback will use this same language.",
    "active_lang":"Active language:",
    "change_language":"Change language",
    "schemes_header":"Supported policy knowledge",
    "pmfby_sub":"Crop insurance",
    "kcc_sub":"Credit & interest",
    "pacs_sub":"Cooperative rules",
    "soil_sub":"Soil testing & card",
    "enam_sub":"Market rules",
    "audio_console_header":"Ask the policy assistant",
    "query_info":"Ask one clear question about KCC, PMFBY, PACS bylaws, Soil Health Card or e-NAM. Answers are generated only from the policy documents indexed in this kiosk.",
    "record_question":"🎙️ Record your question",
    "type_question":"Or type your question",
    "placeholder":"Example: Within how many hours must crop damage be reported under PMFBY?",
    "ask_question":"🔎 Ask this question",
    "q1_btn":"PMFBY reporting", "q1_text":"Within how many hours must crop damage be reported under PMFBY?",
    "q2_btn":"KCC interest", "q2_text":"What interest rate or interest benefit is stated for KCC in the policy documents?",
    "q3_btn":"PACS rule", "q3_text":"What does the PACS policy say about membership?",
    "converting":"🎙️ Converting your speech to text...",
    "checking":"🔎 Checking the verified policy documents...",
    "preparing_voice":"🔊 Preparing voice in the selected language...",
    "user_query_label":"Your question", "ai_resp_label":"Verified answer", "source_label":"Verified source",
    "no_source":"No verified source found.",
    "view_excerpts":"📖 View the exact policy excerpts used for this answer",
    "knowledge_match":"Knowledge match", "response_time":"Response time", "answer_language":"Answer language",
    "voice_unavailable":"🔊 Text answer is ready, but generated voice is unavailable. Use the Listen button below.",
    "listen":"🔊 Listen to answer",
    "helpline_header":"🚨 Official Helpline & Grievance",
    "helpline_info":"Kisan Call Center: 1800-180-1551 • PMFBY: 1800-200-5142 • PACS State Helpline: 1800-233-4567",
    "grievance_title":"Register a grievance ticket", "mobile":"Mobile number", "mobile_placeholder":"Enter 10-digit mobile number",
    "complaint":"Complaint / issue", "complaint_placeholder":"Describe the issue clearly",
    "submit_grievance":"Submit grievance ticket", "ticket_success":"Ticket registered successfully",
    "provide_both":"Please provide both mobile number and complaint.",
    "footer":"Ministry of Cooperation • Primary Agricultural Credit Societies (PACS) Network",
    "terminal":"Terminal", "location":"Location", "connection":"Connection", "online":"Online", "limited":"Limited",
    "new_session":"🔄 New session", "change_language":"Change language",
    "header_kiosk":"🌾 Sahakar-Vaani • Farmer Assistance Kiosk",
    "could_not_understand":"Could not understand the recording.",
}

@st.cache_data(ttl=86400, show_spinner=False)
def translate_ui(language_name):
    if language_name == "English":
        return dict(UI_BASE)
    try:
        from rag_engine import get_groq_client
        client = get_groq_client()
        if not client:
            return {**UI_BASE, **get_ui_translation(language_name)}
        import json
        payload = json.dumps(UI_BASE, ensure_ascii=False)
        result = client.chat.completions.create(
            model=os.getenv("GROQ_CHAT_MODEL", "openai/gpt-oss-120b"),
            messages=[
                {"role":"system","content":f"Translate UI strings into {language_name}. Keep JSON keys unchanged. Keep product names, scheme names, phone numbers, emojis and numbers unchanged. Translate every value naturally for farmers. Return ONLY valid JSON."},
                {"role":"user","content":payload},
            ],
            temperature=0, max_tokens=5000,
        )
        raw=result.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw=raw.strip("`")
            if raw.startswith("json"):
                raw=raw[4:]
        data=json.loads(raw)
        if isinstance(data,dict):
            return {**UI_BASE, **{k:str(v) for k,v in data.items() if k in UI_BASE}}
    except Exception as exc:
        print(f"UI translation warning for {language_name}: {exc}")
    return {**UI_BASE, **get_ui_translation(language_name)}


# -----------------------------------------------------------------------------
# Session state
# IMPORTANT: initialize all session-state values BEFORE any code reads them.
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
    "language_version": 0,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

scale_css = {"Standard": "1", "Large": "1.10", "Extra Large": "1.22"}[st.session_state.text_scale]
st.markdown(
    f"<style>.query-box,.answer-box,.source-box,.info-box,.warning-box,.scheme-card,.section-title,.hero-title,.hero-subtitle {{ zoom:{scale_css}; }}</style>",
    unsafe_allow_html=True,
)

all_langs = list(LANG_MAPPING.keys())
if st.session_state.selected_language not in all_langs:
    st.session_state.selected_language = None

# -----------------------------------------------------------------------------
# Hamburger feature menu — replaces the old top rectangular area.
# -----------------------------------------------------------------------------
menu_col, title_col = st.columns([0.8, 8.2], gap="small")
with menu_col:
    with st.popover("☰", use_container_width=True):
        menu_ui = translate_ui(st.session_state.selected_language or "English")
        st.markdown(f"### {html.escape(menu_ui['menu_title'])}")
        st.caption(menu_ui["menu_caption"])

        current_index = (
            all_langs.index(st.session_state.selected_language)
            if st.session_state.selected_language in all_langs
            else 0
        )
        menu_language = st.selectbox(
            menu_ui["language"],
            all_langs,
            index=current_index,
            key=f"menu_language_{st.session_state.language_version}",
        )
        if st.button(menu_ui["apply_language"], use_container_width=True):
            # Store exactly what the user selected. No preview-language state is used.
            st.session_state.selected_language = menu_language
            st.session_state.last_audio_hash = None
            st.session_state.language_version += 1
            st.rerun()

        st.markdown("---")
        st.markdown(f"**{menu_ui['features']}**")
        st.markdown(menu_ui["feature_questions"])
        st.markdown(menu_ui["feature_sources"])
        st.markdown(menu_ui["feature_grievance"])
        st.markdown(menu_ui["feature_helplines"])

        st.markdown("---")
        st.markdown(f"**{menu_ui['display_voice']}**")
        scale_labels=[menu_ui["standard"],menu_ui["large"],menu_ui["extra_large"]]
        canonical=["Standard","Large","Extra Large"]
        st.session_state.text_scale = canonical[scale_labels.index(st.selectbox(menu_ui["text_size"], scale_labels, index=canonical.index(st.session_state.text_scale), key="menu_text_scale"))]
        speed_label = st.radio(menu_ui["voice_speed"], [menu_ui["normal"], menu_ui["slow"]], index=1 if st.session_state.tts_slow else 0, key="menu_voice_speed")
        st.session_state.tts_slow = speed_label == menu_ui["slow"]

        st.markdown("---")
        st.markdown(f"**{menu_ui['kiosk']}**")
        st.caption(f"{menu_ui['terminal']}: {KIOSK_ID}")
        st.caption(f"{menu_ui['location']}: {KIOSK_DISTRICT}, {KIOSK_STATE}")
        st.caption(f"{menu_ui['connection']}: {menu_ui['online'] if is_internet_available() else menu_ui['limited']}")

        if st.button(menu_ui["new_session"], use_container_width=True):
            lang = st.session_state.selected_language
            st.session_state.clear()
            for k, v in defaults.items():
                st.session_state[k] = v
            st.session_state.selected_language = lang
            st.rerun()

with title_col:
    header_ui = translate_ui(st.session_state.selected_language or "English")
    st.markdown(f'<div class="menu-caption">{html.escape(header_ui["header_kiosk"])}</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Header card
# -----------------------------------------------------------------------------
with st.container(border=True):
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:20px;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg" style="width:72px;height:72px;object-fit:contain;">
            <div>
                <span class="gov-tag">{html.escape(translate_ui(st.session_state.selected_language or "English")["tag"])}</span>
                <div class="hero-title">🏛️ {html.escape(translate_ui(st.session_state.selected_language or "English")["title"])}</div>
                <div class="hero-subtitle">{html.escape(translate_ui(st.session_state.selected_language or "English")["subtitle"])}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# Language gate
# -----------------------------------------------------------------------------
if st.session_state.selected_language is None:
    gate_ui = translate_ui("English")
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
            key=f"gate_language_{st.session_state.language_version}",
        )
        if st.button(gate_ui["gate_btn"], type="primary", use_container_width=True):
            # Exact widget value -> exact application language.
            st.session_state.selected_language = chosen
            st.session_state.last_audio_hash = None
            st.session_state.language_version += 1
            st.rerun()
    st.stop()

active_lang = st.session_state.selected_language
T = translate_ui(active_lang)

# -----------------------------------------------------------------------------
# Active language and status
# -----------------------------------------------------------------------------
with st.container(border=True):
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown(f'<div class="info-box">🌐 {html.escape(T["active_lang"])} <b>{html.escape(active_lang)}</b></div>', unsafe_allow_html=True)
    with c2:
        if st.button(T["change_language"], use_container_width=True):
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
    st.markdown(f'<div class="info-box">{html.escape(T["query_info"])}</div>', unsafe_allow_html=True)

    audio_input = st.audio_input(T["record_question"], key=f"farmer_audio_input_{st.session_state.language_version}")

    typed_query = st.text_input(
        T["type_question"],
        placeholder=T["placeholder"],
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

    ask_typed = st.button(T["ask_question"], type="primary", use_container_width=True)

    final_query = None

    # Audio is processed exactly once per recording.
    if audio_input is not None:
        audio_bytes = audio_input.getvalue()
        audio_hash = hashlib.sha256(audio_bytes).hexdigest()
        if audio_hash != st.session_state.last_audio_hash:
            st.session_state.last_audio_hash = audio_hash
            with st.spinner(T["converting"]):
                transcript = transcribe_audio(audio_bytes, language_name=active_lang)
            if transcript and not transcript.startswith(("Transcription Error", "Invalid")):
                final_query = transcript.strip()
            else:
                st.error(transcript or T["could_not_understand"])

    if final_query is None and preset_query:
        final_query = preset_query
    if final_query is None and ask_typed and typed_query.strip():
        final_query = typed_query.strip()

    if final_query:
        st.session_state.last_query = final_query
        with st.spinner(T["checking"]):
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
            with st.expander(T["view_excerpts"]):
                for i, doc in enumerate(raw_context, 1):
                    src = html.escape(str(doc.get("source", "Unknown")))
                    page = doc.get("page")
                    page_text = f" • page {page}" if page else ""
                    st.markdown(f"**Source {i}: {src}{page_text}**")
                    st.write(doc.get("text", ""))

        with st.container(border=True):
            m1, m2, m3 = st.columns(3)
            m1.metric(T["knowledge_match"], f"{confidence_score}%")
            m2.metric(T["response_time"], f"{latency_ms} ms")
            m3.metric(T["answer_language"], active_lang)

        with st.spinner(T["preparing_voice"]):
            audio_path = generate_ai4bharat_voice(
                response_text,
                active_lang,
                slow=st.session_state.tts_slow,
            )
        if audio_path and os.path.exists(audio_path):
            st.audio(audio_path, format="audio/wav" if audio_path.endswith(".wav") else "audio/mp3", autoplay=True)
        else:
            st.markdown(f'<div class="warning-box">{html.escape(T["voice_unavailable"])}</div>', unsafe_allow_html=True)
            # Browser speech fallback: no second API key is required. The browser uses its installed voice for the selected language.
            browser_codes = {
                "English":"en-IN", "Hindi (हिंदी)":"hi-IN", "Marathi (मराठी)":"mr-IN", "Gujarati (ગુજરાતી)":"gu-IN",
                "Bengali (বাংলা)":"bn-IN", "Assamese (অসমীয়া)":"as-IN", "Odia (ଓଡ଼ିଆ)":"or-IN", "Punjabi (ਪੰਜਾਬੀ)":"pa-IN",
                "Tamil (தமிழ்)":"ta-IN", "Telugu (తెలుగు)":"te-IN", "Kannada (ಕನ್ನಡ)":"kn-IN", "Malayalam (മലയാളം)":"ml-IN",
                "Nepali (नेपाली)":"ne-NP", "Urdu (اردو)":"ur-IN", "Santali (ᱥᱟᱱᱛᱟᱲᱤ)":"sat-IN", "Sanskrit (संस्कृतम्)":"sa-IN",
            }
            voice_text = html.escape(response_text).replace("'", "\'").replace("\n", " ")
            voice_lang = browser_codes.get(active_lang, "hi-IN")
            components.html(f"""<button onclick=\"speak()\" style=\"width:100%;padding:12px;border-radius:10px;border:1px solid #C77F32;background:#D99A5B;color:white;font-weight:800;cursor:pointer\">{html.escape(T['listen'])}</button><script>function speak(){{const u=new SpeechSynthesisUtterance('{voice_text}');u.lang='{voice_lang}';u.rate={0.85 if st.session_state.tts_slow else 1.0};speechSynthesis.cancel();speechSynthesis.speak(u);}}setTimeout(speak,250);</script>""", height=60)

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
    st.markdown(f'<div class="section-title">{html.escape(T["helpline_header"])}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-box">{html.escape(T["helpline_info"])}</div>', unsafe_allow_html=True)

    with st.expander(T["grievance_title"]):
        phone = st.text_input(T["mobile"], placeholder=T["mobile_placeholder"], key="grievance_phone_v2")
        complaint = st.text_area(T["complaint"], placeholder=T["complaint_placeholder"], key="grievance_text_v2")
        if st.button(T["submit_grievance"], type="primary", use_container_width=True):
            if phone.strip() and complaint.strip():
                ticket_id = create_grievance(KIOSK_ID, phone.strip(), complaint.strip())
                st.success(f"{T['ticket_success']}: {ticket_id}")
            else:
                st.warning(T["provide_both"])

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown(f"""
<div class="footer">
    {html.escape(T["footer"])}<br>
    Sahakar-Vaani • Multilingual farmer assistance kiosk
</div>
""", unsafe_allow_html=True)
