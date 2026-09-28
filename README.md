# 🏛️ Sahakar-Vaani (सहकार-वाणी)
> **Voice-First AI Assistance Kiosk & Centralized Governance Dashboard**
> *Developed for the Ministry of Cooperation | Smart India Hackathon*

## 📌 Features
- **Multilingual Speech Ingestion**: Groq Whisper-v3 STT enforcing Devanagari script for regional dialects (Hindi, Marathi, Gujarati).
- **Multi-Scheme Hybrid RAG**: BM25 sparse matching + ChromaDB vector embeddings across PMFBY, PACS Bylaws, KCC, and Soil Health Card schemes.
- **Auditable Citations**: Strict policy grounding with source verification trails.
- **Human-in-the-Loop Escalation**: Voice-recorded grievance ticket creation for complex dispute resolution.
- **Cross-App Data Sync**: Shared SQLite database linking Kiosk (Port 8501) and Admin Dashboard (Port 8503).

## 🚀 Execution Instructions

1. **Activate Environment**:
   ```powershell
   .\venv\Scripts\Activate.ps1