import json
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
LANGUAGES_FILE = BASE_DIR / "languages.json"

# The complete UI is kept in a single schema so every language has the same
# keys. Language-specific packs below override the English defaults.
BASE_UI = {
    "tag": "Ministry of Cooperation • Govt. of India",
    "title": "🏛️ Sahakar-Vaani",
    "subtitle": "National Agriculture Voice Kiosk",
    "gate_title": "🌐 Select Your Language",
    "gate_label": "🔍 Choose your language:",
    "gate_help": "Select the exact language you will speak. Voice transcription, the AI answer and voice playback will use this same language.",
    "gate_btn": "Enter Voice Terminal ➔",
    "active_lang": "🌐 Active Language:",
    "change_lang": "🔄 Change Language",
    "schemes_header": "📚 Integrated Policy Knowledge Schemes",
    "pmfby": "PMFBY",
    "pmfby_sub": "Crop Insurance",
    "kcc": "KCC Card",
    "kcc_sub": "Credit & Loans",
    "pacs": "PACS Bylaws",
    "pacs_sub": "Cooperative Rules",
    "soil": "Soil Health",
    "soil_sub": "Nutrient Testing",
    "enam": "e-NAM",
    "enam_sub": "Mandi Selling",
    "audio_console_header": "🎙️ Ask Sahakar-Vaani",
    "audio_help": "Speak a question or type it below. Answers are grounded in the policy documents stored in this kiosk.",
    "mic_prompt": "🎙️ Click the microphone and speak",
    "typed_label": "⌨️ Or type your question",
    "typed_placeholder": "Example: What is KCC?",
    "quick_header": "Quick questions",
    "ask_btn": "🔎 Ask Sahakar-Vaani",
    "listening_msg": "🎙️ Converting your speech to text...",
    "checking_msg": "🔎 Checking the verified policy documents...",
    "tts_msg": "🔊 Preparing the answer voice...",
    "user_query_label": "🗣️ Farmer Question",
    "ai_resp_label": "🤖 Sahakar-Vaani Response",
    "source_label": "📌 Verified Official Source",
    "view_sources": "📖 View the policy excerpts used for this answer",
    "knowledge_match": "Knowledge match",
    "response_time": "Response time",
    "answer_language": "Answer language",
    "play_answer": "🔊 Play answer",
    "tts_unavailable": "The written answer is ready. Use the Play answer button to hear it in the selected language.",
    "helpline_header": "🚨 Official Helpline & Grievance",
    "grievance_expander": "Register a grievance ticket",
    "mobile_label": "Mobile number",
    "mobile_placeholder": "Enter 10-digit mobile number",
    "complaint_label": "Complaint / issue",
    "complaint_placeholder": "Describe the issue clearly",
    "submit_btn": "Submit grievance ticket",
    "ticket_success": "Ticket registered successfully:",
    "ticket_missing": "Please provide both mobile number and complaint.",
    "menu_title": "Sahakar-Vaani Menu",
    "menu_caption": "Open kiosk features and controls from here.",
    "menu_language": "Language",
    "apply_language": "🌐 Apply selected language",
    "features": "Features",
    "feature_voice": "🎙️ Ask about agriculture schemes",
    "feature_sources": "📖 View policy sources",
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
    "footer": "Ministry of Cooperation • Primary Agricultural Credit Societies (PACS) Network<br>Sahakar-Vaani • Multilingual farmer assistance kiosk",
}

# Core UI packs for all languages in languages.json. These intentionally cover
# the visible controls, headings, scheme labels and voice workflow. Answers are
# generated separately by the RAG engine in the selected language.
PACKS = {
    "English": {
        "title": "🏛️ Sahakar-Vaani",
    },
    "Hindi (हिंदी)": {
        "tag": "सहकारिता मंत्रालय • भारत सरकार",
        "title": "🏛️ सहकार-वाणी",
        "subtitle": "राष्ट्रीय कृषि वॉयस सहायता कियोस्क",
        "gate_title": "🌐 अपनी भाषा चुनें",
        "gate_label": "🔍 अपनी भाषा चुनें:",
        "gate_help": "आप जिस भाषा में बोलेंगे, उसी भाषा में आवाज़ पहचान, AI उत्तर और आवाज़ प्लेबैक होगा।",
        "gate_btn": "वॉयस टर्मिनल में प्रवेश करें ➔",
        "active_lang": "🌐 सक्रिय भाषा:",
        "change_lang": "🔄 भाषा बदलें",
        "schemes_header": "📚 एकीकृत नीति ज्ञान योजनाएं",
        "pmfby_sub": "फसल बीमा", "kcc_sub": "ऋण और क्रेडिट", "pacs_sub": "सहकारी नियम", "soil_sub": "मृदा परीक्षण", "enam_sub": "मंडी बिक्री",
        "audio_console_header": "🎙️ सहकार-वाणी से पूछें",
        "audio_help": "माइक्रोफोन पर क्लिक करके सवाल बोलें या नीचे लिखें। उत्तर इस कियोस्क के नीति दस्तावेजों पर आधारित होगा।",
        "mic_prompt": "🎙️ माइक्रोफोन पर क्लिक करके बोलें", "typed_label": "⌨️ या अपना प्रश्न लिखें", "typed_placeholder": "उदाहरण: किसान क्रेडिट कार्ड क्या है?",
        "quick_header": "त्वरित प्रश्न", "ask_btn": "🔎 सहकार-वाणी से पूछें",
        "listening_msg": "🎙️ आपकी आवाज़ को टेक्स्ट में बदला जा रहा है...", "checking_msg": "🔎 सत्यापित नीति दस्तावेज़ जांचे जा रहे हैं...", "tts_msg": "🔊 उत्तर की आवाज़ तैयार की जा रही है...",
        "user_query_label": "🗣️ किसान का प्रश्न", "ai_resp_label": "🤖 सहकार-वाणी का उत्तर", "source_label": "📌 सत्यापित आधिकारिक स्रोत", "view_sources": "📖 इस उत्तर के लिए उपयोग किए गए नीति अंश देखें",
        "knowledge_match": "ज्ञान मिलान", "response_time": "उत्तर समय", "answer_language": "उत्तर की भाषा", "play_answer": "🔊 उत्तर सुनें",
        "menu_title": "सहकार-वाणी मेनू", "menu_caption": "कियोस्क की सुविधाएं और नियंत्रण यहां खोलें।", "menu_language": "भाषा", "apply_language": "🌐 चुनी गई भाषा लागू करें",
        "features": "सुविधाएं", "feature_voice": "🎙️ कृषि योजनाओं के बारे में पूछें", "feature_sources": "📖 नीति स्रोत देखें", "feature_grievance": "🚨 शिकायत दर्ज करें", "feature_helpline": "📞 सरकारी हेल्पलाइन",
        "display_voice": "डिस्प्ले और आवाज़", "text_size": "टेक्स्ट आकार", "voice_speed": "आवाज़ की गति", "normal": "सामान्य", "slow": "धीमी",
        "kiosk": "कियोस्क", "terminal": "टर्मिनल", "location": "स्थान", "connection": "कनेक्शन", "online": "ऑनलाइन", "limited": "सीमित", "new_session": "🔄 नया सत्र",
    },
    "Marathi (मराठी)": {
        "tag": "सहकार मंत्रालय • भारत सरकार", "title": "🏛️ सहकार-वाणी", "subtitle": "राष्ट्रीय कृषी व्हॉइस सहाय्य किऑस्क",
        "gate_title": "🌐 तुमची भाषा निवडा", "gate_label": "🔍 तुमची भाषा निवडा:", "gate_help": "तुम्ही ज्या भाषेत बोलाल त्याच भाषेत आवाज ओळख, AI उत्तर आणि आवाज प्लेबॅक केला जाईल.", "gate_btn": "व्हॉइस टर्मिनलवर जा ➔",
        "active_lang": "🌐 सध्याची भाषा:", "change_lang": "🔄 भाषा बदला", "schemes_header": "📚 एकत्रित धोरण ज्ञान योजना",
        "pmfby_sub": "पीक विमा", "kcc_sub": "कर्ज आणि क्रेडिट", "pacs_sub": "सहकारी नियम", "soil_sub": "माती परीक्षण", "enam_sub": "मंडी विक्री",
        "audio_console_header": "🎙️ सहकार-वाणीला विचारा", "audio_help": "मायक्रोफोनवर क्लिक करून प्रश्न बोला किंवा खाली लिहा. उत्तर किऑस्कमधील धोरण दस्तऐवजांवर आधारित असेल.",
        "mic_prompt": "🎙️ मायक्रोफोनवर क्लिक करून बोला", "typed_label": "⌨️ किंवा तुमचा प्रश्न लिहा", "typed_placeholder": "उदाहरण: किसान क्रेडिट कार्ड म्हणजे काय?",
        "quick_header": "त्वरित प्रश्न", "ask_btn": "🔎 सहकार-वाणीला विचारा", "listening_msg": "🎙️ तुमचा आवाज मजकुरात बदलला जात आहे...", "checking_msg": "🔎 सत्यापित धोरण दस्तऐवज तपासले जात आहेत...", "tts_msg": "🔊 उत्तराचा आवाज तयार केला जात आहे...",
        "user_query_label": "🗣️ शेतकऱ्याचा प्रश्न", "ai_resp_label": "🤖 सहकार-वाणीचे उत्तर", "source_label": "📌 सत्यापित अधिकृत स्रोत", "view_sources": "📖 या उत्तरासाठी वापरलेले धोरण उतारे पहा",
        "knowledge_match": "ज्ञान जुळणी", "response_time": "उत्तर वेळ", "answer_language": "उत्तराची भाषा", "play_answer": "🔊 उत्तर ऐका",
        "menu_title": "सहकार-वाणी मेनू", "menu_caption": "किऑस्कची वैशिष्ट्ये आणि नियंत्रण येथे उघडा.", "menu_language": "भाषा", "apply_language": "🌐 निवडलेली भाषा लागू करा",
        "features": "वैशिष्ट्ये", "feature_voice": "🎙️ कृषी योजनांबद्दल विचारा", "feature_sources": "📖 धोरण स्रोत पहा", "feature_grievance": "🚨 तक्रार नोंदवा", "feature_helpline": "📞 सरकारी हेल्पलाइन",
        "display_voice": "डिस्प्ले आणि आवाज", "text_size": "मजकूर आकार", "voice_speed": "आवाजाचा वेग", "normal": "सामान्य", "slow": "हळू",
        "kiosk": "किऑस्क", "terminal": "टर्मिनल", "location": "स्थान", "connection": "कनेक्शन", "online": "ऑनलाइन", "limited": "मर्यादित", "new_session": "🔄 नवीन सत्र",
    },
    "Bengali (বাংলা)": {
        "tag": "সমবায় মন্ত্রক • ভারত সরকার", "title": "🏛️ সহকার-বাণী", "subtitle": "জাতীয় কৃষি ভয়েস কিয়স্ক",
        "gate_title": "🌐 আপনার ভাষা নির্বাচন করুন", "gate_label": "🔍 আপনার ভাষা নির্বাচন করুন:", "gate_help": "আপনি যে ভাষায় কথা বলবেন, ভয়েস ট্রান্সক্রিপশন, AI উত্তর ও ভয়েস প্লেব্যাক সেই ভাষাতেই হবে।", "gate_btn": "ভয়েস টার্মিনালে প্রবেশ করুন ➔",
        "active_lang": "🌐 সক্রিয় ভাষা:", "change_lang": "🔄 ভাষা বদলান", "schemes_header": "📚 সমন্বিত নীতি জ্ঞান প্রকল্প",
        "pmfby_sub": "ফসল বীমা", "kcc_sub": "ঋণ ও ক্রেডিট", "pacs_sub": "সমবায় নিয়ম", "soil_sub": "মাটি পরীক্ষা", "enam_sub": "মন্ডি বিক্রয়",
        "audio_console_header": "🎙️ সহকার-বাণীকে জিজ্ঞাসা করুন", "audio_help": "মাইক্রোফোনে ক্লিক করে প্রশ্ন বলুন বা নিচে লিখুন। উত্তর কিয়স্কের নীতি নথির ভিত্তিতে দেওয়া হবে।",
        "mic_prompt": "🎙️ মাইক্রোফোনে ক্লিক করে বলুন", "typed_label": "⌨️ অথবা প্রশ্ন লিখুন", "typed_placeholder": "উদাহরণ: কিষাণ ক্রেডিট কার্ড কী?",
        "quick_header": "দ্রুত প্রশ্ন", "ask_btn": "🔎 সহকার-বাণীকে জিজ্ঞাসা করুন", "listening_msg": "🎙️ আপনার কথা টেক্সটে রূপান্তর করা হচ্ছে...", "checking_msg": "🔎 যাচাইকৃত নীতি নথি পরীক্ষা করা হচ্ছে...", "tts_msg": "🔊 উত্তরের কণ্ঠ প্রস্তুত করা হচ্ছে...",
        "user_query_label": "🗣️ কৃষকের প্রশ্ন", "ai_resp_label": "🤖 সহকার-বাণীর উত্তর", "source_label": "📌 যাচাইকৃত সরকারি উৎস", "view_sources": "📖 এই উত্তরের জন্য ব্যবহৃত নীতি অংশ দেখুন",
        "knowledge_match": "জ্ঞান মিল", "response_time": "উত্তরের সময়", "answer_language": "উত্তরের ভাষা", "play_answer": "🔊 উত্তর শুনুন",
    },
    "Gujarati (ગુજરાતી)": {
        "tag": "સહકાર મંત્રાલય • ભારત સરકાર", "title": "🏛️ સહકાર-વાણી", "subtitle": "રાષ્ટ્રીય કૃષિ વોઇસ કિયોસ્ક",
        "gate_title": "🌐 તમારી ભાષા પસંદ કરો", "gate_label": "🔍 તમારી ભાષા પસંદ કરો:", "gate_help": "તમે જે ભાષામાં બોલશો તે જ ભાષામાં ટ્રાન્સક્રિપ્શન, AI જવાબ અને અવાજ પ્લેબેક થશે.", "gate_btn": "વોઇસ ટર્મિનલમાં પ્રવેશ કરો ➔",
        "active_lang": "🌐 સક્રિય ભાષા:", "change_lang": "🔄 ભાષા બદલો", "schemes_header": "📚 સંકલિત નીતિ જ્ઞાન યોજનાઓ",
        "pmfby_sub": "પાક વીમો", "kcc_sub": "ક્રેડિટ અને લોન", "pacs_sub": "સહકારી નિયમો", "soil_sub": "માટી પરીક્ષણ", "enam_sub": "મંડી વેચાણ",
        "audio_console_header": "🎙️ સહકાર-વાણીને પૂછો", "audio_help": "માઇક્રોફોન પર ક્લિક કરીને પ્રશ્ન બોલો અથવા નીચે લખો. જવાબ કિયોસ્કના નીતિ દસ્તાવેજો પરથી મળશે.",
        "mic_prompt": "🎙️ માઇક્રોફોન પર ક્લિક કરીને બોલો", "typed_label": "⌨️ અથવા તમારો પ્રશ્ન લખો", "typed_placeholder": "ઉદાહરણ: KCC શું છે?",
        "quick_header": "ઝડપી પ્રશ્નો", "ask_btn": "🔎 સહકાર-વાણીને પૂછો", "listening_msg": "🎙️ તમારો અવાજ ટેક્સ્ટમાં બદલાઈ રહ્યો છે...", "checking_msg": "🔎 ચકાસેલા નીતિ દસ્તાવેજો તપાસી રહ્યા છીએ...", "tts_msg": "🔊 જવાબનો અવાજ તૈયાર થઈ રહ્યો છે...",
        "user_query_label": "🗣️ ખેડૂતનો પ્રશ્ન", "ai_resp_label": "🤖 સહકાર-વાણીનો જવાબ", "source_label": "📌 ચકાસાયેલ સત્તાવાર સ્ત્રોત", "view_sources": "📖 આ જવાબ માટે વપરાયેલા નીતિ અંશો જુઓ",
        "knowledge_match": "જ્ઞાન મેળ", "response_time": "જવાબ સમય", "answer_language": "જવાબની ભાષા", "play_answer": "🔊 જવાબ સાંભળો",
    },
}

# Short translations for the remaining supported languages. They ensure that
# the two screens visibly change language instead of falling back to English.
SHORT_PACKS = {
    "Assamese (অসমীয়া)": ("সহকাৰ-ৱাণী", "আপোনাৰ ভাষা বাছনি কৰক", "সক্ৰিয় ভাষা:", "নীতি জ্ঞান আঁচনি", "আপোনাৰ প্ৰশ্ন কওক", "বা আপোনাৰ প্ৰশ্ন লিখক", "দ্ৰুত প্ৰশ্ন", "সহকাৰ-ৱাণীক সোধক", "কৃষকৰ প্ৰশ্ন", "সহকাৰ-ৱাণীৰ উত্তৰ", "উত্তৰ শুনক"),
    "Bodo (बर')": ("सहकार-वाणी", "आंनि राव सायख", "सक्रिय राव:", "नीति बिदिन्थि", "दाजाब हो", "नोबा लिर", "सावजों सों", "सहकार-वाणीजों सों", "दाजाब", "सहकार-वाणि बिदिन्थि", "बिदिन्थि सुन"),
    "Dogri (डोगरी)": ("सहकार-वाणी", "अपनी भाशा चुनो", "सरगर्म भाशा:", "नीति ज्ञान योजनां", "अपना सवाल बोलो", "जां सवाल लिखो", "तुरत सवाल", "सहकार-वाणी गी पुच्छो", "किसान दा सवाल", "सहकार-वाणी दा जवाब", "जवाब सुनो"),
    "Kannada (ಕನ್ನಡ)": ("ಸಹಕಾರ-ವಾಣಿ", "ನಿಮ್ಮ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ", "ಸಕ್ರಿಯ ಭಾಷೆ:", "ನೀತಿ ಜ್ಞಾನ ಯೋಜನೆಗಳು", "ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಹೇಳಿ", "ಅಥವಾ ಪ್ರಶ್ನೆಯನ್ನು ಬರೆಯಿರಿ", "ತ್ವರಿತ ಪ್ರಶ್ನೆಗಳು", "ಸಹಕಾರ-ವಾಣಿಯನ್ನು ಕೇಳಿ", "ರೈತರ ಪ್ರಶ್ನೆ", "ಸಹಕಾರ-ವಾಣಿಯ ಉತ್ತರ", "ಉತ್ತರ ಕೇಳಿ"),
    "Kashmiri (कॉशुर)": ("सहकार-वाणी", "पानस भाषा चुनिव", "मुतहरक भाषा:", "पॉलिसी मालूमात", "पानस सवाल वुछिव", "या सवाल लिखिव", "जल्दी सवाल", "सहकार-वाणी से पुछिव", "किसान सवाल", "सहकार-वाणी जवाब", "जवाब आयिक"),
    "Konkani (कोंकणी)": ("सहकार-वाणी", "आपली भास निवडात", "सक्रिय भास:", "धोरण ज्ञान येवजणां", "आपलो प्रस्न उलोवात", "वा प्रस्न बरयात", "वेगवान प्रस्न", "सहकार-वाणी क विचारात", "शेतकाराचो प्रस्न", "सहकार-वाणीचें जाप", "जाप आयकात"),
    "Maithili (मैथिली)": ("सहकार-वाणी", "अपन भाषा चुनू", "सक्रिय भाषा:", "नीति ज्ञान योजना", "अपन प्रश्न बाजू", "अथवा प्रश्न लिखू", "जल्दी प्रश्न", "सहकार-वाणी सँ पूछू", "किसानक प्रश्न", "सहकार-वाणी केर उत्तर", "उत्तर सुनू"),
    "Malayalam (മലയാളം)": ("സഹകാർ-വാണി", "നിങ്ങളുടെ ഭാഷ തിരഞ്ഞെടുക്കുക", "സജീവ ഭാഷ:", "നയ വിജ്ഞാന പദ്ധതികൾ", "നിങ്ങളുടെ ചോദ്യം പറയുക", "അല്ലെങ്കിൽ ചോദ്യം എഴുതുക", "വേഗത്തിലുള്ള ചോദ്യങ്ങൾ", "സഹകാർ-വാണിയോട് ചോദിക്കുക", "കർഷകന്റെ ചോദ്യം", "സഹകാർ-വാണിയുടെ മറുപടി", "മറുപടി കേൾക്കുക"),
    "Manipuri (ꯃꯩꯇꯩꯂꯣꯟ)": ("ꯁꯍꯀꯥꯔ-ꯋꯥꯅꯤ", "ꯅꯨꯡꯉꯥꯏ ꯂꯣꯟ ꯈꯟꯕꯤꯌꯨ", "ꯑꯦꯛꯇꯤꯕ ꯂꯣꯟ:", "ꯄꯣꯂꯤꯁꯤ ꯅꯣꯡꯃꯥꯏ", "ꯅꯨꯡꯉꯥꯏ ꯋꯥꯍꯪ ꯍꯥꯏꯕꯤꯌꯨ", "ꯅꯠꯇ꯭ꯔꯒꯥ ꯂꯤꯔꯛꯎ", "ꯑꯍꯣꯡꯕ ꯋꯥꯍꯪ", "ꯁꯍꯀꯥꯔ-ꯋꯥꯅꯤꯗ ꯋꯥꯍꯪ", "ꯁꯦꯜꯐꯥꯔ ꯋꯥꯍꯪ", "ꯁꯍꯀꯥꯔ-ꯋꯥꯅꯤ ꯄꯥꯎꯖꯦꯜ", "ꯄꯥꯎꯖꯦꯜ ꯇꯥꯕꯤꯌꯨ"),
    "Nepali (नेपाली)": ("सहकार-वाणी", "आफ्नो भाषा छान्नुहोस्", "सक्रिय भाषा:", "नीति ज्ञान योजनाहरू", "आफ्नो प्रश्न बोल्नुहोस्", "वा प्रश्न लेख्नुहोस्", "छिटो प्रश्नहरू", "सहकार-वाणीलाई सोध्नुहोस्", "किसानको प्रश्न", "सहकार-वाणीको उत्तर", "उत्तर सुन्नुहोस्"),
    "Odia (ଓଡ଼ିଆ)": ("ସହକାର-ବାଣୀ", "ଆପଣଙ୍କ ଭାଷା ବାଛନ୍ତୁ", "ସକ୍ରିୟ ଭାଷା:", "ନୀତି ଜ୍ଞାନ ଯୋଜନା", "ଆପଣଙ୍କ ପ୍ରଶ୍ନ କୁହନ୍ତୁ", "କିମ୍ବା ପ୍ରଶ୍ନ ଲେଖନ୍ତୁ", "ତୁରନ୍ତ ପ୍ରଶ୍ନ", "ସହକାର-ବାଣୀକୁ ପଚାରନ୍ତୁ", "ଚାଷୀଙ୍କ ପ୍ରଶ୍ନ", "ସହକାର-ବାଣୀର ଉତ୍ତର", "ଉତ୍ତର ଶୁଣନ୍ତୁ"),
    "Punjabi (ਪੰਜਾਬੀ)": ("ਸਹਕਾਰ-ਵਾਣੀ", "ਆਪਣੀ ਭਾਸ਼ਾ ਚੁਣੋ", "ਸਰਗਰਮ ਭਾਸ਼ਾ:", "ਨੀਤੀ ਗਿਆਨ ਯੋਜਨਾਵਾਂ", "ਆਪਣਾ ਸਵਾਲ ਬੋਲੋ", "ਜਾਂ ਸਵਾਲ ਲਿਖੋ", "ਤੁਰੰਤ ਸਵਾਲ", "ਸਹਕਾਰ-ਵਾਣੀ ਨੂੰ ਪੁੱਛੋ", "ਕਿਸਾਨ ਦਾ ਸਵਾਲ", "ਸਹਕਾਰ-ਵਾਣੀ ਦਾ ਜਵਾਬ", "ਜਵਾਬ ਸੁਣੋ"),
    "Sanskrit (संस्कृतम्)": ("सहकार-वाणी", "स्वभाषां चिनुत", "सक्रियभाषा:", "नीतिज्ञानयोजनाः", "प्रश्नं वदतु", "वा प्रश्नं लिखतु", "शीघ्रप्रश्नाः", "सहकार-वाणीं पृच्छतु", "कृषकस्य प्रश्नः", "सहकार-वाण्याः उत्तरम्", "उत्तरं शृणुत"),
    "Santali (ᱥᱟᱱᱛᱟᱲᱤ)": ("ᱥᱟᱦᱠᱟᱨ-ᱵᱟᱱᱤ", "ᱟᱢᱟᱜ ᱯᱟᱹᱨᱥᱤ ᱵᱟᱪᱷᱟᱣ", "ᱥᱟᱹᱢᱟᱹᱱ ᱯᱟᱹᱨᱥᱤ:", "ᱱᱤᱛᱤ ᱜᱟᱱ ᱡᱚᱱᱚ", "ᱟᱢᱟᱜ ᱠᱟᱹᱹᱦᱱᱤ ᱦᱟᱹᱹᱭ", "ᱵᱟ ᱠᱟᱹᱹᱦᱱᱤ ᱚᱞ", "ᱞᱟᱹᱜᱤᱫ ᱠᱟᱹᱹᱦᱱᱤ", "ᱥᱟᱦᱠᱟᱨ-ᱵᱟᱱᱤ ᱠᱟᱹᱹᱦᱱᱤ", "ᱠᱤᱥᱟᱱ ᱠᱟᱹᱹᱦᱱᱤ", "ᱥᱟᱦᱠᱟᱨ-ᱵᱟᱱᱤ ᱡᱟᱹᱹᱵᱟᱵ", "ᱡᱟᱹᱹᱵᱟᱵ ᱟᱧᱤᱭᱟᱹ"),
    "Sindhi (सिंधी)": ("सहकार-वाणी", "پنهنجي ٻولي چونڊيو", "فعال ٻولي:", "پاليسي ڄاڻ منصوبا", "پنهنجو سوال ڳالهايو", "يا سوال لکو", "جلدي سوال", "سहकार-वाणी کان پڇو", "هاري جو سوال", "سहकार-वाणी جو جواب", "جواب ٻڌو"),
    "Tamil (தமிழ்)": ("சஹகார்-வாணி", "உங்கள் மொழியைத் தேர்ந்தெடுக்கவும்", "செயலில் உள்ள மொழி:", "கொள்கை அறிவுத் திட்டங்கள்", "உங்கள் கேள்வியைப் பேசுங்கள்", "அல்லது கேள்வியை எழுதுங்கள்", "விரைவு கேள்விகள்", "சஹகார்-வாணியிடம் கேளுங்கள்", "விவசாயியின் கேள்வி", "சஹகார்-வாணியின் பதில்", "பதிலைக் கேளுங்கள்"),
    "Telugu (తెలుగు)": ("సహకార్-వాణి", "మీ భాషను ఎంచుకోండి", "క్రియాశీల భాష:", "విధాన జ్ఞాన పథకాలు", "మీ ప్రశ్నను మాట్లాడండి", "లేదా ప్రశ్నను వ్రాయండి", "త్వరిత ప్రశ్నలు", "సహకార్-వాణిని అడగండి", "రైతు ప్రశ్న", "సహకార్-వాణి సమాధానం", "సమాధానం వినండి"),
    "Urdu (اردو)": ("سہکار-وانی", "اپنی زبان منتخب کریں", "فعال زبان:", "پالیسی علمی منصوبے", "اپنا سوال بولیں", "یا سوال لکھیں", "فوری سوالات", "سہکار-وانی سے پوچھیں", "کسان کا سوال", "سہکار-وانی کا جواب", "جواب سنیں"),
}


# Extra visible strings for the remaining project languages.  The important
# rule here is that once a farmer chooses a language, no English UI fallback
# is used for the dashboard.  Scheme acronyms (PMFBY/KCC/PACS/e-NAM) remain
# unchanged because they are official programme names.
SHORT_EXTRAS = {
    "Assamese (অসমীয়া)": {
        "tag": "সহকাৰ মন্ত্ৰালয় • ভাৰত চৰকাৰ", "subtitle": "ৰাষ্ট্ৰীয় কৃষি ভইচ কিয়স্ক",
        "gate_help": "আপুনি যি ভাষাত কথা ক’ব, সেই ভাষাতেই ভইচ লিখিত ৰূপ, AI উত্তৰ আৰু ভইচ প্লেবেক হ’ব।", "gate_btn": "ভইচ টাৰ্মিনেলত প্ৰৱেশ কৰক ➔",
        "pmfby_sub": "শস্য বীমা", "kcc_sub": "ঋণ আৰু ক্ৰেডিট", "pacs_sub": "সমবায় নিয়ম", "soil_sub": "মাটিৰ পৰীক্ষা", "enam_sub": "বজাৰত বিক্ৰী",
        "audio_help": "মাইক্ৰ’ফোনত ক্লিক কৰি প্ৰশ্ন কওক বা তলত লিখক।", "typed_placeholder": "উদাহৰণ: KCC কি?", "listening_msg": "আপোনাৰ কথা লিখিত ৰূপলৈ সলনি কৰা হৈছে...", "checking_msg": "প্ৰমাণিত নীতি নথি পৰীক্ষা কৰা হৈছে...", "tts_msg": "উত্তৰৰ কণ্ঠ প্ৰস্তুত কৰা হৈছে...",
        "source_label": "📌 প্ৰমাণিত চৰকাৰী উৎস", "view_sources": "📖 এই উত্তৰৰ বাবে ব্যৱহাৰ কৰা নীতিৰ অংশ চাওক", "knowledge_match": "জ্ঞান মিল", "response_time": "উত্তৰৰ সময়", "answer_language": "উত্তৰৰ ভাষা",
        "helpline_header": "🚨 চৰকাৰী সহায় আৰু অভিযোগ", "grievance_expander": "অভিযোগ পঞ্জীয়ন কৰক", "mobile_label": "ম’বাইল নম্বৰ", "complaint_label": "অভিযোগ / সমস্যা", "submit_btn": "অভিযোগ পঠিয়াওক", "ticket_missing": "ম’বাইল নম্বৰ আৰু অভিযোগ দুয়োটা দিয়ক", "new_session": "🔄 নতুন সেশ্যন", "footer": "সহকাৰ-ৱাণী • কৃষক সহায় কিয়স্ক",
        "normal": "স্বাভাৱিক", "slow": "লাহে", "text_size": "লিখনৰ আকাৰ", "voice_speed": "ভইচৰ গতি",
    },
    "Bodo (बर')": {
        "tag": "सहकार मंत्रालय • भारत सरकार", "subtitle": "राष्ट्रीय कृषि भ्वाइस कियोस्क", "gate_help": "नों जेराव बाजो, भ्वाइस लिखित रूप, AI जवाब आरो भ्वाइस प्लेबेक बे रावआव जाबाय।", "gate_btn": "भ्वाइस टर्मिनालाव सिगाङाव ➔",
        "pmfby_sub": "फसल बिमा", "kcc_sub": "ऋण आरो क्रेडिट", "pacs_sub": "सहकारी नियम", "soil_sub": "माटि परीक्षण", "enam_sub": "बजार बिक्री", "audio_help": "माइक्रोफोनआव क्लिक खालामनानै सोंथि बाजो एबा लिर।", "typed_placeholder": "उदाहरण: KCC मा?", "listening_msg": "नोंनि बाजनायखौ लिखितआव सोलायगासिनो...", "checking_msg": "प्रमाणित नीति फोरमाननि नायखांनि...", "tts_msg": "जवाबनि भ्वाइस फोसाबगासिनो...", "source_label": "📌 प्रमाणित सरकारी फोरमान", "view_sources": "📖 बे जवाबनि थाखाय बाहायनाय नीति अंश नाय", "knowledge_match": "ज्ञान मिल", "response_time": "जवाब समय", "answer_language": "जवाबनि राव", "helpline_header": "🚨 सरकारी मदद आरो शिकायत", "grievance_expander": "शिकायत दायेर खालाम", "mobile_label": "मोबाइल नम्बर", "complaint_label": "शिकायत / समस्या", "submit_btn": "शिकायत दाजाब", "ticket_missing": "मोबाइल नम्बर आरो शिकायत दाजाब", "new_session": "🔄 गोदान सेसन", "footer": "सहकार-वाणी • किसान सहायता कियोस्क", "normal": "सामान्य", "slow": "देर", "text_size": "लिरथि साइज", "voice_speed": "भ्वाइसनि स्पीड",
    },
    "Dogri (डोगरी)": {
        "tag": "सहकार मंत्रालय • भारत सरकार", "subtitle": "राष्ट्रीय कृषि आवाज़ कियोस्क", "gate_help": "तुस जिस भाशा च बोलोगे, ओसै भाशा च आवाज़ लिखत, AI जवाब ते आवाज़ सुनाई जाग।", "gate_btn": "आवाज़ टर्मिनल च जाओ ➔", "pmfby_sub": "फसल बीमा", "kcc_sub": "कर्जा ते क्रेडिट", "pacs_sub": "सहकारी नियम", "soil_sub": "मिट्टी जांच", "enam_sub": "मंडी बिक्री", "audio_help": "माइक्रोफोन पर क्लिक करियै सवाल बोलो जां थल्ले लिखो।", "typed_placeholder": "मिसाल: KCC केह् ऐ?", "listening_msg": "तुआढ़ी गल्ल लिखत च बदली जा करदी ऐ...", "checking_msg": "पक्के नीति दस्तावेज़ जांचे जा करदे न...", "tts_msg": "जवाब दी आवाज़ तैयार होआ करदी ऐ...", "source_label": "📌 पक्का सरकारी स्रोत", "view_sources": "📖 इस जवाब आस्तै बरते नीति अंश दिखाओ", "knowledge_match": "ज्ञान मेल", "response_time": "जवाब समां", "answer_language": "जवाब दी भाशा", "helpline_header": "🚨 सरकारी मदद ते शिकायत", "grievance_expander": "शिकायत दर्ज करो", "mobile_label": "मोबाइल नंबर", "complaint_label": "शिकायत / मसला", "submit_btn": "शिकायत जमा करो", "ticket_missing": "मोबाइल नंबर ते शिकायत दोनों भरो", "new_session": "🔄 नमीं सत्र", "footer": "सहकार-वाणी • किसान सहायता कियोस्क", "normal": "सामान्य", "slow": "हौली", "text_size": "लिखत दा आकार", "voice_speed": "आवाज़ दी रफ्तार",
    },
    "Kannada (ಕನ್ನಡ)": {
        "tag": "ಸಹಕಾರ ಸಚಿವಾಲಯ • ಭಾರತ ಸರ್ಕಾರ", "subtitle": "ರಾಷ್ಟ್ರೀಯ ಕೃಷಿ ಧ್ವನಿ ಕಿಯೋಸ್ಕ್", "gate_help": "ನೀವು ಮಾತನಾಡುವ ಭಾಷೆಯಲ್ಲೇ ಧ್ವನಿ ಲಿಪ್ಯಂತರ, AI ಉತ್ತರ ಮತ್ತು ಧ್ವನಿ ಪ್ಲೇಬ್ಯಾಕ್ ಇರುತ್ತದೆ.", "gate_btn": "ಧ್ವನಿ ಟರ್ಮಿನಲ್ ಪ್ರವೇಶಿಸಿ ➔", "pmfby_sub": "ಬೆಳೆ ವಿಮೆ", "kcc_sub": "ಸಾಲ ಮತ್ತು ಕ್ರೆಡಿಟ್", "pacs_sub": "ಸಹಕಾರಿ ನಿಯಮಗಳು", "soil_sub": "ಮಣ್ಣಿನ ಪರೀಕ್ಷೆ", "enam_sub": "ಮಾರುಕಟ್ಟೆ ಮಾರಾಟ", "audio_help": "ಮೈಕ್ರೋಫೋನ್ ಕ್ಲಿಕ್ ಮಾಡಿ ಪ್ರಶ್ನೆ ಕೇಳಿ ಅಥವಾ ಕೆಳಗೆ ಬರೆಯಿರಿ.", "typed_placeholder": "ಉದಾಹರಣೆ: KCC ಎಂದರೇನು?", "listening_msg": "ನಿಮ್ಮ ಮಾತನ್ನು ಪಠ್ಯಕ್ಕೆ ಬದಲಾಯಿಸಲಾಗುತ್ತಿದೆ...", "checking_msg": "ಪರಿಶೀಲಿಸಿದ ನೀತಿ ದಾಖಲೆಗಳನ್ನು ನೋಡಲಾಗುತ್ತಿದೆ...", "tts_msg": "ಉತ್ತರದ ಧ್ವನಿಯನ್ನು ಸಿದ್ಧಪಡಿಸಲಾಗುತ್ತಿದೆ...", "source_label": "📌 ಪರಿಶೀಲಿಸಿದ ಅಧಿಕೃತ ಮೂಲ", "view_sources": "📖 ಈ ಉತ್ತರಕ್ಕೆ ಬಳಸಿದ ನೀತಿ ಭಾಗಗಳನ್ನು ನೋಡಿ", "knowledge_match": "ಜ್ಞಾನ ಹೊಂದಾಣಿಕೆ", "response_time": "ಉತ್ತರ ಸಮಯ", "answer_language": "ಉತ್ತರದ ಭಾಷೆ", "helpline_header": "🚨 ಅಧಿಕೃತ ಸಹಾಯ ಮತ್ತು ದೂರು", "grievance_expander": "ದೂರು ದಾಖಲಿಸಿ", "mobile_label": "ಮೊಬೈಲ್ ಸಂಖ್ಯೆ", "complaint_label": "ದೂರು / ಸಮಸ್ಯೆ", "submit_btn": "ದೂರು ಸಲ್ಲಿಸಿ", "ticket_missing": "ಮೊಬೈಲ್ ಸಂಖ್ಯೆ ಮತ್ತು ದೂರು ಎರಡನ್ನೂ ನೀಡಿ", "new_session": "🔄 ಹೊಸ ಸೆಷನ್", "footer": "ಸಹಕಾರ-ವಾಣಿ • ರೈತ ಸಹಾಯ ಕಿಯೋಸ್ಕ್", "normal": "ಸಾಮಾನ್ಯ", "slow": "ನಿಧಾನ", "text_size": "ಪಠ್ಯ ಗಾತ್ರ", "voice_speed": "ಧ್ವನಿ ವೇಗ",
    },
    "Kashmiri (कॉशुर)": {
        "tag": "सहकार मंत्रालय • भारत सरकार", "subtitle": "राष्ट्रीय कृषि आवाज़ कियोस्क", "gate_help": "युस भाषा तुस वोलिव, तेमिस भाषा च आवाज़ लिखत, AI जवाब ते आवाज़ सुनावन होई।", "gate_btn": "आवाज़ टर्मिनल मंज़ दखल ➔", "pmfby_sub": "फसल बीमा", "kcc_sub": "कर्ज़ ते क्रेडिट", "pacs_sub": "सहकारी क़ायदे", "soil_sub": "मिट्टी जाँच", "enam_sub": "मंडी बिक्री", "audio_help": "माइक्रोफोन पय क्लिक करिथ सवाल वोलिव या थल लिखिव।", "typed_placeholder": "मिसाल: KCC क्या छू?", "listening_msg": "तोह्यी आवाज़ लिखत मंज़ बदलान...", "checking_msg": "पक्का नीति दस्तावेज़ जाँच करान...", "tts_msg": "जवाबु आवाज़ तैयार करान...", "source_label": "📌 पक्का सरकारी स्रोत", "view_sources": "📖 अस जवाब खातिर इस्तेमाल नीति अंश वुछिव", "knowledge_match": "मालूमात मेल", "response_time": "जवाब समय", "answer_language": "जवाब भाषा", "helpline_header": "🚨 सरकारी मदद ते शिकायत", "grievance_expander": "शिकायत दर्ज करिव", "mobile_label": "मोबाइल नंबर", "complaint_label": "शिकायत / मसला", "submit_btn": "शिकायत जमा करिव", "ticket_missing": "मोबाइल नंबर ते शिकायत दुनियी द्यिव", "new_session": "🔄 नव सत्र", "footer": "सहकार-वाणी • किसान सहायता कियोस्क", "normal": "सामान्य", "slow": "आहिस्ता", "text_size": "लिखत आकार", "voice_speed": "आवाज़ रफ्तार",
    },
    "Konkani (कोंकणी)": {
        "tag": "सहकार मंत्रालय • भारत सरकार", "subtitle": "राष्ट्रीय शेती आवाज कियोस्क", "gate_help": "तुमी ज्या भाशेंत उलोवतात, त्याच भाशेंत आवाज लेखन, AI जाप आनी आवाज ऐकपाक मेळटा.", "gate_btn": "आवाज टर्मिनलांत येयात ➔", "pmfby_sub": "पिकाचो विमो", "kcc_sub": "कर्ज आनी क्रेडिट", "pacs_sub": "सहकारी नियम", "soil_sub": "माती तपासणी", "enam_sub": "बाजार विक्री", "audio_help": "मायक्रोफोनार क्लिक करून प्रस्न उलोवात वा सकयल बरयात.", "typed_placeholder": "उदाहरण: KCC कितें?", "listening_msg": "तुमचो आवाज मजकुरांत बदलता...", "checking_msg": "तपासलेली धोरण कागदपत्रां तपासतात...", "tts_msg": "जापाचो आवाज तयार जाता...", "source_label": "📌 तपासलेलो सरकारी स्रोत", "view_sources": "📖 ह्या जापाखातीर वापरिल्ले धोरण भाग पळयात", "knowledge_match": "ज्ञान मेळ", "response_time": "जाप वेळ", "answer_language": "जापाची भास", "helpline_header": "🚨 सरकारी मदत आनी तक्रार", "grievance_expander": "तक्रार नोंदणी करात", "mobile_label": "मोबायल नंबर", "complaint_label": "तक्रार / समस्या", "submit_btn": "तक्रार धाडात", "ticket_missing": "मोबायल नंबर आनी तक्रार दियात", "new_session": "🔄 नवो सत्र", "footer": "सहकार-वाणी • शेतकरी मदत कियोस्क", "normal": "सामान्य", "slow": "हळू", "text_size": "मजकुराचो आकार", "voice_speed": "आवाजाची गती",
    },
    "Maithili (मैथिली)": {
        "tag": "सहकार मंत्रालय • भारत सरकार", "subtitle": "राष्ट्रीय कृषि आवाज कियोस्क", "gate_help": "अहाँ जे भाषा मे बाजब, ओहि भाषा मे आवाज लिखित रूप, AI उत्तर आ आवाज सुनाइ देल जायत।", "gate_btn": "आवाज टर्मिनल मे प्रवेश करू ➔", "pmfby_sub": "फसल बीमा", "kcc_sub": "ऋण आ क्रेडिट", "pacs_sub": "सहकारी नियम", "soil_sub": "माटि परीक्षण", "enam_sub": "मंडी बिक्री", "audio_help": "माइक्रोफोन पर क्लिक कऽ प्रश्न बाजू अथवा नीचाँ लिखू।", "typed_placeholder": "उदाहरण: KCC की अछि?", "listening_msg": "अहाँक बात लिखित रूप मे बदलल जा रहल अछि...", "checking_msg": "प्रमाणित नीति दस्तावेज देखल जा रहल अछि...", "tts_msg": "उत्तरक आवाज तैयार कएल जा रहल अछि...", "source_label": "📌 प्रमाणित सरकारी स्रोत", "view_sources": "📖 एहि उत्तर लेल उपयोग कएल नीति अंश देखू", "knowledge_match": "ज्ञान मिलान", "response_time": "उत्तर समय", "answer_language": "उत्तरक भाषा", "helpline_header": "🚨 सरकारी सहायता आ शिकायत", "grievance_expander": "शिकायत दर्ज करू", "mobile_label": "मोबाइल नंबर", "complaint_label": "शिकायत / समस्या", "submit_btn": "शिकायत जमा करू", "ticket_missing": "मोबाइल नंबर आ शिकायत दुनू दिअ", "new_session": "🔄 नव सत्र", "footer": "सहकार-वाणी • किसान सहायता कियोस्क", "normal": "सामान्य", "slow": "धीमा", "text_size": "पाठ आकार", "voice_speed": "आवाज गति",
    },
    "Malayalam (മലയാളം)": {
        "tag": "സഹകരണ മന്ത്രാലയം • ഭാരത സർക്കാർ", "subtitle": "ദേശീയ കാർഷിക വോയ്സ് കിയോസ്ക്", "gate_help": "നിങ്ങൾ സംസാരിക്കുന്ന അതേ ഭാഷയിൽ ശബ്ദ ലിപ്യന്തരണം, AI മറുപടി, ശബ്ദ പ്ലേബാക്ക് ലഭിക്കും.", "gate_btn": "വോയ്സ് ടെർമിനലിലേക്ക് പ്രവേശിക്കുക ➔", "pmfby_sub": "വിള ഇൻഷുറൻസ്", "kcc_sub": "വായ്പയും ക്രെഡിറ്റും", "pacs_sub": "സഹകരണ നിയമങ്ങൾ", "soil_sub": "മണ്ണ് പരിശോധന", "enam_sub": "ചന്ത വിൽപ്പന", "audio_help": "മൈക്രോഫോണിൽ ക്ലിക്ക് ചെയ്ത് ചോദ്യം പറയുക അല്ലെങ്കിൽ താഴെ എഴുതുക.", "typed_placeholder": "ഉദാഹരണം: KCC എന്താണ്?", "listening_msg": "നിങ്ങളുടെ ശബ്ദം എഴുത്തിലേക്ക് മാറ്റുന്നു...", "checking_msg": "പരിശോധിച്ച നയ രേഖകൾ പരിശോധിക്കുന്നു...", "tts_msg": "മറുപടിയുടെ ശബ്ദം തയ്യാറാക്കുന്നു...", "source_label": "📌 പരിശോധിച്ച ഔദ്യോഗിക ഉറവിടം", "view_sources": "📖 ഈ മറുപടിക്ക് ഉപയോഗിച്ച നയ ഭാഗങ്ങൾ കാണുക", "knowledge_match": "അറിവ് പൊരുത്തം", "response_time": "മറുപടി സമയം", "answer_language": "മറുപടി ഭാഷ", "helpline_header": "🚨 ഔദ്യോഗിക സഹായവും പരാതിയും", "grievance_expander": "പരാതി രജിസ്റ്റർ ചെയ്യുക", "mobile_label": "മൊബൈൽ നമ്പർ", "complaint_label": "പരാതി / പ്രശ്നം", "submit_btn": "പരാതി സമർപ്പിക്കുക", "ticket_missing": "മൊബൈൽ നമ്പറും പരാതിയും നൽകുക", "new_session": "🔄 പുതിയ സെഷൻ", "footer": "സഹകാർ-വാണി • കർഷക സഹായ കിയോസ്ക്", "normal": "സാധാരണ", "slow": "പതുക്കെ", "text_size": "വാചക വലുപ്പം", "voice_speed": "ശബ്ദ വേഗത",
    },
    "Manipuri (ꯃꯩꯇꯩꯂꯣꯟ)": {
        "tag": "ꯁꯍꯀꯥꯔ ꯃꯟꯇ꯭ꯔꯤꯄꯤꯁ • ꯐ꯭ꯔꯤꯇꯤꯁ ꯁꯔꯀꯥꯔ", "subtitle": "ꯅꯦꯁꯅꯦꯜ ꯀ꯭ꯔꯥꯏꯁꯤ ꯋꯣꯏꯁ ꯀꯤꯑꯣꯁ꯭ꯀ", "gate_help": "ꯅꯍꯥꯛꯅ ꯍꯥꯏꯕ ꯂꯣꯟ ꯑꯗꯨꯗꯥ ꯋꯣꯏꯁ ꯇ꯭ꯔꯥꯟꯁꯀ꯭ꯔꯤꯄꯁꯟ, AI ꯄꯥꯎꯖꯦꯜ ꯑꯃꯁꯨꯡ ꯋꯣꯏꯁ ꯄ꯭ꯂꯦꯕꯦꯛ ꯂꯩꯒꯅꯤ।", "gate_btn": "ꯋꯣꯏꯁ ꯇꯔꯃꯤꯅꯦꯜꯗ ꯆꯪꯕꯤꯌꯨ ➔", "pmfby_sub": "ꯐꯁꯜ ꯕꯤꯃꯥ", "kcc_sub": "ꯂꯣꯟ ꯑꯃꯁꯨꯡ ꯀ꯭ꯔꯦꯗꯤꯠ", "pacs_sub": "ꯀꯣꯑꯣꯄꯔꯦꯇꯤꯕ ꯅꯤꯌꯝ", "soil_sub": "ꯃꯇꯤ ꯇꯦꯁ꯭ꯇ", "enam_sub": "ꯃꯥꯔꯀꯦꯠ ꯁꯦꯜ", "audio_help": "ꯃꯥꯏꯀ꯭ꯔꯣꯐꯣꯟꯗ ꯀ꯭ꯂꯤꯛ ꯇꯧꯕꯤꯌꯨ ꯑꯃꯁꯨꯡ ꯋꯥꯍꯪ ꯍꯥꯏꯕꯤꯌꯨ ꯅꯠꯇ꯭ꯔꯒꯥ ꯂꯤꯔꯛꯎ।", "typed_placeholder": "ꯑꯣꯏꯁ꯭ꯇꯔꯦꯜ: KCC ꯀꯔꯤꯅꯣ?", "listening_msg": "ꯅꯍꯥꯛꯀꯤ ꯋꯥꯍꯪ ꯃꯇꯨꯡ ꯄꯥꯎꯖꯦꯜꯗ ꯑꯣꯏꯕꯥ...", "checking_msg": "ꯄ꯭ꯔꯃꯥꯅꯤꯇ ꯅꯤꯌꯝ ꯐꯣꯔꯝ ꯅꯦꯏꯕꯥ...", "tts_msg": "ꯄꯥꯎꯖꯦꯜꯒꯤ ꯋꯣꯏꯁ ꯁꯤꯗ꯭ꯔꯤ...", "source_label": "📌 ꯄ꯭ꯔꯃꯥꯅꯤꯇ ꯁꯔꯀꯥꯔꯤ ꯁꯣꯔꯁ", "view_sources": "📖 ꯃꯁꯤꯒꯤ ꯄꯥꯎꯖꯦꯜꯗ ꯅꯤꯌꯝ ꯑꯪꯁ ꯌꯦꯡꯎ", "knowledge_match": "ꯃꯥꯂꯨꯝ ꯃꯥꯅꯥ", "response_time": "ꯄꯥꯎꯖꯦꯜ ꯃꯇꯝ", "answer_language": "ꯄꯥꯎꯖꯦꯜꯒꯤ ꯂꯣꯟ", "helpline_header": "🚨 ꯁꯔꯀꯥꯔꯤ ꯃꯇꯦꯡ ꯑꯃꯁꯨꯡ ꯁꯤꯇꯤ", "grievance_expander": "ꯁꯤꯇꯤ ꯂꯤꯈꯎ", "mobile_label": "ꯃꯣꯕꯥꯏꯜ ꯅꯝꯕꯔ", "complaint_label": "ꯁꯤꯇꯤ / ꯁꯤꯕꯤꯔ", "submit_btn": "ꯁꯤꯇꯤ ꯊꯥꯗꯣꯛꯎ", "ticket_missing": "ꯃꯣꯕꯥꯏꯜ ꯅꯝꯕꯔ ꯑꯃꯁꯨꯡ ꯁꯤꯇꯤ ꯄꯤꯕꯤꯌꯨ", "new_session": "🔄 ꯑꯅꯧꯕ ꯁꯦꯁꯟ", "footer": "ꯁꯍꯀꯥꯔ-ꯋꯥꯅꯤ • ꯁꯦꯜꯐꯥꯔ ꯁꯍꯥꯏ ꯀꯤꯑꯣꯁ꯭ꯀ", "normal": "ꯅꯣꯔꯃꯥꯜ", "slow": "ꯅꯤꯃꯤꯠ", "text_size": "ꯄꯥꯎꯖꯦꯜ ꯁꯥꯏꯖ", "voice_speed": "ꯋꯣꯏꯁ ꯁ꯭ꯄꯤꯗ",
    },
    "Nepali (नेपाली)": {
        "tag": "सहकार मन्त्रालय • भारत सरकार", "subtitle": "राष्ट्रिय कृषि भ्वाइस कियोस्क", "gate_help": "तपाईंले बोल्ने भाषामै आवाज लिप्यन्तरण, AI उत्तर र आवाज प्लेब्याक हुनेछ।", "gate_btn": "भ्वाइस टर्मिनलमा प्रवेश गर्नुहोस् ➔", "pmfby_sub": "बाली बीमा", "kcc_sub": "ऋण र क्रेडिट", "pacs_sub": "सहकारी नियम", "soil_sub": "माटो परीक्षण", "enam_sub": "बजार बिक्री", "audio_help": "माइक्रोफोनमा क्लिक गरेर प्रश्न बोल्नुहोस् वा तल लेख्नुहोस्।", "typed_placeholder": "उदाहरण: KCC के हो?", "listening_msg": "तपाईंको आवाजलाई पाठमा बदलिँदैछ...", "checking_msg": "प्रमाणित नीति कागजात जाँचिँदैछ...", "tts_msg": "उत्तरको आवाज तयार हुँदैछ...", "source_label": "📌 प्रमाणित आधिकारिक स्रोत", "view_sources": "📖 यो उत्तरका लागि प्रयोग गरिएका नीति अंश हेर्नुहोस्", "knowledge_match": "ज्ञान मिलान", "response_time": "उत्तर समय", "answer_language": "उत्तरको भाषा", "helpline_header": "🚨 सरकारी सहायता र गुनासो", "grievance_expander": "गुनासो दर्ता गर्नुहोस्", "mobile_label": "मोबाइल नम्बर", "complaint_label": "गुनासो / समस्या", "submit_btn": "गुनासो पठाउनुहोस्", "ticket_missing": "मोबाइल नम्बर र गुनासो दुवै दिनुहोस्", "new_session": "🔄 नयाँ सत्र", "footer": "सहकार-वाणी • किसान सहायता कियोस्क", "normal": "सामान्य", "slow": "ढिलो", "text_size": "पाठ आकार", "voice_speed": "आवाज गति",
    },
    "Odia (ଓଡ଼ିଆ)": {
        "tag": "ସମବାୟ ମନ୍ତ୍ରଣାଳୟ • ଭାରତ ସରକାର", "subtitle": "ଜାତୀୟ କୃଷି ଭଏସ୍ କିଓସ୍କ", "gate_help": "ଆପଣ ଯେଉଁ ଭାଷାରେ କହିବେ, ସେହି ଭାଷାରେ ଭଏସ୍ ଲିପ୍ୟନ୍ତରଣ, AI ଉତ୍ତର ଏବଂ ଭଏସ୍ ପ୍ଲେବ୍ୟାକ୍ ହେବ।", "gate_btn": "ଭଏସ୍ ଟର୍ମିନାଲ୍ ପ୍ରବେଶ କରନ୍ତୁ ➔", "pmfby_sub": "ଫସଲ ବୀମା", "kcc_sub": "ଋଣ ଓ କ୍ରେଡିଟ୍", "pacs_sub": "ସମବାୟ ନିୟମ", "soil_sub": "ମାଟି ପରୀକ୍ଷା", "enam_sub": "ମଣ୍ଡି ବିକ୍ରୟ", "audio_help": "ମାଇକ୍ରୋଫୋନରେ କ୍ଲିକ୍ କରି ପ୍ରଶ୍ନ କୁହନ୍ତୁ କିମ୍ବା ତଳେ ଲେଖନ୍ତୁ।", "typed_placeholder": "ଉଦାହରଣ: KCC କ’ଣ?", "listening_msg": "ଆପଣଙ୍କ କଥାକୁ ଲେଖାରେ ବଦଳାଯାଉଛି...", "checking_msg": "ପ୍ରମାଣିତ ନୀତି ଦସ୍ତାବେଜ ଯାଞ୍ଚ ହେଉଛି...", "tts_msg": "ଉତ୍ତରର ଭଏସ୍ ପ୍ରସ୍ତୁତ ହେଉଛି...", "source_label": "📌 ପ୍ରମାଣିତ ସରକାରୀ ଉତ୍ସ", "view_sources": "📖 ଏହି ଉତ୍ତର ପାଇଁ ବ୍ୟବହୃତ ନୀତି ଅଂଶ ଦେଖନ୍ତୁ", "knowledge_match": "ଜ୍ଞାନ ମେଳ", "response_time": "ଉତ୍ତର ସମୟ", "answer_language": "ଉତ୍ତର ଭାଷା", "helpline_header": "🚨 ସରକାରୀ ସହାୟତା ଓ ଅଭିଯୋଗ", "grievance_expander": "ଅଭିଯୋଗ ଦାଖଲ କରନ୍ତୁ", "mobile_label": "ମୋବାଇଲ୍ ନମ୍ବର", "complaint_label": "ଅଭିଯୋଗ / ସମସ୍ୟା", "submit_btn": "ଅଭିଯୋଗ ପଠାନ୍ତୁ", "ticket_missing": "ମୋବାଇଲ୍ ନମ୍ବର ଓ ଅଭିଯୋଗ ଦିଅନ୍ତୁ", "new_session": "🔄 ନୂଆ ସେସନ୍", "footer": "ସହକାର-ବାଣୀ • କୃଷକ ସହାୟତା କିଓସ୍କ", "normal": "ସାଧାରଣ", "slow": "ଧୀର", "text_size": "ପାଠ ଆକାର", "voice_speed": "ଭଏସ୍ ଗତି",
    },
    "Punjabi (ਪੰਜਾਬੀ)": {
        "tag": "ਸਹਿਕਾਰਤਾ ਮੰਤਰਾਲਾ • ਭਾਰਤ ਸਰਕਾਰ", "subtitle": "ਰਾਸ਼ਟਰੀ ਖੇਤੀਬਾੜੀ ਵੌਇਸ ਕਿਓਸਕ", "gate_help": "ਤੁਸੀਂ ਜਿਸ ਭਾਸ਼ਾ ਵਿੱਚ ਬੋਲੋਗੇ, ਉਸੇ ਭਾਸ਼ਾ ਵਿੱਚ ਵੌਇਸ ਲਿਖਤ, AI ਜਵਾਬ ਅਤੇ ਆਵਾਜ਼ ਚੱਲੇਗੀ।", "gate_btn": "ਵੌਇਸ ਟਰਮੀਨਲ ਵਿੱਚ ਦਾਖਲ ਹੋਵੋ ➔", "pmfby_sub": "ਫਸਲ ਬੀਮਾ", "kcc_sub": "ਕਰਜ਼ਾ ਅਤੇ ਕ੍ਰੈਡਿਟ", "pacs_sub": "ਸਹਿਕਾਰੀ ਨਿਯਮ", "soil_sub": "ਮਿੱਟੀ ਜਾਂਚ", "enam_sub": "ਮੰਡੀ ਵਿਕਰੀ", "audio_help": "ਮਾਈਕ੍ਰੋਫੋਨ ਤੇ ਕਲਿੱਕ ਕਰਕੇ ਸਵਾਲ ਬੋਲੋ ਜਾਂ ਹੇਠਾਂ ਲਿਖੋ।", "typed_placeholder": "ਉਦਾਹਰਨ: KCC ਕੀ ਹੈ?", "listening_msg": "ਤੁਹਾਡੀ ਗੱਲ ਨੂੰ ਲਿਖਤ ਵਿੱਚ ਬਦਲਿਆ ਜਾ ਰਿਹਾ ਹੈ...", "checking_msg": "ਪ੍ਰਮਾਣਿਤ ਨੀਤੀ ਦਸਤਾਵੇਜ਼ ਜਾਂਚੇ ਜਾ ਰਹੇ ਹਨ...", "tts_msg": "ਜਵਾਬ ਦੀ ਆਵਾਜ਼ ਤਿਆਰ ਕੀਤੀ ਜਾ ਰਹੀ ਹੈ...", "source_label": "📌 ਪ੍ਰਮਾਣਿਤ ਸਰਕਾਰੀ ਸਰੋਤ", "view_sources": "📖 ਇਸ ਜਵਾਬ ਲਈ ਵਰਤੇ ਨੀਤੀ ਹਿੱਸੇ ਵੇਖੋ", "knowledge_match": "ਗਿਆਨ ਮੇਲ", "response_time": "ਜਵਾਬ ਸਮਾਂ", "answer_language": "ਜਵਾਬ ਦੀ ਭਾਸ਼ਾ", "helpline_header": "🚨 ਸਰਕਾਰੀ ਮਦਦ ਅਤੇ ਸ਼ਿਕਾਇਤ", "grievance_expander": "ਸ਼ਿਕਾਇਤ ਦਰਜ ਕਰੋ", "mobile_label": "ਮੋਬਾਈਲ ਨੰਬਰ", "complaint_label": "ਸ਼ਿਕਾਇਤ / ਸਮੱਸਿਆ", "submit_btn": "ਸ਼ਿਕਾਇਤ ਭੇਜੋ", "ticket_missing": "ਮੋਬਾਈਲ ਨੰਬਰ ਅਤੇ ਸ਼ਿਕਾਇਤ ਦੋਵੇਂ ਦਿਓ", "new_session": "🔄 ਨਵਾਂ ਸੈਸ਼ਨ", "footer": "ਸਹਕਾਰ-ਵਾਣੀ • ਕਿਸਾਨ ਸਹਾਇਤਾ ਕਿਓਸਕ", "normal": "ਸਧਾਰਨ", "slow": "ਹੌਲੀ", "text_size": "ਲਿਖਤ ਆਕਾਰ", "voice_speed": "ਆਵਾਜ਼ ਦੀ ਗਤੀ",
    },
    "Sanskrit (संस्कृतम्)": {
        "tag": "सहकारमन्त्रालयः • भारतसर्वकारः", "subtitle": "राष्ट्रीयकृषिवाणीकेन्द्रम्", "gate_help": "भवान् यया भाषया वदति तस्यामेव भाषायां ध्वनिलिप्यन्तरणं, AI-उत्तरं, ध्वनिप्रसारणं च भविष्यति।", "gate_btn": "वाणीकेन्द्रं प्रविशतु ➔", "pmfby_sub": "सस्यबीमा", "kcc_sub": "ऋणं तथा क्रेडिट्", "pacs_sub": "सहकारिनियमाः", "soil_sub": "मृत्तिकापरीक्षणम्", "enam_sub": "बाजारविक्रयः", "audio_help": "दूरवाणीं क्लिक् कृत्वा प्रश्नं वदतु अथवा अधः लिखतु।", "typed_placeholder": "उदाहरणम्: KCC किम्?", "listening_msg": "भवतः वाणी लेखरूपे परिवर्त्यते...", "checking_msg": "प्रमाणितनीतिदस्तावेजाः परीक्ष्यन्ते...", "tts_msg": "उत्तरस्य ध्वनिः सज्जीक्रियते...", "source_label": "📌 प्रमाणितं सर्वकारीय स्रोतः", "view_sources": "📖 अस्य उत्तरस्य नीत्यंशान् पश्यतु", "knowledge_match": "ज्ञानसाम्यम्", "response_time": "उत्तरसमयः", "answer_language": "उत्तरभाषा", "helpline_header": "🚨 सर्वकारीय सहायता तथा शिकायत", "grievance_expander": "शिकायतां पञ्जीकुरुत", "mobile_label": "दूरभाषसङ्ख्या", "complaint_label": "शिकायत / समस्या", "submit_btn": "शिकायतां प्रेषयतु", "ticket_missing": "दूरभाषसङ्ख्यां शिकायतां च ददातु", "new_session": "🔄 नूतनसत्रम्", "footer": "सहकार-वाणी • कृषकसहायककेन्द्रम्", "normal": "सामान्यम्", "slow": "मन्दम्", "text_size": "पाठपरिमाणम्", "voice_speed": "वाणीवेगः",
    },
    "Santali (ᱥᱟᱱᱛᱟᱲᱤ)": {
        "tag": "ᱥᱟᱦᱠᱟᱨ ᱢᱚᱱᱛᱨᱚᱱᱟᱞᱚᱭ • ᱵᱷᱟᱨᱚᱛ ᱥᱚᱨᱠᱟᱨ", "subtitle": "ᱡᱟᱛᱤᱭᱟ ᱠᱨᱤᱥᱤ ᱵᱷᱚᱭᱤᱥ ᱠᱤᱭᱚᱥᱠ", "gate_help": "ᱟᱢ ᱡᱮ ᱯᱟᱹᱨᱥᱤ ᱨᱮ ᱠᱟᱛᱷᱟ ᱠᱚᱵᱚᱞ, ᱚᱱᱟ ᱯᱟᱹᱨᱥᱤ ᱨᱮ ᱥᱟᱵᱫ ᱚᱞ, AI ᱡᱟᱹᱵᱟᱵ ᱟᱨ ᱥᱟᱵᱫ ᱯᱞᱮᱵᱮᱠ ᱦᱚᱪᱚᱜᱼᱟ।", "gate_btn": "ᱵᱷᱚᱭᱤᱥ ᱴᱟᱨᱢᱤᱱᱟᱞ ᱨᱮ ᱵᱚᱞᱚ ᱢᱮ ➔", "pmfby_sub": "ᱠᱷᱟᱹᱛᱤ ᱵᱤᱢᱟ", "kcc_sub": "ᱡᱚᱱᱚ ᱟᱨ ᱠᱨᱮᱰᱤᱴ", "pacs_sub": "ᱥᱚᱢᱵᱟᱭ ᱱᱤᱭᱚᱢ", "soil_sub": "ᱦᱟᱥᱟ ᱯᱚᱨᱤᱠᱷᱟ", "enam_sub": "ᱵᱟᱡᱟᱨ ᱵᱤᱠᱨᱤ", "audio_help": "ᱢᱟᱭᱠᱨᱚᱯᱷᱚᱱ ᱨᱮ ᱠᱞᱤᱠ ᱠᱟᱛᱮ ᱥᱚᱢᱵᱟᱫ ᱠᱚ ᱵᱚᱞ ᱢᱮ ᱟᱨᱵᱟᱝ ᱞᱤᱠᱷ ᱢᱮ।", "typed_placeholder": "ᱩᱫᱟᱹᱦᱚᱨᱚᱱ: KCC ᱪᱮᱫ?", "listening_msg": "ᱟᱢᱟᱜ ᱠᱟᱛᱷᱟ ᱚᱞ ᱨᱮ ᱵᱚᱫᱚᱞᱚᱜᱼᱟ...", "checking_msg": "ᱯᱨᱢᱟᱱᱤᱛ ᱱᱤᱛᱤ ᱫᱚᱥᱛᱟᱵᱮᱡ ᱧᱮᱞ ᱢᱮ...", "tts_msg": "ᱡᱟᱹᱵᱟᱵ ᱟᱜ ᱵᱷᱚᱭᱤᱥ ᱥᱟᱡᱟᱣ ᱢᱮ...", "source_label": "📌 ᱯᱨᱢᱟᱱᱤᱛ ᱥᱚᱨᱠᱟᱨᱤ ᱥᱚᱨᱥ", "view_sources": "📖 ᱱᱚᱶᱟ ᱡᱟᱹᱵᱟᱵ ᱨᱮ ᱵᱟᱹᱦᱟᱹᱣ ᱱᱤᱛᱤ ᱚᱝᱥ ᱧᱮᱞ ᱢᱮ", "knowledge_match": "ᱡᱟᱱᱟ ᱢᱤᱞ", "response_time": "ᱡᱟᱹᱵᱟᱵ ᱚᱠᱛᱚ", "answer_language": "ᱡᱟᱹᱵᱟᱵ ᱯᱟᱹᱨᱥᱤ", "helpline_header": "🚨 ᱥᱚᱨᱠᱟᱨᱤ ᱢᱟᱫᱟᱛ ᱟᱨ ᱥᱤᱴᱤ", "grievance_expander": "ᱥᱤᱴᱤ ᱫᱟᱠᱷᱤᱞ ᱢᱮ", "mobile_label": "ᱢᱳᱵᱟᱭᱤᱞ ᱱᱟᱢᱵᱚᱨ", "complaint_label": "ᱥᱤᱴᱤ / ᱠᱚᱢᱯᱞᱮᱱ", "submit_btn": "ᱥᱤᱴᱤ ᱡᱟᱢᱟ ᱢᱮ", "ticket_missing": "ᱢᱳᱵᱟᱭᱤᱞ ᱱᱟᱢᱵᱚᱨ ᱟᱨ ᱥᱤᱴᱤ ᱮᱢ ᱢᱮ", "new_session": "🔄 ᱱᱟᱶᱟ ᱥᱮᱥᱚᱱ", "footer": "ᱥᱟᱦᱠᱟᱨ-ᱵᱟᱱᱤ • ᱠᱤᱥᱟᱱ ᱥᱟᱦᱟᱭᱛᱟ ᱠᱤᱭᱚᱥᱠ", "normal": "ᱥᱟᱢᱟᱱᱭᱟ", "slow": "ᱫᱤᱞᱟ", "text_size": "ᱚᱞ ᱢᱟᱯ", "voice_speed": "ᱵᱷᱚᱭᱤᱥ ᱥᱤᱯᱤᱫ",
    },
    "Sindhi (सिंधी)": {
        "tag": "وزارتِ تعاون • حڪومتِ هند", "subtitle": "قومي زرعي وائس ڪِيوسڪ", "gate_help": "توهان جنهن ٻولي ۾ ڳالهائيندا، ساڳي ٻولي ۾ آواز، AI جواب ۽ آواز هلندو.", "gate_btn": "وائس ٽرمينل ۾ داخل ٿيو ➔", "pmfby_sub": "فصل انشورنس", "kcc_sub": "قرض ۽ ڪريڊٽ", "pacs_sub": "سهڪاري ضابطا", "soil_sub": "مٽي جاچ", "enam_sub": "منڊي وڪرو", "audio_help": "مائڪروفون تي ڪلڪ ڪري سوال ڳالهايو يا هيٺ لکو.", "typed_placeholder": "مثال: KCC ڇا آهي؟", "listening_msg": "توهان جي ڳالهه لکڻي ۾ بدلجي رهي آهي...", "checking_msg": "تصديق ٿيل پاليسي دستاويز ڏٺا پيا وڃن...", "tts_msg": "جواب جو آواز تيار ٿي رهيو آهي...", "source_label": "📌 تصديق ٿيل سرڪاري ذريعو", "view_sources": "📖 هن جواب لاءِ استعمال ٿيل پاليسي جا حصا ڏسو", "knowledge_match": "ڄاڻ ميل", "response_time": "جواب جو وقت", "answer_language": "جواب جي ٻولي", "helpline_header": "🚨 سرڪاري مدد ۽ شڪايت", "grievance_expander": "شڪايت داخل ڪريو", "mobile_label": "موبائل نمبر", "complaint_label": "شڪايت / مسئلو", "submit_btn": "شڪايت موڪليو", "ticket_missing": "موبائل نمبر ۽ شڪايت ٻئي ڏيو", "new_session": "🔄 نئون سيشن", "footer": "سہکار-وانی • هاري مدد ڪِيوسڪ", "normal": "عام", "slow": "آهستي", "text_size": "لکت جو ماپ", "voice_speed": "آواز جي رفتار",
    },
    "Tamil (தமிழ்)": {
        "tag": "கூட்டுறவு அமைச்சகம் • இந்திய அரசு", "subtitle": "தேசிய வேளாண்மை குரல் கியோஸ்க்", "gate_help": "நீங்கள் பேசும் அதே மொழியில் குரல் எழுத்தாக்கம், AI பதில் மற்றும் குரல் இயக்கம் இருக்கும்.", "gate_btn": "குரல் முனையத்திற்குள் செல்லவும் ➔", "pmfby_sub": "பயிர் காப்பீடு", "kcc_sub": "கடன் மற்றும் கிரெடிட்", "pacs_sub": "கூட்டுறவு விதிகள்", "soil_sub": "மண் பரிசோதனை", "enam_sub": "சந்தை விற்பனை", "audio_help": "மைக்ரோஃபோனை கிளிக் செய்து கேள்வியைப் பேசுங்கள் அல்லது கீழே எழுதுங்கள்.", "typed_placeholder": "உதாரணம்: KCC என்றால் என்ன?", "listening_msg": "உங்கள் பேச்சு எழுத்தாக மாற்றப்படுகிறது...", "checking_msg": "சரிபார்க்கப்பட்ட கொள்கை ஆவணங்கள் பார்க்கப்படுகின்றன...", "tts_msg": "பதிலின் குரல் தயாராகிறது...", "source_label": "📌 சரிபார்க்கப்பட்ட அதிகாரப்பூர்வ ஆதாரம்", "view_sources": "📖 இந்த பதிலுக்குப் பயன்படுத்திய கொள்கைப் பகுதிகளைப் பார்க்கவும்", "knowledge_match": "அறிவு பொருத்தம்", "response_time": "பதில் நேரம்", "answer_language": "பதில் மொழி", "helpline_header": "🚨 அரசு உதவி மற்றும் புகார்", "grievance_expander": "புகார் பதிவு செய்யவும்", "mobile_label": "மொபைல் எண்", "complaint_label": "புகார் / பிரச்சனை", "submit_btn": "புகாரை அனுப்பவும்", "ticket_missing": "மொபைல் எண்ணையும் புகாரையும் வழங்கவும்", "new_session": "🔄 புதிய அமர்வு", "footer": "சஹகார்-வாணி • விவசாயி உதவி கியோஸ்க்", "normal": "சாதாரணம்", "slow": "மெதுவாக", "text_size": "உரை அளவு", "voice_speed": "குரல் வேகம்",
    },
    "Telugu (తెలుగు)": {
        "tag": "సహకార మంత్రిత్వ శాఖ • భారత ప్రభుత్వం", "subtitle": "జాతీయ వ్యవసాయ వాయిస్ కియోస్క్", "gate_help": "మీరు మాట్లాడే అదే భాషలో వాయిస్ లిప్యంతరీకరణ, AI సమాధానం మరియు వాయిస్ ప్లేబ్యాక్ ఉంటుంది.", "gate_btn": "వాయిస్ టెర్మినల్‌లోకి వెళ్లండి ➔", "pmfby_sub": "పంట బీమా", "kcc_sub": "రుణం మరియు క్రెడిట్", "pacs_sub": "సహకార నియమాలు", "soil_sub": "మట్టి పరీక్ష", "enam_sub": "మార్కెట్ విక్రయం", "audio_help": "మైక్రోఫోన్‌పై క్లిక్ చేసి ప్రశ్న అడగండి లేదా క్రింద రాయండి.", "typed_placeholder": "ఉదాహరణ: KCC అంటే ఏమిటి?", "listening_msg": "మీ మాటలను వచనంగా మారుస్తోంది...", "checking_msg": "ధృవీకరించిన విధాన పత్రాలను పరిశీలిస్తోంది...", "tts_msg": "సమాధానం వాయిస్ సిద్ధమవుతోంది...", "source_label": "📌 ధృవీకరించిన అధికారిక మూలం", "view_sources": "📖 ఈ సమాధానానికి ఉపయోగించిన విధాన భాగాలను చూడండి", "knowledge_match": "జ్ఞాన సరిపోలిక", "response_time": "సమాధాన సమయం", "answer_language": "సమాధాన భాష", "helpline_header": "🚨 ప్రభుత్వ సహాయం మరియు ఫిర్యాదు", "grievance_expander": "ఫిర్యాదు నమోదు చేయండి", "mobile_label": "మొబైల్ నంబర్", "complaint_label": "ఫిర్యాదు / సమస్య", "submit_btn": "ఫిర్యాదు పంపండి", "ticket_missing": "మొబైల్ నంబర్ మరియు ఫిర్యాదు రెండూ ఇవ్వండి", "new_session": "🔄 కొత్త సెషన్", "footer": "సహకార్-వాణి • రైతు సహాయ కియోస్క్", "normal": "సాధారణం", "slow": "నెమ్మదిగా", "text_size": "వచన పరిమాణం", "voice_speed": "వాయిస్ వేగం",
    },
    "Urdu (اردو)": {
        "tag": "وزارتِ تعاون • حکومتِ ہند", "subtitle": "قومی زرعی وائس کیوسک", "gate_help": "آپ جس زبان میں بولیں گے، اسی زبان میں آواز کا متن، AI جواب اور آواز چلائی جائے گی۔", "gate_btn": "وائس ٹرمینل میں داخل ہوں ➔", "pmfby_sub": "فصل بیمہ", "kcc_sub": "قرض اور کریڈٹ", "pacs_sub": "تعاونی قواعد", "soil_sub": "مٹی کی جانچ", "enam_sub": "منڈی فروخت", "audio_help": "مائیکروفون پر کلک کرکے سوال بولیں یا نیچے لکھیں۔", "typed_placeholder": "مثال: KCC کیا ہے؟", "listening_msg": "آپ کی بات کو متن میں بدلا جا رہا ہے...", "checking_msg": "تصدیق شدہ پالیسی دستاویزات دیکھی جا رہی ہیں...", "tts_msg": "جواب کی آواز تیار کی جا رہی ہے...", "source_label": "📌 تصدیق شدہ سرکاری ماخذ", "view_sources": "📖 اس جواب کے لیے استعمال شدہ پالیسی حصے دیکھیں", "knowledge_match": "علم کی مطابقت", "response_time": "جواب کا وقت", "answer_language": "جواب کی زبان", "helpline_header": "🚨 سرکاری مدد اور شکایت", "grievance_expander": "شکایت درج کریں", "mobile_label": "موبائل نمبر", "complaint_label": "شکایت / مسئلہ", "submit_btn": "شکایت بھیجیں", "ticket_missing": "موبائل نمبر اور شکایت دونوں دیں", "new_session": "🔄 نیا سیشن", "footer": "سہکار-وانی • کسان معاون کیوسک", "normal": "عام", "slow": "آہستہ", "text_size": "متن کا سائز", "voice_speed": "آواز کی رفتار",
    },
}


# Complete the remaining visible dashboard labels for the four full packs.
PACK_COMPLETION = {
    "Hindi (हिंदी)": {
        "helpline_header": "🚨 सरकारी हेल्पलाइन और शिकायत", "grievance_expander": "शिकायत दर्ज करें", "mobile_label": "मोबाइल नंबर", "mobile_placeholder": "10 अंकों का मोबाइल नंबर लिखें", "complaint_label": "शिकायत / समस्या", "complaint_placeholder": "समस्या स्पष्ट रूप से लिखें", "submit_btn": "शिकायत भेजें", "ticket_success": "टिकट सफलतापूर्वक दर्ज हुआ:", "ticket_missing": "मोबाइल नंबर और शिकायत दोनों दें", "tts_unavailable": "लिखित उत्तर तैयार है। चयनित भाषा में सुनने के लिए उत्तर सुनें बटन दबाएं।", "footer": "सहकार-वाणी • किसान सहायता कियोस्क",
    },
    "Marathi (मराठी)": {
        "helpline_header": "🚨 सरकारी हेल्पलाइन आणि तक्रार", "grievance_expander": "तक्रार नोंदवा", "mobile_label": "मोबाईल क्रमांक", "mobile_placeholder": "10 अंकी मोबाईल क्रमांक लिहा", "complaint_label": "तक्रार / समस्या", "complaint_placeholder": "समस्या स्पष्टपणे लिहा", "submit_btn": "तक्रार पाठवा", "ticket_success": "तिकीट यशस्वीरीत्या नोंदवले:", "ticket_missing": "मोबाईल क्रमांक आणि तक्रार दोन्ही द्या", "tts_unavailable": "लिखित उत्तर तयार आहे. निवडलेल्या भाषेत ऐकण्यासाठी उत्तर ऐका बटण दाबा.", "footer": "सहकार-वाणी • शेतकरी सहाय्य किऑस्क",
    },
    "Bengali (বাংলা)": {
        "helpline_header": "🚨 সরকারি হেল্পলাইন ও অভিযোগ", "grievance_expander": "অভিযোগ নথিভুক্ত করুন", "mobile_label": "মোবাইল নম্বর", "mobile_placeholder": "১০ সংখ্যার মোবাইল নম্বর লিখুন", "complaint_label": "অভিযোগ / সমস্যা", "complaint_placeholder": "সমস্যাটি স্পষ্টভাবে লিখুন", "submit_btn": "অভিযোগ পাঠান", "ticket_success": "টিকিট সফলভাবে নথিভুক্ত হয়েছে:", "ticket_missing": "মোবাইল নম্বর ও অভিযোগ দুটোই দিন", "tts_unavailable": "লিখিত উত্তর প্রস্তুত। নির্বাচিত ভাষায় শুনতে উত্তর শুনুন বোতাম চাপুন।", "menu_title": "সহকার-বাণী মেনু", "menu_caption": "কিয়স্কের সুবিধা ও নিয়ন্ত্রণ এখানে খুলুন।", "menu_language": "ভাষা", "apply_language": "🌐 নির্বাচিত ভাষা প্রয়োগ করুন", "features": "সুবিধা", "feature_voice": "🎙️ কৃষি প্রকল্প সম্পর্কে জিজ্ঞাসা করুন", "feature_sources": "📖 নীতি উৎস দেখুন", "feature_grievance": "🚨 অভিযোগ নথিভুক্ত করুন", "feature_helpline": "📞 সরকারি হেল্পলাইন", "display_voice": "প্রদর্শন ও কণ্ঠ", "text_size": "লেখার আকার", "voice_speed": "কণ্ঠের গতি", "normal": "স্বাভাবিক", "slow": "ধীর", "kiosk": "কিয়স্ক", "terminal": "টার্মিনাল", "location": "অবস্থান", "connection": "সংযোগ", "online": "অনলাইন", "limited": "সীমিত", "new_session": "🔄 নতুন সেশন", "footer": "সহকার-বাণী • কৃষক সহায়তা কিয়স্ক",
    },
    "Gujarati (ગુજરાતી)": {
        "helpline_header": "🚨 સરકારી હેલ્પલાઇન અને ફરિયાદ", "grievance_expander": "ફરિયાદ નોંધાવો", "mobile_label": "મોબાઇલ નંબર", "mobile_placeholder": "10 અંકનો મોબાઇલ નંબર લખો", "complaint_label": "ફરિયાદ / સમસ્યા", "complaint_placeholder": "સમસ્યા સ્પષ્ટ રીતે લખો", "submit_btn": "ફરિયાદ મોકલો", "ticket_success": "ટિકિટ સફળતાપૂર્વક નોંધાઈ:", "ticket_missing": "મોબાઇલ નંબર અને ફરિયાદ બંને આપો", "tts_unavailable": "લખિત જવાબ તૈયાર છે. પસંદ કરેલી ભાષામાં સાંભળવા જવાબ સાંભળો બટન દબાવો.", "menu_title": "સહકાર-વાણી મેનુ", "menu_caption": "કિયોસ્કની સુવિધાઓ અને નિયંત્રણ અહીં ખોલો.", "menu_language": "ભાષા", "apply_language": "🌐 પસંદ કરેલી ભાષા લાગુ કરો", "features": "સુવિધાઓ", "feature_voice": "🎙️ કૃષિ યોજનાઓ વિશે પૂછો", "feature_sources": "📖 નીતિ સ્ત્રોત જુઓ", "feature_grievance": "🚨 ફરિયાદ નોંધાવો", "feature_helpline": "📞 સરકારી હેલ્પલાઇન", "display_voice": "ડિસ્પ્લે અને અવાજ", "text_size": "લખાણનું કદ", "voice_speed": "અવાજની ગતિ", "normal": "સામાન્ય", "slow": "ધીમું", "kiosk": "કિયોસ્ક", "terminal": "ટર્મિનલ", "location": "સ્થાન", "connection": "કનેક્શન", "online": "ઓનલાઇન", "limited": "મર્યાદિત", "new_session": "🔄 નવું સત્ર", "footer": "સહકાર-વાણી • ખેડૂત સહાય કિયોસ્ક",
    },
}

@st.cache_data
def get_all_languages():
    if LANGUAGES_FILE.exists():
        try:
            data = json.loads(LANGUAGES_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list) and data:
                return data
        except Exception:
            pass
    return list(PACKS.keys())

@st.cache_data
def get_ui_translation(lang_name):
    result = dict(BASE_UI)
    result.update(PACKS.get(lang_name, {}))
    result.update(PACK_COMPLETION.get(lang_name, {}))
    if lang_name in SHORT_PACKS:
        p = SHORT_PACKS[lang_name]
        result.update({
            "title": f"🏛️ {p[0]}",
            "gate_title": f"🌐 {p[1]}",
            "active_lang": f"🌐 {p[2]}",
            "schemes_header": f"📚 {p[3]}",
            "mic_prompt": f"🎙️ {p[4]}",
            "typed_label": f"⌨️ {p[5]}",
            "quick_header": f"⚡ {p[6]}",
            "ask_btn": f"🔎 {p[7]}",
            "user_query_label": f"🗣️ {p[8]}",
            "ai_resp_label": f"🤖 {p[9]}",
            "play_answer": p[10],
            "change_lang": "🔄 " + p[1],
        })
        result.update(SHORT_EXTRAS.get(lang_name, {}))

        # Fill every remaining visible control from already-localized phrases
        # in the short pack. This prevents an English menu/placeholder from
        # appearing after a farmer switches to one of these languages.
        result.update({
            "menu_title": p[0],
            "menu_caption": p[3],
            "menu_language": p[1],
            "apply_language": f"🌐 {p[7]}",
            "features": p[6],
            "feature_voice": f"🎙️ {p[4]}",
            "feature_sources": f"📖 {p[3]}",
            "feature_grievance": f"🚨 {p[6]}",
            "feature_helpline": f"📞 {p[7]}",
            "display_voice": p[3],
            "text_size": result.get("text_size", p[5]),
            "voice_speed": result.get("voice_speed", p[4]),
            "kiosk": p[0],
            "terminal": p[7],
            "location": p[2],
            "connection": p[2],
            "online": p[2],
            "limited": p[2],
            "new_session": result.get("new_session", f"🔄 {p[1]}"),
            "mobile_label": result.get("mobile_label", p[5]),
            "mobile_placeholder": result.get("mobile_placeholder", p[5]),
            "complaint_label": result.get("complaint_label", p[6]),
            "complaint_placeholder": result.get("complaint_placeholder", p[5]),
            "submit_btn": result.get("submit_btn", p[7]),
            "ticket_success": result.get("ticket_success", p[9]),
            "ticket_missing": result.get("ticket_missing", p[5]),
        })
    return result
