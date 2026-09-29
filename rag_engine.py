import hashlib
import json
import os
import re
import tempfile
import time
from functools import lru_cache
from pathlib import Path

import requests
from dotenv import load_dotenv
from groq import Groq
from gtts import gTTS

try:
    from langchain_community.vectorstores import Chroma
    try:
        from langchain_community.embeddings import FastEmbedEmbeddings
    except Exception:
        FastEmbedEmbeddings = None
except Exception:
    Chroma = None
    FastEmbedEmbeddings = None

try:
    import streamlit as st
except Exception:
    st = None

load_dotenv(override=True)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
INDEX_FILE = BASE_DIR / "policy_index.json"
CHROMA_DIR = BASE_DIR / "chroma_db"

GROQ_CHAT_MODEL = os.getenv("GROQ_CHAT_MODEL", "openai/gpt-oss-120b")
WHISPER_MODEL = os.getenv("GROQ_WHISPER_MODEL", "whisper-large-v3-turbo")

# The first value is the ISO-639-1 Whisper code when one exists.
# The second value is the browser/TTS locale.
# The third value is the language name used by the answer prompt.
LANG_MAPPING = {
    "Assamese (অসমীয়া)": ("as", "as-IN", "Assamese"),
    "Bengali (বাংলা)": ("bn", "bn-IN", "Bengali"),
    "Bodo (बर')": (None, "brx-IN", "Bodo"),
    "Dogri (डोगरी)": (None, "doi-IN", "Dogri"),
    "English": ("en", "en-IN", "English"),
    "Gujarati (ગુજરાતી)": ("gu", "gu-IN", "Gujarati"),
    "Hindi (हिंदी)": ("hi", "hi-IN", "Hindi"),
    "Kannada (ಕನ್ನಡ)": ("kn", "kn-IN", "Kannada"),
    "Kashmiri (कॉशुर)": (None, "ks-IN", "Kashmiri"),
    "Konkani (कोंकणी)": (None, "kok-IN", "Konkani"),
    "Maithili (मैथिली)": (None, "mai-IN", "Maithili"),
    "Malayalam (മലയാളം)": ("ml", "ml-IN", "Malayalam"),
    "Manipuri (ꯃꯩꯇꯩꯂꯣꯟ)": (None, "mni-IN", "Manipuri"),
    "Marathi (मराठी)": ("mr", "mr-IN", "Marathi"),
    "Nepali (नेपाली)": ("ne", "ne-NP", "Nepali"),
    "Odia (ଓଡ଼ିଆ)": ("or", "or-IN", "Odia"),
    "Punjabi (ਪੰਜਾਬੀ)": ("pa", "pa-IN", "Punjabi"),
    "Sanskrit (संस्कृतम्)": (None, "sa-IN", "Sanskrit"),
    "Santali (ᱥᱟᱱᱛᱟᱲᱤ)": (None, "sat-IN", "Santali"),
    "Sindhi (सिंधी)": ("sd", "sd-IN", "Sindhi"),
    "Tamil (தமிழ்)": ("ta", "ta-IN", "Tamil"),
    "Telugu (తెలుగు)": ("te", "te-IN", "Telugu"),
    "Urdu (اردو)": ("ur", "ur-IN", "Urdu"),
}

NO_MATCH = {
    "English": "I could not find enough verified information in the kiosk policy documents to answer that question.",
    "Hindi (हिंदी)": "कियोस्क के सत्यापित नीति दस्तावेजों में इस प्रश्न का पर्याप्त उत्तर नहीं मिला।",
    "Marathi (मराठी)": "किऑस्कमधील सत्यापित धोरण दस्तऐवजांमध्ये या प्रश्नाचे पुरेसे उत्तर सापडले नाही.",
    "Bengali (বাংলা)": "কিয়স্কের যাচাইকৃত নীতি নথিতে এই প্রশ্নের পর্যাপ্ত উত্তর পাওয়া যায়নি।",
    "Gujarati (ગુજરાતી)": "કિયોસ્કના ચકાસેલા નીતિ દસ્તાવેજોમાં આ પ્રશ્નનો પૂરતો જવાબ મળ્યો નથી.",
    "Tamil (தமிழ்)": "கியாஸ்கில் உள்ள சரிபார்க்கப்பட்ட கொள்கை ஆவணங்களில் இந்தக் கேள்விக்கான போதுமான பதில் கிடைக்கவில்லை.",
    "Telugu (తెలుగు)": "కియోస్క్‌లోని ధృవీకరించిన విధాన పత్రాల్లో ఈ ప్రశ్నకు తగిన సమాధానం దొరకలేదు.",
    "Kannada (ಕನ್ನಡ)": "ಕಿಯೋಸ್ಕ್‌ನ ಪರಿಶೀಲಿಸಿದ ನೀತಿ ದಾಖಲೆಗಳಲ್ಲಿ ಈ ಪ್ರಶ್ನೆಗೆ ಸಾಕಷ್ಟು ಉತ್ತರ ಸಿಗಲಿಲ್ಲ.",
    "Malayalam (മലയാളം)": "കിയോസ്കിലെ പരിശോധിച്ച നയരേഖകളിൽ ഈ ചോദ്യത്തിന് മതിയായ ഉത്തരം കണ്ടെത്താനായില്ല.",
    "Punjabi (ਪੰਜਾਬੀ)": "ਕਿਓਸਕ ਦੇ ਪ੍ਰਮਾਣਿਤ ਨੀਤੀ ਦਸਤਾਵੇਜ਼ਾਂ ਵਿੱਚ ਇਸ ਸਵਾਲ ਦਾ ਕਾਫ਼ੀ ਜਵਾਬ ਨਹੀਂ ਮਿਲਿਆ।",
    "Odia (ଓଡ଼ିଆ)": "କିଓସ୍କର ଯାଞ୍ଚିତ ନୀତି ଦଲିଲରେ ଏହି ପ୍ରଶ୍ନର ପର୍ଯ୍ୟାପ୍ତ ଉତ୍ତର ମିଳିଲା ନାହିଁ।",
}

# These aliases help retrieval when Whisper produces a common spelling of a
# scheme name in a regional script.
QUERY_ALIASES = {
    "किसान क्रेडिट कार्ड": "Kisan Credit Card KCC",
    "किसान क्रेडिट": "Kisan Credit Card KCC",
    "केसीसी": "Kisan Credit Card KCC",
    "के सी सी": "Kisan Credit Card KCC",
    "पीएमएफबीवाई": "PMFBY",
    "प्रधानमंत्री फसल बीमा": "PMFBY",
    "पैक्स": "PACS",
    "ई-नाम": "e-NAM",
    "इनाम": "e-NAM",
    "मृदा स्वास्थ्य": "Soil Health Card",
    "मिट्टी": "Soil Health Card soil testing",
    "শস্য বীমা": "PMFBY crop insurance",
    "কিষাণ ক্রেডিট": "Kisan Credit Card KCC",
    "પાક વીમો": "PMFBY crop insurance",
    "கிசான் கிரெடிட்": "Kisan Credit Card KCC",
    "పంట బీమా": "PMFBY crop insurance",
}


def get_groq_api_key():
    key = os.getenv("GROQ_API_KEY", "").strip().strip('"').strip("'")
    if key.startswith("gsk_"):
        return key

    if st is not None:
        try:
            secret_key = str(st.secrets.get("GROQ_API_KEY", "")).strip().strip('"').strip("'")
            if secret_key.startswith("gsk_"):
                return secret_key
        except Exception:
            pass

    return ""


def get_hf_token():
    token = os.getenv("HF_TOKEN", "").strip().strip('"').strip("'")
    if token.startswith("hf_"):
        return token
    if st is not None:
        try:
            token = str(st.secrets.get("HF_TOKEN", "")).strip().strip('"').strip("'")
            if token.startswith("hf_"):
                return token
        except Exception:
            pass
    return ""


def get_groq_client():
    key = get_groq_api_key()
    return Groq(api_key=key) if key else None


def normalize_query(text):
    return re.sub(r"\s+", " ", str(text or "").strip())


def _clean_text(text):
    return normalize_query(text)


def clean_and_normalize_query(text):
    cleaned = normalize_query(text)

    for source, replacement in QUERY_ALIASES.items():
        cleaned = cleaned.replace(source, replacement)

    replacements = {
        r"\bपीएम\s*एफ\s*बी\s*वाई\b": "PMFBY",
        r"\bपीएमएफबीवाई\b": "PMFBY",
        r"\bके\s*सी\s*सी\b": "KCC",
        r"\bपैक्स\b": "PACS",
        r"\bई\s*[-–]?\s*नाम\b": "e-NAM",
        r"\bइनाम\b": "e-NAM",
    }

    for pattern, replacement in replacements.items():
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)

    return cleaned


def _tokens(text):
    stop = {
        "the", "a", "an", "is", "are", "was", "were", "what", "when", "where",
        "how", "why", "can", "could", "would", "should", "do", "does", "did",
        "under", "for", "to", "of", "and", "or", "in", "on", "my", "me", "i",
        "please", "tell", "about", "within", "must", "be", "from", "with", "by",
        "farmer", "farmers", "scheme", "rules", "information",
    }
    raw = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [token for token in raw if len(token) > 1 and token not in stop]


def _load_index_file():
    if not INDEX_FILE.exists():
        return []
    try:
        data = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception as exc:
        print(f"Policy index warning: {exc}")
        return []


@lru_cache(maxsize=1)
def load_policy_index():
    index = _load_index_file()
    if index:
        return index

    # Self-healing fallback: rebuild a small searchable index directly from
    # the files in data/ if policy_index.json is missing.
    chunks = []

    try:
        from langchain_community.document_loaders import PyPDFLoader, TextLoader
    except Exception:
        return []

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
            INDEX_FILE.write_text(
                json.dumps(chunks, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    return chunks


def _chunk_text(text, source, page_no=None, chunk_size=1100, overlap=160):
    words = text.split()
    result = []
    start = 0

    while start < len(words):
        piece = " ".join(words[start:start + chunk_size])
        result.append({
            "text": piece,
            "source": source,
            "page": page_no,
        })

        if start + chunk_size >= len(words):
            break

        start += max(1, chunk_size - overlap)

    return result


def _translate_for_retrieval(query, language_name):
    if language_name == "English":
        return clean_and_normalize_query(query)

    client = get_groq_client()
    if not client:
        return clean_and_normalize_query(query)

    language = LANG_MAPPING.get(
        language_name,
        (None, None, language_name),
    )[2]

    prompt = (
        f"Convert this {language} farmer question into one concise English "
        "search query for an Indian agriculture policy knowledge base. "
        "Do not answer the question. Preserve scheme names, numbers and intent. "
        "Return only the English search query.\n\n"
        f"Question: {query}"
    )

    try:
        result = client.chat.completions.create(
            model=GROQ_CHAT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You create precise retrieval queries from farmer questions.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=120,
        )
        translated = normalize_query(result.choices[0].message.content)
        return clean_and_normalize_query(translated or query)
    except Exception as exc:
        print(f"Retrieval translation warning: {exc}")
        return clean_and_normalize_query(query)


@lru_cache(maxsize=1)
def load_vector_db():
    if Chroma is None or FastEmbedEmbeddings is None:
        return None

    if not CHROMA_DIR.exists():
        return None

    try:
        embeddings = FastEmbedEmbeddings(
            model_name="BAAI/bge-small-en-v1.5"
        )
        return Chroma(
            persist_directory=str(CHROMA_DIR),
            embedding_function=embeddings,
        )
    except Exception as exc:
        print(f"Chroma load warning: {exc}")
        return None


def _semantic_retrieve(query, k=8):
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

        metadata = getattr(doc, "metadata", {}) or {}

        docs.append({
            "text": text,
            "source": Path(
                str(metadata.get("source", "Unknown source"))
            ).name,
            "page": metadata.get("page"),
        })

        try:
            distances.append(float(distance))
        except Exception:
            pass

    if not docs:
        return [], 0.0

    best_distance = min(distances) if distances else 1.0
    confidence = int(
        max(
            0.0,
            min(1.0, 1.0 - (best_distance / 1.5)),
        ) * 100
    )

    return docs, confidence


def _keyword_retrieve(query, k=8):
    index = load_policy_index()
    if not index:
        return [], 0.0

    query_lower = query.lower()
    query_tokens = set(_tokens(query))
    important_terms = [
        "pmfby",
        "kcc",
        "kisan credit",
        "pacs",
        "e-nam",
        "enam",
        "soil health",
        "crop insurance",
        "interest",
        "premium",
        "loss",
        "damage",
        "bank",
        "loan",
        "membership",
        "soil",
        "testing",
        "mandi",
        "payment",
    ]

    number_terms = re.findall(r"\b\d+(?:\.\d+)?\b", query_lower)
    scored = []

    for item in index:
        text = str(item.get("text", ""))
        lower = text.lower()
        doc_tokens = set(_tokens(text))

        overlap = len(query_tokens & doc_tokens)

        phrase_bonus = 0
        for term in important_terms:
            if term in query_lower and term in lower:
                phrase_bonus += 5

        number_bonus = 0
        if number_terms:
            number_bonus = sum(2 for number in number_terms if number in lower)

        score = overlap + phrase_bonus + number_bonus

        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda pair: pair[0], reverse=True)

    top = [item for _, item in scored[:k]]
    best = scored[0][0] if scored else 0
    confidence = min(99, int(20 + best * 8)) if best else 0

    return top, confidence


def _dedupe_docs(*groups, limit=8):
    seen = set()
    docs = []

    for group in groups:
        for doc in group:
            key = (
                doc.get("source"),
                doc.get("page"),
                doc.get("text"),
            )

            if key not in seen:
                seen.add(key)
                docs.append(doc)

            if len(docs) >= limit:
                return docs

    return docs


def _source_label(docs):
    if not docs:
        return "No verified source found."

    labels = []

    for doc in docs[:4]:
        source = str(doc.get("source", "Unknown source"))
        page = doc.get("page")

        label = Path(source).name

        if page not in (None, ""):
            try:
                label += f" • page {int(page) + 1}"
            except Exception:
                label += f" • page {page}"

        if label not in labels:
            labels.append(label)

    return "; ".join(labels)



def _target_script_score(text, language_name):
    """Estimate whether an answer actually uses the selected language's script."""
    text = str(text or "")
    if not text:
        return 0.0

    ranges = {
        "Assamese (অসমীয়া)": [(0x0980, 0x09FF)],
        "Bengali (বাংলা)": [(0x0980, 0x09FF)],
        "Bodo (बर')": [(0x0900, 0x097F)],
        "Dogri (डोगरी)": [(0x0900, 0x097F)],
        "Hindi (हिंदी)": [(0x0900, 0x097F)],
        "Kashmiri (कॉशुर)": [(0x0900, 0x097F), (0x0600, 0x06FF)],
        "Konkani (कोंकणी)": [(0x0900, 0x097F)],
        "Maithili (मैथिली)": [(0x0900, 0x097F)],
        "Marathi (मराठी)": [(0x0900, 0x097F)],
        "Nepali (नेपाली)": [(0x0900, 0x097F)],
        "Sanskrit (संस्कृतम्)": [(0x0900, 0x097F)],
        "Sindhi (सिंधी)": [(0x0600, 0x06FF)],
        "Urdu (اردو)": [(0x0600, 0x06FF)],
        "Gujarati (ગુજરાતી)": [(0x0A80, 0x0AFF)],
        "Punjabi (ਪੰਜਾਬੀ)": [(0x0A00, 0x0A7F)],
        "Odia (ଓଡ଼ିଆ)": [(0x0B00, 0x0B7F)],
        "Tamil (தமிழ்)": [(0x0B80, 0x0BFF)],
        "Telugu (తెలుగు)": [(0x0C00, 0x0C7F)],
        "Kannada (ಕನ್ನಡ)": [(0x0C80, 0x0CFF)],
        "Malayalam (മലയാളം)": [(0x0D00, 0x0D7F)],
        "Manipuri (ꯃꯩꯇꯩꯂꯣꯟ)": [(0xABC0, 0xABFF)],
        "Santali (ᱥᱟᱱᱛᱟᱲᱤ)": [(0x1C50, 0x1C7F)],
    }

    if language_name == "English":
        return 1.0 if re.search(r"[A-Za-z]", text) else 0.0

    selected_ranges = ranges.get(language_name)
    if not selected_ranges:
        return 1.0

    letters = [ch for ch in text if ch.isalpha()]
    if not letters:
        return 0.0

    native = 0
    for ch in letters:
        code = ord(ch)
        if any(start <= code <= end for start, end in selected_ranges):
            native += 1

    return native / max(1, len(letters))


def _translate_answer_to_target(draft, question, language_name):
    """
    Repair a model response that came back in the wrong language.

    This is deliberately a second, conditional call: normal answers do not
    pay the extra latency. It is used when the script check shows that the
    selected-language text is missing or clearly insufficient.
    """
    client = get_groq_client()
    if not client:
        return draft

    language = LANG_MAPPING.get(
        language_name,
        (None, None, language_name),
    )[2]

    script_rules = {
        "Santali": "Write in Ol Chiki script (Unicode).",
        "Manipuri": "Write in Meitei Mayek script (Unicode).",
        "Urdu": "Write in Urdu script.",
        "Sindhi": "Write in Sindhi Arabic-derived script.",
        "Punjabi": "Write in Gurmukhi script.",
        "Assamese": "Write in Assamese script.",
        "Bengali": "Write in Bengali script.",
        "Hindi": "Write in Devanagari script.",
        "Marathi": "Write in Devanagari script.",
        "Nepali": "Write in Devanagari script.",
        "Bodo": "Write in Devanagari script.",
        "Dogri": "Write in Devanagari script.",
        "Konkani": "Write in Devanagari script.",
        "Maithili": "Write in Devanagari script.",
        "Sanskrit": "Write in Devanagari script.",
        "Gujarati": "Write in Gujarati script.",
        "Odia": "Write in Odia script.",
        "Tamil": "Write in Tamil script.",
        "Telugu": "Write in Telugu script.",
        "Kannada": "Write in Kannada script.",
        "Malayalam": "Write in Malayalam script.",
        "Kashmiri": "Write in the selected Kashmiri script; use Kashmiri/Devanagari text, not English.",
    }

    script_hint = script_rules.get(
        language,
        f"Use the normal native script of {language}.",
    )

    prompt = f"""
Rewrite the draft answer below in {language} for a farmer.

MANDATORY:
- Output ONLY the final answer.
- Do NOT answer in English, Hindi, or another language.
- {script_hint}
- Keep all facts, numbers, percentages, time periods and scheme names exactly accurate.
- Do not add facts that are not present in the draft.
- Keep it simple and natural for a farmer listening to it aloud.
- Scheme names such as KCC, PMFBY, PACS and e-NAM may remain in official form.

FARMER QUESTION:
{question}

DRAFT ANSWER:
{draft}
"""

    try:
        result = client.chat.completions.create(
            model=GROQ_CHAT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict multilingual agriculture-policy "
                        "answer translator. Never change policy facts."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=450,
        )
        repaired = normalize_query(result.choices[0].message.content)
        return repaired or draft
    except Exception as exc:
        print(f"Target-language answer repair warning: {exc}")
        return draft


def _answer_from_context(question, language_name, docs):
    client = get_groq_client()

    if not client:
        return (
            "Groq API key is missing. Add GROQ_API_KEY to your .env file "
            "or Streamlit secrets."
        )

    language = LANG_MAPPING.get(
        language_name,
        (None, None, language_name),
    )[2]

    script_rules = {
        "Santali": "Use Ol Chiki script when possible.",
        "Manipuri": "Use Meitei Mayek when possible.",
        "Kashmiri": "Use the normal Kashmiri script appropriate for the selected language.",
        "Urdu": "Use Urdu script.",
        "Punjabi": "Use Gurmukhi script.",
        "Sindhi": "Use Sindhi script.",
    }

    script_hint = script_rules.get(
        language,
        f"Use the normal native script of {language}.",
    )

    context_parts = []

    for index, doc in enumerate(docs, 1):
        context_parts.append(
            f"SOURCE {index} — {doc.get('source', 'Unknown source')}\n"
            f"{doc.get('text', '')}"
        )

    context = "\n\n".join(context_parts)

    system = f"""
You are Sahakar-Vaani, a multilingual agriculture policy assistant.

Answer the farmer's exact question using ONLY the supplied policy excerpts.

TARGET LANGUAGE: {language}
SCRIPT REQUIREMENT: {script_hint}

STRICT RULES:
1. The final answer must be in {language}.
2. Do not switch the answer to Hindi or English.
3. Do not invent facts, rates, deadlines, eligibility, penalties or benefits.
4. If the supplied excerpts do not contain the requested fact, clearly say that the verified policy documents do not provide enough information.
5. Preserve every number and time period accurately.
6. Keep the answer simple and suitable for a farmer listening to it aloud.
7. Prefer 2-5 short sentences or bullets.
8. Scheme names such as KCC, PMFBY, PACS and e-NAM may remain in their official form when that is clearer.
9. Do not mention prompts, vector databases, embeddings, retrieval or internal system details.
"""

    user = (
        f"FARMER QUESTION:\n{question}\n\n"
        f"VERIFIED POLICY EXCERPTS:\n{context}"
    )

    try:
        result = client.chat.completions.create(
            model=GROQ_CHAT_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0,
            max_tokens=400,
        )

        answer = normalize_query(result.choices[0].message.content)

        if not answer:
            return NO_MATCH.get(
                language_name,
                NO_MATCH["English"],
            )

        # The main prompt normally produces the requested language. For
        # languages with a distinct native script, verify the actual output
        # before showing it. If the model accidentally replies in English or
        # another Indian language, repair it with one targeted translation
        # call instead of allowing the wrong-language answer through.
        score = _target_script_score(answer, language_name)
        if language_name != "English" and score < 0.18:
            repaired = _translate_answer_to_target(
                answer,
                question,
                language_name,
            )
            if repaired:
                answer = repaired

        return answer

    except Exception as exc:
        return f"AI answer generation failed: {exc}"


def answer_farmer_query(query, language_name="Hindi (हिंदी)", fast_mode=False):
    start = time.time()
    query = normalize_query(query)

    if not query:
        return (
            NO_MATCH.get(language_name, NO_MATCH["English"]),
            "No verified source found.",
            [],
            0,
            0,
        )

    # Start with a completely local retrieval pass. This is especially useful
    # for voice input because it avoids an extra Groq "translate the query"
    # round-trip for common KCC/PMFBY/PACS/e-NAM/soil questions.
    canonical_faq_queries = {
        normalize_query(item["question"])
        for item in FAQS
    }
    local_query = clean_and_normalize_query(query)

    if query in canonical_faq_queries:
        search_query = local_query
        semantic_1, sem_conf_1 = _semantic_retrieve(search_query, k=8)
        semantic_2, sem_conf_2 = [], 0.0
        keyword_1, key_conf_1 = _keyword_retrieve(search_query, k=8)
        keyword_2, key_conf_2 = [], 0.0
    else:
        semantic_1, sem_conf_1 = _semantic_retrieve(local_query, k=8)
        keyword_1, key_conf_1 = _keyword_retrieve(local_query, k=8)
        semantic_2, sem_conf_2 = [], 0.0
        keyword_2, key_conf_2 = [], 0.0

        local_docs = _dedupe_docs(
            semantic_1,
            keyword_1,
            limit=8,
        )

        # If the local pass did not find enough evidence, use the existing
        # multilingual Groq query translation as a fallback. Normal voice
        # questions therefore get the fast path whenever possible, while
        # difficult regional-language questions retain the accurate path.
        needs_translation = not local_docs or (
            (not fast_mode) and max(sem_conf_1, key_conf_1) < 35
        )

        if needs_translation:
            translated_query = _translate_for_retrieval(
                query,
                language_name,
            )

            if translated_query and translated_query != local_query:
                semantic_2, sem_conf_2 = _semantic_retrieve(
                    translated_query,
                    k=8,
                )
                keyword_2, key_conf_2 = _keyword_retrieve(
                    translated_query,
                    k=8,
                )

    docs = _dedupe_docs(
        semantic_1,
        semantic_2,
        keyword_1,
        keyword_2,
        limit=8,
    )

    confidence = max(
        sem_conf_1,
        sem_conf_2,
        key_conf_1,
        key_conf_2,
    )

    has_evidence = bool(docs)

    if not has_evidence:
        latency = int((time.time() - start) * 1000)
        return (
            NO_MATCH.get(language_name, NO_MATCH["English"]),
            "No verified source found.",
            [],
            0,
            latency,
        )

    answer = _answer_from_context(
        query,
        language_name,
        docs,
    )

    latency = int((time.time() - start) * 1000)

    return (
        answer,
        _source_label(docs),
        docs,
        confidence,
        latency,
    )


def transcribe_audio(audio_bytes, language_name="Hindi (हिंदी)"):
    """
    Transcribe the actual browser recording.

    Streamlit st.audio_input normally returns WebM/Opus browser audio.
    The previous implementation forced a .wav suffix, which could cause
    Groq to receive a file whose extension did not match its real container.
    """
    client = get_groq_client()

    if not client:
        return (
            "Transcription Error: GROQ_API_KEY is missing. "
            "Check your .env file."
        )

    if not audio_bytes:
        return "Transcription Error: No audio was recorded."

    whisper_code, _, language = LANG_MAPPING.get(
        language_name,
        ("hi", "hi-IN", "Hindi"),
    )

    # Groq accepts webm directly. For languages without ISO-639-1 codes,
    # omit language and guide Whisper with a prompt.
    suffix = ".webm"

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    ) as audio_file:
        audio_file.write(audio_bytes)
        audio_path = audio_file.name

    try:
        with open(audio_path, "rb") as file:
            payload = {
                "file": (
                    os.path.basename(audio_path),
                    file.read(),
                ),
                "model": WHISPER_MODEL,
                "response_format": "json",
                "temperature": 0.0,
                "prompt": (
                    f"This is a farmer speaking in {language}. "
                    "Agriculture terms may include KCC, PMFBY, PACS, "
                    "Soil Health Card and e-NAM."
                ),
            }

            if whisper_code:
                payload["language"] = whisper_code

            result = client.audio.transcriptions.create(**payload)

        text = normalize_query(result.text)

        if len(text) < 2:
            return (
                "Transcription Error: No meaningful speech was detected."
            )

        return text

    except Exception as exc:
        return f"Transcription Error: {exc}"

    finally:
        try:
            os.remove(audio_path)
        except OSError:
            pass


def generate_ai4bharat_voice(
    text,
    language_name="Hindi (हिंदी)",
    slow=False,
):
    """
    Generate answer audio without silently changing the selected language.

    The order is intentionally:
      1. gTTS for the languages it explicitly supports.
      2. AI4Bharat Indic Parler-TTS for the broader Indic set when a
         Hugging Face token is available.
      3. Return an empty path so kiosk_app.py can use browser speech as the
         final fallback.
    """
    text = normalize_query(text)

    if not text:
        return ""

    if text.startswith(("AI answer generation failed:", "Transcription Error:")):
        return ""

    # gTTS is a simple, stable fallback for the most common kiosk languages.
    # It is attempted first because it returns a directly playable MP3 and
    # does not depend on the Hugging Face inference API being available.
    gtts_codes = {
        "English": "en",
        "Bengali (বাংলা)": "bn",
        "Gujarati (ગુજરાતી)": "gu",
        "Hindi (हिंदी)": "hi",
        "Kannada (ಕನ್ನಡ)": "kn",
        "Malayalam (മലയാളം)": "ml",
        "Marathi (मराठी)": "mr",
        "Nepali (नेपाली)": "ne",
        "Odia (ଓଡ଼ିଆ)": "or",
        "Punjabi (ਪੰਜਾਬੀ)": "pa",
        "Tamil (தமிழ்)": "ta",
        "Telugu (తెలుగు)": "te",
        "Urdu (اردو)": "ur",
    }

    gtts_code = gtts_codes.get(language_name)

    if gtts_code:
        try:
            output = BASE_DIR / "response.mp3"
            tts = gTTS(
                text=text,
                lang=gtts_code,
                slow=slow,
            )
            tts.save(str(output))
            if output.exists() and output.stat().st_size > 1000:
                return str(output)
        except Exception as exc:
            print(f"gTTS warning for {language_name}: {exc}")

    # AI4Bharat covers a wider Indic language set than gTTS. Use it when a
    # Hugging Face token is configured, but never pretend success if the
    # endpoint does not return actual audio bytes.
    token = get_hf_token()

    if token:
        try:
            url = (
                "https://api-inference.huggingface.co/models/"
                "ai4bharat/indic-parler-tts"
            )

            headers = {
                "Authorization": f"Bearer {token}",
            }

            language_label = LANG_MAPPING.get(
                language_name,
                ("", "", language_name),
            )[2]

            payload = {
                "inputs": text,
                "parameters": {
                    "description": (
                        f"Clear, natural agricultural speech in {language_label}."
                    )
                },
            }

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=45,
            )

            if response.ok and len(response.content) > 1000:
                content_type = response.headers.get("content-type", "").lower()

                if (
                    "audio" in content_type
                    or response.content[:4] == b"RIFF"
                    or response.content[:3] == b"ID3"
                ):
                    extension = (
                        ".wav"
                        if response.content[:4] == b"RIFF"
                        else ".mp3"
                    )
                    output = BASE_DIR / f"response{extension}"
                    output.write_bytes(response.content)
                    return str(output)

        except Exception as exc:
            print(f"AI4Bharat TTS warning: {exc}")

    # Empty string tells the UI to use browser speech. That path supports the
    # selected locale when the browser/OS has a matching voice installed.
    return ""


def get_browser_language_code(language_name):
    return LANG_MAPPING.get(
        language_name,
        ("en", "en-IN", "English"),
    )[1]


def is_internet_available():
    try:
        requests.get(
            "https://www.google.com",
            timeout=3,
        )
        return True
    except Exception:
        return False


def check_audio_amplitude(audio_bytes):
    if not audio_bytes:
        return 0.0
    return min(
        1.0,
        len(audio_bytes) / 100000.0,
    )


# Stable FAQ intents. The UI translates their labels; the backend always
# searches the same canonical policy question so a click produces an answer
# immediately and consistently.
FAQS = [
    {
        "id": "kcc",
        "emoji": "💳",
        "question": "What is the Kisan Credit Card (KCC) and what are its main interest-subvention rules?",
    },
    {
        "id": "kcc_eligibility",
        "emoji": "👨‍🌾",
        "question": "Who is eligible for the Kisan Credit Card?",
    },
    {
        "id": "kcc_collateral",
        "emoji": "🏦",
        "question": "What is the collateral waiver limit for KCC agricultural credit?",
    },
    {
        "id": "pmfby",
        "emoji": "🌾",
        "question": "What are the farmer premium rates under PMFBY?",
    },
    {
        "id": "pmfby_loss",
        "emoji": "⏱️",
        "question": "Within how many hours must an individual localized crop loss be reported under PMFBY?",
    },
    {
        "id": "pmfby_postharvest",
        "emoji": "🌧️",
        "question": "How long are eligible post-harvest losses covered under PMFBY?",
    },
    {
        "id": "pacs",
        "emoji": "🏢",
        "question": "Who can become an A-class member of a PACS?",
    },
    {
        "id": "pacs_credit",
        "emoji": "🐄",
        "question": "What allied activities can PACS finance as non-agricultural credit?",
    },
    {
        "id": "soil",
        "emoji": "🧪",
        "question": "What does the Soil Health Card scheme provide to farmers?",
    },
    {
        "id": "soil_cycle",
        "emoji": "🔬",
        "question": "How often are soil samples collected under the Soil Health Card scheme?",
    },
    {
        "id": "enam",
        "emoji": "🛒",
        "question": "How are sale proceeds transferred to a farmer after an e-NAM trade?",
    },
    {
        "id": "enam_testing",
        "emoji": "📊",
        "question": "What quality testing is available for produce in e-NAM mandis?",
    },
]


# Short, farmer-friendly FAQ labels.  These are UI labels only;
# the backend continues to use the canonical English FAQ question for retrieval.
FAQ_LABELS = {
    "English": [
        "What is KCC and its main interest rules?",
        "Who is eligible for KCC?",
        "What is the KCC collateral waiver limit?",
        "What are PMFBY farmer premium rates?",
        "When must PMFBY crop loss be reported?",
        "How long are PMFBY post-harvest losses covered?",
        "Who can become an A-class PACS member?",
        "What allied activities can PACS finance?",
        "What does the Soil Health Card provide?",
        "How often are soil samples collected?",
        "How are e-NAM sale proceeds paid to farmers?",
        "What quality testing is available in e-NAM?",
    ],
    "Hindi (हिंदी)": [
        "KCC क्या है और इसकी ब्याज नियम क्या हैं?",
        "KCC के लिए कौन पात्र है?",
        "KCC कृषि ऋण में बिना जमानत की सीमा क्या है?",
        "PMFBY में किसान प्रीमियम दरें क्या हैं?",
        "PMFBY में फसल नुकसान कब तक बताना होता है?",
        "PMFBY में कटाई के बाद का नुकसान कितने समय तक कवर है?",
        "PACS का A-वर्ग सदस्य कौन बन सकता है?",
        "PACS किन संबद्ध गतिविधियों के लिए ऋण दे सकता है?",
        "मृदा स्वास्थ्य कार्ड किसानों को क्या देता है?",
        "मिट्टी के नमूने कितनी बार लिए जाते हैं?",
        "e-NAM की बिक्री राशि किसान को कैसे मिलती है?",
        "e-NAM में उपज की कौन-सी गुणवत्ता जांच होती है?",
    ],
    "Marathi (मराठी)": [
        "KCC काय आहे आणि त्याचे व्याज नियम काय आहेत?",
        "KCC साठी कोण पात्र आहे?",
        "KCC कृषी कर्जासाठी तारणमुक्त मर्यादा किती आहे?",
        "PMFBY मधील शेतकरी प्रीमियम दर काय आहेत?",
        "PMFBY मध्ये पीक नुकसान कधी कळवावे?",
        "PMFBY मध्ये काढणीनंतरचे नुकसान किती काळ भरपाईत येते?",
        "PACS चा A-वर्ग सदस्य कोण होऊ शकतो?",
        "PACS कोणत्या पूरक कामांसाठी कर्ज देऊ शकते?",
        "मृदा आरोग्य कार्ड शेतकऱ्यांना काय देते?",
        "मातीचे नमुने किती वेळा घेतले जातात?",
        "e-NAM मधील विक्रीची रक्कम शेतकऱ्याला कशी मिळते?",
        "e-NAM मध्ये मालाची कोणती गुणवत्ता तपासणी होते?",
    ],
    "Bengali (বাংলা)": [
        "KCC কী এবং এর সুদের নিয়ম কী?",
        "কারা KCC পাওয়ার যোগ্য?",
        "KCC কৃষি ঋণে জামানত ছাড়ের সীমা কত?",
        "PMFBY-তে কৃষকের প্রিমিয়াম হার কত?",
        "PMFBY-তে ফসলের ক্ষতি কখন জানাতে হয়?",
        "PMFBY-তে ফসল কাটার পরের ক্ষতি কতদিন কভার হয়?",
        "PACS-এর A-শ্রেণির সদস্য কে হতে পারেন?",
        "PACS কোন সহযোগী কাজের জন্য ঋণ দিতে পারে?",
        "মাটি স্বাস্থ্য কার্ড কৃষকদের কী দেয়?",
        "মাটির নমুনা কত ঘন ঘন নেওয়া হয়?",
        "e-NAM বিক্রির টাকা কৃষককে কীভাবে দেওয়া হয়?",
        "e-NAM-এ পণ্যের কী গুণমান পরীক্ষা হয়?",
    ],
    "Gujarati (ગુજરાતી)": [
        "KCC શું છે અને તેના વ્યાજના નિયમો શું છે?",
        "KCC માટે કોણ પાત્ર છે?",
        "KCC કૃષિ ધિરાણમાં જામીનમુક્તિની મર્યાદા કેટલી છે?",
        "PMFBYમાં ખેડૂત પ્રીમિયમ દર કેટલા છે?",
        "PMFBYમાં પાકનું નુકસાન ક્યારે જણાવવું પડે?",
        "PMFBYમાં લણણી પછીનું નુકસાન કેટલા સમય સુધી આવરી લેવાય છે?",
        "PACSનો A-વર્ગ સભ્ય કોણ બની શકે?",
        "PACS કઈ સહાયક પ્રવૃત્તિઓ માટે ધિરાણ આપી શકે?",
        "માટી આરોગ્ય કાર્ડ ખેડૂતને શું આપે છે?",
        "માટીના નમૂના કેટલી વાર લેવામાં આવે છે?",
        "e-NAMની વેચાણ રકમ ખેડૂતને કેવી રીતે મળે છે?",
        "e-NAMમાં ઉપજની કઈ ગુણવત્તા ચકાસણી થાય છે?",
    ],
    "Assamese (অসমীয়া)": [
        "KCC কি আৰু ইয়াৰ সুদৰ নিয়ম কি?",
        "KCC পাবলৈ কোন যোগ্য?",
        "KCC কৃষি ঋণত জামিনমুক্ত সীমা কিমান?",
        "PMFBY-ত কৃষকৰ প্ৰিমিয়াম হাৰ কিমান?",
        "PMFBY-ত শস্যৰ ক্ষতি কেতিয়া জনাব লাগে?",
        "PMFBY-ত চপোৱাৰ পিছৰ ক্ষতি কিমান দিন আৱৃত?",
        "PACS-ৰ A-শ্ৰেণীৰ সদস্য কোন হ'ব পাৰে?",
        "PACS-এ কোনবোৰ আনুষংগিক কামৰ বাবে ঋণ দিব পাৰে?",
        "মাটি স্বাস্থ্য কাৰ্ডে কৃষকক কি দিয়ে?",
        "মাটিৰ নমুনা কিমান সঘনাই লোৱা হয়?",
        "e-NAM-ৰ বিক্ৰী ধন কৃষকক কেনেকৈ দিয়া হয়?",
        "e-NAM-ত উৎপাদনৰ কি গুণমান পৰীক্ষা হয়?",
    ],
    "Kannada (ಕನ್ನಡ)": [
        "KCC ಎಂದರೇನು ಮತ್ತು ಅದರ ಬಡ್ಡಿ ನಿಯಮಗಳು ಯಾವುವು?",
        "KCCಗೆ ಯಾರು ಅರ್ಹರು?",
        "KCC ಕೃಷಿ ಸಾಲದ ಜಾಮೀನು ವಿನಾಯಿತಿ ಮಿತಿ ಎಷ್ಟು?",
        "PMFBY ರೈತ ಪ್ರೀಮಿಯಂ ದರಗಳು ಯಾವುವು?",
        "PMFBYಯಲ್ಲಿ ಬೆಳೆ ನಷ್ಟವನ್ನು ಯಾವಾಗ ತಿಳಿಸಬೇಕು?",
        "PMFBYಯಲ್ಲಿ ಕೊಯ್ಲಿನ ನಂತರದ ನಷ್ಟ ಎಷ್ಟು ಕಾಲ ಒಳಗೊಂಡಿದೆ?",
        "PACSನ A-ವರ್ಗದ ಸದಸ್ಯರಾಗಲು ಯಾರು ಅರ್ಹರು?",
        "PACS ಯಾವ ಪೂರಕ ಚಟುವಟಿಕೆಗಳಿಗೆ ಸಾಲ ನೀಡಬಹುದು?",
        "ಮಣ್ಣು ಆರೋಗ್ಯ ಕಾರ್ಡ್ ರೈತರಿಗೆ ಏನು ನೀಡುತ್ತದೆ?",
        "ಮಣ್ಣಿನ ಮಾದರಿಗಳನ್ನು ಎಷ್ಟು ಬಾರಿ ಸಂಗ್ರಹಿಸಲಾಗುತ್ತದೆ?",
        "e-NAM ಮಾರಾಟದ ಹಣ ರೈತರಿಗೆ ಹೇಗೆ ಸಿಗುತ್ತದೆ?",
        "e-NAMನಲ್ಲಿ ಉತ್ಪನ್ನದ ಯಾವ ಗುಣಮಟ್ಟ ಪರೀಕ್ಷೆ ಇದೆ?",
    ],
    "Malayalam (മലയാളം)": [
        "KCC എന്താണ്, അതിന്റെ പലിശ നിയമങ്ങൾ എന്തൊക്കെയാണ്?",
        "KCCയ്ക്ക് ആരാണ് അർഹർ?",
        "KCC കാർഷിക വായ്പയിലെ ഈടില്ലാ പരിധി എത്ര?",
        "PMFBYയിലെ കർഷക പ്രീമിയം നിരക്കുകൾ എന്തൊക്കെയാണ്?",
        "PMFBYയിൽ വിളനാശം എപ്പോൾ അറിയിക്കണം?",
        "PMFBYയിൽ വിളവെടുപ്പിന് ശേഷമുള്ള നഷ്ടം എത്രകാലം പരിരക്ഷിക്കും?",
        "PACS-ലെ A-ക്ലാസ് അംഗമാകാൻ ആര്‍ക്ക് കഴിയും?",
        "PACS ഏത് അനുബന്ധ പ്രവർത്തനങ്ങൾക്ക് വായ്പ നൽകാം?",
        "മണ്ണ് ആരോഗ്യ കാർഡ് കർഷകർക്ക് എന്ത് നൽകുന്നു?",
        "മണ്ണിന്റെ സാമ്പിളുകൾ എത്ര ഇടവേളയിൽ എടുക്കുന്നു?",
        "e-NAM വിൽപ്പന തുക കർഷകന് എങ്ങനെ ലഭിക്കും?",
        "e-NAMൽ ഉൽപ്പന്നത്തിന്റെ ഏത് ഗുണനിലവാര പരിശോധനയുണ്ട്?",
    ],
    "Tamil (தமிழ்)": [
        "KCC என்றால் என்ன? அதன் வட்டி விதிகள் என்ன?",
        "KCC பெற யார் தகுதியானவர்?",
        "KCC விவசாயக் கடனுக்கான பிணையமில்லா வரம்பு என்ன?",
        "PMFBY விவசாயி பிரீமியம் விகிதங்கள் என்ன?",
        "PMFBY-யில் பயிர் இழப்பை எப்போது தெரிவிக்க வேண்டும்?",
        "PMFBY-யில் அறுவடைக்குப் பிந்தைய இழப்பு எவ்வளவு காலம் பாதுகாக்கப்படுகிறது?",
        "PACS A-வகுப்பு உறுப்பினராக யார் ஆகலாம்?",
        "PACS எந்த இணை நடவடிக்கைகளுக்கு கடன் வழங்கலாம்?",
        "மண் சுகாதார அட்டை விவசாயிகளுக்கு என்ன வழங்குகிறது?",
        "மண் மாதிரிகள் எவ்வளவு அடிக்கடி சேகரிக்கப்படுகின்றன?",
        "e-NAM விற்பனைத் தொகை விவசாயிக்கு எப்படி வழங்கப்படுகிறது?",
        "e-NAM-ல் விளைபொருளுக்கு என்ன தரப் பரிசோதனை உள்ளது?",
    ],
    "Telugu (తెలుగు)": [
        "KCC అంటే ఏమిటి? దాని వడ్డీ నియమాలు ఏమిటి?",
        "KCCకి ఎవరు అర్హులు?",
        "KCC వ్యవసాయ రుణానికి తాకట్టు మినహాయింపు పరిమితి ఎంత?",
        "PMFBY రైతు ప్రీమియం రేట్లు ఏమిటి?",
        "PMFBYలో పంట నష్టాన్ని ఎప్పుడు తెలియజేయాలి?",
        "PMFBYలో కోత తర్వాత నష్టం ఎంతకాలం కవరవుతుంది?",
        "PACS A-తరగతి సభ్యుడు ఎవరు కావచ్చు?",
        "PACS ఏ అనుబంధ కార్యకలాపాలకు రుణం ఇవ్వగలదు?",
        "మట్టి ఆరోగ్య కార్డు రైతులకు ఏమి అందిస్తుంది?",
        "మట్టి నమూనాలు ఎంత తరచుగా సేకరిస్తారు?",
        "e-NAM అమ్మకాల డబ్బు రైతుకు ఎలా అందుతుంది?",
        "e-NAMలో ఉత్పత్తికి ఏ నాణ్యత పరీక్ష ఉంటుంది?",
    ],
    "Odia (ଓଡ଼ିଆ)": [
        "KCC କ’ଣ ଏବଂ ଏହାର ସୁଧ ନିୟମ କ’ଣ?",
        "KCC ପାଇଁ କିଏ ଯୋଗ୍ୟ?",
        "KCC କୃଷି ଋଣରେ ଜମାନତ ଛାଡ଼ ସୀମା କେତେ?",
        "PMFBYରେ କୃଷକ ପ୍ରିମିୟମ ହାର କେତେ?",
        "PMFBYରେ ଫସଲ କ୍ଷତି କେବେ ଜଣାଇବାକୁ ପଡ଼େ?",
        "PMFBYରେ ଅମଳ ପରବର୍ତ୍ତୀ କ୍ଷତି କେତେଦିନ ଆବୃତ?",
        "PACSର A-ଶ୍ରେଣୀ ସଦସ୍ୟ କିଏ ହୋଇପାରିବେ?",
        "PACS କେଉଁ ସହାୟକ କାର୍ଯ୍ୟକଳାପକୁ ଋଣ ଦେଇପାରେ?",
        "ମୃତ୍ତିକା ସ୍ୱାସ୍ଥ୍ୟ କାର୍ଡ କୃଷକଙ୍କୁ କ’ଣ ଦିଏ?",
        "ମାଟି ନମୁନା କେତେଥର ସଂଗ୍ରହ କରାଯାଏ?",
        "e-NAM ବିକ୍ରୟ ଟଙ୍କା କୃଷକଙ୍କୁ କିପରି ମିଳେ?",
        "e-NAMରେ ଉତ୍ପାଦର କେଉଁ ଗୁଣବତ୍ତା ପରୀକ୍ଷା ହୁଏ?",
    ],
    "Punjabi (ਪੰਜਾਬੀ)": [
        "KCC ਕੀ ਹੈ ਅਤੇ ਇਸ ਦੇ ਵਿਆਜ ਨਿਯਮ ਕੀ ਹਨ?",
        "KCC ਲਈ ਕੌਣ ਯੋਗ ਹੈ?",
        "KCC ਖੇਤੀ ਕਰਜ਼ੇ ਲਈ ਜਮਾਨਤ-ਮੁਕਤ ਹੱਦ ਕੀ ਹੈ?",
        "PMFBY ਵਿੱਚ ਕਿਸਾਨ ਪ੍ਰੀਮੀਅਮ ਦਰਾਂ ਕੀ ਹਨ?",
        "PMFBY ਵਿੱਚ ਫਸਲ ਨੁਕਸਾਨ ਕਦੋਂ ਦੱਸਣਾ ਹੈ?",
        "PMFBY ਵਿੱਚ ਕਟਾਈ ਤੋਂ ਬਾਅਦ ਦਾ ਨੁਕਸਾਨ ਕਿੰਨੇ ਸਮੇਂ ਲਈ ਕਵਰ ਹੈ?",
        "PACS ਦਾ A-ਸ਼੍ਰੇਣੀ ਮੈਂਬਰ ਕੌਣ ਬਣ ਸਕਦਾ ਹੈ?",
        "PACS ਕਿਹੜੀਆਂ ਸਹਾਇਕ ਗਤੀਵਿਧੀਆਂ ਲਈ ਕਰਜ਼ਾ ਦੇ ਸਕਦੀ ਹੈ?",
        "ਮਿੱਟੀ ਸਿਹਤ ਕਾਰਡ ਕਿਸਾਨਾਂ ਨੂੰ ਕੀ ਦਿੰਦਾ ਹੈ?",
        "ਮਿੱਟੀ ਦੇ ਨਮੂਨੇ ਕਿੰਨੀ ਵਾਰ ਲਏ ਜਾਂਦੇ ਹਨ?",
        "e-NAM ਦੀ ਵਿਕਰੀ ਰਕਮ ਕਿਸਾਨ ਨੂੰ ਕਿਵੇਂ ਮਿਲਦੀ ਹੈ?",
        "e-NAM ਵਿੱਚ ਉਤਪਾਦ ਦੀ ਕਿਹੜੀ ਗੁਣਵੱਤਾ ਜਾਂਚ ਹੁੰਦੀ ਹੈ?",
    ],
    "Urdu (اردو)": [
        "KCC کیا ہے اور اس کے سود کے اصول کیا ہیں؟",
        "KCC کے لیے کون اہل ہے؟",
        "KCC زرعی قرض میں ضمانت سے استثنا کی حد کیا ہے؟",
        "PMFBY میں کسان پریمیم کی شرحیں کیا ہیں؟",
        "PMFBY میں فصل کے نقصان کی اطلاع کب دینی ہے؟",
        "PMFBY میں کٹائی کے بعد کا نقصان کتنے عرصے تک شامل ہے؟",
        "PACS کا A-درجہ رکن کون بن سکتا ہے؟",
        "PACS کن متعلقہ سرگرمیوں کے لیے قرض دے سکتی ہے؟",
        "مٹی صحت کارڈ کسانوں کو کیا فراہم کرتا ہے؟",
        "مٹی کے نمونے کتنی بار لیے جاتے ہیں؟",
        "e-NAM کی فروخت کی رقم کسان کو کیسے ملتی ہے؟",
        "e-NAM میں پیداوار کی کون سی معیار جانچ ہوتی ہے؟",
    ],
    "Nepali (नेपाली)": [
        "KCC के हो र यसको ब्याज नियम के हुन्?",
        "KCC का लागि को योग्य छन्?",
        "KCC कृषि ऋणमा धितो छुटको सीमा कति हो?",
        "PMFBY मा किसान प्रिमियम दर कति छन्?",
        "PMFBY मा बाली क्षति कहिले जानकारी गराउने?",
        "PMFBY मा कटानीपछिको क्षति कति समय समेटिन्छ?",
        "PACS को A-वर्ग सदस्य को बन्न सक्छ?",
        "PACS ले कुन सहायक गतिविधिका लागि ऋण दिन सक्छ?",
        "माटो स्वास्थ्य कार्डले किसानलाई के दिन्छ?",
        "माटोका नमुना कति पटक लिइन्छ?",
        "e-NAM बिक्री रकम किसानलाई कसरी दिइन्छ?",
        "e-NAM मा उत्पादनको कुन गुणस्तर परीक्षण हुन्छ?",
    ],
    "Sanskrit (संस्कृतम्)": [
        "KCC किम् अस्ति तथा तस्य ब्याजनियमाः के?",
        "KCC प्राप्तुं के योग्याः?",
        "KCC कृषिऋणे बन्धकरहितसीमा कियती?",
        "PMFBY मध्ये कृषकस्य प्रीमियम-दराः काः?",
        "PMFBY मध्ये फसलक्षतिः कदा निवेदनीया?",
        "PMFBY मध्ये कटनोत्तरक्षतिः कियत्कालं संरक्षिता?",
        "PACS मध्ये A-श्रेणी-सदस्यः कः भवितुम् अर्हति?",
        "PACS केषां सहायकक्रियाणां कृते ऋणं दातुं शक्नोति?",
        "मृदास्वास्थ्यपत्रं कृषकेभ्यः किं ददाति?",
        "मृदानमूनानि कियत्सु कालेषु गृह्यन्ते?",
        "e-NAM विक्रयधनं कृषकाय कथं दीयते?",
        "e-NAM मध्ये उत्पादस्य का गुणवत्तापरीक्षा भवति?",
    ],
    "Sindhi (सिंधी)": [
        "KCC ڇا آهي ۽ ان جا وياج جا اصول ڪهڙا آهن؟",
        "KCC لاءِ ڪير اهل آهي؟",
        "KCC زرعي قرض ۾ ضمانت کان ڇوٽ جي حد ڪيتري آهي؟",
        "PMFBY ۾ هاري جي پريميئم شرح ڪيتري آهي؟",
        "PMFBY ۾ فصل جي نقصان جي خبر ڪڏهن ڏيڻي آهي؟",
        "PMFBY ۾ لاباري کان پوءِ نقصان ڪيتري وقت تائين شامل آهي؟",
        "PACS جو A-درجو ميمبر ڪير ٿي سگهي ٿو؟",
        "PACS ڪهڙين لاڳاپيل سرگرمين لاءِ قرض ڏئي سگهي ٿي؟",
        "مٽي جي صحت وارو ڪارڊ هارين کي ڇا ڏئي ٿو؟",
        "مٽي جا نمونا ڪيتري وقفي سان ورتا وڃن ٿا؟",
        "e-NAM جي وڪري جي رقم هاري کي ڪيئن ملي ٿي؟",
        "e-NAM ۾ پيداوار جي ڪهڙي معيار جاچ ٿئي ٿي؟",
    ],
    "Konkani (कोंकणी)": [
        "KCC कितें आसा आनी ताचे व्याजाचे नियम कितले?",
        "KCC खातीर कोण पात्र आसा?",
        "KCC शेती कर्जाची तारणमुक्त मर्यादा कितली?",
        "PMFBY शेतकार प्रीमियम दर कितले?",
        "PMFBY त पीक नुकसाण केन्ना कळोवपाचें?",
        "PMFBY त कापणी उपरांतलें नुकसाण कितले काळ कव्हर जाता?",
        "PACS चो A-वर्ग सभासद कोण जावंक शकता?",
        "PACS कोणत्या पूरक कामां खातीर कर्ज दिवंक शकता?",
        "माती आरोग्य कार्ड शेतकारांक कितें दिता?",
        "मातीचे नमुने कितल्या वेळान घेतले जाता?",
        "e-NAM विक्रीची रक्कम शेतकाराक कशी मेळटा?",
        "e-NAM त मालाची खंयची गुणवत्ता तपासणी जाता?",
    ],
    "Maithili (मैथिली)": [
        "KCC की अछि आ एकर ब्याज नियम की अछि?",
        "KCC लेल के पात्र छथि?",
        "KCC कृषि ऋणमे बिना जमानत सीमा कतेक अछि?",
        "PMFBY मे किसान प्रीमियम दर की अछि?",
        "PMFBY मे फसल क्षति केखन बताबय पड़ैत अछि?",
        "PMFBY मे कटनीक बादक क्षति कतेक समय धरि कवर अछि?",
        "PACS केर A-श्रेणी सदस्य के बनि सकैत छथि?",
        "PACS कोन सहायक गतिविधिक लेल ऋण द' सकैत अछि?",
        "माटिक स्वास्थ्य कार्ड किसानकेँ की दैत अछि?",
        "माटिक नमूना कतेक बेर लेल जाइत अछि?",
        "e-NAM बिक्रीक राशि किसानकेँ कोना भेटैत अछि?",
        "e-NAM मे उपजक कोन गुणवत्ता जाँच होइत अछि?",
    ],
    "Dogri (डोगरी)": [
        "KCC के ऐ ते इसदे ब्याज दे नियम केह् न?",
        "KCC लेई कौन योग्य ऐ?",
        "KCC खेती कर्जे दी जमानत-रहित हद केह् ऐ?",
        "PMFBY च किसान प्रीमियम दरां केह् न?",
        "PMFBY च फसल दा नुकसान कदूं दस्सना ऐ?",
        "PMFBY च कटाई बाद दा नुकसान किन्ने चिरै तक कवर ऐ?",
        "PACS दा A-श्रेणी सदस्य कौन बनी सकदा ऐ?",
        "PACS केह्ड़ियां सहायक गतिविधियां लेई कर्ज देई सकदी ऐ?",
        "मिट्टी सेहत कार्ड किसानें गी केह् दिंदा ऐ?",
        "मिट्टी दे नमूने किन्ने बार लैते जंदे न?",
        "e-NAM दी बिक्री रकम किसानें गी किस चाल्ली मिलदी ऐ?",
        "e-NAM च उपज दी केह्ड़ी गुणवत्ता जांच ऐ?",
    ],
    "Kashmiri (कॉशुर)": [
        "KCC کیاہ چھُ تۄنٛدۍ سودس قاعدٕ کیاہ چھِ؟",
        "KCC خٲطرٕ کَس چھُ اہل؟",
        "KCC زرعی قرضس منز ضمانت بغیر حد کتھ چھِ؟",
        "PMFBY منز کسان پریمیم ریٹ کیاہ چھِ؟",
        "PMFBY منز فصل نقصان کتھ کُن اطلاع دینی چھِ؟",
        "PMFBY منز کٹائی پَتہ نقصان کتھ وقت تام شامل چھُ؟",
        "PACS ہُنٛد A-درجہ ممبر کَس بَنِتھ ہیکہ؟",
        "PACS کِن متعلقہ کمَن خٲطرٕ قرض دِتھ ہیکہ؟",
        "مٹی صحت کارڈ کسانن کیٛاہ دِوان چھُ؟",
        "مٹی نمونہ کتھ وار لیوان چھِ؟",
        "e-NAM فروخت رقم کسانس کتھ دِوان چھِ؟",
        "e-NAM منز پیداوار ہُنٛد کُن معیار ٹیسٹ چھُ؟",
    ],
    "Manipuri (ꯃꯩꯇꯩꯂꯣꯟ)": [
        "KCC ꯀꯔꯤꯅꯣ ꯑꯃꯁꯨꯡ ꯁꯨꯗꯀꯤ ꯅꯤꯌꯃ ꯀꯔꯤꯅꯣ?",
        "KCC ꯐꯪꯅꯕꯥ ꯀꯅꯥ ꯑꯔꯍꯥꯏ?",
        "KCC ꯑꯔꯣꯏꯕ ꯀꯔꯖꯃꯤ ꯆꯦꯜ ꯁꯤꯡ ꯀꯌꯥ?",
        "PMFBY ꯗ ꯐꯝꯔꯤꯒꯤ ꯄ꯭ꯔꯤꯃꯤꯌꯝ ꯔꯦꯠ ꯀꯌꯥ?",
        "PMFBY ꯗ ꯄꯣꯠꯁꯥꯔ ꯂꯨꯞꯇꯕꯒꯤ ꯈꯔꯤ ꯅꯣꯡꯒꯤ?",
        "PMFBY ꯗ ꯂꯥꯏꯔꯤꯕ ꯄꯣꯠꯂꯣꯟ ꯂꯣꯏꯁꯤꯡ ꯀꯌꯥ ꯆꯥꯎꯕ?",
        "PACS ꯑꯦ A-ꯀ꯭ꯂꯥꯁ ꯃꯦꯃꯕꯔ ꯀꯅꯥ ꯑꯣꯏꯕ?",
        "PACS ꯅ ꯀꯔꯤ ꯂꯥꯡꯊꯣꯛ ꯊꯧꯔꯣꯜꯒꯤ ꯀꯔꯖ ꯄꯤꯕ?",
        "ꯃꯇꯤ ꯁꯦꯂꯅ ꯀꯔꯗ ꯐꯝꯔꯤꯗ ꯀꯔꯤ ꯄꯤꯕ?",
        "ꯃꯇꯤꯒꯤ ꯅꯝꯄꯨ ꯀꯌꯥ ꯊꯣꯛꯂꯤ?",
        "e-NAM ꯗ ꯁꯦꯜ ꯐꯝꯔꯤꯗ ꯀꯔꯤ ꯊꯣꯛꯂꯤ?",
        "e-NAM ꯗ ꯃꯁꯤꯡꯒꯤ ꯀꯥꯏꯗꯥ ꯊꯧꯕ?",
    ],
    "Bodo (बर')": [
        "KCC मा आरो बिदामनि ब्याज नियम मा?",
        "KCC मोननो हांनो सोद्रोमाफोर सोदों?",
        "KCC कृषी ऋणनि जमानत-बिनानि सीमा सोरबा?",
        "PMFBY आव फार्मारनि प्रीमियम रेट सोरबा?",
        "PMFBY आव फसल नोक्सानखौ मा समाव फोरमायनो नांगौ?",
        "PMFBY आव कटाइनि उनाव नोक्सान मा सम फाव कभर जायो?",
        "PACS नि A-श्रेणी सदस्य सोर जायो?",
        "PACS आ मा सहायक थाखोफोरखौ ऋण होनो हायो?",
        "माटी स्वास्थ्य कार्डआ फार्मारखौ मा होयो?",
        "माटी नमुना मा सम समाव लायो?",
        "e-NAM नि बिक्री धन फार्मारखौ माबोरै होयो?",
        "e-NAM आव फसलनि क्वालिटी टेस्ट मा जायो?",
    ],
    "Santali (ᱥᱟᱱᱛᱟᱲᱤ)": [
        "KCC ᱪᱮᱫ ᱠᱟᱱᱟ ᱟᱨ ᱱᱚᱣᱟᱜ ᱥᱩᱫ ᱱᱤᱭᱚᱢ ᱪᱮᱫ?",
        "KCC ᱞᱟᱹᱜᱤᱫ ᱚᱠᱚ ᱡᱚᱜᱽᱭᱚ?",
        "KCC ᱠᱨᱤᱥᱤ ᱨᱤᱱ ᱨᱮ ᱡᱟᱢᱤᱱ ᱵᱟᱹᱝ ᱥᱤᱢᱟ ᱪᱮᱫ?",
        "PMFBY ᱨᱮ ᱪᱟᱥᱤ ᱯᱨᱤᱢᱤᱭᱟᱢ ᱫᱚᱨ ᱪᱮᱫ?",
        "PMFBY ᱨᱮ ᱫᱷᱟᱱ ᱱᱟᱥᱟ ᱠᱟᱛᱮ ᱡᱟᱹᱦᱤᱨ ᱠᱟᱱᱟ?",
        "PMFBY ᱨᱮ ᱠᱟᱴᱟ ᱦᱟᱹᱛᱤ ᱱᱟᱥᱟ ᱛᱤᱱᱟᱹ ᱫᱤᱱ ᱠᱟᱵᱟ?",
        "PACS ᱨᱮ A-ᱥᱨᱮᱱᱤ ᱥᱟᱫᱚᱥᱭᱚ ᱚᱠᱚ ᱵᱟᱹᱱᱟ?",
        "PACS ᱪᱮᱫ ᱥᱟᱦᱟᱭᱚᱜ ᱠᱟᱹᱢ ᱞᱟᱹᱜᱤᱫ ᱨᱤᱱ ᱫᱟᱹᱱ?",
        "ᱢᱟᱹᱴᱤ ᱥᱟᱹᱛᱟ ᱠᱟᱨᱰ ᱪᱟᱥᱤ ᱠᱟᱹᱛᱮ ᱪᱮᱫ ᱫᱟᱹᱱ?",
        "ᱢᱟᱹᱴᱤ ᱱᱟᱢᱩᱱᱟ ᱛᱤᱱᱟᱹ ᱵᱟᱹᱨ ᱧᱟᱢ?",
        "e-NAM ᱨᱮ ᱡᱚᱜᱟᱛ ᱫᱟᱢ ᱪᱟᱥᱤ ᱠᱟᱛᱮ ᱧᱟᱢ?",
        "e-NAM ᱨᱮ ᱠᱷᱚᱱᱟ ᱠᱩᱞᱤᱛ ᱢᱟᱱ ᱯᱚᱨᱤᱠᱷᱟ ᱪᱮᱫ?",
    ],
}

# Languages for which the UI does not have a complete FAQ sentence pack above.
# We still provide native-script, short topic labels so English FAQ text never
# leaks into a non-selected-language dashboard.
FAQ_TOPIC_LABELS = {
    "Sanskrit (संस्कृतम्)": ["KCC नियमाः", "KCC पात्रता", "KCC बन्धकरहित सीमा", "PMFBY प्रीमियम", "PMFBY क्षतिसूचना", "PMFBY कटनोत्तर क्षतिः", "PACS A-सदस्यता", "PACS सहायक ऋण", "मृदास्वास्थ्यपत्रम्", "मृदानमूना चक्रः", "e-NAM विक्रयधनम्", "e-NAM गुणवत्तापरीक्षा"],
    "Sindhi (सिंधी)": ["KCC ۽ وياج", "KCC لاءِ اهل", "KCC ضمانت حد", "PMFBY پريميئم", "PMFBY نقصان اطلاع", "PMFBY ڪٽائي کان پوءِ نقصان", "PACS A درجو", "PACS لاڳاپيل قرض", "مٽي صحت ڪارڊ", "مٽي نمونو چڪر", "e-NAM وڪري جي رقم", "e-NAM معيار جاچ"],
    "Kashmiri (कॉशुर)": ["KCC تہ سود", "KCC اہلیت", "KCC ضمانت حد", "PMFBY پریمیم", "PMFBY نقصان اطلاع", "PMFBY کٹائی پتہ نقصان", "PACS A درجہ", "PACS متعلقہ قرض", "مٹی صحت کارڈ", "مٹی نمونہ", "e-NAM فروخت رقم", "e-NAM معیار"],
    "Konkani (कोंकणी)": ["KCC आनी व्याज", "KCC पात्रताय", "KCC तारणमुक्त मर्यादा", "PMFBY प्रीमियम", "PMFBY पीक नुकसाण", "PMFBY कापणी उपरांत", "PACS A-वर्ग", "PACS पूरक कर्ज", "माती आरोग्य कार्ड", "माती नमुने", "e-NAM विक्री रकम", "e-NAM गुणवत्ता तपासणी"],
    "Maithili (मैथिली)": ["KCC आ ब्याज", "KCC पात्रता", "KCC बिना जमानत सीमा", "PMFBY प्रीमियम", "PMFBY क्षति सूचना", "PMFBY कटनी बाद क्षति", "PACS A-श्रेणी", "PACS सहायक ऋण", "माटि स्वास्थ्य कार्ड", "माटि नमूना", "e-NAM बिक्री राशि", "e-NAM गुणवत्ता जाँच"],
    "Manipuri (ꯃꯩꯇꯩꯂꯣꯟ)": ["KCC ꯑꯃꯁꯨꯡ ꯁꯨꯗ", "KCC ꯑꯔꯍꯥꯏ", "KCC ꯖꯥꯃꯤꯟ ꯂꯦꯜ", "PMFBY ꯄ꯭ꯔꯤꯃꯤꯌꯝ", "PMFBY ꯅꯣꯛꯁꯥꯟ", "PMFBY ꯂꯣꯏꯁꯤꯡ", "PACS A-ꯀ꯭ꯂꯥꯁ", "PACS ꯂꯥꯡꯊꯣꯛ", "ꯃꯇꯤ ꯁꯦꯂ ꯀꯥꯔꯗ", "ꯃꯇꯤ ꯅꯝꯄꯨ", "e-NAM ꯁꯦꯜ", "e-NAM ꯀ꯭ꯋꯥꯂꯤꯇꯤ"],
    "Bodo (बर')": ["KCC आरो ब्याज", "KCC सोद्रोम", "KCC जमानत सीमा", "PMFBY प्रीमियम", "PMFBY फसल नोक्सान", "PMFBY कटाइ उनाव", "PACS A-श्रेणी", "PACS सहायक ऋण", "माटी स्वास्थ्य कार्ड", "माटी नमुना", "e-NAM बिक्री धन", "e-NAM क्वालिटी टेस्ट"],
    "Dogri (डोगरी)": ["KCC ते ब्याज", "KCC योग्यता", "KCC जमानत-रहित हद", "PMFBY प्रीमियम", "PMFBY नुकसान सूचना", "PMFBY कटाई बाद नुकसान", "PACS A-श्रेणी", "PACS सहायक कर्ज", "मिट्टी सेहत कार्ड", "मिट्टी नमूने", "e-NAM बिक्री रकम", "e-NAM गुणवत्ता जांच"],
}

@lru_cache(maxsize=32)
def get_localized_faqs(language_name):
    items = FAQS
    labels = FAQ_LABELS.get(language_name)
    if labels is None:
        labels = FAQ_TOPIC_LABELS.get(language_name)

    if not labels or len(labels) != len(items):
        labels = FAQ_LABELS["English"]

    return [
        {
            "id": item["id"],
            "emoji": item["emoji"],
            "question": labels[index],
        }
        for index, item in enumerate(items)
    ]

