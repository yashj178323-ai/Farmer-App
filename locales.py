import json
import os
import streamlit as st

LANGUAGES_FILE = "languages.json"

@st.cache_data
def get_all_languages():
    if os.path.exists(LANGUAGES_FILE):
        with open(LANGUAGES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return ["English", "Hindi (हिंदी)", "Odia (ଓଡ଼ିଆ)", "Marathi (मराठी)"]

def get_ui_translation(lang_name):
    l_str = str(lang_name).lower()

    # English Default
    t = {
        "tag": "Ministry of Cooperation • Govt. of India",
        "title": "🏛️ Sahakar-Vaani (सहकार-वाणी)",
        "subtitle": "National Agriculture Voice Kiosk | AI4Bharat & Groq Powered",
        "gate_title": "🌐 Select Your Language / भाषा चुनें",
        "gate_label": "🔍 Choose from 22 Official Scheduled Languages:",
        "gate_btn": "Enter Voice Terminal ➔",
        "active_lang": "🌐 Active Language:",
        "change_lang": "🔄 Change Language",
        "schemes_header": "📚 Integrated Policy Knowledge Schemes",
        "pmfby_sub": "Crop Insurance",
        "kcc_sub": "Credit & Loans",
        "pacs_sub": "Loan Rules",
        "soil_sub": "Nutrient Testing",
        "enam_sub": "Mandi Selling",
        "tab_voice": "🎙️ Voice Assistance Terminal",
        "tab_grievance": "🚨 Official Helpline & Grievance Ticket",
        "quick_faq_header": "🔥 Dynamic Quick Questions (One-Click)",
        "q1_btn": "💳 KCC Interest Subvention Rules",
        "q1_text": "What are the interest rates and subvention rules for Kisan Credit Card?",
        "q2_btn": "🌾 PMFBY Loss Intimation Window",
        "q2_text": "Within how many hours must crop damage be reported under PMFBY?",
        "q3_btn": "🛒 e-NAM Bank Settlement Time",
        "q3_text": "When is money transferred to the bank account after selling on e-NAM?",
        "audio_console_header": "🎙️ Audio Interaction Console (AI4Bharat Engine)",
        "mic_prompt": "Press microphone icon to speak into the terminal:",
        "listening_msg": "🎙️ Transcribing via AI4Bharat Speech Engine...",
        "user_query_label": "🗣️ Farmer Speech Query:",
        "ai_resp_label": "🤖 Sahakar-Vaani Response:",
        "source_label": "📌 Verified Official Source Citation:",
        "audit_label": "🔍 Official Audit Trail: Grounded Document Excerpt",
        "mobile_label": "Mobile Number:",
        "complaint_label": "Complaint Description:",
        "submit_btn": "Submit Grievance Ticket",
        "helpline_header": "📞 Official Government Toll-Free Helplines",
        "footer": "Ministry of Cooperation • Primary Agricultural Credit Societies (PACS) Network<br>Powered by AI4Bharat Model Suite (Indic-Parler-TTS & IndicWhisper)"
    }

    # 1. Hindi, Dogri, Maithili, Bodo, Konkani, Sanskrit, Nepali
    if any(k in l_str for k in ["hindi", "हिंदी", "dogri", "डोगरी", "maithili", "मैथिली", "bodo", "बर'", "konkani", "कोंकणी", "sanskrit", "संस्कृतम्", "nepali", "नेपाली"]):
        t.update({
            "tag": "सहकारिता मंत्रालय • भारत सरकार",
            "title": "🏛️ सहकार-वाणी (Sahakar-Vaani)",
            "subtitle": "राष्ट्रीय कृषि वॉयस सहायता कियोस्क | AI4Bharat बहुभाषी इंजन",
            "gate_title": "🌐 अपनी भाषा चुनें",
            "gate_label": "🔍 22 आधिकारिक भाषाओं में से चुनें:",
            "gate_btn": "वॉयस टर्मिनल में प्रवेश करें ➔",
            "active_lang": "🌐 सक्रिय भाषा:",
            "change_lang": "🔄 भाषा बदलें",
            "schemes_header": "📚 एकीकृत नीति ज्ञान योजनाएं",
            "pmfby_sub": "फसल बीमा",
            "kcc_sub": "ऋण और क्रेडिट",
            "pacs_sub": "पैक्स उपनियम",
            "soil_sub": "मृदा परीक्षण",
            "enam_sub": "मंडी बिक्री",
            "tab_voice": "🎙️ वॉयस असिस्टेंट टर्मिनल",
            "tab_grievance": "🚨 शिकायत निवारण टिकट",
            "quick_faq_header": "🔥 त्वरित प्रश्न (एक क्लिक में)",
            "q1_btn": "💳 केसीसी ब्याज नियम",
            "q2_btn": "🌾 फसल नुकसान सूचना सीमा",
            "q3_btn": "🛒 ई-नाम बैंक भुगतान समय",
            "audio_console_header": "🎙️ ऑडियो कंसोल (AI4Bharat इंजन)",
            "mic_prompt": "टर्मिनल में बोलने के लिए माइक पर क्लिक करें:",
            "listening_msg": "🎙️ आपकी आवाज सुनी जा रही है...",
            "user_query_label": "🗣️ किसान का प्रश्न:",
            "ai_resp_label": "🤖 सहकार-वाणी का उत्तर:"
        })

    # 2. Odia (ଓଡ଼ିଆ)
    elif any(k in l_str for k in ["odia", "ଓଡ଼ିଆ", "oriya"]):
        t.update({
            "tag": "ସମବାୟ ମନ୍ତ୍ରଣାଳୟ • ଭାରତ ସରକାର",
            "title": "🏛️ ସହକାର-ବାଣୀ (Sahakar-Vaani)",
            "gate_title": "🌐 ଆପଣଙ୍କର ଭାଷା ବାଛନ୍ତୁ",
            "gate_label": "🔍 ୨୨ଟି ସରକାରୀ ଭାଷାରୁ ବାଛନ୍ତୁ:",
            "gate_btn": "ଭଏସ୍ ଟର୍ମିନାଲକୁ ଯାଆନ୍ତୁ ➔",
            "active_lang": "🌐 ସକ୍ରିୟ ଭାଷା:",
            "change_lang": "🔄 ଭାଷା ବଦଳାନ୍ତୁ",
            "schemes_header": "📚 ନୀତି ଜ୍ଞାନ ଯୋଜନା",
            "pmfby_sub": "ଫସଲ ବୀମା",
            "kcc_sub": "କୃଷି ଋଣ",
            "pacs_sub": "ପ୍ୟାକ୍ସ ନିୟମ",
            "soil_sub": "ମୃତ୍ତିକା ପରୀକ୍ଷା",
            "enam_sub": "ମଣ୍ଡି ବିକ୍ରି",
            "user_query_label": "🗣️ ଚାଷୀଙ୍କ ପ୍ରଶ୍ନ:",
            "ai_resp_label": "🤖 ସହକାର-ବାଣୀ ଉତ୍ତର:"
        })

    # 3. Marathi (मराठी)
    elif "marathi" in l_str or "मराठी" in l_str:
        t.update({
            "tag": "सहकार मंत्रालय • भारत सरकार",
            "gate_title": "🌐 तुमची भाषा निवडा",
            "gate_label": "🔍 २२ अधिकृत भाषांमधून निवडा:",
            "gate_btn": "व्हॉइस टर्मिनलवर जा ➔",
            "active_lang": "🌐 सध्याची भाषा:",
            "change_lang": "🔄 भाषा बदला",
            "user_query_label": "🗣️ शेतकऱ्याचा प्रश्न:",
            "ai_resp_label": "🤖 सहकार-वाणी उत्तर:"
        })

    # 4. Gujarati (ગુજરાતી)
    elif "gujarati" in l_str or "ગુજરાતી" in l_str:
        t.update({
            "tag": "સહકાર મંત્રાલય • ભારત સરકાર",
            "gate_title": "🌐 તમારી ભાષા પસંદ કરો",
            "gate_label": "🔍 ૨૨ સત્તાવાર ભાષાઓમાંથી પસંદ કરો:",
            "gate_btn": "વોઇસ ટર્મિનલમાં પ્રવેશ કરો ➔",
            "active_lang": "🌐 સક્રિય ભાષા:",
            "change_lang": "🔄 ભાષા બદલો",
            "user_query_label": "🗣️ ખેડૂતનો પ્રશ્ન:",
            "ai_resp_label": "🤖 સહકાર-વાણીનો જવાબ:"
        })

    # 5. Bengali (বাংলা) & Assamese (অসমীয়া)
    elif any(k in l_str for k in ["bengali", "বাংলা", "assamese", "অসমীয়া"]):
        t.update({
            "tag": "সমবায় মন্ত্রক • ভারত সরকার",
            "gate_title": "🌐 আপনার ভাষা নির্বাচন করুন",
            "gate_label": "🔍 ২২টি সরকারি ভাষার থেকে বেছে নিন:",
            "gate_btn": "ভয়েস টার্মিনালে প্রবেশ করুন ➔",
            "active_lang": "🌐 সক্রিয় ভাষা:",
            "change_lang": "🔄 ভাষা পরিবর্তন করুন",
            "user_query_label": "🗣️ কৃষকের প্রশ্ন:",
            "ai_resp_label": "🤖 সহকার-বাণী উত্তর:"
        })

    # 6. Tamil (தமிழ்)
    elif "tamil" in l_str or "தமிழ்" in l_str:
        t.update({
            "tag": "கூட்டுறவு அமைச்சகம் • இந்திய அரசு",
            "gate_title": "🌐 உங்கள் மொழியைத் தேர்ந்தெடுக்கவும்",
            "gate_label": "🔍 22 அதிகாரப்பூர்வ மொழிகளில் இருந்து தேர்ந்தெடுக்கவும்:",
            "gate_btn": "குரல் முனையத்திற்குச் செல்லவும் ➔",
            "active_lang": "🌐 தற்போதைய மொழி:",
            "change_lang": "🔄 மொழியை மாற்றவும்",
            "user_query_label": "🗣️ விவசாயியின் கேள்வி:",
            "ai_resp_label": "🤖 சககார்-வாணி பதில்:"
        })

    # 7. Telugu (తెలుగు)
    elif "telugu" in l_str or "తెలుగు" in l_str:
        t.update({
            "tag": "సహకార మంత్రిత్వ శాఖ • భారత ప్రభుత్వం",
            "gate_title": "🌐 మీ భాషను ఎంచుకోండి",
            "gate_label": "🔍 22 అధికారిక భాషల నుండి ఎంచుకోండి:",
            "gate_btn": "వాయిస్ టెర్మినల్‌లోకి ప్రవేశించండి ➔",
            "active_lang": "🌐 ప్రస్తుత భాష:",
            "change_lang": "🔄 భాష మార్చండి",
            "user_query_label": "🗣️ రైతు ప్రశ్న:",
            "ai_resp_label": "🤖 సహకార్-వాణి సమాధానం:"
        })

    # 8. Kannada (ಕನ್ನಡ)
    elif "kannada" in l_str or "ಕನ್ನಡ" in l_str:
        t.update({
            "tag": "ಸಹಕಾರ ಸಚಿವಾಲಯ • ಭಾರತ ಸರ್ಕಾರ",
            "gate_title": "🌐 ನಿಮ್ಮ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",
            "gate_label": "🔍 22 ಅಧಿಕೃತ ಭಾಷೆಗಳಿಂದ ಆಯ್ಕೆಮಾಡಿ:",
            "gate_btn": "ವಾಯ್ಸ್ ಟರ್ಮಿನಲ್‌ಗೆ ಹೋಗಿ ➔",
            "active_lang": "🌐 ಸಕ್ರಿಯ ಭಾಷೆ:",
            "change_lang": "🔄 ಭಾಷೆಯನ್ನು ಬದಲಾಯಿಸಿ",
            "user_query_label": "🗣️ ರೈತರ ಪ್ರಶ್ನೆ:",
            "ai_resp_label": "🤖 ಸಹಕಾರ್-ವಾಣಿ ಉತ್ತರ:"
        })

    # 9. Malayalam (മലയാളം)
    elif "malayalam" in l_str or "മലയാളം" in l_str:
        t.update({
            "tag": "സഹകരണ മന്ത്രാലയം • ഭാരത സർക്കാർ",
            "gate_title": "🌐 നിങ്ങളുടെ ഭാഷ തിരഞ്ഞെടുക്കുക",
            "gate_label": "🔍 22 ഔദ്യോഗിക ഭാഷകളിൽ നിന്ന് തിരഞ്ഞെടുക്കുക:",
            "gate_btn": "വോയ്സ് ടെർമിനലിലേക്ക് പ്രവേശിക്കുക ➔",
            "user_query_label": "🗣️ കർഷകന്റെ ചോദ്യം:",
            "ai_resp_label": "🤖 സഹകാർ-വാണി മറുപടി:"
        })

    # 10. Punjabi (ਪੰਜਾਬੀ)
    elif "punjabi" in l_str or "ਪੰਜਾਬੀ" in l_str:
        t.update({
            "tag": "ਸਹਿਕਾਰਤਾ ਮੰਤਰਾਲਾ • ਭਾਰਤ ਸਰਕਾਰ",
            "gate_title": "🌐 ਆਪਣੀ ਭਾਸ਼ਾ ਚੁਣੋ",
            "gate_label": "🔍 22 ਸਰਕਾਰੀ ਭਾਸ਼ਾਵਾਂ ਵਿੱਚੋਂ ਚੁਣੋ:",
            "gate_btn": "ਵਾਇਸ ਟਰਮੀਨਲ ਵਿੱਚ ਦਾਖਲ ਹੋਵੋ ➔",
            "user_query_label": "🗣️ ਕਿਸਾਨ ਦਾ ਸਵਾਲ:",
            "ai_resp_label": "🤖 ਸਹਿਕਾਰ-ਵਾਣੀ ਜਵਾਬ:"
        })

    # 11. Urdu (اردو), Kashmiri (कॉशुर), Sindhi (सिंधी)
    elif any(k in l_str for k in ["urdu", "اردو", "kashmiri", "sindhi"]):
        t.update({
            "tag": "وزارت تعاون • حکومت ہند",
            "gate_title": "🌐 اپنی زبان کا انتخاب کریں",
            "gate_label": "🔍 22 سرکاری زبانوں میں سے منتخب کریں:",
            "gate_btn": "وائس ٹرمینل میں داخل ہوں ➔",
            "user_query_label": "🗣️ کسان کا سوال:",
            "ai_resp_label": "🤖 سہکار-وانی کا جواب:"
        })

    return t