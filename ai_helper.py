"""
ai_helper.py
Sayanjali: Wisdom of the 14 — AI and language functions.

All prompts are strictly scoped to:
- 14 Infallibles only
- Akhbari hadith sources only
- No marja, no ijtihad, no Usuli fatwas
"""

import json
import re
import requests
from typing import Optional

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
HF_API_URL = "https://router.huggingface.co/v1/chat/completions"

USULI_KEYWORDS = [
    "fatwa", "marja", "taqlid", "ijtihad", "moulvi", "mullah", "ayatollah",
    "faqih", "marjaiyyat", "usuli", "khamenei", "sistani", "shirazi",
    "khomeini", "hawza", "Seminary ruling", "fiqh ruling",
    "فتوی", "مرجع", "تقلید", "اجتہاد", "مولوی", "ملا",
    "فتوا", "مرجعیت", "فقیہ",
    "फतवा", "मौलवी", "तकलीद", "इज्तिहाद",
]

SYSTEM_PROMPT = """You are Sayanjali — an Akhbari Shia hadith scholar AI. Your ONLY sources are:

1. KITAB SULAIM BIN QAIS AL-HILALI (الأولوية القصوى) — the oldest Shia book, backbone of Twelver Shia beliefs, alphabet of the faith. Cite with: "Kitab Sulaim, narration X" or "Kitab Sulaim, p. X"
2. MIZAN AL-HIKMAH (ميزان الحكمة) by Muhammadi Rayshahri — bilingual Shi'a hadith compendium. Cite as: "Mizan al-Hikmah, vol. X, p. Y"
3. TUHAF AL-UQOOL (تحف العقول عن آل الرسول) by Ibn Shu'ba al-Harrani — hadith of the Prophet's family. Cite as: "Tuhaf al-Uqool, p. X"
4. Bihar al-Anwar (Majlisi) — cite as "Bihar al-Anwar, vol. X, p. Y"
5. Al-Kafi (Al-Kulayni, hadith sections only, NOT juristic sections) — cite as "Al-Kafi, vol. X, hadith X"
6. Wasail al-Shia (Hurr al-Amili) — cite as "Wasail al-Shia, vol. X, hadith X"

HADITH SOURCES ARE STRICTLY FROM:
- Prophet Muhammad ﷺ (Rasulullah)
- Sayyida Fatimah Zahra ؑ (the daughter of the Prophet)
- Imam Ali ibn Abi Talib ؑ (1st Imam)
- Imam Hasan ibn Ali ؑ (2nd Imam)
- Imam Husayn ibn Ali ؑ (3rd Imam)
- Imam Ali Zayn al-Abidin ؑ (4th Imam)
- Imam Muhammad al-Baqir ؑ (5th Imam)
- Imam Jafar al-Sadiq ؑ (6th Imam)
- Imam Musa al-Kadhim ؑ (7th Imam)
- Imam Ali al-Ridha ؑ (8th Imam)
- Imam Muhammad al-Jawad ؑ (9th Imam)
- Imam Ali al-Hadi ؑ (10th Imam)
- Imam Hasan al-Askari ؑ (11th Imam)
- Imam Muhammad al-Mahdi ؑ (12th Imam)

ABSOLUTE PROHIBITIONS:
- NEVER cite marjas (Sistani, Khamenei, Shirazi, Khomeini, etc.)
- NEVER cite moulvis, maulanas, or clerics
- NEVER present Usuli fatwas or ijtihad as valid guidance
- NEVER cite Sunni hadith books (Bukhari, Muslim, etc.)
- If asked about Usuli fatwas: STATE CLEARLY that Akhbari Shia Islam REJECTS marja authority and ijtihad as innovations, then provide the relevant hadith of the Imams instead.

AKHBARI POSITION ON USULI FATWAS:
The Akhbari school holds that following a living marja (taqlid) is an innovation (bid'ah) with no basis in the hadith of the Imams. The Imams themselves never instructed their followers to follow scholars — they said "return to our narrators of hadith." Therefore all Usuli jurisprudential authority is rejected.

RESPONSE FORMAT:
You MUST respond in valid JSON only. No markdown, no prose outside JSON. Format:

{
  "usuli_warning": null OR "string explaining Akhbari rejection if query involves Usuli topics",
  "hadiths": [
    {
      "imam": "Name of the Infallible ؑ",
      "arabic": "Original Arabic text of hadith",
      "english": "English translation",
      "urdu": "Urdu translation (اردو)",
      "hindi": "Hindi translation (हिन्दी)",
      "source": "Book name, volume/page/narration number",
      "chain": "Brief narrator chain if known (optional)"
    }
  ]
}

TRANSLATION RULES based on detected_lang field:
- If detected_lang = "en": provide arabic + english + urdu + hindi
- If detected_lang = "ur": provide arabic + english + urdu + hindi  
- If detected_lang = "hi": provide arabic + english + urdu + hindi
- Always provide ALL three languages (English, Urdu, Hindi) plus Arabic original
- Urdu must be in Nastaliq script (right-to-left)
- Hindi must be in Devanagari script

Provide 1-3 relevant hadiths maximum. Quality over quantity. If no exact hadith is found on a topic, provide the closest thematically relevant hadith from the Infallibles and state the connection.
"""


# ─────────────────────────────────────────────
#  LANGUAGE DETECTION
# ─────────────────────────────────────────────
def detect_language(text: str) -> str:
    """
    Detect language of query text.
    Returns ISO 639-1 code: 'en', 'ur', 'hi', 'ar'
    Falls back gracefully if langdetect unavailable.
    """
    if not text or not text.strip():
        return "en"

    # Fast character-set heuristics (runs even without langdetect)
    arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    devanagari_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    total = len(text.replace(" ", ""))

    if total == 0:
        return "en"

    # Arabic-script covers both Arabic and Urdu
    if arabic_chars / total > 0.3:
        # Distinguish Urdu vs Arabic by presence of Urdu-specific chars
        urdu_specific = sum(1 for c in text if c in 'ٹڈڑژڈگڈ' or '\u0679' <= c <= '\u06D3')
        return "ur" if urdu_specific > 0 or arabic_chars > 5 else "ar"

    if devanagari_chars / total > 0.3:
        return "hi"

    # Try langdetect if available
    try:
        from langdetect import detect
        lang = detect(text)
        # Map langdetect codes
        mapping = {
            "ur": "ur", "hi": "hi", "en": "en",
            "ar": "ar", "fa": "ur",  # Farsi → treat as Urdu script
        }
        return mapping.get(lang, "en")
    except Exception:
        pass

    # Default to English
    return "en"


# ─────────────────────────────────────────────
#  USULI DETECTION
# ─────────────────────────────────────────────
def has_usuli_content(text: str) -> bool:
    """Check if query involves Usuli/marja topics."""
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in USULI_KEYWORDS)


# ─────────────────────────────────────────────
#  HF INFERENCE API CALL
# ─────────────────────────────────────────────
def call_hf_api(
    messages: list,
    hf_token: str,
    model: str,
    max_tokens: int = 2048,
    temperature: float = 0.3,
) -> Optional[str]:
    """
    Call Hugging Face Inference API.
    Returns raw text content or detailed error.
    """

    headers = {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
    }

    try:
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json=payload,
            timeout=90,
        )

        # DEBUG: show actual HF error
        if response.status_code != 200:
            return f"__HTTP_{response.status_code}__\n{response.text}"

        data = response.json()

        # DEBUG: unexpected response format
        if "choices" not in data:
            return f"__BAD_RESPONSE__\n{json.dumps(data, indent=2)}"

        print("HF RESPONSE:", data)
            return data["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        return "__TIMEOUT__"

    except requests.exceptions.HTTPError as e:
        return f"__HTTP_ERROR__ {str(e)}"

    except Exception as e:
        return f"__ERROR__ {str(e)}"

# ─────────────────────────────────────────────
#  PARSE AI RESPONSE
# ─────────────────────────────────────────────
def parse_hadith_response(raw: str) -> dict:
    """
    Parse JSON response from AI. Returns structured dict.
    Falls back to raw text if JSON parsing fails.
    """
    if not raw:
        return {"hadiths": [], "raw": "No response received from AI."}

    # Special error codes
    if raw == "__RATE_LIMIT__":
        return {"hadiths": [], "raw": "⚠ Rate limit reached. Please wait a moment and try again."}
    if raw == "__AUTH_ERROR__":
        return {"hadiths": [], "raw": "⚠ Invalid API token. Please check your Hugging Face token in the sidebar."}

    # Strip markdown code fences if present
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r'^```[a-zA-Z]*\n?', '', cleaned)
        cleaned = re.sub(r'\n?```$', '', cleaned)
    cleaned = cleaned.strip()

    # Try to find JSON block
    json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if json_match:
        cleaned = json_match.group()

    try:
        data = json.loads(cleaned)
        # Validate structure
        if "hadiths" not in data:
            data["hadiths"] = []
        if "usuli_warning" not in data:
            data["usuli_warning"] = None
        return data
    except json.JSONDecodeError:
        # Return raw as fallback
        return {
            "hadiths": [],
            "raw": cleaned or "Response could not be parsed. Please try again.",
        }


# ─────────────────────────────────────────────
#  MAIN QUERY FUNCTION
# ─────────────────────────────────────────────
def query_hadith_ai(
    query: str,
    detected_lang: str,
    hf_token: str,
    model: str,
) -> dict:
    """
    Main function: takes user query, returns structured hadith response.
    """
    # Build user message
    lang_instruction = {
        "en": "The user asked in English. Provide translations in: English, Urdu (اردو), Hindi (हिन्दी).",
        "ur": "The user asked in Urdu (اردو). Provide translations in: English, Urdu (اردو), Hindi (हिन्दी).",
        "hi": "The user asked in Hindi (हिन्दी). Provide translations in: English, Urdu (اردو), Hindi (हिन्दी).",
        "ar": "The user asked in Arabic. Provide translations in: English, Urdu (اردو), Hindi (हिन्दी).",
    }.get(detected_lang, "Provide translations in: English, Urdu (اردو), Hindi (हिन्दी).")

    usuli_flag = ""
    if has_usuli_content(query):
        usuli_flag = (
            "\n\n[AKHBARI TRIGGER]: This query involves Usuli topics. "
            "First explain the Akhbari rejection of marja authority/ijtihad/fatwas clearly. "
            "Then provide relevant hadith of the Infallibles on this topic."
        )

    user_message = f"""Query: {query}

detected_lang: {detected_lang}
{lang_instruction}
{usuli_flag}

Priority source order:
1. Kitab Sulaim Bin Qais al-Hilali (HIGHEST PRIORITY)
2. Mizan al-Hikmah
3. Tuhaf al-Uqool
4. Other Akhbari-accepted books

Respond in valid JSON only."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    raw = call_hf_api(messages, hf_token, model, max_tokens=2048, temperature=0.25)
    return parse_hadith_response(raw)


# ─────────────────────────────────────────────
#  DAILY HADITH
# ─────────────────────────────────────────────
def get_welcome_hadith(hf_token: str, model: str) -> dict:
    """
    Returns a random/daily hadith from one of the 14 Infallibles.
    Cycles through different topics for variety.
    """
    import random
    topics = [
        "knowledge and seeking wisdom",
        "patience and gratitude",
        "the rights of believers upon each other",
        "the importance of prayer and remembrance of Allah",
        "justice and speaking truth to power",
        "love of the Ahlul Bayt",
        "the Day of Judgment and accountability",
        "helping the poor and caring for the weak",
        "the virtue of silence and wise speech",
        "the nature of the world (dunya) and its deceptions",
    ]
    topic = random.choice(topics)

    user_message = f"""Please provide one beautiful and profound hadith from the 14 Infallibles on the topic of: "{topic}"

Prioritize sources in this order:
1. Kitab Sulaim Bin Qais al-Hilali (HIGHEST PRIORITY)
2. Mizan al-Hikmah
3. Tuhaf al-Uqool

detected_lang: en
Provide Arabic original + English + Urdu + Hindi translations.
Respond in valid JSON only."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    raw = call_hf_api(messages, hf_token, model, max_tokens=1500, temperature=0.4)
    return parse_hadith_response(raw)


# ─────────────────────────────────────────────
#  STANDALONE TRANSLATION (optional utility)
# ─────────────────────────────────────────────
def translate_text(text: str, from_lang: str, to_lang: str, hf_token: str, model: str) -> str:
    """
    Translate text between languages using HF API.
    Used as fallback utility.
    """
    lang_names = {"en": "English", "ur": "Urdu", "hi": "Hindi", "ar": "Arabic"}
    from_name = lang_names.get(from_lang, from_lang)
    to_name = lang_names.get(to_lang, to_lang)

    messages = [
        {
            "role": "system",
            "content": f"You are a precise translator. Translate the following text from {from_name} to {to_name}. Return ONLY the translation, no explanations.",
        },
        {"role": "user", "content": text},
    ]
    result = call_hf_api(messages, hf_token, model, max_tokens=500, temperature=0.1)
    return result or text
