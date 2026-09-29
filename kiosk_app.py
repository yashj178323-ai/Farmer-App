import hashlib
import html
import json
import time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from db_manager import create_grievance, init_db, log_query, ping_kiosk
from locales import get_all_languages, get_ui_translation
from rag_engine import (
    FAQS,
    LANG_MAPPING,
    answer_farmer_query,
    generate_ai4bharat_voice,
    get_browser_language_code,
    get_localized_faqs,
    is_internet_available,
    transcribe_audio,
)

# ---------------------------------------------------------------------------
# Kiosk configuration
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

KIOSK_ID = "PACS-MH-012"
KIOSK_STATE = "Maharashtra"
KIOSK_DISTRICT = "Pune District"

ALL_LANGUAGES = get_all_languages()

st.set_page_config(
    page_title="Sahakar-Vaani | Farmer Kiosk",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Database heartbeat
# ---------------------------------------------------------------------------
try:
    init_db()
    ping_kiosk(
        KIOSK_ID,
        state=KIOSK_STATE,
        district=KIOSK_DISTRICT,
    )
except Exception as exc:
    print(f"Kiosk database warning: {exc}")

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
DEFAULTS = {
    "selected_language": None,
    "last_audio_hash": None,
    "last_query": "",
    "last_response": "",
    "last_source": "",
    "last_context": "",
    "last_confidence": 0.0,
    "last_latency": 0.0,
    "last_audio_path": "",
    "text_scale": "Standard",
    "tts_slow": False,
    "typed_question": "",
    "auto_play_answer": False,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------------------------------------------------------------------
# Visual system
# ---------------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+Devanagari:wght@400;500;600;700;800&display=swap');

:root {
    --navy: #17324D;
    --navy-dark: #10263A;
    --muted: #536273;
    --saffron: #D68B3A;
    --saffron-dark: #B86F25;
    --green: #258653;
    --green-dark: #1C7044;
    --line: #D9E2EA;
    --card: rgba(255,255,255,.96);
    --soft: #F5F8FA;
}

html, body, [class*="css"] {
    font-family: "Inter", "Noto Sans Devanagari", sans-serif;
}

.stApp {
    min-height: 100vh;
    background:
        linear-gradient(rgba(20,42,58,.42), rgba(20,42,58,.42)),
        url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1920&auto=format&fit=crop");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

[data-testid="stHeader"],
[data-testid="stToolbar"],
.stAppDeployButton {
    display: none !important;
}

/* IMPORTANT: the main page itself stays transparent so the farm scene is
   visible between the individual white text/card surfaces. */
.block-container {
    max-width: 1180px !important;
    padding: 18px 22px 36px 22px !important;
    margin: 12px auto 24px auto !important;
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--card) !important;
    border: 1px solid rgba(217,226,234,.95) !important;
    border-radius: 16px !important;
    box-shadow: 0 8px 24px rgba(0,0,0,.16) !important;
    padding: 5px 8px 9px 8px !important;
    margin-bottom: 14px !important;
}

div[data-testid="stMarkdownContainer"],
div[data-testid="stMarkdownContainer"] p,
div[data-testid="stMarkdownContainer"] li {
    color: #1F2D3D !important;
}

label,
[data-testid="stWidgetLabel"] p {
    color: #26384A !important;
    font-weight: 700 !important;
}

div[data-baseweb="select"] > div,
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: #FFFFFF !important;
    color: #17283A !important;
    border: 1px solid #C9D5E0 !important;
    border-radius: 10px !important;
}

[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder {
    color: #687787 !important;
    opacity: 1 !important;
}

button[kind="primary"] {
    background: var(--saffron) !important;
    border-color: var(--saffron) !important;
    color: #FFFFFF !important;
    font-weight: 800 !important;
    border-radius: 10px !important;
}

button[kind="primary"]:hover {
    background: var(--saffron-dark) !important;
    border-color: var(--saffron-dark) !important;
}

.stButton > button {
    border-radius: 10px !important;
    font-weight: 700 !important;
    min-height: 42px !important;
    height: auto !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    line-height: 1.35 !important;
    padding: 9px 11px !important;
}

.menu-caption {
    color: #FFFFFF;
    font-size: 14px;
    font-weight: 800;
    margin: 3px 0 10px 4px;
    text-shadow: 0 1px 4px rgba(0,0,0,.72);
}

.hero-card {
    background: rgba(255,255,255,.97);
    border: 1px solid #D7E0E8;
    border-radius: 16px;
    padding: 14px 18px 12px 18px;
}

.hero-title {
    color: var(--navy);
    font-size: 30px;
    font-weight: 800;
    line-height: 1.16;
}

.hero-subtitle {
    color: var(--muted);
    font-size: 13px;
    font-weight: 600;
    margin-top: 5px;
}

.gov-tag {
    display: inline-block;
    background: #FFF0DF;
    color: #9A5B1E;
    border: 1px solid #EFC894;
    border-radius: 999px;
    padding: 5px 10px;
    font-size: 11px;
    font-weight: 800;
    margin-bottom: 6px;
}

.tricolor-bar {
    width: 100%;
    height: 5px;
    margin-top: 10px;
    border-radius: 999px;
    background: linear-gradient(
        90deg,
        #FF9933 0%,
        #FF9933 33.33%,
        #FFFFFF 33.33%,
        #FFFFFF 66.66%,
        #138808 66.66%,
        #138808 100%
    );
    border: 1px solid rgba(23,50,77,.12);
}

.section-title {
    display: block;
    width: fit-content;
    max-width: 100%;
    background: rgba(255,255,255,.97);
    color: var(--navy);
    font-size: 17px;
    font-weight: 800;
    line-height: 1.35;
    margin: 3px 0 10px 0;
    padding: 7px 11px;
    border: 1px solid #DCE5EC;
    border-radius: 10px;
    box-shadow: 0 3px 10px rgba(0,0,0,.08);
}

.section-help {
    display: block;
    background: rgba(255,255,255,.96);
    color: #536273;
    border: 1px solid #DCE5EC;
    border-radius: 10px;
    padding: 8px 11px;
    margin: -2px 0 10px 0;
    font-size: 12px;
    font-weight: 600;
    line-height: 1.5;
}

.text-surface {
    background: #FFFFFF;
    border: 1px solid #DCE5EC;
    border-radius: 11px;
    padding: 11px 13px;
    color: #26384A;
    line-height: 1.55;
}

.info-box {
    background: #FFFFFF;
    border: 1px solid #DCE5EC;
    border-radius: 10px;
    padding: 11px 13px;
    color: #35485A;
    font-size: 13px;
    line-height: 1.55;
}

.scheme-card {
    min-height: 96px;
    background: #FFFFFF;
    border: 1px solid #DCE5EC;
    border-top: 4px solid var(--saffron);
    border-radius: 12px;
    padding: 12px;
}

.scheme-title {
    color: var(--navy);
    font-size: 14px;
    font-weight: 800;
}

.scheme-subtitle {
    color: var(--muted);
    font-size: 11px;
    line-height: 1.35;
    margin-top: 6px;
}

.voice-card {
    background: #FFFFFF;
    border: 1px solid #D8E5DD;
    border-radius: 14px;
    padding: 18px 14px;
    text-align: center;
    min-height: 115px;
}

.voice-icon {
    font-size: 34px;
    margin-bottom: 2px;
}

.voice-title {
    color: var(--navy);
    font-size: 16px;
    font-weight: 800;
}

.voice-subtitle {
    color: var(--muted);
    font-size: 11px;
    margin-top: 4px;
}

.question-card {
    background: #FFFFFF;
    border: 1px solid #DDE5EC;
    border-left: 5px solid var(--navy);
    border-radius: 12px;
    padding: 14px 16px;
    color: #1F2D3D;
    line-height: 1.65;
}

.answer-card {
    background: #FFFFFF;
    border: 1px solid #D5E7DA;
    border-left: 5px solid var(--green);
    border-radius: 12px;
    padding: 16px;
    color: #1D3C2B;
    line-height: 1.7;
}

.source-card {
    background: #FFFFFF;
    border: 1px solid #DDE5EC;
    border-radius: 10px;
    padding: 11px 13px;
    color: #536273;
    font-size: 12px;
}

.metric-card {
    background: #FFFFFF;
    border: 1px solid #DDE5EC;
    border-radius: 10px;
    padding: 9px 11px;
    text-align: center;
}

.metric-value {
    color: var(--navy);
    font-size: 16px;
    font-weight: 800;
}

.metric-label {
    color: var(--muted);
    font-size: 10px;
    margin-top: 3px;
}

.faq-card {
    background: #FFFFFF;
    border: 1px solid #DCE5EC;
    border-left: 4px solid var(--saffron);
    border-radius: 10px;
    padding: 9px 11px;
    color: #26384A;
    min-height: 56px;
    font-size: 12px;
    line-height: 1.4;
}

.footer {
    color: rgba(255,255,255,.94);
    text-align: center;
    font-size: 11px;
    font-weight: 700;
    margin-top: 8px;
    text-shadow: 0 1px 4px rgba(0,0,0,.75);
}

[data-testid="stAudioInput"] {
    width: 100%;
}

.audio-help {
    display: block;
    background: rgba(255,255,255,.96);
    color: #536273;
    border: 1px solid #DCE5EC;
    border-radius: 10px;
    padding: 8px 11px;
    margin: 5px 0 10px 0;
    font-size: 12px;
    font-weight: 600;
    line-height: 1.5;
}

.quick-label {
    display: inline-block;
    background: rgba(255,255,255,.97);
    color: var(--navy);
    border: 1px solid #DCE5EC;
    border-radius: 9px;
    padding: 6px 10px;
    margin: 8px 0 7px 0;
    font-size: 13px;
    font-weight: 800;
}

@media (max-width: 800px) {
    .block-container {
        padding: 10px 9px 26px 9px !important;
    }

    .hero-title {
        font-size: 23px;
    }

    .hero-card img {
        width: 54px !important;
        height: 54px !important;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def esc(value):
    return html.escape(str(value or ""))


def reset_answer_state():
    st.session_state.last_query = ""
    st.session_state.last_response = ""
    st.session_state.last_source = ""
    st.session_state.last_context = ""
    st.session_state.last_confidence = 0.0
    st.session_state.last_latency = 0.0
    st.session_state.last_audio_path = ""
    st.session_state.auto_play_answer = False


def run_question(
    query,
    language_name,
    play_voice=True,
    server_tts=True,
    display_query=None,
    fast_mode=False,
):
    query = str(query or "").strip()

    if not query:
        st.warning("Please speak or type a question first.")
        return

    with st.spinner(get_ui_translation(language_name)["checking_msg"]):
        answer, source, context, confidence, latency = answer_farmer_query(
            query,
            language_name,
            fast_mode=fast_mode,
        )

    # The backend query remains canonical/stable, while the farmer-facing
    # question can be shown in the selected language (especially for FAQs).
    st.session_state.last_query = str(display_query or query)
    st.session_state.last_response = str(answer)
    st.session_state.last_source = str(source)
    st.session_state.last_context = context
    st.session_state.last_confidence = float(confidence or 0)
    st.session_state.last_latency = float(latency or 0)
    st.session_state.last_audio_path = ""
    st.session_state.auto_play_answer = False

    if (
        play_voice
        and server_tts
        and answer
        and not str(answer).startswith(
            ("Groq", "AI answer generation failed:", "API Key Error")
        )
    ):
        # Server audio is useful for normal typed/voice questions, but FAQ
        # buttons use the browser voice path so the answer appears without
        # waiting for a second network TTS request.
        with st.spinner(get_ui_translation(language_name)["tts_msg"]):
            audio_path = generate_ai4bharat_voice(
                answer,
                language_name,
                slow=st.session_state.tts_slow,
            )

        if audio_path:
            st.session_state.last_audio_path = audio_path

        if not audio_path:
            st.session_state.auto_play_answer = True
    elif play_voice:
        st.session_state.auto_play_answer = True

    try:
        log_query(
            KIOSK_ID,
            query,
            str(answer),
            language_name,
            float(confidence or 0),
            int(latency or 0),
        )
    except Exception:
        pass


def browser_speech(text, language_name, autoplay=False):
    """Render a reliable browser speech control in the selected language."""
    locale = get_browser_language_code(language_name)

    script_text = json.dumps(str(text), ensure_ascii=False)
    locale_text = json.dumps(locale)
    speed = 0.82 if st.session_state.tts_slow else 0.95
    auto_script = "setTimeout(speakNow, 250);" if autoplay else ""

    components.html(
        f"""
        <div style="
            font-family:Inter,Arial,sans-serif;
            background:#fff;
            border:1px solid #DDE5EC;
            border-radius:10px;
            padding:9px 10px;
        ">
            <button id="playVoice" style="
                border:1px solid #D68B3A;
                background:#FFF7EC;
                color:#7E4B18;
                border-radius:8px;
                padding:9px 13px;
                font-weight:800;
                cursor:pointer;
            ">🔊 Play answer</button>
            <button id="stopVoice" style="
                border:1px solid #C9D5E0;
                background:#F7F9FB;
                color:#31465A;
                border-radius:8px;
                padding:9px 13px;
                font-weight:700;
                cursor:pointer;
                margin-left:6px;
            ">■ Stop</button>
            <span id="voiceStatus" style="
                margin-left:8px;
                color:#536273;
                font-size:12px;
            "></span>
        </div>

        <script>
        const answerText = {script_text};
        const targetLocale = {locale_text};
        const targetRate = {speed};
        const status = document.getElementById("voiceStatus");

        function chooseVoice() {{
            const voices = window.speechSynthesis.getVoices() || [];
            if (!voices.length) return null;

            const wanted = targetLocale.toLowerCase();
            const base = wanted.split("-")[0];

            return voices.find(v => (v.lang || "").toLowerCase() === wanted)
                || voices.find(v => (v.lang || "").toLowerCase().startsWith(base + "-"))
                || voices.find(v => (v.lang || "").toLowerCase() === base)
                || null;
        }}

        function speakNow() {{
            if (!("speechSynthesis" in window)) {{
                status.textContent = "Browser voice is not available on this device.";
                return;
            }}

            window.speechSynthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(answerText);
            const voice = chooseVoice();

            // Never let an English/default browser voice read an Indic answer.
            // That can result in only Latin tokens such as KCC/PACS/e-NAM being
            // audible while the native-script sentence is skipped or mangled.
            if (!voice && !targetLocale.toLowerCase().startsWith("en")) {{
                status.textContent =
                    "A matching voice is not installed in this browser. Use the audio player above.";
                return;
            }}

            utterance.lang = targetLocale;
            if (voice) utterance.voice = voice;
            utterance.rate = targetRate;
            utterance.pitch = 1.0;

            utterance.onstart = function() {{
                status.textContent = "Playing in the selected language…";
            }};

            utterance.onend = function() {{
                status.textContent = "Finished";
            }};

            utterance.onerror = function(event) {{
                status.textContent = "Browser voice could not play (" +
                    (event.error || "unknown error") + ").";
            }};

            window.speechSynthesis.speak(utterance);
        }}

        document.getElementById("playVoice").onclick = speakNow;
        document.getElementById("stopVoice").onclick = function() {{
            if ("speechSynthesis" in window) window.speechSynthesis.cancel();
            status.textContent = "Stopped";
        }};

        if ("speechSynthesis" in window) {{
            window.speechSynthesis.onvoiceschanged = function() {{
                chooseVoice();
            }};
        }}

        {auto_script}
        </script>
        """,
        height=70,
        scrolling=False,
    )


# ---------------------------------------------------------------------------
# Top menu
# ---------------------------------------------------------------------------
selected_language = st.session_state.selected_language
# Before the farmer enters the terminal, use the language currently shown in
# the selector so the gate and header change immediately with the dropdown.
_preview_language = (
    selected_language
    or (st.session_state.get("gate_language") if st.session_state.get("gate_language") in ALL_LANGUAGES else ALL_LANGUAGES[0])
)
T = get_ui_translation(_preview_language)

menu_col, caption_col = st.columns([0.8, 8.2], gap="small")

with menu_col:
    with st.popover("☰", use_container_width=True):
        menu_T = get_ui_translation(selected_language or "English")

        st.markdown(f"### {esc(menu_T['menu_title'])}")
        st.caption(menu_T["menu_caption"])

        current_index = (
            ALL_LANGUAGES.index(selected_language)
            if selected_language in ALL_LANGUAGES
            else 0
        )

        menu_language = st.selectbox(
            menu_T["menu_language"],
            ALL_LANGUAGES,
            index=current_index,
            key="menu_language",
        )

        if st.button(
            menu_T["apply_language"],
            use_container_width=True,
        ):
            st.session_state.selected_language = menu_language
            reset_answer_state()
            st.session_state.last_audio_hash = None
            st.rerun()

        st.markdown("---")
        st.markdown(f"**{menu_T['features']}**")
        st.markdown(menu_T["feature_voice"])
        st.markdown(menu_T["feature_sources"])
        st.markdown(menu_T["feature_grievance"])
        st.markdown(menu_T["feature_helpline"])

        st.markdown("---")
        st.markdown(f"**{menu_T['display_voice']}**")

        st.session_state.text_scale = st.selectbox(
            menu_T["text_size"],
            ["Standard", "Large", "Extra Large"],
            index=[
                "Standard",
                "Large",
                "Extra Large",
            ].index(st.session_state.text_scale),
            key="menu_text_scale",
        )

        speed = st.radio(
            menu_T["voice_speed"],
            [menu_T["normal"], menu_T["slow"]],
            index=1 if st.session_state.tts_slow else 0,
            key="menu_voice_speed",
        )
        st.session_state.tts_slow = speed == menu_T["slow"]

        st.markdown("---")
        st.markdown(f"**{menu_T['kiosk']}**")
        st.caption(f"{menu_T['terminal']}: {KIOSK_ID}")
        st.caption(
            f"{menu_T['location']}: "
            f"{KIOSK_DISTRICT}, {KIOSK_STATE}"
        )

        # Do not perform a live connectivity request while the menu is
        # rendering. That request can make every menu interaction feel slow.
        # The actual Groq/TTS calls already report their own errors when needed.
        st.caption(
            f"{menu_T['connection']}: "
            f"{menu_T['online']}"
        )

        if st.button(
            menu_T["new_session"],
            use_container_width=True,
        ):
            selected = st.session_state.selected_language
            st.session_state.clear()

            for key, value in DEFAULTS.items():
                st.session_state[key] = value

            st.session_state.selected_language = selected
            st.rerun()

with caption_col:
    st.markdown(
        '<div class="menu-caption">🌾 Sahakar-Vaani • Farmer Assistance Kiosk</div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Header - white only behind the heading text, with tricolor border
# ---------------------------------------------------------------------------
with st.container(border=True):
    header_language = st.session_state.selected_language or _preview_language
    header_T = get_ui_translation(header_language)

    st.markdown(
        f"""
        <div class="hero-card">
            <div style="display:flex;align-items:center;gap:16px;">
                <img
                    src="https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg"
                    style="width:66px;height:66px;object-fit:contain;"
                >
                <div style="flex:1;">
                    <span class="gov-tag">{esc(header_T["tag"])}</span>
                    <div class="hero-title">
                        {esc(header_T["title"])}
                    </div>
                    <div class="hero-subtitle">
                        {esc(header_T["subtitle"])}
                    </div>
                    <div class="tricolor-bar"></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Page 1: Language selection
# ---------------------------------------------------------------------------
if st.session_state.selected_language is None:
    # The language selector itself is the source of truth on this screen.
    # Streamlit reruns when the selection changes, so all visible text below
    # immediately switches to the newly selected language.
    preview_language = (
        st.session_state.get("gate_language")
        if st.session_state.get("gate_language") in ALL_LANGUAGES
        else ALL_LANGUAGES[0]
    )
    gate_T = get_ui_translation(preview_language)

    with st.container(border=True):
        st.markdown(
            f'<div class="section-title">{esc(gate_T["gate_title"])}</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="info-box">{esc(gate_T["gate_help"])}</div>',
            unsafe_allow_html=True,
        )

        chosen = st.selectbox(
            gate_T["gate_label"],
            ALL_LANGUAGES,
            index=ALL_LANGUAGES.index(preview_language),
            key="gate_language",
        )

        if st.button(
            gate_T["gate_btn"],
            type="primary",
            use_container_width=True,
        ):
            st.session_state.selected_language = chosen
            reset_answer_state()
            st.session_state.last_audio_hash = None
            st.rerun()

    st.markdown(
        '<div class="footer">Sahakar-Vaani • Farmer Assistance Kiosk</div>',
        unsafe_allow_html=True,
    )

    st.stop()

# ---------------------------------------------------------------------------
# Page 2: Dynamic dashboard
# ---------------------------------------------------------------------------
active_language = st.session_state.selected_language
T = get_ui_translation(active_language)

with st.container(border=True):
    active_col, change_col = st.columns([3.4, 1.8])

    with active_col:
        st.markdown(
            f"""
            <div class="info-box">
                {esc(T["active_lang"])}
                <b>{esc(active_language)}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with change_col:
        dashboard_language = st.selectbox(
            T["change_lang"],
            ALL_LANGUAGES,
            index=ALL_LANGUAGES.index(active_language),
            key=f"dashboard_language_{active_language}",
            label_visibility="visible",
        )

        if dashboard_language != active_language:
            st.session_state.selected_language = dashboard_language
            st.session_state.last_audio_hash = None
            reset_answer_state()
            st.rerun()

# ---------------------------------------------------------------------------
# Scheme cards
# ---------------------------------------------------------------------------
with st.container(border=True):
    st.markdown(
        f'<div class="section-title">{esc(T["schemes_header"])}</div>',
        unsafe_allow_html=True,
    )

    scheme_columns = st.columns(5)

    schemes = [
        ("🌾", T["pmfby"], T["pmfby_sub"]),
        ("💳", T["kcc"], T["kcc_sub"]),
        ("🏢", T["pacs"], T["pacs_sub"]),
        ("🧪", T["soil"], T["soil_sub"]),
        ("🛒", T["enam"], T["enam_sub"]),
    ]

    for column, (icon, title, subtitle) in zip(
        scheme_columns,
        schemes,
    ):
        with column:
            st.markdown(
                f"""
                <div class="scheme-card">
                    <div class="scheme-title">
                        {icon} {esc(title)}
                    </div>
                    <div class="scheme-subtitle">
                        {esc(subtitle)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ---------------------------------------------------------------------------
# Voice / text terminal
# ---------------------------------------------------------------------------
with st.container(border=True):
    st.markdown(
        f'<div class="section-title">{esc(T["audio_console_header"])}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="audio-help">{esc(T["audio_help"])}</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown(
            f"""
            <div class="voice-card">
                <div class="voice-icon">🎙️</div>
                <div class="voice-title">
                    {esc(T["mic_prompt"])}
                </div>
                <div class="voice-subtitle">
                    {esc(T["audio_help"])}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        audio_value = st.audio_input(
            T["mic_prompt"],
            key="farmer_audio",
        )

    with right:
        st.markdown(
            f'<div class="section-title" style="font-size:14px;">📝 {esc(T["typed_label"])}</div>',
            unsafe_allow_html=True,
        )

        typed_question = st.text_input(
            "Question",
            value=st.session_state.typed_question,
            placeholder=T["typed_placeholder"],
            label_visibility="collapsed",
            key="typed_question",
        )

        st.markdown(
            f'<div class="quick-label">⚡ {esc(T["quick_header"])}</div>',
            unsafe_allow_html=True,
        )

        # Translate FAQ labels at page load/cache time. The query used by the
        # RAG engine remains canonical English for stable retrieval.
        localized_faqs = get_localized_faqs(active_language)

        # Two columns give each farmer question enough horizontal space to
        # remain readable instead of truncating it to a few words.
        faq_rows = [
            localized_faqs[0:2],
            localized_faqs[2:4],
            localized_faqs[4:6],
            localized_faqs[6:8],
            localized_faqs[8:10],
            localized_faqs[10:12],
        ]

        faq_clicked = None
        faq_clicked_label = None

        with st.container(border=True):
            for row in faq_rows:
                cols = st.columns(2, gap="medium")
                for col, faq in zip(cols, row):
                    with col:
                        full_label = f"{faq['emoji']}  {faq['question']}"

                        if st.button(
                            full_label,
                            key=f"faq_{faq['id']}",
                            use_container_width=True,
                        ):
                            faq_clicked = faq["id"]
                            faq_clicked_label = faq["question"]

    # The recording is processed automatically as soon as the user stops
    # recording. No second Ask click is required for voice input.
    if audio_value is not None:
        try:
            audio_bytes = audio_value.getvalue()
        except Exception:
            audio_bytes = bytes(audio_value)

        if audio_bytes:
            audio_hash = hashlib.sha256(audio_bytes).hexdigest()

            if audio_hash != st.session_state.last_audio_hash:
                st.session_state.last_audio_hash = audio_hash

                with st.spinner(T["listening_msg"]):
                    transcription = transcribe_audio(
                        audio_bytes,
                        active_language,
                    )

                if transcription and not str(transcription).startswith(
                    "Transcription Error:"
                ):
                    spoken_question = str(transcription).strip()
                    run_question(
                        spoken_question,
                        active_language,
                        play_voice=True,
                        fast_mode=True,
                    )
                else:
                    st.error(
                        transcription
                        or T["listening_msg"]
                    )

    # FAQ clicks are also processed immediately and produce the answer plus
    # generated voice where the configured TTS provider supports it.
    if faq_clicked:
        selected_faq = next(
            (
                item
                for item in FAQS
                if item["id"] == faq_clicked
            ),
            None,
        )

        if selected_faq:
            run_question(
                selected_faq["question"],
                active_language,
                play_voice=True,
                server_tts=True,
                display_query=faq_clicked_label or selected_faq["question"],
            )

    if st.button(
        T["ask_btn"],
        type="primary",
        use_container_width=True,
    ):
        question = (typed_question or "").strip()

        if not question:
            st.warning(T["typed_placeholder"])
        else:
            run_question(
                question,
                active_language,
                play_voice=True,
            )

# ---------------------------------------------------------------------------
# Answer section
# ---------------------------------------------------------------------------
if st.session_state.last_query:
    st.markdown(
        f'<div class="section-title">{esc(T["user_query_label"])}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="question-card">
            {esc(st.session_state.last_query)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="section-title" style="margin-top:15px;">{esc(T["ai_resp_label"])}</div>',
        unsafe_allow_html=True,
    )

    response_text = st.session_state.last_response or ""

    st.markdown(
        f"""
        <div class="answer-card">
            {esc(response_text).replace(chr(10), "<br>")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Server-generated audio, if available.
    audio_path = st.session_state.last_audio_path

    if audio_path and Path(audio_path).exists():
        suffix = Path(audio_path).suffix.lower()
        audio_format = {
            ".mp3": "audio/mp3",
            ".wav": "audio/wav",
        }.get(suffix, "audio/mp3")

        try:
            with open(audio_path, "rb") as audio_file:
                audio_bytes = audio_file.read()

            st.audio(
                audio_bytes,
                format=audio_format,
                autoplay=False,
            )

            st.caption(T["play_answer"])
        except Exception:
            pass

    # Always provide a browser-language voice button as a reliable second
    # playback path. This works even when the server TTS provider is slow,
    # unavailable, or does not support the selected language.
    browser_speech(
        response_text,
        active_language,
        autoplay=st.session_state.auto_play_answer,
    )

    metric1, metric2, metric3 = st.columns(3)

    with metric1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">
                    {st.session_state.last_confidence:.0f}%
                </div>
                <div class="metric-label">
                    {esc(T["knowledge_match"])}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with metric2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">
                    {st.session_state.last_latency:.0f} ms
                </div>
                <div class="metric-label">
                    {esc(T["response_time"])}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with metric3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">🌐</div>
                <div class="metric-label">
                    {esc(T["answer_language"])}:
                    {esc(active_language)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f'<div class="section-title" style="margin-top:16px;">{esc(T["source_label"])}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="source-card">
            <b>{esc(st.session_state.last_source)}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.last_context:
        with st.expander(T["view_sources"]):
            for document in st.session_state.last_context:
                if isinstance(document, dict):
                    st.markdown(
                        f"**{esc(document.get('source', 'Source'))}**"
                    )
                    st.write(document.get("text", ""))
                else:
                    st.write(document)

# ---------------------------------------------------------------------------
# Grievance section
# ---------------------------------------------------------------------------
with st.container(border=True):
    st.markdown(
        f'<div class="section-title">{esc(T["helpline_header"])}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="info-box">
            Kisan Call Center: <b>1800-180-1551</b>
            &nbsp;•&nbsp;
            PMFBY: <b>1800-200-5142</b>
            &nbsp;•&nbsp;
            PACS State Helpline: <b>1800-233-4567</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander(T["grievance_expander"]):
        mobile = st.text_input(
            T["mobile_label"],
            placeholder=T["mobile_placeholder"],
            key="grievance_mobile",
        )

        complaint = st.text_area(
            T["complaint_label"],
            placeholder=T["complaint_placeholder"],
            key="grievance_complaint",
        )

        if st.button(
            T["submit_btn"],
            use_container_width=True,
        ):
            if not mobile.strip() or not complaint.strip():
                st.warning(T["ticket_missing"])
            else:
                try:
                    ticket = create_grievance(
                        KIOSK_ID,
                        mobile.strip(),
                        complaint.strip(),
                    )
                except Exception as exc:
                        ticket = None
                        st.error(str(exc))

                if ticket is not None:
                    st.success(
                        f"{T['ticket_success']} {ticket}"
                    )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="footer">
        {T["footer"]}<br>
        {esc(KIOSK_ID)}
    </div>
    """,
    unsafe_allow_html=True,
)
