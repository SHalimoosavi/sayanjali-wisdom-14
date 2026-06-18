"""
ai_helper.py
Sayanjali: Wisdom of the 14 — AI and language functions.
Hugging Face Router endpoint: https://router.huggingface.co/v1/chat/completions

All prompts are strictly scoped to:
- 14 Infallibles only (Prophet Muhammad, Fatimah Zahra, 12 Imams)
- Akhbari hadith sources only
- No marja, no ijtihad, no Usuli fatwas
"""

import json
import re
import requests
from typing import Optional

# ---------------------------------------------------------------------------
#  CONSTANTS
# ---------------------------------------------------------------------------

HF_ROUTER_URL = "https://router.huggingface.co/v1/chat/completions"

SUPPORTED_MODELS = [
    "Qwen/QwQ-32B",
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
    "Qwen/Qwen2.5-72B-Instruct",
]

USULI_KEYWORDS = [
    # English
    "fatwa", "marja", "taqlid", "ijtihad", "moulvi", "maulvi", "mullah",
    "ayatollah", "faqih", "marjaiyyat", "usuli", "hawza", "seminary ruling",
    "fiqh ruling", "jurisprudential", "legal ruling", "religious decree",
    "khamenei", "sistani", "shirazi", "khomeini", "makarem", "safi golpaygani",
    "follow a scholar", "follow a marja", "emulate a scholar",
    # Arabic / transliterated
    "fatawa", "maraje", "taqleed", "ijtihaad", "fuqaha", "al-fiqh",
    # Urdu
    "\u0641\u062a\u0648\u06cc", "\u0645\u0631\u062c\u0639",
    "\u062a\u0642\u0644\u06cc\u062f", "\u0627\u062c\u062a\u06c1\u0627\u062f",
    "\u0645\u0648\u0644\u0648\u06cc", "\u0645\u0644\u0627",
    "\u0641\u062a\u0648\u0627", "\u0645\u0631\u062c\u0639\u06cc\u062a",
    "\u0641\u0642\u06cc\u06c1",
    # Hindi
    "\u092b\u0924\u0935\u093e", "\u092e\u094c\u0932\u0935\u0940",
    "\u0924\u0915\u0932\u0940\u0926", "\u0907\u091c\u094d\u0924\u093f\u0939\u093e\u0926",
]

# ---------------------------------------------------------------------------
#  SYSTEM PROMPT
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are Sayanjali — an Akhbari Shia hadith scholar AI. Your ONLY sources are:

1. KITAB SULAIM BIN QAIS AL-HILALI (highest priority) — the oldest surviving Shia book, the backbone and alphabet of Twelver Shia beliefs. Cite as: "Kitab Sulaim, narration X" or "Kitab Sulaim, p. X"
2. MIZAN AL-HIKMAH by Muhammadi Rayshahri — bilingual Shi'a hadith compendium. Cite as: "Mizan al-Hikmah, vol. X, p. Y"
3. TUHAF AL-UQOOL (Tuhaf al-'uqool 'an Aalil-Rasool) by Ibn Shu'ba al-Harrani. Cite as: "Tuhaf al-Uqool, p. X"
4. Bihar al-Anwar (Majlisi). Cite as: "Bihar al-Anwar, vol. X, p. Y"
5. Al-Kafi (Al-Kulayni, hadith sections only). Cite as: "Al-Kafi, vol. X, hadith X"
6. Wasail al-Shia (Hurr al-Amili). Cite as: "Wasail al-Shia, vol. X, hadith X"

NARRATORS (14 INFALLIBLES ONLY):
- Prophet Muhammad ibn Abdullah (Rasulullah) sallallahu alayhi wa alihi
- Sayyida Fatimah al-Zahra bint Muhammad alayha al-salam
- Imam Ali ibn Abi Talib (1st Imam) alayhi al-salam
- Imam Hasan ibn Ali (2nd Imam) alayhi al-salam
- Imam Husayn ibn Ali (3rd Imam) alayhi al-salam
- Imam Ali ibn Husayn Zayn al-Abidin (4th Imam) alayhi al-salam
- Imam Muhammad ibn Ali al-Baqir (5th Imam) alayhi al-salam
- Imam Jafar ibn Muhammad al-Sadiq (6th Imam) alayhi al-salam
- Imam Musa ibn Jafar al-Kadhim (7th Imam) alayhi al-salam
- Imam Ali ibn Musa al-Ridha (8th Imam) alayhi al-salam
- Imam Muhammad ibn Ali al-Jawad (9th Imam) alayhi al-salam
- Imam Ali ibn Muhammad al-Hadi (10th Imam) alayhi al-salam
- Imam Hasan ibn Ali al-Askari (11th Imam) alayhi al-salam
- Imam Muhammad ibn Hasan al-Mahdi (12th Imam) alayhi al-salam

ABSOLUTE PROHIBITIONS — NEVER violate these:
- NEVER cite any marja: Sistani, Khamenei, Shirazi, Khomeini, Makarem, or any other
- NEVER cite moulvis, maulanas, sheikhs, or clerics as religious authorities
- NEVER present Usuli fatwas or ijtihad as valid guidance
- NEVER cite Sunni hadith collections (Bukhari, Muslim, Tirmidhi, etc.)
- NEVER fabricate hadith — if a hadith cannot be traced to the Infallibles, say so honestly

AKHBARI POSITION (state this clearly when Usuli topics arise):
Akhbari Shia Islam rejects marja-following (taqlid), ijtihad, and Usuli jurisprudence as innovations (bid'ah) with no basis in the hadith of the Imams. The Imams said: "Return to our narrators of hadith." Therefore all Usuli clerical authority is categorically rejected.

RESPONSE FORMAT:

You MUST respond in valid JSON only.

For hadith questions:

{
  "response_type": "hadith",
  "usuli_warning": null,
  "hadiths": [
    {
      "imam": "",
      "arabic": "",
      "english": "",
      "urdu": "",
      "hindi": "",
      "source": "",
      "chain": ""
    }
  ]
}

For general knowledge questions:

{
  "response_type": "knowledge",
  "title": "",
  "content": ""
}

General knowledge includes:
- Who are the 14 Infallibles
- What is Karbala
- What is Ghadir Khumm
- What is Imamate
- History of an Imam
- Biography questions
- Events
- Concepts

Hadith questions should use response_type="hadith"

Knowledge questions should use response_type="knowledge"
"""

# ---------------------------------------------------------------------------
#  1. LANGUAGE DETECTION
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
#  1. LANGUAGE DETECTION
# ---------------------------------------------------------------------------

def detect_language(text: str) -> str:
    """
    Detect the language of the input text.
    Returns ISO 639-1 code: 'en', 'ur', 'hi', or 'ar'.
    Uses Unicode block heuristics first, then langdetect as fallback.
    Always returns a valid string — never raises.
    """
    if not text or not text.strip():
        return "en"

    stripped = text.replace(" ", "").replace("\n", "")
    if not stripped:
        return "en"

    total = len(stripped)

    # Count characters by Unicode block
    arabic_count = sum(1 for c in stripped if "\u0600" <= c <= "\u06FF")
    devanagari_count = sum(1 for c in stripped if "\u0900" <= c <= "\u097F")
    latin_count = sum(1 for c in stripped if c.isascii() and c.isalpha())

    arabic_ratio = arabic_count / total
    devanagari_ratio = devanagari_count / total
    latin_ratio = latin_count / total

    # Urdu-specific characters (not found in Arabic)
    urdu_specific = set("\u0679\u0688\u0691\u06BA\u06BE\u06C1\u06C3\u06CC\u06D2")
    has_urdu_chars = any(c in urdu_specific for c in stripped)

    if arabic_ratio > 0.25:
        # Arabic-script text — distinguish Urdu from Arabic
        if has_urdu_chars or arabic_ratio < 0.85:
            return "ur"
        return "ar"

    if devanagari_ratio > 0.25:
        return "hi"

    if latin_ratio > 0.40:
        return "en"

    # Fall back to langdetect if available
    try:
        from langdetect import detect, LangDetectException
        try:
            detected = detect(text)
            lang_map = {
                "ur": "ur",
                "hi": "hi",
                "en": "en",
                "ar": "ar",
                "fa": "ur",   # Farsi uses same script as Urdu
                "pa": "ur",   # Punjabi (Shahmukhi) — treat as Urdu
            }
            return lang_map.get(detected, "en")
        except LangDetectException:
            return "en"
    except ImportError:
        pass

    return "en"


# ---------------------------------------------------------------------------
#  2. USULI CONTENT DETECTION
# ---------------------------------------------------------------------------

def has_usuli_content(text: str) -> bool:
    """
    Return True if the query text contains Usuli/marja-related keywords
    that require the Akhbari rejection statement.
    Case-insensitive for ASCII keywords.
    """
    if not text:
        return False
    text_lower = text.lower()
    for keyword in USULI_KEYWORDS:
        if keyword.lower() in text_lower:
            return True
    return False


# ---------------------------------------------------------------------------
#  3. HUGGING FACE ROUTER API CALL
# ---------------------------------------------------------------------------

def call_hf_api(
    messages: list,
    hf_token: str,
    model: str,
    max_tokens: int = 2048,
    temperature: float = 0.3,
) -> str:
    """
    Call the Hugging Face Router endpoint (OpenAI-compatible).
    Returns the raw assistant message content string, or an error sentinel:
        __HTTP_401__   — invalid or missing token
        __HTTP_403__   — token lacks permission for this model
        __HTTP_404__   — model not found on HF Router
        __HTTP_429__   — rate limit exceeded
        __BAD_RESPONSE__ — unexpected response structure
        __ERROR__      — network error, timeout, or other exception
    Never raises an exception.
    """
    if not hf_token or not hf_token.strip():
        return "__HTTP_401__"

    if model not in SUPPORTED_MODELS:
        # Allow unsupported models but warn via error sentinel only on failure
        pass

    headers = {
        "Authorization": f"Bearer {hf_token.strip()}",
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
            HF_ROUTER_URL,
            headers=headers,
            json=payload,
            timeout=120,
        )
    except requests.exceptions.Timeout:
        return "__ERROR__"
    except requests.exceptions.ConnectionError:
        return "__ERROR__"
    except requests.exceptions.RequestException:
        return "__ERROR__"

    # Handle HTTP error codes with specific sentinels
    if response.status_code == 401:
        return "__HTTP_401__"
    if response.status_code == 403:
        return "__HTTP_403__"
    if response.status_code == 404:
        return "__HTTP_404__"
    if response.status_code == 429:
        return "__HTTP_429__"
    if not response.ok:
        # Capture any other HTTP error
        return f"__ERROR__ HTTP {response.status_code}"

    try:
        data = response.json()
    except (json.JSONDecodeError, ValueError):
        return "__BAD_RESPONSE__"

    try:
        content = data["choices"][0]["message"]["content"]
        if not isinstance(content, str):
            return "__BAD_RESPONSE__"
        return content
    except (KeyError, IndexError, TypeError):
        return "__BAD_RESPONSE__"


# ---------------------------------------------------------------------------
#  4. PARSE HADITH RESPONSE
# ---------------------------------------------------------------------------

def parse_hadith_response(raw: str) -> dict:
    """
    Parse the raw string returned by call_hf_api into a structured dict.

    Successful result shape:
        {
            "usuli_warning": str | None,
            "hadiths": [ { imam, arabic, english, urdu, hindi, source, chain? }, ... ]
        }

    Error result shape:
        {
            "hadiths": [],
            "raw": "Human-readable error message"
        }

    Never raises an exception.
    """
    if not raw:
        return {
            "hadiths": [],
            "raw": "No response received from the AI. Please try again.",
        }

    # Map sentinel strings to user-friendly messages
    error_messages = {
        "__HTTP_401__": (
            "Authentication failed (HTTP 401). Your Hugging Face token is invalid or missing. "
            "Please check the token in the sidebar — it should start with hf_"
        ),
        "__HTTP_403__": (
            "Access denied (HTTP 403). Your Hugging Face token does not have permission to access "
            "this model. Try switching to a different model in the sidebar, or upgrade your HF account."
        ),
        "__HTTP_404__": (
            "Model not found (HTTP 404). The selected model is unavailable on the Hugging Face Router. "
            "Please switch to another model in the sidebar."
        ),
        "__HTTP_429__": (
            "Rate limit reached (HTTP 429). The Hugging Face free tier has a request limit. "
            "Please wait 30–60 seconds and try again."
        ),
        "__BAD_RESPONSE__": (
            "The AI returned an unexpected response format. "
            "This may be a temporary issue — please try again."
        ),
        "__ERROR__": (
            "A network error occurred while contacting the Hugging Face API. "
            "Please check your internet connection and try again."
        ),
    }

    # Check for exact sentinel match first
    if raw in error_messages:
        return {"hadiths": [], "raw": error_messages[raw]}

    # Check for prefixed ERROR sentinel (e.g. "__ERROR__ HTTP 502")
    if raw.startswith("__ERROR__"):
        suffix = raw[len("__ERROR__"):].strip()
        msg = "A server error occurred"
        if suffix:
            msg += f" ({suffix})"
        msg += ". Please try again in a moment."
        return {"hadiths": [], "raw": msg}

    # Strip markdown code fences if the model wrapped its JSON
    cleaned = raw.strip()
    fence_pattern = re.compile(r"^```[a-zA-Z]*\s*", re.MULTILINE)
    cleaned = fence_pattern.sub("", cleaned)
    cleaned = re.sub(r"\s*```\s*$", "", cleaned).strip()

    # Some models prepend reasoning or prose before the JSON object — find it
    json_start = cleaned.find("{")
    json_end = cleaned.rfind("}")
    if json_start != -1 and json_end != -1 and json_end > json_start:
        cleaned = cleaned[json_start : json_end + 1]
    elif json_start == -1:
        # No JSON object found — return raw text as fallback
        return {
            "hadiths": [],
            "raw": cleaned if cleaned else "The AI did not return a valid response. Please try again.",
        }

    try:
        data = json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        # Attempt a second pass with relaxed cleaning (remove trailing commas)
        cleaned_relaxed = re.sub(r",\s*([}\]])", r"\1", cleaned)
        try:
            data = json.loads(cleaned_relaxed)
        except (json.JSONDecodeError, ValueError):
            return {
                "hadiths": [],
                "raw": (
                    "The AI response could not be parsed. "
                    "This sometimes happens with complex queries — please try rephrasing."
                ),
            }

    # Normalise structure
    if not isinstance(data, dict):
        return {
            "hadiths": [],
            "raw": "Unexpected response structure from AI. Please try again.",
        }

    result = {
        "usuli_warning": data.get("usuli_warning") or None,
        "hadiths": [],
    }

    raw_hadiths = data.get("hadiths", [])
    if not isinstance(raw_hadiths, list):
        raw_hadiths = []

    for item in raw_hadiths:
        if not isinstance(item, dict):
            continue
        hadith = {
            "imam":    str(item.get("imam", "")).strip(),
            "arabic":  str(item.get("arabic", "")).strip(),
            "english": str(item.get("english", "")).strip(),
            "urdu":    str(item.get("urdu", "")).strip(),
            "hindi":   str(item.get("hindi", "")).strip(),
            "source":  str(item.get("source", "")).strip(),
        }
        if item.get("chain"):
            hadith["chain"] = str(item["chain"]).strip()
        result["hadiths"].append(hadith)

    return result


# ---------------------------------------------------------------------------
#  5. MAIN QUERY FUNCTION
# ---------------------------------------------------------------------------

def query_hadith_ai(
    query: str,
    detected_lang: str,
    hf_token: str,
    model: str,
) -> dict:
    """
    Primary entry point: take a user query and return a parsed hadith dict.
    Injects language instructions and Usuli-trigger flags into the prompt.
    Returns the same shape as parse_hadith_response.
    """
    lang_labels = {
        "en": "English",
        "ur": "Urdu (اردو)",
        "hi": "Hindi (हिन्दी)",
        "ar": "Arabic (العربية)",
    }
    lang_label = lang_labels.get(detected_lang, "English")

    translation_instruction = (
        "Provide the hadith with all four fields populated: "
        "arabic (original), english, urdu (Nastaliq script), hindi (Devanagari script)."
    )

    usuli_injection = ""
    if has_usuli_content(query):
        usuli_injection = (
            "\n\n[AKHBARI TRIGGER DETECTED]: This query touches on Usuli topics "
            "(marja, fatwa, ijtihad, taqlid, or clerical authority). "
            "You MUST set the usuli_warning field to a clear explanation of the Akhbari "
            "rejection of such authority. Then provide the most relevant hadith of the "
            "14 Infallibles on this topic from the priority source list."
        )

    user_content = (
        f"Query language detected: {lang_label}\n"
        f"User query: {query}\n\n"
        f"{translation_instruction}\n"
        f"Source priority: 1) Kitab Sulaim  2) Mizan al-Hikmah  3) Tuhaf al-Uqool  4) Bihar al-Anwar  5) Al-Kafi  6) Wasail al-Shia\n"
        f"{usuli_injection}\n\n"
        f"Respond with valid JSON only. No text before or after the JSON object."
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_content},
    ]

    raw = call_hf_api(
        messages=messages,
        hf_token=hf_token,
        model=model,
        max_tokens=2048,
        temperature=0.25,
    )
    return parse_hadith_response(raw)


# ---------------------------------------------------------------------------
#  6. DAILY / WELCOME HADITH
# ---------------------------------------------------------------------------

def get_welcome_hadith(hf_token: str, model: str) -> dict:
    """
    Return one beautiful daily hadith from a randomly selected topic.
    Rotates through 12 topics — one per Imam, thematically appropriate.
    Returns the same shape as parse_hadith_response.
    """
    import random

    topics = [
        ("knowledge and the obligation to seek it", "Imam Ali ibn Abi Talib"),
        ("patience (sabr) and its rewards", "Imam Husayn ibn Ali"),
        ("gratitude to Allah (shukr)", "Imam Zayn al-Abidin"),
        ("the rights of believers upon one another (huquq al-mu'minin)", "Imam Muhammad al-Baqir"),
        ("the reality of the world (dunya) and its deception", "Imam Jafar al-Sadiq"),
        ("prayer (salah) and remembrance of Allah (dhikr)", "Imam Musa al-Kadhim"),
        ("justice and speaking truth", "Prophet Muhammad"),
        ("love of the Ahlul Bayt", "Imam Ali al-Ridha"),
        ("generosity and helping the poor", "Imam Muhammad al-Jawad"),
        ("tawakkul — reliance upon Allah", "Imam Ali al-Hadi"),
        ("humility (tawadu') and avoiding arrogance", "Imam Hasan al-Askari"),
        ("hope in Allah's mercy and the awaited relief", "Imam Muhammad al-Mahdi"),
    ]

    topic, preferred_imam = random.choice(topics)

    user_content = (
        f"Please provide one profound and authentic hadith on the topic of: \"{topic}\"\n\n"
        f"Preferred narrator (if a strong narration exists): {preferred_imam}\n"
        f"Source priority: 1) Kitab Sulaim  2) Mizan al-Hikmah  3) Tuhaf al-Uqool  4) Bihar al-Anwar\n\n"
        f"Provide all four fields: arabic (original), english, urdu (Nastaliq), hindi (Devanagari).\n"
        f"Respond with valid JSON only. No text before or after the JSON object."
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_content},
    ]

    raw = call_hf_api(
        messages=messages,
        hf_token=hf_token,
        model=model,
        max_tokens=1500,
        temperature=0.40,
    )
    return parse_hadith_response(raw)


# ---------------------------------------------------------------------------
#  7. STANDALONE TRANSLATION UTILITY
# ---------------------------------------------------------------------------

def translate_text(
    text: str,
    from_lang: str,
    to_lang: str,
    hf_token: str,
    model: str,
) -> str:
    """
    Translate text between languages using the HF Router API.
    Returns the translated string, or the original text on any failure.
    Intended as a utility/fallback — main translations are handled in-prompt.

    Supported lang codes: 'en', 'ur', 'hi', 'ar'
    """
    lang_names = {
        "en": "English",
        "ur": "Urdu (Nastaliq script, right-to-left)",
        "hi": "Hindi (Devanagari script)",
        "ar": "Arabic (right-to-left)",
    }

    from_name = lang_names.get(from_lang, from_lang)
    to_name   = lang_names.get(to_lang, to_lang)

    if from_lang == to_lang:
        return text

    system_msg = (
        f"You are a precise literary translator specialising in Islamic texts. "
        f"Translate the following text from {from_name} to {to_name}. "
        f"Preserve the meaning, register, and spiritual tone exactly. "
        f"Return ONLY the translation — no explanations, no preamble, no quotation marks."
    )

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user",   "content": text},
    ]

    raw = call_hf_api(
        messages=messages,
        hf_token=hf_token,
        model=model,
        max_tokens=800,
        temperature=0.10,
    )

    # On any error sentinel, return the original text unchanged
    if raw.startswith("__"):
        return text

    return raw.strip() if raw else text
