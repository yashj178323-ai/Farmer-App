import json
import os
import streamlit as st

LANGUAGES_FILE = "languages.json"

<<<<<<< HEAD
# Base labels used by the kiosk. The language-specific UI pack can be generated
# by Groq for any of the 22 scheduled languages, with deterministic fallbacks
# for the languages already covered by this project.
BASE_UI = {
    "tag": "Ministry of Cooperation • Govt. of India",
    "title": "🏛️ Sahakar-Vaani (सहकार-वाणी)",
    "subtitle": "National Agriculture Voice Kiosk | AI4Bharat & Groq Powered",
    "gate_title": "🌐 Select Your Language / भाषा चुनें",
    "gate_label": "🔍 Choose from 22 Official Scheduled Languages + English:",
    "gate_help": "Select the exact language you will speak. The transcription, AI answer and voice playback will use this same language.",
    "gate_btn": "Enter Voice Terminal ➔",
    "active_lang": "🌐 Active Language:",
    "change_lang": "🔄 Change Language",
    "schemes_header": "📚 Integrated Policy Knowledge Schemes",
    "pmfby_sub": "Crop Insurance",
    "kcc_sub": "Credit & Loans",
    "pacs_sub": "Loan Rules",
    "soil_sub": "Nutrient Testing",
    "enam_sub": "Mandi Selling",
    "q1_btn": "💳 KCC Interest Subvention Rules",
    "q1_text": "What are the interest rates and subvention rules for Kisan Credit Card?",
    "q2_btn": "🌾 PMFBY Loss Intimation Window",
    "q2_text": "Within how many hours must crop damage be reported under PMFBY?",
    "q3_btn": "🛒 e-NAM Bank Settlement Time",
    "q3_text": "When is money transferred to the bank account after selling on e-NAM?",
    "audio_console_header": "🎙️ Voice Assistance Terminal",
    "audio_help": "Ask one clear question about KCC, PMFBY, PACS bylaws, Soil Health Card or e-NAM. Answers are grounded in the verified policy documents indexed in this kiosk.",
    "mic_prompt": "🎙️ Record your question",
    "typed_label": "Or type your question",
    "typed_placeholder": "Example: Within how many hours must crop damage be reported under PMFBY?",
    "ask_btn": "🔎 Ask this question",
    "listening_msg": "🎙️ Converting your speech to text...",
    "checking_msg": "🔎 Checking the verified policy documents...",
    "tts_msg": "🔊 Preparing voice in the selected language...",
    "user_query_label": "🗣️ Farmer Speech Query:",
    "ai_resp_label": "🤖 Sahakar-Vaani Response:",
    "source_label": "📌 Verified Official Source Citation:",
    "audit_label": "🔍 Official Audit Trail: Grounded Document Excerpt",
    "view_sources": "📖 View the exact policy excerpts used for this answer",
    "knowledge_match": "Knowledge match",
    "response_time": "Response time",
    "answer_language": "Answer language",
    "tts_unavailable": "🔊 The answer is ready, but voice playback could not be generated for this language. You can still use the browser Read Aloud control below.",
    "browser_read": "🔊 Read answer aloud",
    "helpline_header": "🚨 Official Helpline & Grievance",
    "helpline_text": "Kisan Call Center: 1800-180-1551 • PMFBY: 1800-200-5142 • PACS State Helpline: 1800-233-4567",
    "grievance_expander": "Register a grievance ticket",
    "mobile_label": "Mobile number",
    "mobile_placeholder": "Enter 10-digit mobile number",
    "complaint_label": "Complaint / issue",
    "complaint_placeholder": "Describe the issue clearly",
    "submit_btn": "Submit grievance ticket",
    "ticket_success": "Ticket registered successfully:",
    "ticket_missing": "Please provide both mobile number and complaint.",
    "footer": "Ministry of Cooperation • Primary Agricultural Credit Societies (PACS) Network<br>Sahakar-Vaani • Multilingual farmer assistance kiosk",
    "menu_title": "Sahakar-Vaani Menu",
    "menu_caption": "Open the kiosk features and controls from here.",
    "menu_language": "Language",
    "apply_language": "🌐 Apply selected language",
    "features": "Features",
    "feature_voice": "🎙️ Ask about government schemes",
    "feature_sources": "📖 View retrieved policy sources",
    "feature_grievance": "🚨 Register a grievance",
    "feature_helpline": "📞 Government helplines",
    "display_voice": "Display & voice",
    "text_size": "Text size",
    "voice_speed": "Voice speed",
    "normal": "Normal",
    "slow": "Slow",
    "kiosk": "Kiosk",
    "terminal": "Terminal",
    "location": "Location",
    "connection": "Connection",
    "online": "Online",
    "limited": "Limited",
    "new_session": "🔄 New session",
    "connection_error": "Could not understand the recording.",
}

# Good-quality static packs for the languages most likely to be used in a field
# kiosk. Missing packs are completed by the runtime translator in kiosk_app.py.
STATIC_PACKS = {
    "Hindi (हिंदी)": {
        "tag":"सहकारिता मंत्रालय • भारत सरकार", "title":"🏛️ सहकार-वाणी", "subtitle":"राष्ट्रीय कृषि वॉयस सहायता कियोस्क | AI4Bharat एवं Groq द्वारा संचालित",
        "gate_title":"🌐 अपनी भाषा चुनें", "gate_label":"🔍 22 आधिकारिक अनुसूचित भाषाओं में से चुनें:", "gate_help":"आप जिस भाषा में बोलेंगे वही भाषा आवाज़ पहचान, AI उत्तर और आवाज़ में उपयोग होगी।", "gate_btn":"वॉयस टर्मिनल में प्रवेश करें ➔",
        "active_lang":"🌐 सक्रिय भाषा:", "change_lang":"🔄 भाषा बदलें", "schemes_header":"📚 एकीकृत नीति ज्ञान योजनाएं", "pmfby_sub":"फसल बीमा", "kcc_sub":"ऋण और क्रेडिट", "pacs_sub":"पैक्स नियम", "soil_sub":"मृदा परीक्षण", "enam_sub":"मंडी बिक्री",
        "audio_console_header":"🎙️ वॉयस सहायता टर्मिनल", "audio_help":"KCC, PMFBY, PACS नियम, मृदा स्वास्थ्य कार्ड या e-NAM के बारे में स्पष्ट प्रश्न पूछें। उत्तर सत्यापित नीति दस्तावेजों पर आधारित होगा।", "mic_prompt":"🎙️ अपना प्रश्न रिकॉर्ड करें", "typed_label":"या अपना प्रश्न लिखें", "ask_btn":"🔎 प्रश्न पूछें", "listening_msg":"🎙️ आपकी आवाज़ को टेक्स्ट में बदला जा रहा है...", "checking_msg":"🔎 सत्यापित नीति दस्तावेज़ जांचे जा रहे हैं...", "tts_msg":"🔊 चुनी गई भाषा में आवाज़ तैयार की जा रही है...", "user_query_label":"🗣️ किसान का प्रश्न:", "ai_resp_label":"🤖 सहकार-वाणी का उत्तर:", "source_label":"📌 सत्यापित आधिकारिक स्रोत:", "view_sources":"📖 इस उत्तर के लिए उपयोग किए गए नीति अंश देखें", "knowledge_match":"ज्ञान मिलान", "response_time":"उत्तर समय", "answer_language":"उत्तर की भाषा", "tts_unavailable":"🔊 उत्तर तैयार है, लेकिन इस भाषा में सर्वर आवाज़ उपलब्ध नहीं हो सकी। नीचे ब्राउज़र से उत्तर सुन सकते हैं।", "browser_read":"🔊 उत्तर सुनें", "helpline_header":"🚨 आधिकारिक हेल्पलाइन और शिकायत", "grievance_expander":"शिकायत टिकट दर्ज करें", "mobile_label":"मोबाइल नंबर", "complaint_label":"शिकायत / समस्या", "submit_btn":"शिकायत टिकट जमा करें", "ticket_success":"टिकट सफलतापूर्वक दर्ज हुआ:", "ticket_missing":"मोबाइल नंबर और शिकायत दोनों दर्ज करें।", "menu_title":"सहकार-वाणी मेनू", "menu_caption":"यहां से कियोस्क की सुविधाएं और नियंत्रण खोलें।", "menu_language":"भाषा", "apply_language":"🌐 चुनी गई भाषा लागू करें", "features":"सुविधाएं", "feature_voice":"🎙️ सरकारी योजनाओं के बारे में पूछें", "feature_sources":"📖 प्राप्त नीति स्रोत देखें", "feature_grievance":"🚨 शिकायत दर्ज करें", "feature_helpline":"📞 सरकारी हेल्पलाइन", "display_voice":"डिस्प्ले और आवाज़", "text_size":"टेक्स्ट आकार", "voice_speed":"आवाज़ की गति", "normal":"सामान्य", "slow":"धीमी", "kiosk":"कियोस्क", "terminal":"टर्मिनल", "location":"स्थान", "connection":"कनेक्शन", "online":"ऑनलाइन", "limited":"सीमित", "new_session":"🔄 नया सत्र", "connection_error":"रिकॉर्डिंग समझ में नहीं आई।"
    },
    "Marathi (मराठी)": {
        "tag":"सहकार मंत्रालय • भारत सरकार", "title":"🏛️ सहकार-वाणी", "subtitle":"राष्ट्रीय कृषी व्हॉइस सहाय्य किऑस्क | AI4Bharat आणि Groq द्वारे संचालित", "gate_title":"🌐 तुमची भाषा निवडा", "gate_label":"🔍 २२ अधिकृत अनुसूचित भाषांमधून निवडा:", "gate_help":"तुम्ही ज्या भाषेत बोलाल त्याच भाषेत आवाज ओळख, AI उत्तर आणि आवाज प्लेबॅक केला जाईल.", "gate_btn":"व्हॉइस टर्मिनलवर जा ➔", "active_lang":"🌐 सध्याची भाषा:", "change_lang":"🔄 भाषा बदला", "schemes_header":"📚 एकत्रित धोरण ज्ञान योजना", "pmfby_sub":"पीक विमा", "kcc_sub":"कर्ज आणि क्रेडिट", "pacs_sub":"पॅक्स नियम", "soil_sub":"माती परीक्षण", "enam_sub":"मंडी विक्री", "audio_console_header":"🎙️ व्हॉइस सहाय्य टर्मिनल", "audio_help":"KCC, PMFBY, PACS नियम, मृदा आरोग्य कार्ड किंवा e-NAM बद्दल स्पष्ट प्रश्न विचारा. उत्तर सत्यापित धोरण दस्तऐवजांवर आधारित असेल.", "mic_prompt":"🎙️ तुमचा प्रश्न रेकॉर्ड करा", "typed_label":"किंवा तुमचा प्रश्न लिहा", "ask_btn":"🔎 प्रश्न विचारा", "listening_msg":"🎙️ तुमचा आवाज मजकुरात बदलला जात आहे...", "checking_msg":"🔎 सत्यापित धोरण दस्तऐवज तपासले जात आहेत...", "tts_msg":"🔊 निवडलेल्या भाषेत आवाज तयार केला जात आहे...", "user_query_label":"🗣️ शेतकऱ्याचा प्रश्न:", "ai_resp_label":"🤖 सहकार-वाणीचे उत्तर:", "source_label":"📌 सत्यापित अधिकृत स्रोत:", "view_sources":"📖 या उत्तरासाठी वापरलेले धोरण उतारे पहा", "knowledge_match":"ज्ञान जुळणी", "response_time":"उत्तर वेळ", "answer_language":"उत्तराची भाषा", "tts_unavailable":"🔊 उत्तर तयार आहे, पण या भाषेसाठी सर्व्हर आवाज उपलब्ध झाला नाही. खाली ब्राउझरमधून उत्तर ऐकू शकता.", "browser_read":"🔊 उत्तर ऐका", "helpline_header":"🚨 अधिकृत हेल्पलाइन आणि तक्रार", "grievance_expander":"तक्रार तिकीट नोंदवा", "mobile_label":"मोबाईल क्रमांक", "complaint_label":"तक्रार / समस्या", "submit_btn":"तक्रार तिकीट जमा करा", "ticket_success":"तिकीट यशस्वीरित्या नोंदवले:", "ticket_missing":"मोबाईल क्रमांक आणि तक्रार दोन्ही भरा.", "menu_title":"सहकार-वाणी मेनू", "menu_caption":"येथून किऑस्कची वैशिष्ट्ये आणि नियंत्रण उघडा.", "menu_language":"भाषा", "apply_language":"🌐 निवडलेली भाषा लागू करा", "features":"वैशिष्ट्ये", "feature_voice":"🎙️ सरकारी योजनांबद्दल विचारा", "feature_sources":"📖 मिळालेले धोरण स्रोत पहा", "feature_grievance":"🚨 तक्रार नोंदवा", "feature_helpline":"📞 सरकारी हेल्पलाइन", "display_voice":"डिस्प्ले आणि आवाज", "text_size":"मजकूर आकार", "voice_speed":"आवाजाचा वेग", "normal":"सामान्य", "slow":"हळू", "kiosk":"किऑस्क", "terminal":"टर्मिनल", "location":"स्थान", "connection":"कनेक्शन", "online":"ऑनलाइन", "limited":"मर्यादित", "new_session":"🔄 नवीन सत्र", "connection_error":"रेकॉर्डिंग समजली नाही."
    },
    "Gujarati (ગુજરાતી)": {
        "tag":"સહકાર મંત્રાલય • ભારત સરકાર", "title":"🏛️ સહકાર-વાણી", "subtitle":"રાષ્ટ્રીય કૃષિ વોઇસ સહાય કિયોસ્ક | AI4Bharat અને Groq સંચાલિત", "gate_title":"🌐 તમારી ભાષા પસંદ કરો", "gate_label":"🔍 ૨૨ સત્તાવાર અનુસૂચિત ભાષાઓમાંથી પસંદ કરો:", "gate_help":"તમે જે ભાષામાં બોલશો તે જ ભાષામાં ટ્રાન્સક્રિપ્શન, AI જવાબ અને અવાજ પ્લેબેક થશે.", "gate_btn":"વોઇસ ટર્મિનલમાં પ્રવેશ કરો ➔", "active_lang":"🌐 સક્રિય ભાષા:", "change_lang":"🔄 ભાષા બદલો", "schemes_header":"📚 સંકલિત નીતિ જ્ઞાન યોજનાઓ", "pmfby_sub":"પાક વીમો", "kcc_sub":"ક્રેડિટ અને લોન", "pacs_sub":"પેક્સ નિયમો", "soil_sub":"માટી પરીક્ષણ", "enam_sub":"મંડી વેચાણ", "audio_console_header":"🎙️ વોઇસ સહાય ટર્મિનલ", "audio_help":"KCC, PMFBY, PACS નિયમો, સોઇલ હેલ્થ કાર્ડ અથવા e-NAM વિશે સ્પષ્ટ પ્રશ્ન પૂછો. જવાબ ચકાસેલા નીતિ દસ્તાવેજો પરથી આપવામાં આવશે.", "mic_prompt":"🎙️ તમારો પ્રશ્ન રેકોર્ડ કરો", "typed_label":"અથવા તમારો પ્રશ્ન લખો", "ask_btn":"🔎 પ્રશ્ન પૂછો", "listening_msg":"🎙️ તમારો અવાજ ટેક્સ્ટમાં બદલાઈ રહ્યો છે...", "checking_msg":"🔎 ચકાસેલા નીતિ દસ્તાવેજો તપાસી રહ્યા છીએ...", "tts_msg":"🔊 પસંદ કરેલી ભાષામાં અવાજ તૈયાર થઈ રહ્યો છે...", "user_query_label":"🗣️ ખેડૂતનો પ્રશ્ન:", "ai_resp_label":"🤖 સહકાર-વાણીનો જવાબ:", "source_label":"📌 ચકાસાયેલ સત્તાવાર સ્ત્રોત:", "view_sources":"📖 આ જવાબ માટે ઉપયોગમાં લેવાયેલા નીતિ અંશો જુઓ", "knowledge_match":"જ્ઞાન મેળ", "response_time":"જવાબ સમય", "answer_language":"જવાબની ભાષા", "tts_unavailable":"🔊 જવાબ તૈયાર છે, પરંતુ આ ભાષામાં સર્વર અવાજ બની શક્યો નથી. નીચે બ્રાઉઝરથી જવાબ સાંભળી શકો છો.", "browser_read":"🔊 જવાબ સાંભળો", "helpline_header":"🚨 સત્તાવાર હેલ્પલાઇન અને ફરિયાદ", "grievance_expander":"ફરિયાદ ટિકિટ નોંધાવો", "mobile_label":"મોબાઇલ નંબર", "complaint_label":"ફરિયાદ / સમસ્યા", "submit_btn":"ફરિયાદ ટિકિટ સબમિટ કરો", "ticket_success":"ટિકિટ સફળતાપૂર્વક નોંધાઈ:", "ticket_missing":"મોબાઇલ નંબર અને ફરિયાદ બંને દાખલ કરો.", "menu_title":"સહકાર-વાણી મેનુ", "menu_caption":"અહીંથી કિયોસ્કની સુવિધાઓ અને નિયંત્રણો ખોલો.", "menu_language":"ભાષા", "apply_language":"🌐 પસંદ કરેલી ભાષા લાગુ કરો", "features":"સુવિધાઓ", "feature_voice":"🎙️ સરકારી યોજનાઓ વિશે પૂછો", "feature_sources":"📖 મળેલા નીતિ સ્ત્રોત જુઓ", "feature_grievance":"🚨 ફરિયાદ નોંધાવો", "feature_helpline":"📞 સરકારી હેલ્પલાઇન", "display_voice":"ડિસ્પ્લે અને અવાજ", "text_size":"ટેક્સ્ટ કદ", "voice_speed":"અવાજની ઝડપ", "normal":"સામાન્ય", "slow":"ધીમું", "kiosk":"કિયોસ્ક", "terminal":"ટર્મિનલ", "location":"સ્થાન", "connection":"કનેક્શન", "online":"ઓનલાઇન", "limited":"મર્યાદિત", "new_session":"🔄 નવું સત્ર", "connection_error":"રેકોર્ડિંગ સમજાઈ નથી."
    },
}

=======
>>>>>>> f6b31d8cf48c2d556f483b57b5e8ff29e8c474f2
@st.cache_data
def get_all_languages():
    if os.path.exists(LANGUAGES_FILE):
        with open(LANGUAGES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return ["English", "Hindi (हिंदी)", "Odia (ଓଡ଼ିଆ)", "Marathi (मराठी)"]

<<<<<<< HEAD

def get_ui_translation(lang_name):
    """Return a complete UI dictionary; never return a partially translated pack."""
    t = dict(BASE_UI)
    if lang_name in STATIC_PACKS:
        t.update(STATIC_PACKS[lang_name])
    return t
=======
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
>>>>>>> f6b31d8cf48c2d556f483b57b5e8ff29e8c474f2
