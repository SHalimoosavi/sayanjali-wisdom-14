"""
Sayanjali: Wisdom of the 14
Akhbari Shia Hadith Platform

Powered by:
- Streamlit
- Hugging Face Router API
- Qwen / DeepSeek Models

Sources:
- Kitab Sulaim bin Qais
- Mizan al-Hikmah
- Tuhaf al-Uqool
- Bihar al-Anwar
- Al-Kafi
- Wasail al-Shia
"""

import os
import streamlit as st

from ai_helper import (
    detect_language,
    query_hadith_ai,
    get_welcome_hadith,
)

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Sayanjali: Wisdom of the 14",
    page_icon="☪",
    layout="centered",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# CUSTOM THEME
# --------------------------------------------------

st.markdown(
    """
<style>

@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Lato:wght@300;400;700&family=Noto+Nastaliq+Urdu&display=swap');

:root{
    --bg:#0D0F14;
    --card:#13161E;
    --panel:#1A1E2A;

    --gold:#C9A84C;
    --gold-soft:#E8CC80;
    --gold-dark:#7A6230;

    --teal:#2E8B7A;
    --teal-light:#4ABFA8;

    --text:#E8E2D5;
    --muted:#8A8478;

    --border:#2A2E3E;
}

/* ------------------------------------------------ */
/* GLOBAL */
/* ------------------------------------------------ */

html, body, [class*="css"]{
    background-color:var(--bg)!important;
    color:var(--text)!important;
    font-family:'Lato', sans-serif;
}

#MainMenu,
footer,
header{
    visibility:hidden;
}

.block-container{
    max-width:900px;
    padding-top:1rem;
}

/* ------------------------------------------------ */
/* MASTHEAD */
/* ------------------------------------------------ */

.masthead{
    text-align:center;
    padding:2rem 1rem;
    margin-bottom:1.5rem;
    border-bottom:1px solid var(--border);
}

.masthead-ar{
    font-family:'Amiri', serif;
    color:var(--gold);
    font-size:2.3rem;
}

.masthead-title{
    color:var(--text);
    font-size:1rem;
    letter-spacing:.2em;
    text-transform:uppercase;
}

.masthead-sub{
    color:var(--gold-dark);
    font-size:.8rem;
    margin-top:.4rem;
}

/* ------------------------------------------------ */
/* CARD */
/* ------------------------------------------------ */

.hadith-card{
    background:var(--card);
    border:1px solid var(--border);
    border-left:3px solid var(--gold);
    border-radius:8px;
    padding:1.2rem;
    margin:1rem 0;
}

/* ------------------------------------------------ */
/* BADGES */
/* ------------------------------------------------ */

.imam-badge{
    display:inline-block;
    background:#17352d;
    border:1px solid var(--teal);
    color:var(--teal-light);
    padding:.2rem .6rem;
    border-radius:5px;
    font-size:.75rem;
    font-weight:700;
}

/* ------------------------------------------------ */
/* LANGUAGES */
/* ------------------------------------------------ */

.lang-label{
    color:var(--gold-soft);
    font-size:.8rem;
    font-weight:700;
    margin-bottom:.25rem;
}

.arabic{
    direction:rtl;
    text-align:right;
    font-family:'Amiri', serif;
    font-size:1.3rem;
    line-height:2;
    color:var(--gold-soft);
}

.urdu{
    direction:rtl;
    text-align:right;
    font-family:'Noto Nastaliq Urdu', serif;
    line-height:2;
}

.english{
    line-height:1.8;
}

.hindi{
    line-height:1.8;
}

/* ------------------------------------------------ */
/* SIDEBAR */
/* ------------------------------------------------ */

[data-testid="stSidebar"]{
    background:var(--card)!important;
}

.sidebar-heading{
    color:var(--gold);
    font-size:.8rem;
    letter-spacing:.12em;
    font-weight:700;
    margin-top:1rem;
    margin-bottom:.4rem;
}

.book-card{
    background:var(--panel);
    border:1px solid var(--border);
    padding:.7rem;
    border-radius:6px;
    margin-bottom:.4rem;
}

.book-title{
    color:var(--gold-soft);
    font-weight:700;
}

.book-desc{
    color:var(--muted);
    font-size:.8rem;
}

/* ------------------------------------------------ */
/* NOTICE */
/* ------------------------------------------------ */

.notice{
    background:#1a1010;
    border:1px solid #8b2e2e;
    border-left:3px solid #c0392b;
    padding:.8rem;
    border-radius:6px;
    color:#d4837a;
    font-size:.82rem;
}

/* ------------------------------------------------ */
/* BUTTONS */
/* ------------------------------------------------ */

.stButton > button{
    background:linear-gradient(
        135deg,
        #1e4a3e,
        #2e8b7a
    )!important;

    color:white!important;
    border:none!important;
    border-radius:6px!important;
}

/* ------------------------------------------------ */
/* TEXTAREA */
/* ------------------------------------------------ */

textarea{
    background:var(--panel)!important;
    color:var(--text)!important;
}

</style>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = []

if "hf_token" not in st.session_state:
    try:
        st.session_state.hf_token = st.secrets.get("HF_TOKEN", "")
    except Exception:
        st.session_state.hf_token = os.environ.get("HF_TOKEN", "")

    if not st.session_state.hf_token:
        st.session_state.hf_token = os.getenv(
            "HF_TOKEN",
            "",
        )

if "model_choice" not in st.session_state:
    st.session_state.model_choice = "Qwen/QwQ-32B"

if "prefill" not in st.session_state:
    st.session_state.prefill = ""

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown(
        """
        <div style="text-align:center;padding:1rem;">
            <div style="
                font-family:'Amiri',serif;
                color:#C9A84C;
                font-size:1.7rem;
            ">
                سيانجالي
            </div>

            <div style="
                color:#8A8478;
                letter-spacing:.2em;
                text-transform:uppercase;
                font-size:.7rem;
            ">
                Wisdom of the 14
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # ------------------------------------------
    # HF TOKEN
    # ------------------------------------------

    st.markdown(
        '<div class="sidebar-heading">🔑 HUGGING FACE TOKEN</div>',
        unsafe_allow_html=True,
    )

    token = st.text_input(
        "HF Token",
        value=st.session_state.hf_token,
        type="password",
        placeholder="hf_xxxxxxxxxxxxx",
        label_visibility="collapsed",
    )

    if token:
        st.session_state.hf_token = token

    if st.session_state.hf_token:
        st.success("Token loaded")
    else:
        st.warning("Enter Hugging Face token")

    # ------------------------------------------
    # MODEL
    # ------------------------------------------

    st.markdown(
        '<div class="sidebar-heading">🤖 MODEL</div>',
        unsafe_allow_html=True,
    )

    selected_model = st.selectbox(
        "Model",
        [
            "Qwen/QwQ-32B",
            "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
            "Qwen/Qwen2.5-72B-Instruct",
        ],
        label_visibility="collapsed",
    )

    st.session_state.model_choice = selected_model

    # ------------------------------------------
    # SOURCES
    # ------------------------------------------

    st.markdown(
        '<div class="sidebar-heading">📚 SOURCES</div>',
        unsafe_allow_html=True,
    )

    sources = [
        (
            "Kitab Sulaim Bin Qais",
            "Oldest surviving Shia source",
        ),
        (
            "Mizan al-Hikmah",
            "Scale of Wisdom",
        ),
        (
            "Tuhaf al-Uqool",
            "Teachings of Ahlul Bayt",
        ),
        (
            "Bihar al-Anwar",
            "Major hadith collection",
        ),
        (
            "Al-Kafi",
            "Core Twelver hadith work",
        ),
        (
            "Wasail al-Shia",
            "Legal narrations collection",
        ),
    ]

    for title, desc in sources:

        st.markdown(
            f"""
            <div class="book-card">
                <div class="book-title">
                    {title}
                </div>

                <div class="book-desc">
                    {desc}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    st.markdown(
        """
        <div class="notice">
            <b>Akhbari Notice</b><br>
            This platform is configured to provide
            narrations and knowledge from the
            14 Infallibles and the selected source
            collections only.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    if st.button(
        "🗑 Clear History",
        use_container_width=True,
    ):
        st.session_state.history = []
        st.rerun()

# --------------------------------------------------
# MASTHEAD
# --------------------------------------------------

st.markdown(
    """
    <div class="masthead">

        <div class="masthead-ar">
            حِكْمَةُ الأَرْبَعَةَ عَشَرَ
        </div>

        <div class="masthead-title">
            SAYANJALI · WISDOM OF THE 14
        </div>

        <div class="masthead-sub">
            Hadith • Knowledge • History
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# TABS
# --------------------------------------------------

tab_search, tab_imams, tab_about = st.tabs(
    [
        "🔍 Ask & Search",
        "☪ The 14 Infallibles",
        "ℹ About",
    ]
)

# --------------------------------------------------
# TAB 1 : SEARCH
# --------------------------------------------------

with tab_search:

    st.markdown(
        """
        <div style="
            color:#8A8478;
            line-height:1.8;
            margin-bottom:1rem;
        ">
        Ask your question in English, Urdu, Hindi or Arabic.
        The AI will search for relevant narrations and
        return a structured response.
        </div>
        """,
        unsafe_allow_html=True,
    )

    examples = [
        "What did Imam Ali say about knowledge?",
        "What is patience according to Imam Husayn?",
        "What is Imamate?",
        "علم کے بارے میں امام علی نے کیا فرمایا؟",
        "امام حسین نے کربلا میں کیا فرمایا؟",
        "धैर्य के बारे में इमाम हुसैन ने क्या कहा?",
    ]

    st.markdown(
        '<div class="sidebar-heading">EXAMPLE QUERIES</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    for i, ex in enumerate(examples):

        if i % 2 == 0:
            with col1:
                if st.button(
                    ex,
                    key=f"example_{i}",
                    use_container_width=True,
                ):
                    st.session_state.prefill = ex
                    st.rerun()
        else:
            with col2:
                if st.button(
                    ex,
                    key=f"example_{i}",
                    use_container_width=True,
                ):
                    st.session_state.prefill = ex
                    st.rerun()

    st.markdown(
        '<div class="ornament">✦ ✦ ✦</div>',
        unsafe_allow_html=True,
    )

    prefill = st.session_state.get("prefill", "")

    query = st.text_area(
        "Question",
        value=prefill,
        height=120,
        placeholder="Ask a question...",
        label_visibility="collapsed",
    )

    col_a, col_b, _ = st.columns([1, 1, 2])

    with col_a:
        search_btn = st.button(
            "🔍 Seek Wisdom",
            use_container_width=True,
        )

    with col_b:
        daily_btn = st.button(
            "✨ Daily Hadith",
            use_container_width=True,
        )

    # ------------------------------------------
    # DAILY HADITH
    # ------------------------------------------

    if daily_btn:

        if not st.session_state.hf_token:

            st.error(
                "Please add a Hugging Face token first."
            )

        else:

            with st.spinner(
                "Seeking wisdom..."
            ):

                result = get_welcome_hadith(
                    hf_token=st.session_state.hf_token,
                    model=st.session_state.model_choice,
                )

                if result:

                    st.session_state.history.insert(
                        0,
                        {
                            "query": "✨ Daily Hadith",
                            "lang": "en",
                            "result": result,
                        },
                    )

                    st.rerun()

    # ------------------------------------------
    # USER QUERY
    # ------------------------------------------

    if search_btn and query.strip():

        if not st.session_state.hf_token:

            st.error(
                "Please add a Hugging Face token first."
            )

        else:

            with st.spinner(
                "Consulting the wisdom of the 14 Infallibles..."
            ):

                lang = detect_language(query)

                result = query_hadith_ai(
                    query=query,
                    detected_lang=lang,
                    hf_token=st.session_state.hf_token,
                    model=st.session_state.model_choice,
                )

                st.session_state.history.insert(
                    0,
                    {
                        "query": query,
                        "lang": lang,
                        "result": result,
                    },
                )

                st.rerun()

    # ------------------------------------------
    # EMPTY STATE
    # ------------------------------------------

    if not st.session_state.history:

        st.markdown(
            """
            <div style="
                text-align:center;
                padding:3rem 1rem;
                color:#666;
            ">

                <div style="
                    font-size:2.2rem;
                    margin-bottom:.5rem;
                ">
                    ☪
                </div>

                Ask a question to begin your journey
                into the wisdom of the 14 Infallibles.

            </div>
            """,
            unsafe_allow_html=True,
        )

    # ------------------------------------------
    # HISTORY RENDER
    # ------------------------------------------

    else:

        st.markdown(
            '<div class="ornament">· · ·</div>',
            unsafe_allow_html=True,
        )

        lang_map = {
            "en": "English",
            "ur": "Urdu",
            "hi": "Hindi",
            "ar": "Arabic",
        }

        for idx, entry in enumerate(
            st.session_state.history
        ):

            result = entry["result"]

            label = entry["query"]

            if len(label) > 70:
                label = label[:70] + "..."

            with st.expander(
                label,
                expanded=(idx == 0),
            ):

                if entry["query"] != "✨ Daily Hadith":

                    st.markdown(
                        f"""
                        <span style="font-size:.8rem;color:#7A6230;">
                        Detected Language:
                        </span>

                        <span class="lang-pill">
                        {lang_map.get(entry['lang'],'English')}
                        </span>
                        """,
                        unsafe_allow_html=True,
                    )

                st.session_state["_current_result"] = result

# ----------------------------------
                # KNOWLEDGE RESPONSE
                # ----------------------------------

                if result.get("response_type") == "knowledge":

                    title = result.get(
                        "title",
                        "Knowledge",
                    )

                    content = result.get(
                        "content",
                        "",
                    )

                    st.markdown(
                        f"""
                        <div class="hadith-card">

                            <h3 style="
                                color:#E8CC80;
                                margin-bottom:1rem;
                            ">
                                📚 {title}
                            </h3>

                            <div class="hadith-english"
                                 style="line-height:1.8;">
                                {content}
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # ----------------------------------
                # USULI WARNING
                # ----------------------------------

                if result.get("usuli_warning"):

                    st.markdown(
                        f"""
                        <div class="notice">

                            <b>⚠ Akhbari Position</b><br>

                            {result['usuli_warning']}

                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # ----------------------------------
                # HADITH RESULTS
                # ----------------------------------

                elif result.get("hadiths"):

                    for hadith in result["hadiths"]:

                        imam = hadith.get(
                            "imam",
                            "",
                        )

                        arabic = hadith.get(
                            "arabic",
                            "",
                        )

                        english = hadith.get(
                            "english",
                            "",
                        )

                        urdu = hadith.get(
                            "urdu",
                            "",
                        )

                        hindi = hadith.get(
                            "hindi",
                            "",
                        )

                        source = hadith.get(
                            "source",
                            "",
                        )

                        chain = hadith.get(
                            "chain",
                            "",
                        )

                        imam_html = ""

                        if imam:
                            imam_html = (
                                f'<span class="imam-badge">{imam}</span>'
                            )

                        arabic_html = ""

                        if arabic:
                            arabic_html = f"""
                            <div class="hadith-lang-row">

                                <span class="hadith-lang-label">
                                    📖 Arabic Original
                                </span>

                                <div class="hadith-arabic">
                                    {arabic}
                                </div>

                            </div>
                            """

                        english_html = ""

                        if english:
                            english_html = f"""
                            <div class="hadith-lang-row">

                                <span class="hadith-lang-label">
                                    🇬🇧 English
                                </span>

                                <div class="hadith-english">
                                    {english}
                                </div>

                            </div>
                            """

                        urdu_html = ""

                        if urdu:
                            urdu_html = f"""
                            <div class="hadith-lang-row">

                                <span class="hadith-lang-label">
                                    🇵🇰 Urdu
                                </span>

                                <div class="hadith-urdu">
                                    {urdu}
                                </div>

                            </div>
                            """

                        hindi_html = ""

                        if hindi:
                            hindi_html = f"""
                            <div class="hadith-lang-row">

                                <span class="hadith-lang-label">
                                    🇮🇳 Hindi
                                </span>

                                <div class="hadith-hindi">
                                    {hindi}
                                </div>

                            </div>
                            """

                        source_html = ""

                        if source:
                            source_html = f"""
                            <div class="hadith-source">
                                📚 <b>Source:</b> {source}
                            </div>
                            """

                        chain_html = ""

                        if chain:
                            chain_html = f"""
                            <div style="
                                font-size:.75rem;
                                color:#7A7A7A;
                                margin-top:.4rem;
                            ">
                                Chain: {chain}
                            </div>
                            """

                        st.markdown(
                            f"""
                            <div class="hadith-card">

                                <div style="margin-bottom:.7rem;">
                                    {imam_html}
                                </div>

                                {arabic_html}

                                {english_html}

                                {urdu_html}

                                {hindi_html}

                                {source_html}

                                {chain_html}

                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                # ----------------------------------
                # RAW RESPONSE / ERROR
                # ----------------------------------

                else:

                    raw = result.get(
                        "raw",
                        "No response received.",
                    )

                    st.markdown(
                        f"""
                        <div class="hadith-card">

                            <div class="hadith-english">
                                {raw}
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

# --------------------------------------------------
# TAB 2 : THE 14 INFALLIBLES
# --------------------------------------------------

with tab_imams:

    infallibles = [

        (
            "Prophet Muhammad ﷺ",
            "570–632 CE",
            "Seal of the Prophets and Messenger of Allah."
        ),

        (
            "Sayyida Fatimah Zahra ؑ",
            "605–632 CE",
            "Daughter of Rasulullah and Lady of Paradise."
        ),

        (
            "Imam Ali ibn Abi Talib ؑ",
            "600–661 CE",
            "Commander of the Faithful and Gate of Knowledge."
        ),

        (
            "Imam Hasan ibn Ali ؑ",
            "624–670 CE",
            "Second Imam and embodiment of patience."
        ),

        (
            "Imam Husayn ibn Ali ؑ",
            "626–680 CE",
            "Master of Martyrs and hero of Karbala."
        ),

        (
            "Imam Ali Zayn al-Abidin ؑ",
            "658–713 CE",
            "Author of Sahifa Sajjadiyya."
        ),

        (
            "Imam Muhammad al-Baqir ؑ",
            "676–733 CE",
            "The Splitter of Knowledge."
        ),

        (
            "Imam Jafar al-Sadiq ؑ",
            "702–765 CE",
            "The Truthful and teacher of Islamic sciences."
        ),

        (
            "Imam Musa al-Kadhim ؑ",
            "745–799 CE",
            "The Patient One."
        ),

        (
            "Imam Ali al-Ridha ؑ",
            "765–818 CE",
            "Imam of Khorasan."
        ),

        (
            "Imam Muhammad al-Jawad ؑ",
            "811–835 CE",
            "The Generous."
        ),

        (
            "Imam Ali al-Hadi ؑ",
            "827–868 CE",
            "The Guide."
        ),

        (
            "Imam Hasan al-Askari ؑ",
            "846–874 CE",
            "The Eleventh Imam."
        ),

        (
            "Imam Muhammad al-Mahdi ؑ",
            "869 CE – Present",
            "The Awaited Imam in Occultation."
        ),
    ]

    st.markdown(
        """
        <div style="
            color:#8A8478;
            line-height:1.8;
            margin-bottom:1rem;
        ">
        The 14 Infallibles are the central figures of guidance
        whose teachings form the foundation of this platform.
        </div>
        """,
        unsafe_allow_html=True,
    )

    for idx, (name, dates, desc) in enumerate(infallibles):

        num = str(idx + 1).zfill(2)

        st.markdown(
            f"""
            <div class="hadith-card">

                <div style="
                    display:flex;
                    gap:1rem;
                    align-items:flex-start;
                ">

                    <div style="
                        color:#7A6230;
                        font-size:1.4rem;
                        min-width:40px;
                    ">
                        {num}
                    </div>

                    <div>

                        <div style="
                            color:#E8CC80;
                            font-weight:700;
                            font-size:1rem;
                        ">
                            {name}
                        </div>

                        <div style="
                            color:#5A8A78;
                            font-size:.8rem;
                            margin-top:.2rem;
                        ">
                            {dates}
                        </div>

                        <div style="
                            color:#8A8478;
                            margin-top:.5rem;
                        ">
                            {desc}
                        </div>

                    </div>

                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

# --------------------------------------------------
# TAB 3 : ABOUT
# --------------------------------------------------

with tab_about:

    st.markdown(
        """
        <div class="hadith-card">

            <h3 style="color:#C9A84C;">
                About Sayanjali: Wisdom of the 14
            </h3>

            <p>
            Sayanjali is a multilingual hadith and
            knowledge platform powered by Streamlit
            and Hugging Face AI models.
            </p>

            <p>
            It supports English, Urdu, Hindi,
            and Arabic queries and presents
            responses in a structured format.
            </p>

            <p>
            Features include:
            </p>

            <ul>
                <li>AI-powered hadith search</li>
                <li>Daily Hadith generation</li>
                <li>Multilingual support</li>
                <li>Knowledge articles</li>
                <li>Source citations</li>
            </ul>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="notice">

            <b>Disclaimer</b><br>

            AI-generated content should always be
            verified with authentic source texts.
            The application is intended for
            educational and research purposes.

        </div>
        """,
        unsafe_allow_html=True,
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown(
    """
    <div style="
        text-align:center;
        margin-top:2rem;
        padding:1rem;
        color:#555;
        font-size:.75rem;
        letter-spacing:.08em;
    ">
        SAYANJALI NEXUS PRIVATE LIMITED<br>
        Wisdom of the 14 • Streamlit • Hugging Face
    </div>
    """,
    unsafe_allow_html=True,
)
