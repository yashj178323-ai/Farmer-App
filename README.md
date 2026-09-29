# 🌾 Sahakar-Vaani

### Voice-first AI assistant for cooperatives and farmers

Ask in your own language. Get answers grounded in official policy. Escalate to a real officer when AI isn't enough.

![Python](https://img.shields.io/badge/Python-3.10+-16a34a?style=flat-square&labelColor=1e293b&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-16a34a?style=flat-square&labelColor=1e293b&logo=streamlit&logoColor=white)
![Whisper](https://img.shields.io/badge/Speech-Whisper-16a34a?style=flat-square&labelColor=1e293b)
![Search](https://img.shields.io/badge/Search-BM25%20%2B%20ChromaDB-16a34a?style=flat-square&labelColor=1e293b)
![LLM](https://img.shields.io/badge/LLM-Groq-16a34a?style=flat-square&labelColor=1e293b)
![DB](https://img.shields.io/badge/Database-SQLite-16a34a?style=flat-square&labelColor=1e293b&logo=sqlite&logoColor=white)

<p align="center">
  <img src="https://raw.githubusercontent.com/yashj178323-ai/Sahakar-Vaani/main/kiosk-home.jpg" alt="Sahakar-Vaani farmer kiosk home screen with Hindi language selection" width="900">
  <br>
  <sub><i>Farmer kiosk home screen: the farmer picks a language, and speech recognition, AI answers and voice playback all run in that language.</i></sub>
</p>

---

## 📖 Overview

**Sahakar-Vaani** is a voice-first, multilingual assistant for Primary Agricultural Credit Societies (PACS), farming cooperatives, and rural communities in India.

A farmer speaks or types a question at a kiosk. A hybrid retrieval pipeline finds the relevant policy passages, and an LLM answers in plain language **with citations**. If the answer doesn't solve the problem, the farmer raises a **grievance ticket** that PACS officers review from a separate admin dashboard, so a human stays in the loop.

## 🎯 The Problem

| Challenge | Impact | Our approach |
|---|---|---|
| Complex policy language | Circulars and PACS frameworks are hard for non-experts to read. | Plain-language answers generated from the source text |
| Language barriers | Most portals are English or Hindi only. | Multilingual UI and localized responses |
| Low digital literacy | Web forms and menus are hard to use. | A voice-first kiosk |
| Hallucination risk | Generic chatbots can invent schemes or eligibility rules. | Answers come only from retrieved policy chunks, with citations |
| Unresolved cases | A chatbot cannot resolve disputes. | Grievance tickets routed to PACS officers |

---

## ✨ Features

| | Feature | Details |
|:---:|---|---|
| 🎙️ | **Voice input** | Record a question on the kiosk; Whisper transcribes it. |
| 🌐 | **Multilingual** | Localized UI and output language via `languages.json` and `locales.py`. |
| 🧠 | **Hybrid RAG** | BM25 keyword search and ChromaDB vector search are fused; the LLM answers only from retrieved chunks and cites sources. |
| 🔊 | **Read-aloud answers** | Each answer is shown on screen and spoken back. |
| 📝 | **Grievance tickets** | Unresolved issues are stored in SQLite (`db_manager.py`). |
| 👨‍💼 | **Admin dashboard** | Officers filter, review, and update tickets, and view usage analytics (`admin_app.py`). |
| 📊 | **PDF reports** | Export grievance and resolution summaries (`report_generator.py`). |

---

## 🏗️ Architecture

```mermaid
%%{init: {'themeVariables': {'fontSize': '18px'}, 'flowchart': {'nodeSpacing': 45, 'rankSpacing': 60}}}%%
flowchart TB
    classDef blue fill:#1D4ED8,stroke:#1E3A8A,stroke-width:2px,color:#FFFFFF
    classDef green fill:#15803D,stroke:#14532D,stroke-width:2px,color:#FFFFFF
    classDef amber fill:#B45309,stroke:#78350F,stroke-width:2px,color:#FFFFFF
    classDef gray fill:#334155,stroke:#0F172A,stroke-width:2px,color:#FFFFFF

    LOC["Localization (locales.py)"]:::blue
    KIOSK["Farmer Kiosk (kiosk_app.py)"]:::blue
    ADMIN["Admin Dashboard (admin_app.py)"]:::blue

    STT["Whisper speech-to-text"]:::green
    RAG["Hybrid RAG Engine (rag_engine.py)"]:::green
    REP["PDF Reports (report_generator.py)"]:::green
    LLM["Groq LLM API (external)"]:::gray

    DB[("SQLite grievances")]:::amber
    CDB[("ChromaDB vectors")]:::amber
    BM[("BM25 keyword index")]:::amber
    DOCS[("Policy docs (data/)")]:::amber

    LOC --- KIOSK
    KIOSK --> STT
    KIOSK --> RAG
    KIOSK --> DB
    ADMIN --> DB
    ADMIN --> REP
    REP --> DB
    RAG --> CDB
    RAG --> BM
    RAG --> LLM
    DOCS -.-> CDB
    DOCS -.-> BM

    linkStyle default stroke:#64748B,stroke-width:3px
```

***Colors:** blue = interface · green = application and AI · amber = data stores · gray = external service. Dashed lines: `ingest.py` builds the indexes from policy documents.*

| Component | File | Role |
|---|---|---|
| Farmer Kiosk | `kiosk_app.py` | Voice/text input, answers, grievance form |
| Admin Dashboard | `admin_app.py` | Review tickets, update status, analytics |
| Whisper | (in kiosk) | Speech-to-text |
| Hybrid RAG Engine | `rag_engine.py` | BM25 + ChromaDB retrieval, LLM calls |
| PDF Report Generator | `report_generator.py` | Grievance and resolution reports |
| SQLite | `db_manager.py` | Grievance tickets and app state |
| ChromaDB / BM25 | built by `ingest.py` | Vector and keyword indexes |
| Localization | `locales.py`, `languages.json` | Multilingual UI and output |

---

## ⚙️ How It Works

### 1. Answering a question

```mermaid
flowchart LR
    classDef blue fill:#DBEAFE,stroke:#1D4ED8,stroke-width:2px,color:#0F172A
    classDef green fill:#DCFCE7,stroke:#15803D,stroke-width:2px,color:#0F172A

    Q(["Farmer asks voice or text"]):::blue
    STT["Whisper transcribes"]:::green
    RET["Hybrid retrieval BM25 + ChromaDB"]:::green
    LLM["Groq LLM writes answer"]:::green
    OUT(["Cited answer text and audio"]):::blue

    Q --> STT --> RET --> LLM --> OUT
```

### 2. Hybrid retrieval

BM25 is precise on scheme names, policy numbers, and numeric limits. Vector search handles paraphrases and colloquial wording. Fusing both covers what either alone would miss.

```mermaid
flowchart LR
    classDef blue fill:#DBEAFE,stroke:#1D4ED8,stroke-width:2px,color:#0F172A
    classDef green fill:#DCFCE7,stroke:#15803D,stroke-width:2px,color:#0F172A

    Q["User query"]:::blue
    BM["BM25 exact terms"]:::green
    VEC["ChromaDB meaning"]:::green
    FUSE["Rank fusion"]:::green
    CTX["Top-K policy chunks"]:::green
    LLM["Strict prompt and LLM"]:::green

    Q --> BM --> FUSE
    Q --> VEC --> FUSE
    FUSE --> CTX --> LLM
```

### 3. Building the knowledge base

```mermaid
flowchart LR
    classDef amber fill:#FEF3C7,stroke:#B45309,stroke-width:2px,color:#0F172A
    classDef green fill:#DCFCE7,stroke:#15803D,stroke-width:2px,color:#0F172A

    SRC[("Policy documents data/")]:::amber
    A["Extract and clean"]:::green
    B["Chunk with overlap"]:::green
    C["Tag metadata"]:::green
    V[("ChromaDB")]:::amber
    K[("BM25 index")]:::amber

    SRC --> A --> B --> C
    C --> V
    C --> K
```

Overlapping chunks preserve context across boundaries. Run `python ingest.py` once, and again whenever documents change.

### 4. Human-in-the-loop escalation

```mermaid
flowchart TB
    classDef blue fill:#DBEAFE,stroke:#1D4ED8,stroke-width:2px,color:#0F172A
    classDef green fill:#DCFCE7,stroke:#15803D,stroke-width:2px,color:#0F172A
    classDef amber fill:#FEF3C7,stroke:#B45309,stroke-width:2px,color:#0F172A
    classDef gray fill:#E2E8F0,stroke:#475569,stroke-width:2px,color:#0F172A

    A["Farmer query"]:::blue
    B["RAG answer"]:::green
    C{"Resolved?"}:::gray
    D(["Done"]):::blue
    E["Register grievance"]:::blue
    F[("SQLite ticket")]:::amber
    G["Officer reviews and decides"]:::green
    H["Update status"]:::green

    A --> B --> C
    C -->|Yes| D
    C -->|No| E --> F --> G --> H
```

Ticket lifecycle:

```mermaid
stateDiagram-v2
    direction LR
    state "In Progress" as InProgress
    [*] --> Submitted
    Submitted --> InProgress: Officer picks up
    InProgress --> Resolved: Issue addressed
    Resolved --> [*]
```

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| App and UI | Python 3.10+, Streamlit |
| Speech-to-text | OpenAI Whisper |
| Retrieval | ChromaDB (dense), `rank_bm25` (sparse) |
| Embeddings | Sentence-Transformers |
| Generation | Groq API |
| Voice output | Text-to-speech |
| Storage | SQLite |
| Reporting | PDF generation |
| Localization | JSON + Python dicts |

---

## 🔮 Future Scope

| Idea | Goal |
|---|---|
| Regional dialect ASR | Fine-tuned speech models for rural Indian dialects |
| WhatsApp / SMS alerts | Notify farmers when a grievance status changes |
| Offline RAG | Lightweight local models for low-connectivity kiosks |
| Government API integration | Read-only links to state cooperative portals |

## 🌾 Expected Impact

- **Less friction** in reaching cooperative policy information
- **Wider inclusion** for non-literate and elderly farmers
- **More transparency** through structured grievance logs
- **Faster resolution** with standardized ticket tracking
