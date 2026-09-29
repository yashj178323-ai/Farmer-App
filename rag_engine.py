import json
import os
import re
import tempfile
import time
import hashlib
from functools import lru_cache
from pathlib import Path

import requests
from dotenv import load_dotenv
from groq import Groq
from gtts import gTTS

<<<<<<< HEAD
try:
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import FastEmbedEmbeddings
except Exception:
    Chroma = None
    FastEmbedEmbeddings = None

=======
>>>>>>> f6b31d8cf48c2d556f483b57b5e8ff29e8c474f2
load_dotenv(override=True)

try:
    import streamlit as st
except Exception:
    st = None

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
INDEX_FILE = BASE_DIR / "policy_index.json"
CHROMA_DIR = BASE_DIR / "chroma_db"
GROQ_CHAT_MODEL = os.getenv("GROQ_CHAT_MODEL", "openai/gpt-oss-120b")
WHISPER_MODEL = os.getenv("GROQ_WHISPER_MODEL", "whisper-large-v3")

LANG_MAPPING = {
<<<<<<< HEAD
    "Assamese (অসমীয়া)": ("as", "as", "Assamese"),
    "Bengali (বাংলা)": ("bn", "bn", "Bengali"),
    "Bodo (बर')": (None, "brx", "Bodo"),
    "Dogri (डोगरी)": (None, "doi", "Dogri"),
=======
    "Assamese (অসমীয়া)": ("as", "bn", "Assamese"),
    "Bengali (বাংলা)": ("bn", "bn", "Bengali"),
    "Bodo (बर')": ("hi", "hi", "Bodo"),
    "Dogri (डोगरी)": ("hi", "hi", "Dogri"),
>>>>>>> f6b31d8cf48c2d556f483b57b5e8ff29e8c474f2
    "English": ("en", "en", "English"),
    "Gujarati (ગુજરાતી)": ("gu", "gu", "Gujarati"),
    "Hindi (हिंदी)": ("hi", "hi", "Hindi"),
    "Kannada (ಕನ್ನಡ)": ("kn", "kn", "Kannada"),
<<<<<<< HEAD
    "Kashmiri (कॉशुर)": (None, "ks", "Kashmiri"),
    "Konkani (कोंकणी)": (None, "gom", "Konkani"),
    "Maithili (मैथिली)": (None, "mai", "Maithili"),
    "Malayalam (മലയാളം)": ("ml", "ml", "Malayalam"),
    "Manipuri (ꯃꯩꯇꯩꯂꯣꯟ)": (None, "mni", "Manipuri"),
    "Marathi (मराठी)": ("mr", "mr", "Marathi"),
    "Nepali (नेपाली)": ("ne", "ne", "Nepali"),
    "Odia (ଓଡ଼ିଆ)": ("or", "or", "Odia"),
    "Punjabi (ਪੰਜਾਬੀ)": ("pa", "pa", "Punjabi"),
    "Sanskrit (संस्कृतम्)": ("sa", "sa", "Sanskrit"),
    "Santali (ᱥᱟᱱᱛᱟᱲᱤ)": (None, "sat", "Santali"),
    "Sindhi (सिंधी)": ("sd", "sd", "Sindhi"),
=======
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
>>>>>>> f6b31d8cf48c2d556f483b57b5e8ff29e8c474f2
    "Tamil (தமிழ்)": ("ta", "ta", "Tamil"),
    "Telugu (తెలుగు)": ("te", "te", "Telugu"),
    "Urdu (اردو)": ("ur", "ur", "Urdu"),
}

NO_MATCH = {
    "English": "I could not find enough verified policy information to answer that question. Please ask about KCC, PMFBY, PACS bylaws, Soil Health Card or e-NAM.",
    "Hindi (हिंदी)": "मुझे इस सवाल का जवाब देने के लिए पर्याप्त सत्यापित नीति जानकारी नहीं मिली। कृपया KCC, PMFBY, PACS नियम, मृदा स्वास्थ्य कार्ड या e-NAM से जुड़ा सवाल पूछें।",
    "Marathi (मराठी)": "या प्रश्नाचे उत्तर देण्यासाठी पुरेशी सत्यापित धोरण माहिती सापडली नाही. कृपया KCC, PMFBY, PACS नियम, मृदा आरोग्य कार्ड किंवा e-NAM बद्दल विचारा.",
    "Assamese (অসমীয়া)": "এই প্ৰশ্নৰ উত্তৰ দিবলৈ পৰ্যাপ্ত সত্যাপিত নীতি তথ্য পোৱা নগ'ল। KCC, PMFBY, PACS নিয়ম, Soil Health Card বা e-NAM সম্পৰ্কে সুধিব পাৰে।",
    "Bengali (বাংলা)": "এই প্রশ্নের উত্তর দেওয়ার জন্য পর্যাপ্ত যাচাইকৃত নীতি তথ্য পাওয়া যায়নি। KCC, PMFBY, PACS নিয়ম, Soil Health Card বা e-NAM সম্পর্কে জিজ্ঞাসা করুন।",
}


def get_groq_api_key():
    # 1) .env / process environment
    key = os.getenv("GROQ_API_KEY", "").strip().strip('"').strip("'")
    if key.startswith("gsk_"):
        return key

    # 2) Streamlit project secrets, if configured
    if st is not None:
        try:
            secret_key = str(st.secrets.get("GROQ_API_KEY", "")).strip().strip('"').strip("'")
            if secret_key.startswith("gsk_"):
                return secret_key
        except Exception:
            pass

    return ""


def get_groq_client():
    key = get_groq_api_key()
    return Groq(api_key=key) if key.startswith("gsk_") else None


def normalize_query(text):
    return re.sub(r"\s+", " ", (text or "").strip())


def _clean_text(text):
    text = text or ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _tokens(text):
    # Keep useful policy terms and numbers. Remove very common English stopwords.
    stop = {
        "the", "a", "an", "is", "are", "was", "were", "what", "when", "where",
        "how", "why", "can", "could", "would", "should", "do", "does", "did",
        "under", "for", "to", "of", "and", "or", "in", "on", "my", "me", "i",
        "please", "tell", "about", "within", "must", "be", "from", "with", "by",
    }
    raw = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [x for x in raw if len(x) > 1 and x not in stop]


def _load_index_file():
    if not INDEX_FILE.exists():
        return []
    try:
        return json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


@lru_cache(maxsize=1)
def load_policy_index():
    index = _load_index_file()
    if index:
        return index

    # Self-healing fallback: build the small local index directly from data/.
    try:
        from langchain_community.document_loaders import PyPDFLoader, TextLoader
    except Exception:
        return []

    chunks = []
    if not DATA_DIR.exists():
        return []

    for path in sorted(DATA_DIR.iterdir()):
        try:
            if path.suffix.lower() == ".pdf":
                pages = PyPDFLoader(str(path)).load()
                for page_no, page in enumerate(pages, 1):
                    text = _clean_text(page.page_content)
                    if text:
                        chunks.extend(_chunk_text(text, path.name, page_no))
            elif path.suffix.lower() in {".txt", ".md"}:
                text = TextLoader(str(path), encoding="utf-8").load()[0].page_content
                text = _clean_text(text)
                if text:
                    chunks.extend(_chunk_text(text, path.name, None))
        except Exception as exc:
            print(f"Policy load warning for {path.name}: {exc}")

    if chunks:
        try:
            INDEX_FILE.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass
    return chunks


def _chunk_text(text, source, page_no=None, chunk_size=1100, overlap=160):
    words = text.split()
    out = []
    start = 0
    while start < len(words):
        piece = " ".join(words[start:start + chunk_size])
        out.append({
            "text": piece,
            "source": source,
            "page": page_no,
        })
        if start + chunk_size >= len(words):
            break
        start += max(1, chunk_size - overlap)
    return out


def _translate_for_retrieval(query, language_name):
    if language_name == "English":
        return query
    client = get_groq_client()
    if not client:
        return query
    language = LANG_MAPPING.get(language_name, ("hi", "hi", language_name))[2]
    prompt = (
        f"Translate/rewrite this {language} farmer question into one concise English "
        "search query for an Indian government agriculture policy knowledge base. "
        "Do not answer it. Preserve scheme names, numbers, deadlines, eligibility "
        "terms and the exact intent. Return only the search query.\n\n"
        f"Question: {query}"
    )
    try:
        result = client.chat.completions.create(
            model=GROQ_CHAT_MODEL,
            messages=[
                {"role": "system", "content": "You create precise retrieval queries from farmer questions."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=120,
        )
        return normalize_query(result.choices[0].message.content) or query
    except Exception as exc:
        print(f"Retrieval translation warning: {exc}")
        return query


<<<<<<< HEAD
@lru_cache(maxsize=1)
def load_vector_db():
    """Load the same Chroma DB/embedding model used by ingest.py."""
    if Chroma is None or FastEmbedEmbeddings is None:
        return None
    if not CHROMA_DIR.exists():
        return None
    try:
        embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
        return Chroma(
            persist_directory=str(CHROMA_DIR),
            embedding_function=embeddings,
        )
    except Exception as exc:
        print(f"Chroma load warning: {exc}")
        return None


def _semantic_retrieve(query, k=8):
    """Semantic retrieval for natural-language and multilingual farmer questions."""
    db = load_vector_db()
    if db is None:
        return [], 0.0

    try:
        results = db.similarity_search_with_score(query, k=k)
    except Exception as exc:
        print(f"Semantic retrieval warning: {exc}")
        return [], 0.0

    docs = []
    distances = []
    for doc, distance in results:
        text = _clean_text(getattr(doc, "page_content", ""))
        if not text:
            continue
        meta = getattr(doc, "metadata", {}) or {}
        docs.append({
            "text": text,
            "source": Path(str(meta.get("source", "Unknown source"))).name,
            "page": meta.get("page"),
        })
        try:
            distances.append(float(distance))
        except Exception:
            pass

    if not docs:
        return [], 0.0

    # Chroma returns a distance where lower means more similar. This is only
    # a display confidence, not a probability. Do not use a harsh threshold:
    # policy questions often have different wording from the source document.
    best_distance = min(distances) if distances else 1.0
    confidence = int(max(0.0, min(1.0, 1.0 - (best_distance / 1.5))) * 100)
    return docs, confidence


=======
>>>>>>> f6b31d8cf48c2d556f483b57b5e8ff29e8c474f2
def _keyword_retrieve(query, k=6):
    index = load_policy_index()
    if not index:
        return [], 0.0

    q_tokens = set(_tokens(query))
    # Give exact phrases and important scheme names extra weight.
    q_lower = query.lower()
    scheme_terms = ["pmfby", "kcc", "kisan credit", "pacs", "e-nam", "enam", "soil health", "crop insurance"]
    scores = []
    for item in index:
        text = item.get("text", "")
        lower = text.lower()
        doc_tokens = set(_tokens(text))
        overlap = len(q_tokens & doc_tokens)
        phrase_bonus = sum(3 for term in scheme_terms if term in q_lower and term in lower)
        number_bonus = 2 if any(n in lower for n in re.findall(r"\b\d+(?:\.\d+)?\b", q_lower)) else 0
        score = overlap * 1.0 + phrase_bonus + number_bonus
        if score > 0:
            scores.append((score, item))

    scores.sort(key=lambda x: x[0], reverse=True)
    top = [item for _, item in scores[:k]]
    best = scores[0][0] if scores else 0
    # Convert heuristic score to a stable 0-100 display score.
    confidence = min(99, int(25 + best * 9)) if best else 0
    return top, confidence


def _source_label(docs):
    if not docs:
        return "No verified source found."
    labels = []
    for doc in docs[:4]:
        src = doc.get("source", "Unknown source") if isinstance(doc, dict) else getattr(doc, "metadata", {}).get("source", "Unknown source")
        page = doc.get("page") if isinstance(doc, dict) else getattr(doc, "metadata", {}).get("page")
        label = str(src)
        if page not in (None, ""):
            try:
                label += f" • page {int(page) + 1}"
            except Exception:
                label += f" • page {page}"
        if label not in labels:
            labels.append(label)
    return "; ".join(labels)


def _answer_from_context(question, language_name, docs):
    client = get_groq_client()
    if not client:
        return "Groq API key is missing. Add GROQ_API_KEY to your project .env file or Streamlit secrets."

<<<<<<< HEAD
    language = LANG_MAPPING.get(language_name, (None, None, language_name))[2]
    script_hint = {
        "Santali": "Write in Santali using Ol Chiki script. Do not answer in Hindi.",
        "Bodo": "Write in Bodo using Devanagari script.",
        "Dogri": "Write in Dogri using Devanagari script.",
        "Kashmiri": "Write in Kashmiri using its normal script; do not substitute Hindi.",
        "Manipuri": "Write in Manipuri using Meitei Mayek where practical.",
        "Konkani": "Write in Konkani; do not substitute Marathi.",
        "Maithili": "Write in Maithili; do not substitute Hindi.",
    }.get(language, f"Write in {language} using its normal native script.")
=======
    language = LANG_MAPPING.get(language_name, ("hi", "hi", language_name))[2]
>>>>>>> f6b31d8cf48c2d556f483b57b5e8ff29e8c474f2
    context_parts = []
    for i, doc in enumerate(docs, 1):
        context_parts.append(f"SOURCE {i} — {doc.get('source', 'Unknown')}\n{doc.get('text', '')}")
    context = "\n\n".join(context_parts)

    system = f"""You are Sahakar-Vaani, a government agriculture policy assistant.
Answer the farmer's exact question using ONLY the supplied policy excerpts.
<<<<<<< HEAD
Write the final answer in {language}. {script_hint}
=======
Write the final answer in {language}.
>>>>>>> f6b31d8cf48c2d556f483b57b5e8ff29e8c474f2

Rules:
1. Do not invent rates, deadlines, eligibility, procedures, penalties, or benefits.
2. If the excerpts do not contain the requested fact, say clearly that the verified policy documents do not provide enough information.
3. Do not answer a different but related question.
4. If a number or time period appears in the excerpts, reproduce it accurately.
5. Keep the answer practical and concise (2-5 short sentences or bullets).
6. Do not mention retrieval, embeddings, vector databases, prompts, or internal system details.
"""
    user = f"Farmer question:\n{question}\n\nVerified policy excerpts:\n{context}"
    try:
        result = client.chat.completions.create(
            model=GROQ_CHAT_MODEL,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0,
            max_tokens=350,
        )
        answer = normalize_query(result.choices[0].message.content)
        return answer or NO_MATCH.get(language_name, NO_MATCH["English"])
    except Exception as exc:
        return f"AI answer generation failed: {exc}"


def answer_farmer_query(query, language_name="Hindi (हिंदी)"):
    start = time.time()
    query = normalize_query(query)
    if not query:
        return NO_MATCH.get(language_name, NO_MATCH["English"]), "No verified source found.", [], 0, 0

<<<<<<< HEAD
    # Convert the question to English for the English policy corpus, but also
    # search the original wording. The semantic model handles both paths.
    translated = _translate_for_retrieval(query, language_name)

    semantic_docs_1, sem_conf_1 = _semantic_retrieve(translated, k=8)
    semantic_docs_2, sem_conf_2 = _semantic_retrieve(query, k=8)

    # Keyword retrieval is retained as a fallback for exact scheme names,
    # numbers, and cases where Chroma is unavailable.
    keyword_docs_1, key_conf_1 = _keyword_retrieve(translated, k=6)
    keyword_docs_2, key_conf_2 = _keyword_retrieve(query, k=6)

    seen = set()
    docs = []
    for doc in semantic_docs_1 + semantic_docs_2 + keyword_docs_1 + keyword_docs_2:
=======
    translated = _translate_for_retrieval(query, language_name)
    # Search both the translated English query and original text. This matters for English policy docs and multilingual farmer speech.
    docs1, conf1 = _keyword_retrieve(translated, k=6)
    docs2, conf2 = _keyword_retrieve(query, k=6)

    seen = set()
    docs = []
    for doc in docs1 + docs2:
>>>>>>> f6b31d8cf48c2d556f483b57b5e8ff29e8c474f2
        key = (doc.get("source"), doc.get("page"), doc.get("text"))
        if key not in seen:
            seen.add(key)
            docs.append(doc)
<<<<<<< HEAD

    docs = docs[:8]
    confidence = max(sem_conf_1, sem_conf_2, key_conf_1, key_conf_2)

    # A very low semantic score and no lexical evidence means the question is
    # outside the policy corpus. Otherwise let the LLM decide from the actual
    # excerpts whether the requested fact is present.
    has_semantic_evidence = bool(semantic_docs_1 or semantic_docs_2) and max(sem_conf_1, sem_conf_2) >= 18
    has_keyword_evidence = bool(keyword_docs_1 or keyword_docs_2) and max(key_conf_1, key_conf_2) >= 25

    if not docs or not (has_semantic_evidence or has_keyword_evidence):
=======
    docs = docs[:6]
    confidence = max(conf1, conf2)

    # If keyword retrieval is weak, still give the model a chance only when we have some evidence.
    if not docs or confidence < 30:
>>>>>>> f6b31d8cf48c2d556f483b57b5e8ff29e8c474f2
        latency = int((time.time() - start) * 1000)
        return NO_MATCH.get(language_name, NO_MATCH["English"]), "No verified source found.", docs, confidence, latency

    answer = _answer_from_context(query, language_name, docs)
    latency = int((time.time() - start) * 1000)
    return answer, _source_label(docs), docs, confidence, latency


def transcribe_audio(audio_bytes, language_name="Hindi (हिंदी)"):
    client = get_groq_client()
    if not client:
        return "Invalid or missing GROQ_API_KEY. Check your project .env file or Streamlit secrets."
    whisper_code = LANG_MAPPING.get(language_name, ("hi", "hi", "Hindi"))[0]
    suffix = ".webm"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
        f.write(audio_bytes)
        path = f.name
    try:
        with open(path, "rb") as audio_file:
<<<<<<< HEAD
            kwargs = {
                "file": (os.path.basename(path), audio_file.read()),
                "model": WHISPER_MODEL,
                "response_format": "json",
                "temperature": 0.0,
            }
            # Groq expects ISO-639-1 language codes. For languages outside that set,
            # omit the parameter and let multilingual Whisper auto-detect.
            if whisper_code:
                kwargs["language"] = whisper_code
            result = client.audio.transcriptions.create(**kwargs)
=======
            result = client.audio.transcriptions.create(
                file=(os.path.basename(path), audio_file.read()),
                model=WHISPER_MODEL,
                language=whisper_code,
                response_format="json",
                temperature=0.0,
            )
>>>>>>> f6b31d8cf48c2d556f483b57b5e8ff29e8c474f2
        text = normalize_query(result.text)
        return text if len(text) >= 2 else "Transcription Error: No meaningful speech was detected."
    except Exception as exc:
        return f"Transcription Error: {exc}"
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


def generate_ai4bharat_voice(text, language_name="Hindi (हिंदी)", slow=False):
    if not text:
        return ""
    # gTTS fallback is allowed only for languages with a matching voice code.
    # Never silently convert an unsupported language to Hindi.
    gtts_codes = {
        "English": "en", "Bengali (বাংলা)": "bn", "Gujarati (ગુજરાતી)": "gu",
        "Hindi (हिंदी)": "hi", "Kannada (ಕನ್ನಡ)": "kn", "Malayalam (മലയാളം)": "ml",
        "Marathi (मराठी)": "mr", "Nepali (नेपाली)": "ne", "Odia (ଓଡ଼ିଆ)": "or",
        "Punjabi (ਪੰਜਾਬੀ)": "pa", "Tamil (தமிழ்)": "ta", "Telugu (తెలుగు)": "te",
        "Urdu (اردو)": "ur",
    }
    lang_code = gtts_codes.get(language_name)

    # First try the multilingual AI4Bharat hosted inference endpoint when a token is available.
    hf_token = os.getenv("HF_TOKEN", "").strip()
    if hf_token:
        try:
            url = "https://api-inference.huggingface.co/models/ai4bharat/indic-parler-tts"
            headers = {"Authorization": f"Bearer {hf_token}"}
            payload = {"inputs": text}
            response = requests.post(url, headers=headers, json=payload, timeout=45)
            if response.ok and response.content[:4] == b"RIFF":
                out = BASE_DIR / "response.wav"
                out.write_bytes(response.content)
                return str(out)
        except Exception as exc:
            print(f"AI4Bharat TTS warning: {exc}")

    # Safe fallback: use gTTS only when it has a matching language code.
    if not lang_code:
        return ""
    try:
        out = BASE_DIR / "response.mp3"
        tts = gTTS(text=text, lang=lang_code, slow=slow)
        tts.save(str(out))
        return str(out)
    except Exception as exc:
        print(f"gTTS warning for {language_name}: {exc}")
        return ""


def is_internet_available():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except Exception:
        return False


def check_audio_amplitude(audio_bytes):
    if not audio_bytes:
        return 0.0
    return min(1.0, len(audio_bytes) / 100000.0)
