"""
Sayanjali: Wisdom of the 14
Akhbari Shia Hadith Platform — sourced exclusively from the 14 Infallibles.
Deploys free on Streamlit Community Cloud via Hugging Face Inference API.
"""

import streamlit as st
import os
from ai_helper import (
    detect_language,
    query_hadith_ai,
    translate_text,
    get_welcome_hadith,
)

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Sayanjali: Wisdom of the 14",
    page_icon="☪",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS — Calligraphic dark theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Lato:wght@300;400;700&family=Noto+Nastaliq+Urdu&display=swap');

/* ── Root palette ── */
:root {
  --bg-deep:    #0D0F14;
  --bg-card:    #13161E;
  --bg-panel:   #1A1E2A;
  --gold:       #C9A84C;
  --gold-soft:  #E8CC80;
  --gold-dim:   #7A6230;
  --teal:       #2E8B7A;
  --teal-light: #4ABFA8;
  --text-main:  #E8E2D5;
  --text-muted: #8A8478;
  --border:     #2A2E3E;
  --red-warn:   #8B2E2E;
}

/* ── Global reset ── */
html, body, [class*="css"] {
  background-color: var(--bg-deep) !important;
  color: var(--text-main) !important;
  font-family: 'Lato', sans-serif;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; max-width: 820px; }

/* ── Masthead ── */
.masthead {
  text-align: center;
  padding: 2.2rem 1rem 1.4rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1.6rem;
}
.masthead-arabic {
  font-family: 'Amiri', serif;
  font-size: 2.4rem;
  color: var(--gold);
  letter-spacing: 0.04em;
  line-height: 1.3;
  margin-bottom: 0.3rem;
}
.masthead-title {
  font-family: 'Lato', sans-serif;
  font-size: 1.05rem;
  font-weight: 300;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  color: var(--text-muted);
}
.masthead-sub {
  font-size: 0.78rem;
  color: var(--gold-dim);
  margin-top: 0.3rem;
  letter-spacing: 0.1em;
}

/* ── Ornament divider ── */
.ornament {
  text-align: center;
  color: var(--gold-dim);
  font-size: 1.1rem;
  margin: 0.8rem 0;
  letter-spacing: 0.5em;
}

/* ── Input area ── */
.stTextArea textarea {
  background-color: var(--bg-panel) !important;
  border: 1px solid var(--border) !important;
  border-radius: 6px !important;
  color: var(--text-main) !important;
  font-family: 'Lato', sans-serif !important;
  font-size: 0.97rem !important;
  line-height: 1.6 !important;
  padding: 0.8rem !important;
}
.stTextArea textarea:focus {
  border-color: var(--gold-dim) !important;
  box-shadow: 0 0 0 1px var(--gold-dim) !important;
}

/* ── Buttons ── */
.stButton > button {
  background: linear-gradient(135deg, #1E4A3E, #2E8B7A) !important;
  border: 1px solid var(--teal) !important;
  color: #E8FAF6 !important;
  border-radius: 5px !important;
  font-family: 'Lato', sans-serif !important;
  font-weight: 700 !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  font-size: 0.82rem !important;
  padding: 0.55rem 1.4rem !important;
  transition: all 0.2s ease !important;
}
.stButton > button:hover {
  background: linear-gradient(135deg, #2E8B7A, #4ABFA8) !important;
  border-color: var(--teal-light) !important;
  transform: translateY(-1px);
}

/* ── Hadith card ── */
.hadith-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-left: 3px solid var(--gold);
  border-radius: 8px;
  padding: 1.4rem 1.6rem;
  margin: 1rem 0;
  line-height: 1.85;
}
.hadith-lang-row {
  margin-bottom: 0.75rem;
  font-size: 0.95rem;
}
.hadith-lang-label {
  color: var(--gold-soft);
  font-weight: 700;
  font-size: 0.78rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  display: block;
  margin-bottom: 0.2rem;
}
.hadith-arabic {
  font-family: 'Amiri', serif;
  font-size: 1.3rem;
  direction: rtl;
  text-align: right;
  color: var(--gold-soft);
  line-height: 2;
}
.hadith-urdu {
  font-family: 'Noto Nastaliq Urdu', 'Amiri', serif;
  font-size: 1.05rem;
  direction: rtl;
  text-align: right;
  color: var(--text-main);
  line-height: 2;
}
.hadith-hindi {
  font-size: 1rem;
  color: var(--text-main);
}
.hadith-english {
  font-size: 0.97rem;
  color: var(--text-main);
  font-style: italic;
}
.hadith-source {
  margin-top: 1rem;
  padding-top: 0.7rem;
  border-top: 1px solid var(--border);
  font-size: 0.8rem;
  color: var(--gold-dim);
  letter-spacing: 0.06em;
}
.imam-badge {
  display: inline-block;
  background: #1A2E28;
  border: 1px solid var(--teal);
  color: var(--teal-light);
  border-radius: 4px;
  padding: 0.15rem 0.55rem;
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  margin-right: 0.4rem;
}

/* ── Warning box ── */
.akhbari-notice {
  background: #1A1010;
  border: 1px solid var(--red-warn);
  border-left: 3px solid #C0392B;
  border-radius: 6px;
  padding: 0.9rem 1.2rem;
  font-size: 0.83rem;
  color: #D4837A;
  margin: 0.8rem 0;
  line-height: 1.6;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background-color: var(--bg-card) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text-main) !important; }
.sidebar-section {
  font-size: 0.78rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.15em;
  margin: 1.2rem 0 0.4rem;
  font-weight: 700;
}
.sidebar-book {
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: 5px;
  padding: 0.6rem 0.8rem;
  margin-bottom: 0.4rem;
  font-size: 0.82rem;
  line-height: 1.5;
}
.sidebar-book-title {
  color: var(--gold-soft);
  font-weight: 700;
  font-size: 0.8rem;
}
.sidebar-book-desc {
  color: var(--text-muted);
  font-size: 0.75rem;
  margin-top: 0.15rem;
}

/* ── Spinner / status ── */
.stSpinner > div { border-top-color: var(--gold) !important; }

/* ── Select box ── */
.stSelectbox > div > div {
  background-color: var(--bg-panel) !important;
  border-color: var(--border) !important;
  color: var(--text-main) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--bg-card) !important;
  border-bottom: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
  color: var(--text-muted) !important;
  font-size: 0.82rem !important;
  letter-spacing: 0.1em !important;
}
.stTabs [aria-selected="true"] {
  color: var(--gold) !important;
  border-bottom-color: var(--gold) !important;
}

/* ── Detected lang pill ── */
.lang-pill {
  display: inline-block;
  background: #1E2A20;
  border: 1px solid #2E4A30;
  color: #7ABF85;
  border-radius: 12px;
  padding: 0.1rem 0.6rem;
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  margin-left: 0.4rem;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "hf_token" not in st.session_state:
    # Try from Streamlit secrets first, then env
    st.session_state.hf_token = (
        st.secrets.get("HF_TOKEN", None)
        or os.environ.get("HF_TOKEN", "")
    )
if "model_choice" not in st.session_state:
    st.session_state.model_choice = "Qwen/QwQ-32B"
if "welcome_shown" not in st.session_state:
    st.session_state.welcome_shown = False


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 0.5rem;">
      <div style="font-family:'Amiri',serif;font-size:1.6rem;color:#C9A84C;">
        سيانجالي
      </div>
      <div style="font-size:0.7rem;color:#8A8478;letter-spacing:0.2em;text-transform:uppercase;margin-top:0.2rem;">
        Wisdom of the 14
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # API Token
    st.markdown('<div class="sidebar-section">🔑 Hugging Face API</div>', unsafe_allow_html=True)
    token_input = st.text_input(
        "HF Token (hf_...)",
        value=st.session_state.hf_token or "",
        type="password",
        placeholder="hf_xxxxxxxxxxxxxxxx",
        help="Get free token at huggingface.co/settings/tokens",
        label_visibility="collapsed",
    )
    if token_input:
        st.session_state.hf_token = token_input

    if st.session_state.hf_token:
        st.success("✓ Token set", icon="🔐")
    else:
        st.warning("Add HF token to enable AI", icon="⚠")

    # Model
    st.markdown('<div class="sidebar-section">🤖 AI Model</div>', unsafe_allow_html=True)
    model = st.selectbox(
        "Model",
        options=[
            "Qwen/QwQ-32B",
            "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
            "Qwen/Qwen2.5-72B-Instruct",
        ],
        index=0,
        label_visibility="collapsed",
    )
    st.session_state.model_choice = model

    # Source Priority
    st.markdown('<div class="sidebar-section">📚 Source Priority</div>', unsafe_allow_html=True)

    books = [
        ("① Kitab Sulaim Bin Qais", "Oldest Shia hadith — backbone of Twelver beliefs"),
        ("② Mizan al-Hikmah", "Scale of Wisdom — bilingual Shi'a hadith compendium"),
        ("③ Tuhaf al-Uqool", "Masterpiece of the Intellect — Aal al-Rasool hadith"),
        ("④ Other Akhbari Books", "Bihar al-Anwar, Al-Kafi (hadith sections), Wasail"),
    ]
    for title, desc in books:
        st.markdown(f"""
        <div class="sidebar-book">
          <div class="sidebar-book-title">{title}</div>
          <div class="sidebar-book-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Akhbari notice
    st.markdown("""
    <div class="akhbari-notice">
      <b>⚠ Akhbari Shia Only</b><br>
      This app rejects Usuli marja following, ijtihad, and jurisprudential fatwas.
      All wisdom is sourced exclusively from the <b>14 Infallibles</b> via authenticated Akhbari hadith chains.
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Clear history
    if st.button("🗑 Clear History", use_container_width=True):
        st.session_state.history = []
        st.rerun()


# ─────────────────────────────────────────────
#  MASTHEAD
# ─────────────────────────────────────────────
st.markdown("""
<div class="masthead">
  <div class="masthead-arabic">حِكْمَةُ الأَرْبَعَةَ عَشَرَ</div>
  <div class="masthead-title">Sayanjali · Wisdom of the 14</div>
  <div class="masthead-sub">Akhbari Shia Hadith — The 14 Infallibles Only</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────
tab_search, tab_imams, tab_about = st.tabs(["🔍 Ask & Search", "☪ The 14 Infallibles", "ℹ About"])


# ════════════════════════════════════════════
#  TAB 1: SEARCH / ASK
# ════════════════════════════════════════════
with tab_search:
    st.markdown("""
    <div style="font-size:0.85rem;color:#8A8478;margin-bottom:1rem;line-height:1.6;">
      Ask a question or enter a topic in <b>English, Urdu, or Hindi</b>.
      The AI will respond with authentic hadith from the 14 Infallibles,
      sourced from Akhbari books (Kitab Sulaim, Mizan al-Hikmah, Tuhaf al-Uqool).
    </div>
    """, unsafe_allow_html=True)

    # Example queries
    examples = [
        "What did Imam Ali say about knowledge?",
        "علم کے بارے میں امام علی نے کیا فرمایا؟",
        "धैर्य के बारे में पैगंबर ने क्या कहा?",
        "What is the importance of Salah according to Imam Sadiq?",
        "امام حسین نے کربلا میں کیا فرمایا؟",
    ]

    col_ex1, col_ex2 = st.columns(2)
    with col_ex1:
        st.markdown('<div style="font-size:0.76rem;color:#7A6230;margin-bottom:0.3rem;">EXAMPLE QUERIES</div>', unsafe_allow_html=True)
        for ex in examples[:3]:
            if st.button(ex, key=f"ex_{ex[:20]}", use_container_width=True):
                st.session_state["prefill"] = ex
    with col_ex2:
        st.markdown('<div style="font-size:0.76rem;color:#7A6230;margin-bottom:0.3rem;">&nbsp;</div>', unsafe_allow_html=True)
        for ex in examples[3:]:
            if st.button(ex, key=f"ex_{ex[:20]}", use_container_width=True):
                st.session_state["prefill"] = ex

    st.markdown('<div class="ornament">✦ ✦ ✦</div>', unsafe_allow_html=True)

    prefill_val = st.session_state.pop("prefill", "")

    query = st.text_area(
        "Your question",
        value=prefill_val,
        placeholder="Ask in English, اردو, or हिंदी…",
        height=100,
        label_visibility="collapsed",
    )

    col_btn1, col_btn2, _ = st.columns([1, 1, 2])
    with col_btn1:
        search_btn = st.button("🔍 Seek Wisdom", use_container_width=True)
    with col_btn2:
        daily_btn = st.button("✨ Daily Hadith", use_container_width=True)

    # ── Process Daily Hadith ──
    if daily_btn:
        if not st.session_state.hf_token:
            st.error("Please add your Hugging Face API token in the sidebar.")
        else:
            with st.spinner("Seeking wisdom from the Infallibles…"):
                result = get_welcome_hadith(
                    hf_token=st.session_state.hf_token,
                    model=st.session_state.model_choice,
                )
                if result:
                    st.session_state.history.insert(0, {
                        "query": "✨ Daily Hadith",
                        "lang": "en",
                        "result": result,
                    })

    # ── Process Search ──
    if search_btn and query.strip():
        if not st.session_state.hf_token:
            st.error("Please add your Hugging Face API token in the sidebar.")
        else:
            with st.spinner("Consulting the hadith of the 14 Infallibles…"):
                lang = detect_language(query)
                result = query_hadith_ai(
                    query=query,
                    detected_lang=lang,
                    hf_token=st.session_state.hf_token,
                    model=st.session_state.model_choice,
                )
                if result:
                    st.session_state.history.insert(0, {
                        "query": query,
                        "lang": lang,
                        "result": result,
                    })

    # ── Render history ──
    if st.session_state.history:
        st.markdown('<div class="ornament">· · ·</div>', unsafe_allow_html=True)
        for i, entry in enumerate(st.session_state.history):
            r = entry["result"]
            lang = entry.get("lang", "en")
            lang_names = {"en": "English", "ur": "Urdu", "hi": "Hindi", "ar": "Arabic"}
            lang_label = lang_names.get(lang, lang.upper())

            with st.expander(
                f"{'✨ Daily' if entry['query'] == '✨ Daily Hadith' else '🔍'} {entry['query'][:70]}…" if len(entry['query']) > 70 else entry['query'],
                expanded=(i == 0),
            ):
                # Language detected
                if entry['query'] != "✨ Daily Hadith":
                    st.markdown(f'<span style="font-size:0.78rem;color:#7A6230;">Detected language:</span> <span class="lang-pill">{lang_label}</span>', unsafe_allow_html=True)

                # Check for Usuli warning
                if r.get("usuli_warning"):
                    st.markdown(f"""
                    <div class="akhbari-notice">
                      ⚠ <b>Akhbari Position:</b> {r['usuli_warning']}
                    </div>
                    """, unsafe_allow_html=True)

                # Main hadith card
                if r.get("hadiths"):
                    for h in r["hadiths"]:
                        imam = h.get("imam", "")
                        arabic = h.get("arabic", "")
                        english = h.get("english", "")
                        urdu = h.get("urdu", "")
                        hindi = h.get("hindi", "")
                        source = h.get("source", "")
                        chain = h.get("chain", "")

                        imam_html = f'<span class="imam-badge">{imam}</span>' if imam else ""
                        arabic_html = f'<div class="hadith-lang-row"><span class="hadith-lang-label">📖 Arabic Original</span><div class="hadith-arabic">{arabic}</div></div>' if arabic else ""
                        english_html = f'<div class="hadith-lang-row"><span class="hadith-lang-label">🇬🇧 English</span><div class="hadith-english">{english}</div></div>' if english else ""
                        urdu_html = f'<div class="hadith-lang-row"><span class="hadith-lang-label">🇵🇰 Urdu</span><div class="hadith-urdu">{urdu}</div></div>' if urdu else ""
                        hindi_html = f'<div class="hadith-lang-row"><span class="hadith-lang-label">🇮🇳 Hindi</span><div class="hadith-hindi">{hindi}</div></div>' if hindi else ""
                        source_html = f'<div class="hadith-source">📚 <b>Source:</b> {source}</div>' if source else ""
                        chain_html = f'<div style="font-size:0.75rem;color:#5A5448;margin-top:0.3rem;">Chain: {chain}</div>' if chain else ""

                        st.markdown(f"""
                        <div class="hadith-card">
                          <div style="margin-bottom:0.6rem;">{imam_html}</div>
                          {arabic_html}
                          {english_html}
                          {urdu_html}
                          {hindi_html}
                          {source_html}
                          {chain_html}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    # Fallback: raw response
                    raw = r.get("raw", "No response received.")
                    st.markdown(f"""
                    <div class="hadith-card">
                      <div class="hadith-english">{raw}</div>
                    </div>
                    """, unsafe_allow_html=True)

    elif not st.session_state.history:
        st.markdown("""
        <div style="text-align:center;padding:2.5rem 1rem;color:#4A4840;">
          <div style="font-size:2rem;margin-bottom:0.5rem;">☪</div>
          <div style="font-size:0.85rem;letter-spacing:0.1em;">
            Ask a question above to begin your journey<br>into the wisdom of the 14 Infallibles
          </div>
        </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════
#  TAB 2: THE 14 INFALLIBLES
# ════════════════════════════════════════════
with tab_imams:
    infallibles = [
        ("Prophet Muhammad ﷺ", "570–632 CE", "The Seal of Prophets. All hadith chains trace to him."),
        ("Sayyida Fatimah Zahra ؑ", "605–632 CE", "Daughter of the Prophet ﷺ. The mother of the Imams. Lady of Light."),
        ("Imam Ali ibn Abi Talib ؑ", "600–661 CE", "1st Imam. Commander of the Faithful. Gate of the City of Knowledge."),
        ("Imam Hasan ibn Ali ؑ", "624–670 CE", "2nd Imam. Grandson of the Prophet ﷺ. Embodiment of forbearance."),
        ("Imam Husayn ibn Ali ؑ", "626–680 CE", "3rd Imam. Master of Martyrs. The revolution of Karbala."),
        ("Imam Ali Zayn al-Abidin ؑ", "658–713 CE", "4th Imam. Author of Al-Sahifa Al-Sajjadiyya — the Psalms of Islam."),
        ("Imam Muhammad al-Baqir ؑ", "676–733 CE", "5th Imam. The Splitter of Knowledge — revived Shia scholarship."),
        ("Imam Jafar al-Sadiq ؑ", "702–765 CE", "6th Imam. The Truthful. Greatest jurisprudential teacher of the Imams."),
        ("Imam Musa al-Kadhim ؑ", "745–799 CE", "7th Imam. The Patient One. Imprisoned by Harun al-Rashid."),
        ("Imam Ali al-Ridha ؑ", "765–818 CE", "8th Imam. Imam of Khorasan. The Guarantor of a Deer."),
        ("Imam Muhammad al-Jawad ؑ", "811–835 CE", "9th Imam. The Generous. Became Imam at age 9."),
        ("Imam Ali al-Hadi ؑ", "827–868 CE", "10th Imam. The Guide. Kept under house arrest in Samarra."),
        ("Imam Hasan al-Askari ؑ", "846–874 CE", "11th Imam. Lived under Abbasid surveillance in Askar."),
        ("Imam Muhammad al-Mahdi ؑ", "869–present", "12th Imam. The Awaited Savior. In Occultation since 874 CE."),
    ]

    st.markdown("""
    <div style="font-size:0.85rem;color:#8A8478;margin-bottom:1.2rem;line-height:1.6;">
      The <b>14 Infallibles (Ma'sumeen)</b> are the sole authorities in Akhbari Shia Islam.
      Their hadith — transmitted through authenticated chains — constitute the complete divine guidance
      alongside the Holy Quran. No marja, moulvi, or scholar holds interpretive authority over them.
    </div>
    """, unsafe_allow_html=True)

    for i, (name, dates, desc) in enumerate(infallibles):
        num = f"0{i+1}" if i < 9 else str(i+1)
        role = "Prophet & Messenger" if i == 0 else ("Daughter of the Prophet" if i == 1 else f"Imam {i-1}")
        st.markdown(f"""
        <div class="hadith-card" style="margin:0.5rem 0;padding:0.9rem 1.2rem;">
          <div style="display:flex;align-items:flex-start;gap:0.8rem;">
            <div style="font-family:'Amiri',serif;font-size:1.4rem;color:#7A6230;min-width:2rem;text-align:center;">{num}</div>
            <div style="flex:1;">
              <div style="font-weight:700;color:#E8CC80;font-size:0.97rem;">{name}</div>
              <div style="font-size:0.77rem;color:#5A8A78;margin:0.15rem 0;">{dates} · {role}</div>
              <div style="font-size:0.82rem;color:#8A8478;margin-top:0.3rem;">{desc}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════
#  TAB 3: ABOUT
# ════════════════════════════════════════════
with tab_about:
    st.markdown("""
    <div class="hadith-card">
      <div style="font-size:1rem;font-weight:700;color:#C9A84C;margin-bottom:0.8rem;">About Sayanjali: Wisdom of the 14</div>
      <div style="font-size:0.87rem;line-height:1.85;color:#C8C2B5;">
        <b>Sayanjali</b> is an Akhbari Shia hadith platform that sources wisdom exclusively
        from the <b>14 Infallibles</b> — the Prophet Muhammad ﷺ, Sayyida Fatimah Zahra ؑ,
        and the 12 Imams of the Ahlul Bayt.
        <br><br>
        <b>Akhbari Shia Islam</b> holds that the Quran and the authenticated hadith of the
        Infallibles are the only two sources of guidance. It rejects the Usuli doctrine of
        marja-following, ijtihad (independent juristic reasoning), and clerical fatwas as
        human innovations with no sanction in the hadith of the Imams.
        <br><br>
        <b>Primary Sources Used:</b>
        <ul style="margin:0.6rem 0 0.6rem 1rem;color:#A09890;">
          <li><b>Kitab Sulaim Bin Qais al-Hilali</b> — The oldest surviving Shia book; the alphabet of Twelver beliefs</li>
          <li><b>Mizan al-Hikmah</b> (Rayshahri) — Comprehensive bilingual Shi'a hadith encyclopedia</li>
          <li><b>Tuhaf al-Uqool</b> (Ibn Shu'ba al-Harrani) — Hadith of the Aal al-Rasool</li>
          <li>Bihar al-Anwar, Al-Kafi, Wasail al-Shia, and other Akhbari-accepted collections</li>
        </ul>
        <b>Technology:</b> Built with Streamlit + Hugging Face Inference API (Qwen QwQ-32B / DeepSeek).
        Supports multilingual queries in English, Urdu, and Hindi with automatic translation.
      </div>
    </div>
    <div class="akhbari-notice">
      <b>⚠ Important Disclaimer:</b> This platform explicitly rejects all Usuli marja fatwas,
      jurisprudential ijtihad, and clerical interpretations. If a query involves Usuli rulings,
      the AI will state the Akhbari rejection of such authority and redirect to hadith of the Infallibles only.
    </div>
    <div style="text-align:center;color:#3A3830;font-size:0.75rem;margin-top:1.5rem;letter-spacing:0.1em;">
      SAYANJALI NEXUS PRIVATE LIMITED · Built on Android · Powered by Open-Source AI
    </div>
    """, unsafe_allow_html=True)
