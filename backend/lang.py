"""Language help for Hindi / English / Hinglish.

1) detect_language()  -> 'hindi' | 'hinglish' | 'english'
2) language_directive() -> one clear sentence added to the LAST user turn (small models obey that best)
3) expand_query() -> adds English keywords so Hinglish/Hindi questions still find the English knowledge files
"""
import re

DEVANAGARI = re.compile(r"[\u0900-\u097F]")

HINGLISH_WORDS = {
    "kya", "kaise", "kese", "kaisa", "kaun", "kyu", "kyun", "kahan", "kaha", "kab", "kitna", "kitne",
    "hai", "hain", "hoga", "hogi", "hota", "hoti", "tha", "thi", "mujhe", "mughe", "mera", "meri", "mere",
    "apna", "apne", "apni", "tum", "tumhara", "aap", "aapka", "hum", "humara", "batao", "bta", "bata", "btao",
    "dijiye", "do", "karo", "karna", "kare", "karu", "kar", "chahiye", "chahie", "chahta", "chahti", "nahi", "nhi",
    "aur", "ya", "mein", "isme", "esme", "usme", "iske", "uske", "wala", "wali", "vala", "vali", "banao", "banana",
    "bnana", "banau", "bnau", "samjhao", "samjha", "sikhao", "sikhna", "seekhna", "lagta", "sabse", "bahut",
    "thoda", "abhi", "kaam", "liye", "ke", "ka", "ki", "ko", "se", "par", "per", "sirf", "bhi", "toh", "koi",
    "kuch", "sab", "pura", "poora", "achha", "accha", "acha", "shuru", "aasan", "asaan", "mushkil", "matlab",
}
STRONG = {"kya", "kaise", "kese", "mujhe", "mughe", "batao", "bta", "hai", "hain", "chahiye", "nahi", "nhi",
          "samjhao", "banao", "banana", "bnana", "karna", "mera", "meri", "mere", "kaun", "kyu", "kyun", "ke", "ka", "ki"}

EXPLICIT_EN = re.compile(r"\b(in english|english mein|english me|reply in english)\b", re.I)


def detect_language(text):
    text = text or ""
    letters = re.findall(r"[A-Za-z\u0900-\u097F]", text)
    if not letters:
        return "english"
    if EXPLICIT_EN.search(text):
        return "english"
    if len(DEVANAGARI.findall(text)) / len(letters) > 0.3:
        return "hindi"
    words = re.findall(r"[a-z]+", text.lower())
    hits = [w for w in words if w in HINGLISH_WORDS]
    strong = [w for w in hits if w in STRONG]
    if len(hits) >= 2 and strong or (words and len(hits) / len(words) >= 0.3):
        return "hinglish"
    if re.search(r"\bhindi\b", text.lower()):
        return "hinglish"
    return "english"


def language_directive(lang):
    if lang == "hindi":
        return ("Answer in simple Hindi (Devanagari script). Keep technical words such as Flask, API, database, "
                "Python in English. Explain like a friendly senior to a beginner.")
    if lang == "hinglish":
        return ("Answer in Hinglish: Hindi written in English/Roman letters mixed with English technical words, "
                "like a friendly senior explaining to a beginner. Do NOT use Devanagari script.")
    return "Answer in simple, clear English for a beginner."


# Roman-Hindi / Hindi words -> English keywords (used only to help retrieval)
EXPAND = {
    "kaise": "how to", "kese": "how to", "kaisa": "how", "kya": "what", "kyu": "why", "kyun": "why",
    "banau": "build create", "bnau": "build create", "banana": "build create", "bnana": "build create",
    "banao": "build create", "banaye": "build create", "banane": "build create",
    "samjhao": "explain", "samjha": "explain", "matlab": "meaning", "sikhna": "learn", "seekhna": "learn",
    "sikhao": "teach learn", "shuru": "start", "kaam": "work steps", "aasan": "simple easy",
    "idea": "idea", "vichar": "idea", "pariyojana": "project", "database": "database sqlite",
    "tarika": "method steps", "saaf": "clear", "nahi": "not", "error": "error debugging fix",
    "प्रोजेक्ट": "project", "आइडिया": "idea", "कैसे": "how to", "बनाना": "build create", "बनाएं": "build create",
    "डेटाबेस": "database", "मशीन": "machine", "लर्निंग": "learning", "वेबसाइट": "website", "समझाओ": "explain",
    "समझाइए": "explain", "रोडमैप": "roadmap", "स्टैक": "stack", "लॉगिन": "login", "रिपोर्ट": "report",
    "वाइवा": "viva", "क्या": "what", "क्यों": "why", "सीखें": "learn", "एप": "app", "ऐप": "app",
}


def expand_query(text):
    extra = []
    for w in re.findall(r"[\w\u0900-\u097F]+", (text or "").lower()):
        if w in EXPAND:
            extra.append(EXPAND[w])
    return (text + " " + " ".join(extra)).strip() if extra else text
