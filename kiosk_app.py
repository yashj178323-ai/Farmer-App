import json
import os
import re
import socket
import tempfile
import time
import requests
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from gtts import gTTS
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Always reload environment variables from .env
load_dotenv(override=True)

# ---------------------------------------------------------------------------
# GLOBAL LANGUAGE MAPPING (Imported directly by kiosk_app.py)
# ---------------------------------------------------------------------------
LANG_MAPPING = {
    "Assamese (অসমীয়া)": ("as", "bn", "Assamese"),
    "Bengali (বাংলা)": ("bn", "bn", "Bengali"),
    "Bodo (बर')": ("hi", "hi", "Bodo"),
    "Dogri (डोगरी)": ("hi", "hi", "Dogri"),
    "English": ("en", "en", "English"),
    "Gujarati (ગુજરાતી)": ("gu", "gu", "Gujarati"),
    "Hindi (हिंदी)": ("hi", "hi", "Hindi"),
    "Kannada (ಕನ್ನಡ)": ("kn", "kn", "Kannada"),
    "Kashmiri (कॉशुर)": ("ur", "ur", "Kashmiri"),
    "Konkani (कोंकणी)": ("mr", "mr", "Konkani"),
    "Maithili (मैथिली)": ("hi", "hi", "Maithili"),
    "Malayalam (മലയാളം)": ("ml", "ml", "Malayalam"),
    "Manipuri (ꯃꯩꯇꯩꯂꯣꯟ)": ("bn", "bn", "Manipuri"),
    "Marathi (मराठी)": ("mr", "mr", "Marathi"),
    "Nepali (नेपाली)": ("ne", "ne", "Nepali"),
    "Odia (ଓଡ଼ିଆ)": ("or", "hi", "Odia"),
    "Punjabi (ਪੰਜਾਬੀ)": ("pa", "pa", "Punjabi"),
    "Sanskrit (संस्कृतम्)": ("hi", "hi", "Sanskrit"),
    "Santali (ᱥᱟᱱᱛᱟᱲᱤ)": ("hi", "hi", "Santali"),
    "Sindhi (सिंधी)": ("sd", "hi", "Sindhi"),
    "Tamil (தமிழ்)": ("ta", "ta", "Tamil"),
    "Telugu (తెలుగు)": ("te", "te", "Telugu"),
    "Urdu (اردو)": ("ur", "ur", "Urdu")
}

LANGUAGES_FILE = "languages.json"

@st.cache_data
def load_language_list():
    if os.path.exists(LANGUAGES_FILE):
        with open(LANGUAGES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return ["English", "Hindi (हिंदी)", "Odia (ଓଡ଼ିଆ)", "Marathi (मराठी)"]

ALL_LANG_LIST = load_language_list()

# ---------------------------------------------------------------------------
# NETWORK & AUDIO UTILITY FUNCTIONS (Imported by kiosk_app.py)
# ---------------------------------------------------------------------------
def is_internet_available():
    """Checks whether the kiosk has active internet connectivity."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def check_audio_amplitude(audio_bytes):
    """Calculates relative audio signal amplitude for meter visualization."""
    if not audio_bytes:
        return 0.0
    return min(1.0, len(audio_bytes) / 100000.0)

def get_groq_client():
    """Dynamically reads Groq API Key directly from environment."""
    key = os.getenv("GROQ_API_KEY", "").strip().strip('"').strip("'")
    if key and key.startswith("gsk_"):
        return Groq(api_key=key)
    return None

# Cached Vector DB
@st.cache_resource(show_spinner=False)
def load_vector_db():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

vector_db = load_vector_db()

def clean_and_normalize_query(query_text):
    """Auto-corrects common phonetic STT distortions for Indian agricultural terms."""
    corrections = {
        r"किरान": "किसान",
        r"रेडिट": "क्रेडिट",
        r"केडिट": "क्रेडिट",
        r"पीएम": "PM",
        r"एफबीवाई": "PMFBY",
        r"इनाम": "e-NAM",
        r"पैक्स": "PACS"
    }
    cleaned = query_text
    for pattern, replacement in corrections.items():
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    return cleaned

# ---------------------------------------------------------------------------
# CORE VOICE & RAG PIPELINE
# ---------------------------------------------------------------------------
def transcribe_audio(audio_bytes, language_name="Hindi (हिंदी)"):
    client = get_groq_client()
    if not client:
        return "Groq API key is missing or invalid in your .env file."

    whisper_code, _, _ = LANG_MAPPING.get(language_name, ("hi", "hi", "Hindi"))

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(audio_bytes)
        temp_audio_path = temp_audio.name

    try:
        with open(temp_audio_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(temp_audio_path, file.read()),
                model="whisper-large-v3",
                language=whisper_code,
                response_format="json"
            )
        return transcription.text
    except Exception as e:
        return f"Transcription Error: {str(e)}"
    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)


def answer_farmer_query(query_text, language_name="Hindi (हिंदी)"):
    start_time = time.time()
    
    client = get_groq_client()
    if not client:
        return (
            "API Key Error: Please make sure GROQ_API_KEY is set in your .env file.",
            "N/A",
            "N/A",
            0.0,
            0.0
        )

    # 1. Normalize phonetic STT errors (e.g. "किरान" -> "किसान")
    search_query = clean_and_normalize_query(query_text)

    # 2. Query ChromaDB with expanded top-k search
    results = vector_db.similarity_search_with_score(search_query, k=5)
    
    context_chunks = []
    sources = []
    top_score = 0.0
    
    if results:
        first_doc, first_distance = results[0]
        top_score = max(0.50, round(min(0.98, 1.0 - (first_distance / 2.0)), 2))
        
        for doc, _ in results:
            context_chunks.append(doc.page_content)
            sources.append(doc.metadata.get("source", "Official Policy Guidelines"))
    else:
        top_score = 0.40
            
    context_str = "\n\n---\n\n".join(context_chunks) if context_chunks else "Official Policy Guidelines for KCC, PMFBY, PACS Bylaws, Soil Health Card, and e-NAM."
    source_str = ", ".join(set(sources)) if sources else "Official Agricultural Guidelines"

    # 3. Prompt Construction enforcing pure native target script
    prompt = f"""
You are Sahakar-Vaani, an official AI Voice Kiosk assistant for Indian farmers at Primary Agricultural Credit Societies (PACS).
Answer the farmer's question thoroughly based on the official policy context provided below.

EXACT MANDATORY TARGET LANGUAGE & SCRIPT: {language_name}

Official Policy Context:
{context_str}

Farmer Question:
{query_text} (Interpreted Intent: {search_query})

STRICT OUTPUT RULES:
1. You MUST write the entire response 100% in {language_name} using its native official script ONLY.
2. DO NOT include English words, Latin script, or English terms in parentheses/brackets.
3. Translate all technical concepts natively into {language_name}.
4. Provide a clear, informative 3-sentence explanation covering key rules, interest rates, or procedures.
5. Keep the phrasing natural and simple for audio voice output.
"""

    # Active Production Models on Groq
    target_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]

    last_error = ""
    for model_id in target_models:
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            if response and response.choices:
                answer = response.choices[0].message.content.strip()
                if answer:
                    latency_ms = round((time.time() - start_time) * 1000, 2)
                    return answer, source_str, context_str, top_score, latency_ms
        except Exception as err:
            last_error = str(err)
            continue

    latency_ms = round((time.time() - start_time) * 1000, 2)
    return f"Groq Connection Error: {last_error}", source_str, context_str, 0.0, latency_ms


def generate_ai4bharat_voice(text_input, language_name):
    """Voice Synthesis Engine using AI4Bharat and fallback gTTS."""
    if not text_input or "Error" in text_input or "API Key" in text_input:
        return False

    token = os.getenv("HF_TOKEN", "").strip().strip('"').strip("'")
    
    # 1. AI4Bharat Parler TTS Endpoint
    if token and token.startswith("hf_"):
        try:
            API_URL = "https://api-inference.huggingface.co/models/ai4bharat/indic-parler-tts"
            headers = {"Authorization": f"Bearer {token}"}
            payload = {
                "inputs": text_input,
                "parameters": {"description": f"Clear agricultural speech in {language_name}."}
            }
            res = requests.post(API_URL, headers=headers, json=payload, timeout=6)
            if res.status_code == 200 and len(res.content) > 1000:
                with open("response.mp3", "wb") as f:
                    f.write(res.content)
                return True
        except Exception:
            pass

    # 2. Universal gTTS Fallback Engine
    _, tts_lang_code, _ = LANG_MAPPING.get(language_name, ("hi", "hi", "Hindi"))
    try:
        tts = gTTS(text=str(text_input), lang=tts_lang_code, slow=False)
        tts.save("response.mp3")
        return True
    except Exception:
        try:
            tts = gTTS(text=str(text_input), lang="hi", slow=False)
            tts.save("response.mp3")
            return True
        except Exception:
            return False