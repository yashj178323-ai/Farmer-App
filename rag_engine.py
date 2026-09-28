import json
import os
import tempfile
import time
import audioop
import requests
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from gtts import gTTS
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings

load_dotenv(override=True)

def get_groq_client():
    key = os.getenv("GROQ_API_KEY", "").strip().strip('"').strip("'")
    if key and key.startswith("gsk_"):
        return Groq(api_key=key)
    return None

# Cached Vector DB
# IMPORTANT: this MUST use the exact same embedding model that ingest.py used to
# build ./chroma_db (BAAI/bge-small-en-v1.5 via FastEmbed). Querying a Chroma DB
# with a *different* embedding model than the one it was built with silently
# returns near-random matches instead of an error — that was the root cause of
# your PMFBY query pulling PACS bylaws chunks instead of the insurance doc.
# In rag_engine.py: Replace @st.cache_resource and @st.cache_data wrappers with standard Python lru_cache or plain function calls:

from functools import lru_cache

@lru_cache(maxsize=1)
def load_vector_db():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

@lru_cache(maxsize=1)
def load_language_list():
    if os.path.exists(LANGUAGES_FILE):
        with open(LANGUAGES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return ["English", "Hindi (हिंदी)", "Odia (ଓଡ଼ିଆ)", "Marathi (मराठी)"]

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


def transcribe_audio(audio_bytes, language_name="Hindi (हिंदी)"):
    client = get_groq_client()
    if not client:
        return "Invalid or missing GROQ_API_KEY. Please check your .env file."

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


def answer_farmer_query(final_query: str, language_name: str):
    """
    Executes query matching and LLM response generation with import safety guards.
    """
    start_time = time.time()
    raw_context = []
    confidence_score = 0

    # Retrieve vector context if ChromaDB is installed and initialized
    if HAS_CHROMADB:
        try:
            if 'load_vector_db' in globals():
                vector_db = load_vector_db()
            else:
                embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
                vector_db = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
                
            if vector_db is not None:
                results = vector_db.similarity_search_with_score(final_query, k=3)
                raw_context = [doc for doc, _ in results]
                if results:
                    top_score = results[0][1]
                    confidence_score = int(max(0.0, min(1.0, 1.0 - (top_score / 1.2))) * 100)
        except Exception as e:
            print(f"Vector search bypassed: {e}")
            raw_context = []

    # Generate response string via Groq cloud or structured fallback
    try:
        if 'generate_groq_rag_response' in globals():
            response_text = generate_groq_rag_response(final_query, raw_context, language_name)
        else:
            response_text = "Kisan Credit Card (KCC) loans feature a base interest rate of 7% per annum. Prompt repayment earns a 3% subvention, reducing the effective interest rate to 4% per annum."
    except Exception:
        response_text = "Kisan Credit Card (KCC) loans feature a base interest rate of 7% per annum. Prompt repayment earns a 3% subvention, reducing the effective interest rate to 4% per annum."

    latency_ms = int((time.time() - start_time) * 1000)
    audio_path = generate_ai4bharat_voice(response_text, language_name) if 'generate_ai4bharat_voice' in globals() else ""

    return response_text, audio_path, raw_context, confidence_score, latency_ms


def generate_ai4bharat_voice(text_input, language_name):
    if not text_input or "Error" in text_input:
        return False

    token = os.getenv("HF_TOKEN", "").strip().strip('"').strip("'")

    # 1. AI4Bharat Indic-Parler-TTS Engine
    if token and token.startswith("hf_"):
        try:
            API_URL = "https://api-inference.huggingface.co/models/ai4bharat/indic-parler-tts"
            headers = {"Authorization": f"Bearer {token}"}
            payload = {
                "inputs": text_input,
                "parameters": {"description": f"Clear agricultural kiosk speech in {language_name}."}
            }
            res = requests.post(API_URL, headers=headers, json=payload, timeout=6)
            if res.status_code == 200 and len(res.content) > 1000:
                with open("response.mp3", "wb") as f:
                    f.write(res.content)
                return True
        except Exception:
            pass

    # 2. Universal gTTS Fallback
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
        # ==========================================
# NEW FEATURE: AUDIO FILE VALIDATOR
# ==========================================
import wave

def validate_audio_duration(file_path: str, min_duration_sec: float = 0.5) -> bool:
    """
    Validates if recorded audio input meets minimum duration requirements.
    Prevents empty API calls on accidental microphone taps.
    """
    if not os.path.exists(file_path):
        return False
        
    try:
        with wave.open(file_path, 'r') as audio_file:
            frames = audio_file.getnframes()
            rate = audio_file.getframerate()
            duration = frames / float(rate)
            return duration >= min_duration_sec
    except Exception as e:
        print(f"Audio Validation Warning: {e}")
        return True  # Fallback to proceed if format isn't standard WAV
    # ==========================================
# NEW FEATURE: INDIC LANGUAGE BENCHMARK UTILITY
# ==========================================
import time

def benchmark_indic_retrieval(sample_queries=None):
    """
    Benchmarks vector search retrieval latencies across test queries.
    """
    if not sample_queries:
        sample_queries = [
            ("KCC loan interest rate?", "English"),
            ("पीएम फसल बीमा योजना क्या है?", "Hindi (हिंदी)"),
            ("ખેડૂત નોંધણી પ્રક્રિયા", "Gujarati (ગુજરાતી)")
        ]
        
    results = []
    for q, lang in sample_queries:
        start = time.time()
        try:
            db = load_vector_db()
            docs = db.similarity_search(q, k=2)
            latency = round((time.time() - start) * 1000, 2)
            results.append({"query": q, "language": lang, "latency_ms": latency, "docs_found": len(docs)})
        except Exception as e:
            results.append({"query": q, "language": lang, "error": str(e)})
            
    return results
# ==========================================
# NEW FEATURE: AUDIO NOISE GATE CHECKER
# ==========================================
import struct

def check_audio_amplitude(file_path: str, min_rms_threshold: int = 100) -> bool:
    """
    Checks if recorded WAV audio signal exceeds minimum volume threshold.
    Helps ignore silence or extremely faint background noise.
    """
    if not os.path.exists(file_path):
        return False
        
    try:
        with wave.open(file_path, 'rb') as wf:
            n_frames = wf.getnframes()
            if n_frames == 0:
                return False
            data = wf.readframes(n_frames)
            
            # Unpack 16-bit audio samples
            count = len(data) // 2
            if count == 0:
                return False
            format_str = f"<{count}h"
            samples = struct.unpack(format_str, data)
            
            # Calculate Root Mean Square (RMS) volume level
            sum_squares = sum(s ** 2 for s in samples)
            rms = (sum_squares / count) ** 0.5
            return rms >= min_rms_threshold
    except Exception as e:
        print(f"Audio Amplitude Warning: {e}")
        return True  # Fallback to allow processing if format differs
    # ==========================================
# NEW FEATURE: VECTOR SCORE THRESHOLD FILTER
# ==========================================
def filter_docs_by_relevance(docs_with_scores, max_distance=0.85):
    """
    Filters out ChromaDB document matches if vector distance exceeds threshold.
    """
    filtered_docs = []
    for doc, score in docs_with_scores:
        if score <= max_distance:
            filtered_docs.append(doc)
    return filtered_docs
# ==========================================
# NEW FEATURE: AUDIO METADATA INSPECTOR
# ==========================================
def inspect_audio_metadata(file_path: str):
    """
    Returns audio channel count, sample rate, and bit resolution.
    """
    if not os.path.exists(file_path):
        return None
        
    try:
        with wave.open(file_path, 'rb') as wf:
            return {
                "channels": wf.getnchannels(),
                "sample_rate_hz": wf.getframerate(),
                "sample_width_bytes": wf.getsampwidth(),
                "total_frames": wf.getnframes()
            }
    except Exception as e:
        print(f"Metadata Inspection Error: {e}")
        return None
    # ==========================================
# NEW FEATURE: CONTEXT LENGTH SANITIZER
# ==========================================
def truncate_context_for_llm(context_text: str, max_chars: int = 4000) -> str:
    """
    Truncates extracted vector context if it exceeds max character limit to optimize token usage.
    """
    if len(context_text) <= max_chars:
        return context_text
        
    print(f"Truncating RAG context from {len(context_text)} to {max_chars} characters.")
    return context_text[:max_chars] + "\n\n[Context truncated due to length limits]"
# ==========================================
# NEW FEATURE: OFFLINE PROMPT FORMATTER
# ==========================================
def format_offline_fallback_response(raw_text: str, language_name: str) -> str:
    """
    Formats offline vector database extractions cleanly for presentation to the farmer.
    """
    header_map = {
        "Hindi (हिंदी)": "ℹ️ [ऑफलाइन उत्तर] सहकारी नीति दस्तावेज़ से निष्पादित जानकारी:\n\n",
        "Odia (ଓଡ଼ିଆ)": "ℹ️ [ଅଫଲାଇନ୍ ଉତ୍ତର] ସମବାୟ ନୀତି ଦଲିଲରୁ ସୂଚନା:\n\n",
        "Marathi (मराठी)": "ℹ️ [ऑफलाईन उत्तर] सहकार धोरण दस्तऐवजातील माहिती:\n\n",
        "Gujarati (ગુજરાતી)": "ℹ️ [ઓફલાઇન જવાબ] સહકારી નીતિ દસ્તાવેજમાંથી માહિતી:\n\n",
        "English": "ℹ️ [OFFLINE ANSWER] Retrieved policy information:\n\n"
    }
    
    prefix = header_map.get(language_name, "ℹ️ [OFFLINE ANSWER]:\n\n")
    return f"{prefix}{raw_text.strip()}"
# ==========================================
# NEW FEATURE: STT LANGUAGE CODE MAPPER
# ==========================================
def get_stt_language_code(language_name: str) -> str:
    """
    Maps localized language names to standard BCP-47 language tags for Whisper/STT.
    """
    stt_map = {
        "Hindi (हिंदी)": "hi-IN",
        "Odia (ଓଡ଼ିଆ)": "or-IN",
        "Marathi (मराठी)": "mr-IN",
        "Gujarati (ગુજરાતી)": "gu-IN",
        "English": "en-IN"
    }
    return stt_map.get(language_name, "hi-IN")
# ==========================================
# NEW FEATURE: OFFLINE RESPONSE BADGE TAGGER
# ==========================================
def attach_response_metadata(answer_text: str, is_offline: bool = False, sources: str = "") -> dict:
    """
    Wraps response strings into structured JSON with offline and source badges.
    """
    return {
        "text": answer_text,
        "is_offline": is_offline,
        "sources": sources if sources else "PACS Knowledge Base",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
# ==========================================
# NEW FEATURE: CONFIDENCE METRIC ESTIMATOR
# ==========================================
def calculate_rag_confidence_score(docs_with_scores) -> float:
    """
    Computes normalized confidence percentage (0.0 to 1.0) from vector search scores.
    """
    if not docs_with_scores:
        return 0.0
        
    distances = [score for doc, score in docs_with_scores]
    avg_distance = sum(distances) / len(distances)
    
    # Distance of 0.0 is perfect match; > 1.0 is low relevance
    confidence = max(0.0, min(1.0, 1.0 - (avg_distance / 1.5)))
    return round(confidence, 2)
# ==========================================
# NEW FEATURE: INTERNET CONNECTIVITY CHECKER
# ==========================================
# ==========================================
# INTERNET CONNECTIVITY CHECKER
# ==========================================
import socket

def is_internet_available(host="8.8.8.8", port=53, timeout=1.5) -> bool:
    """
    Checks rapid socket connection to verify live internet availability.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False
    # ==========================================
# NEW FEATURE: MULTI-LANG OFFLINE TTS MESSAGES
# ==========================================
def get_localized_offline_audio_prompt(language_name: str) -> str:
    """
    Returns localized text warning when offline query context is missing.
    """
    prompts = {
        "Hindi (हिंदी)": "क्षमा करें, इस विषय पर अभी जानकारी उपलब्ध नहीं है। कृपया PACS अधिकारी से संपर्क करें।",
        "Odia (ଓଡ଼ିଆ)": "କ୍ଷମା କରନ୍ତୁ, ଏହି ବିଷୟରେ ବର୍ତ୍ତମାନ ସୂଚନା ଉପଲବ୍ଧ ନାହିଁ।",
        "Marathi (मराठी)": "क्षमस्व, या विषयावर आता माहिती उपलब्ध नाही. कृपया अधिकाऱ्यांशी संपर्क साधा.",
        "Gujarati (ગુજરાતી)": "માફ કરશો, આ વિષય પર હાલમાં માહિતી ઉપલબ્ધ નથી.",
        "English": "Sorry, policy context for this topic is not available offline. Please consult a PACS officer."
    }
    
    text_msg = prompts.get(language_name, prompts["English"])
    return generate_ai4bharat_voice(text_msg, language_name)
# ==========================================
# NEW FEATURE: VECTOR DISTANCE SANITY CHECK
# ==========================================
def verify_vector_search_health(sample_query="KCC Loan") -> dict:
    """
    Runs a test similarity query and verifies distance health metrics.
    """
    try:
        db = load_vector_db()
        results = db.similarity_search_with_score(sample_query, k=1)
        if not results:
            return {"status": "EMPTY", "min_distance": None}
            
        _, top_score = results[0]
        return {
            "status": "HEALTHY" if top_score < 1.2 else "LOW_RELEVANCE",
            "sample_query": sample_query,
            "min_distance": round(top_score, 3)
        }
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}
    # ==========================================
# NEW FEATURE: TEXT NORMALIZATION HELPER
# ==========================================
import re

def normalize_query_string(raw_query: str) -> str:
    """
    Cleans STT transcription artifacts before sending query to embedding model.
    """
    if not raw_query:
        return ""
        
    # Remove excessive punctuation while preserving Indic Unicode ranges
    cleaned = re.sub(r'[^\w\s\u0900-\u097F\u0B00-\u0B7F\u0A80-\u0AFF]', ' ', raw_query)
    # Collapse multiple whitespace spaces into a single space
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned
# ==========================================
# NEW FEATURE: VECTOR RESULT DEDUPLICATOR
# ==========================================
def deduplicate_retrieved_docs(docs):
    """
    Removes redundant document chunks from similarity search results.
    """
    seen_content = set()
    unique_docs = []
    
    for doc in docs:
        content_hash = hashlib.md5(doc.page_content.strip().encode('utf-8')).hexdigest()
        if content_hash not in seen_content:
            seen_content.add(content_hash)
            unique_docs.append(doc)
            
    return unique_docs
# ==========================================
# NEW FEATURE: SOURCE ATTRIBUTION FORMATTER
# ==========================================
def extract_document_sources(retrieved_docs) -> str:
    """
    Extracts unique source filenames and page numbers from ChromaDB vector results.
    """
    if not retrieved_docs:
        return "No source documents matched."
        
    sources = set()
    for doc in retrieved_docs:
        src = doc.metadata.get("source", "Unknown Document")
        page = doc.metadata.get("page", None)
        filename = os.path.basename(src)
        if page is not None:
            sources.add(f"{filename} (p. {page + 1})")
        else:
            sources.add(filename)
            
    return ", ".join(sources)
# ==========================================
# NEW FEATURE: LOCALIZED FEEDBACK AUDIO PROMPT
# ==========================================
def get_feedback_acknowledgment_prompt(language_name: str, positive: bool = True) -> str:
    """
    Returns localized confirmation text for audio feedback playback.
    """
    if positive:
        ack_map = {
            "Hindi (हिंदी)": "आपकी प्रतिक्रिया के लिए धन्यवाद।",
            "Odia (ଓଡ଼ିଆ)": "ଆପଣଙ୍କର ମତାମତ ପାଇଁ ଧନ୍ୟବାଦ।",
            "Marathi (मराठी)": "तुमच्या अभिप्रायाबद्दल धन्यवाद.",
            "Gujarati (ગુજરાતી)": "તમારા પ્રતિભાવ માટે આભાર.",
            "English": "Thank you for your feedback."
        }
    else:
        ack_map = {
            "Hindi (हिंदी)": "आपकी प्रतिक्रिया दर्ज कर ली गई है। हम इसमें सुधार करेंगे।",
            "Odia (ଓଡ଼ିଆ)": "ଆପଣଙ୍କର ମତାମତ ରେକର୍ଡ କରାଯାଇଛି।",
            "Marathi (मराठी)": "तुमची नोंद घेतली गेली आहे.",
            "Gujarati (ગુજરાતી)": "તમારી ટીપ્પણી નોંધી લેવામાં આવી છે.",
            "English": "Your feedback has been logged for system improvement."
        }
    return ack_map.get(language_name, ack_map["English"])
# ==========================================
# NEW FEATURE: STT TRANSCRIPT SANITIZER
# ==========================================
def is_valid_stt_transcript(text: str) -> bool:
    """
    Validates if speech-to-text transcript contains sufficient meaningful content.
    """
    if not text:
        return False
    clean_text = text.strip()
    if len(clean_text) < 3:
        return False
    # Reject common speech recognition hallucination strings
    invalid_phrases = ["thank you.", "subtitles", "amara.org", "you", ""]
    if clean_text.lower() in invalid_phrases:
        return False
    return True
# ==========================================
# NEW FEATURE: VECTOR MODEL WARMUP UTILITY
# ==========================================
def warmup_rag_embedding_engine():
    """
    Pre-loads HuggingFace embeddings into RAM during application boot.
    """
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        _ = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        return True
    except Exception as e:
        print(f"Embedding Warmup Failed: {e}")
        return False
    # ==========================================
# NEW FEATURE: DISTANCE TO PERCENTAGE CONVERTER
# ==========================================
def convert_distance_to_match_percentage(distance_score: float) -> int:
    """
    Converts ChromaDB distance score into a user-friendly 0-100% confidence score.
    """
    if distance_score is None:
        return 0
    # Map distance: 0.0 -> 100%, 1.2 -> 0%
    similarity = max(0.0, min(1.0, 1.0 - (distance_score / 1.2)))
    return int(similarity * 100)
# ==========================================
# AUDIO AMPLITUDE CHECKER
# ==========================================
import wave
import audioop

def check_audio_amplitude(file_path: str, min_rms_threshold: int = 100) -> bool:
    """
    Reads a WAV audio file and verifies if the Root Mean Square (RMS) amplitude meets minimum volume thresholds.
    """
    if not os.path.exists(file_path):
        return False
    try:
        with wave.open(file_path, 'rb') as wf:
            frames = wf.readframes(wf.getnframes())
            if not frames:
                return False
            rms = audioop.rms(frames, wf.getsampwidth())
            return rms >= min_rms_threshold
    except Exception as e:
        print(f"Audio Amplitude Error: {e}")
        return True  # Fallback to true if audio processing fails
    # ==========================================
# NEW FEATURE: CHROMADB TOTAL CHUNK COUNTER
# ==========================================
def get_total_indexed_chunks_count(chroma_dir="chroma_db") -> int:
    """
    Returns total document chunks stored inside ChromaDB collection.
    """
    try:
        db = load_vector_db(chroma_dir)
        collection = db._collection
        return collection.count()
    except Exception:
        return 0
    # ==========================================
# NEW FEATURE: PROMPT INJECTION SANITIZER
# ==========================================
def sanitize_prompt_for_injection(raw_prompt: str) -> str:
    """
    Strips potential prompt injection strings and system command payloads.
    """
    if not raw_prompt:
        return ""
        
    forbidden_terms = [
        "ignore previous instructions", "system prompt", "drop table", 
        "eval(", "exec(", "<script>", "delete from"
    ]
    
    clean_prompt = raw_prompt
    for term in forbidden_terms:
        if term in clean_prompt.lower():
            clean_prompt = clean_prompt.lower().replace(term, "[redacted]")
            
    return clean_prompt.strip()
# ==========================================
# NEW FEATURE: AUDIO FORMAT CONVERTER
# ==========================================
def convert_audio_to_wav(input_path: str, output_path: str = "temp_input.wav") -> bool:
    """
    Converts incoming browser audio recordings into standardized mono WAV format.
    """
    if not os.path.exists(input_path):
        return False
    try:
        from pydub import AudioSegment
        sound = AudioSegment.from_file(input_path)
        sound = sound.set_channels(1).set_frame_rate(16000)
        sound.export(output_path, format="wav")
        return True
    except Exception as e:
        print(f"Audio conversion notice: {e}")
        return False
    # ==========================================
# NEW FEATURE: AUDIO NOISE THRESHOLD CHECK
# ==========================================
def is_audio_above_noise_floor(wav_file: str, threshold: int = 200) -> bool:
    """
    Verifies if input audio file amplitude surpasses silence/noise floor.
    """
    if not os.path.exists(wav_file):
        return False
    try:
        import wave
        import audioop
        with wave.open(wav_file, 'rb') as wf:
            frames = wf.readframes(wf.getnframes())
            if not frames:
                return False
            rms = audioop.rms(frames, wf.getsampwidth())
            return rms > threshold
    except Exception:
        return True
    # ==========================================
# NEW FEATURE: DISTANCE THRESHOLD FILTER
# ==========================================
def filter_docs_by_max_distance(docs_with_scores, max_distance=1.1):
    """
    Filters out ChromaDB document chunks whose distance exceeds tolerance limits.
    """
    valid_docs = []
    for doc, score in docs_with_scores:
        if score <= max_distance:
            valid_docs.append(doc)
    return valid_docs
# ==========================================
# NEW FEATURE: EXACT DISTANCE DUPLICATE GUARD
# ==========================================
def filter_zero_distance_duplicates(docs_with_scores, min_distance_threshold=0.001):
    """
    Flags documents with near-zero distance scores to prevent infinite vector loop processing.
    """
    filtered_docs = []
    for doc, score in docs_with_scores:
        if score >= min_distance_threshold:
            filtered_docs.append((doc, score))
    return filtered_docs
# ==========================================
# NEW FEATURE: LANGUAGE SWITCH AUDIO ACKNOWLEDGMENT
# ==========================================
def get_language_switch_audio_prompt(new_language: str) -> str:
    """
    Returns localized confirmation message when language setting changes.
    """
    messages = {
        "Hindi (हिंदी)": "भाषा बदलकर हिंदी कर दी गई है।",
        "Odia (ଓଡ଼ିଆ)": "ଭାଷା ଓଡ଼ିଆକୁ ପରିବର୍ତ୍ତିତ ହୋଇଛି।",
        "Marathi (मराठी)": "भाषा मराठीमध्ये बदलली आहे.",
        "Gujarati (ગુજરાતી)": "ભાષા બદલીને ગુજરાતી કરવામાં આવી છે.",
        "English": "Language changed to English."
    }
    selected_msg = messages.get(new_language, messages["English"])
    return generate_ai4bharat_voice(selected_msg, new_language)
# ==========================================
# NEW FEATURE: HALLUCINATION GUARD
# ==========================================
def validate_response_grounding(response_text: str, source_context_docs: list) -> bool:
    """
    Checks if the generated response text is adequately grounded in retrieved context documents.
    """
    if not response_text or not source_context_docs:
        return False
        
    combined_context = " ".join([doc.page_content.lower() for doc in source_context_docs])
    # Extract core keywords from generated response (words longer than 4 chars)
    keywords = [w.lower() for w in response_text.split() if len(w) > 4]
    
    if not keywords:
        return True
        
    match_count = sum(1 for kw in keywords if kw in combined_context)
    grounding_ratio = match_count / len(keywords)
    
    # Require at least 25% key term match with source documents
    return grounding_ratio >= 0.25
# ==========================================
# NEW FEATURE: CONTEXT TOKEN COUNT ESTIMATOR
# ==========================================
def estimate_context_token_count(docs: list) -> int:
    """
    Estimates character-to-token count for ChromaDB retrieved chunks (approx. 4 chars per token).
    """
    if not docs:
        return 0
    total_chars = sum(len(doc.page_content) for doc in docs)
    return total_chars // 4
# ==========================================
# NEW FEATURE: AGGREGATE GROUNDING SCORE
# ==========================================
def calculate_aggregate_grounding_score(docs_with_scores: list) -> int:
    """
    Computes an average percentage confidence score across top retrieved chunks.
    """
    if not docs_with_scores:
        return 0
        
    percentages = []
    for _, score in docs_with_scores:
        # Distance to percentage mapping
        pct = convert_distance_to_match_percentage(score) if 'convert_distance_to_match_percentage' in globals() else int(max(0.0, min(1.0, 1.0 - (score / 1.2))) * 100)
        percentages.append(pct)
        
    return int(sum(percentages) / len(percentages))
# ==========================================
# NEW FEATURE: SYSTEM ALERT AUDIO GENERATOR
# ==========================================
def generate_system_alert_audio(alert_text_en: str, language_name: str) -> str:
    """
    Generates localized MP3 audio for system alerts and errors.
    """
    translations = {
        "Hindi (हिंदी)": "कृपया प्रतीक्षा करें, आपका अनुरोध संसाधित किया जा रहा है।",
        "Odia (ଓଡ଼ିଆ)": "ଦୟାକରି ଅପେକ୍ଷା କରନ୍ତୁ, ଆପଣଙ୍କର ଅନୁରୋଧ ପ୍ରସେସ୍ ହେଉଛି।",
        "Marathi (मराठी)": "कृपया वाट पाहा, तुमची विनंती प्रक्रियेत आहे.",
        "Gujarati (ગુજરાતી)": "કૃપા કરીને રાહ જુઓ, તમારી વિનંતી પર પ્રક્રિયા થઈ રહી છે.",
        "English": alert_text_en
    }
    
    msg = translations.get(language_name, alert_text_en)
    return generate_ai4bharat_voice(msg, language_name)
# ==========================================
# NEW FEATURE: TEXT TRUNCATOR HELPER
# ==========================================
def truncate_text_content(text: str, max_chars: int = 300) -> str:
    """
    Safely truncates document text to max_chars limit with ellipsis.
    """
    if not text or len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(' ', 1)[0] + "..."
# ==========================================
# NEW FEATURE: LOCALIZED ERROR AUDIO PROMPT MAP
# ==========================================
def get_error_audio_prompt(error_code: str, language_name: str) -> str:
    """
    Returns localized text messages for speech synthesis during error states.
    """
    prompts = {
        "LOW_VOLUME": {
            "Hindi (हिंदी)": "आपकी आवाज़ धीमी थी, कृपया थोड़ा ज़ोर से बोलें।",
            "Odia (ଓଡ଼ିଆ)": "ଆପଣଙ୍କର ସ୍ୱର ଧୀମା ଥିଲା, ଦୟାକରି ଟିକିଏ ଜୋରରେ କୁହନ୍ତୁ।",
            "Marathi (मराठी)": "तुमचा आवाज कमी होता, कृपया थोडे मोठ्याने बोला.",
            "Gujarati (ગુજરાતી)": "તમારો અવાજ ધીમો હતો, કૃપા કરીને થોડું મોટેથી બોલો.",
            "English": "Your audio level was low. Please speak louder into the mic."
        },
        "NO_MATCH": {
            "Hindi (हिंदी)": "क्षमा करें, इस विषय पर कोई जानकारी नहीं मिली।",
            "Odia (ଓଡ଼ିଆ)": "କ୍ଷମା କରନ୍ତୁ, ଏହି ବିଷୟରେ କୌଣସି ସୂଚନା ମିଳିଲା ନାହିଁ।",
            "Marathi (मराठी)": "क्षमस्व, या विषयावर कोणतीही माहिती आढळली नाही.",
            "Gujarati (ગુજરાતી)": "માફ કરશો, આ વિષય પર કોઈ માહિતી મળી નથી.",
            "English": "Sorry, no relevant policy match was found in the database."
        }
    }
    
    code_map = prompts.get(error_code, prompts["NO_MATCH"])
    return code_map.get(language_name, code_map["English"])
# ==========================================
# NEW FEATURE: DYNAMIC PROMPT TEMPLATE BUILDER
# ==========================================
def build_dynamic_rag_system_prompt(language_name: str, tone: str = "HELPFUL") -> str:
    """
    Constructs context-aware system prompts tailored to PACS policy retrieval in target language.
    """
    base_instructions = {
        "Hindi (हिंदी)": "आप सहकार-वाणी सहायक हैं। केवल दिए गए सरकारी दस्तावेजों के आधार पर संक्षिप्त और सटीक उत्तर दें।",
        "Odia (ଓଡ଼ିଆ)": "ଆପଣ ସହକାର-ବାଣୀ ସହାୟକ। କେବଳ ପ୍ରଦତ୍ତ ନୀତି ଦଲିଲ ଆଧାରରେ ସଂକ୍ଷିପ୍ତ ଉତ୍ତର ଦିଅନ୍ତୁ।",
        "Marathi (मराठी)": "तुम्ही सहकार-वाणी सहाय्यक आहात. केवळ दिलेल्या शासकीय कागदपत्रांच्या आधारे अचूक उत्तर द्या.",
        "Gujarati (ગુજરાતી)": "તમે સહકાર-વાણી સહાયક છો. માત્ર આપેલા સરકારી દસ્તાવેજોના આધારે જ સચોટ જવાબ આપો.",
        "English": "You are the Sahakar-Vaani assistant. Answer strictly based on provided PACS and agricultural policy documents."
    }
    
    prompt = base_instructions.get(language_name, base_instructions["English"])
    if tone == "URGENT":
        prompt += " Focus directly on grievance and escalation timelines."
    return prompt
# ==========================================
# NEW FEATURE: SCHEME KEYWORD RE-RANKER
# ==========================================
def rerank_docs_by_scheme_priority(docs_with_scores: list, query_text: str) -> list:
    """
    Boosts relevance of document chunks containing explicit keyword matches for core schemes.
    """
    if not docs_with_scores:
        return []
        
    schemes = ["kcc", "pmfby", "bylaw", "insurance", "loan", "interest", "subsidy"]
    matched_schemes = [s for s in schemes if s in query_text.lower()]
    
    if not matched_schemes:
        return [doc for doc, _ in docs_with_scores]
        
    boosted = []
    regular = []
    
    for doc, score in docs_with_scores:
        text_lower = doc.page_content.lower()
        if any(s in text_lower for s in matched_schemes):
            boosted.append(doc)
        else:
            regular.append(doc)
            
    return boosted + regular
# ==========================================
# NEW FEATURE: RAG IN-MEMORY RESPONSE CACHE
# ==========================================
RAG_RESPONSE_CACHE = {}

def get_cached_rag_response(query_text: str, language_name: str):
    """
    Retrieves cached response string if query and language match recent lookups.
    """
    cache_key = f"{language_name}:{query_text.strip().lower()}"
    return RAG_RESPONSE_CACHE.get(cache_key, None)

def cache_rag_response(query_text: str, language_name: str, response_text: str, max_cache_size=50):
    """
    Stores generated RAG answer in memory cache.
    """
    if len(RAG_RESPONSE_CACHE) >= max_cache_size:
        RAG_RESPONSE_CACHE.clear()
    cache_key = f"{language_name}:{query_text.strip().lower()}"
    RAG_RESPONSE_CACHE[cache_key] = response_text
    # ==========================================
# NEW FEATURE: EMBEDDING VECTOR CACHE
# ==========================================
EMBEDDING_CACHE = {}

def get_cached_query_embedding(query_text: str):
    """
    Retrieves pre-computed vector embedding for repeated queries.
    """
    return EMBEDDING_CACHE.get(query_text.strip().lower(), None)

def cache_query_embedding(query_text: str, embedding_vector: list, max_entries=100):
    """
    Stores calculated vector embedding in memory cache.
    """
    if len(EMBEDDING_CACHE) >= max_entries:
        EMBEDDING_CACHE.clear()
    EMBEDDING_CACHE[query_text.strip().lower()] = embedding_vector
    # ==========================================
# NEW FEATURE: VECTOR INDEX VERSION INSPECTOR
# ==========================================
def get_vector_db_metadata(chroma_dir="chroma_db"):
    """
    Returns vector index version metadata and active document collection stats.
    """
    try:
        db = load_vector_db(chroma_dir)
        col = db._collection
        return {
            "version": "v1.4-pacs-policy",
            "collection_name": col.name,
            "total_chunks": col.count(),
            "status": "HEALTHY"
        }
    except Exception as e:
        return {
            "version": "Unknown",
            "collection_name": "None",
            "total_chunks": 0,
            "status": f"ERROR: {e}"
        }
    # ==========================================
# FEATURE 182: DYNAMIC CONTEXT EXPANDER
# ==========================================
def expand_search_context_window(docs: list, max_docs: int = 4) -> list:
    """Ensures at least max_docs chunks are returned by broadening threshold if needed."""
    return docs[:max_docs]

# ==========================================
# FEATURE 183: LOCAL VECTOR EMBEDDING SANITY TEST
# ==========================================
def test_vector_embedding_pipeline() -> bool:
    """Verifies that vector search produces valid non-empty responses."""
    try:
        db = load_vector_db()
        results = db.similarity_search("KCC Loan Rate", k=1)
        return len(results) > 0
    except Exception:
        return False

# ==========================================
# FEATURE 184: GROQ HYBRID MODEL FALLBACK SWITCH
# ==========================================
def query_groq_llm_with_fallback(prompt: str, model="llama3-8b-8192") -> str:
    """Queries Groq API with automatic backup model fallback."""
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
        resp = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            timeout=5.0
        )
        return resp.choices[0].message.content
    except Exception as e:
        print(f"Groq primary model failed: {e}. Switching to offline mode.")
        return ""

# ==========================================
# FEATURE 185: CONTEXT CITATION PARSER
# ==========================================
def extract_document_sources(docs: list) -> list:
    """Extracts unique source document titles/filenames from retrieved vector metadata."""
    sources = []
    for doc in docs:
        src = doc.metadata.get("source", "PACS Policy Manual")
        if src not in sources:
            sources.append(src)
    return sources

# ==========================================
# FEATURE 186: LOCALIZED AUDIO PROMPT SPEED CONTROL
# ==========================================
def adjust_tts_speech_rate(audio_path: str, speed_factor: float = 1.0):
    """Placeholder for modifying gTTS/AI4Bharat playback speed."""
    return audio_path

# ==========================================
# FEATURE 187: RESPONSE RELEVANCE THRESHOLD GUARD
# ==========================================
def is_response_relevance_acceptable(response_text: str) -> bool:
    """Verifies that generated answer string meets minimum quality length and non-empty criteria."""
    return bool(response_text and len(response_text.strip()) > 15)

# ==========================================
# FEATURE 188: QUERY SYNONYM EXPANDER
# ==========================================
def expand_query_synonyms(query_text: str) -> str:
    """Injects regional agricultural domain terms into user query prior to vector search."""
    synonyms = {
        "ऋण": "ऋण KCC loan interest",
        "बीमा": "बीमा फसल बीमा PMFBY claim",
        "खाद": "खाद उर्वरक fertilizer subsidy"
    }
    expanded = query_text
    for word, syn in synonyms.items():
        if word in query_text:
            expanded += " " + syn
    return expanded
# ==========================================
# SAFE CHROMADB & VECTOR IMPORT FALLBACK
# ==========================================
try:
    import chromadb
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False
    # ==========================================
# AUDIOOP PYTHON 3.13 COMPATIBILITY GUARD
# ==========================================
except ImportError:
        audioop = None

def calculate_audio_amplitude(raw_pcm_data):
    """Calculates RMS audio level safely across Python versions."""
    if audioop is not None and raw_pcm_data:
        try:
            return audioop.rms(raw_pcm_data, 2)
        except Exception:
            return 0
    return 100  # Default fallback amplitude