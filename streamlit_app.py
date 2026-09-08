import streamlit as st

from app.rag import RAGService


# ============================================================
# Page configuration
# ============================================================

st.set_page_config(
    page_title="AI Manufacturing Troubleshooting Copilot",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# Custom styling
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background: linear-gradient(
            180deg,
            #f5f7fa 0%,
            #ffffff 50%,
            #f8fafc 100%
        );
    }

    .block-container {
        max-width: 1180px;
        padding-top: 1.25rem;
        padding-bottom: 2.5rem;
    }

    /* ---------------- Hero ---------------- */

    .hero {
        background: linear-gradient(
            135deg,
            #0f172a 0%,
            #17345d 52%,
            #2563eb 100%
        );
        padding: 1.55rem 1.9rem 1.65rem 1.9rem;
        border-radius: 18px;
        margin-bottom: 1.15rem;
        box-shadow: 0 12px 28px rgba(15, 23, 42, 0.14);
    }

    .hero-icon {
        width: 64px;
        height: 50px;
        position: relative;
        margin-bottom: 0.65rem;
    }

    .factory-main {
        position: absolute;
        left: 3px;
        bottom: 2px;
        width: 57px;
        height: 29px;
        border: 3px solid #ffffff;
        border-radius: 3px;
        box-sizing: border-box;
    }

    .factory-roof {
        position: absolute;
        left: 5px;
        top: 7px;
        width: 31px;
        height: 18px;
        border-top: 3px solid #ffffff;
        border-right: 3px solid #ffffff;
        transform: skewY(-27deg);
        box-sizing: border-box;
    }

    .factory-stack {
        position: absolute;
        right: 8px;
        top: 1px;
        width: 11px;
        height: 34px;
        border: 3px solid #ffffff;
        border-bottom: none;
        box-sizing: border-box;
    }

    .factory-window {
        position: absolute;
        width: 9px;
        height: 9px;
        border: 2px solid #ffffff;
        box-sizing: border-box;
    }

    .factory-window.w1 {
        left: 12px;
        bottom: 10px;
    }

    .factory-window.w2 {
        left: 27px;
        bottom: 10px;
    }

    .factory-door {
        position: absolute;
        right: 11px;
        bottom: 2px;
        width: 10px;
        height: 19px;
        border: 2px solid #ffffff;
        border-bottom: none;
        box-sizing: border-box;
    }

    .hero-title {
        color: #ffffff;
        font-size: 2.15rem;
        font-weight: 750;
        line-height: 1.15;
        margin: 0;
    }

    .hero-subtitle {
        color: #dbeafe;
        font-size: 1rem;
        line-height: 1.5;
        margin-top: 0.55rem;
    }

    .equipment-badge {
        display: inline-block;
        margin-top: 0.85rem;
        padding: 0.42rem 0.78rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.18);
        color: #e0f2fe;
        font-size: 0.84rem;
    }

    /* ---------------- Section ---------------- */

    .section-heading {
        font-size: 1.22rem;
        font-weight: 700;
        color: #0f172a;
        margin-top: 0.7rem;
        margin-bottom: 0.5rem;
    }

    .section-description {
        color: #64748b;
        font-size: 0.91rem;
        margin-bottom: 0.7rem;
    }

    /* ---------------- Query ---------------- */

    .query-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 15px;
        padding: 0.2rem 0.45rem 0.1rem 0.45rem;
        box-shadow: 0 5px 16px rgba(15, 23, 42, 0.05);
    }

    /* ---------------- Button ---------------- */

    .stButton > button {
        width: 100%;
        min-height: 3rem;
        border-radius: 10px;
        font-weight: 700;
    }

    /* ---------------- Answer ---------------- */

    .answer-header {
        font-size: 1.22rem;
        font-weight: 700;
        color: #0f172a;
        margin-top: 1.15rem;
        margin-bottom: 0.35rem;
    }

    .answer-card {
        background: #ffffff;
        border: 1px solid #dbe3ee;
        border-left: 5px solid #2563eb;
        border-radius: 14px;
        padding: 1.1rem 1.35rem;
        box-shadow: 0 7px 20px rgba(15, 23, 42, 0.06);
    }

    /* ---------------- Safety ---------------- */

    .safety-box {
        background: #fff8ed;
        border: 1px solid #fed7aa;
        border-left: 5px solid #f97316;
        padding: 0.9rem 1.1rem;
        border-radius: 12px;
        color: #7c2d12;
        margin-top: 1.25rem;
    }

    .safety-title {
        font-weight: 700;
        margin-bottom: 0.3rem;
    }

    /* ---------------- Footer ---------------- */

    .footer {
        text-align: center;
        color: #64748b;
        font-size: 0.8rem;
        padding-top: 1.35rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Cached RAG service
# ============================================================

@st.cache_resource
def get_rag_service():
    return RAGService()


# ============================================================
# Hero
# ============================================================

st.html(
    '''
    <div class="hero">

        <div class="hero-icon" aria-label="Industrial factory">

            <div class="factory-main"></div>
            <div class="factory-roof"></div>
            <div class="factory-stack"></div>

            <div class="factory-window w1"></div>
            <div class="factory-window w2"></div>

            <div class="factory-door"></div>

        </div>

        <div class="hero-title">
            AI Manufacturing Troubleshooting Copilot
        </div>

        <div class="hero-subtitle">
            Evidence-based AI assistance for industrial maintenance
            and troubleshooting.
        </div>

        <div class="equipment-badge">
            Equipment Knowledge Base:
            Danfoss VLT AutomationDrive FC 302
        </div>

    </div>
    '''
)


# ============================================================
# Query section
# ============================================================

st.markdown(
    '<div class="section-heading">🔍 Ask a Maintenance Question</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-description">'
    'Describe the equipment condition, alarm, warning, or maintenance issue.'
    '</div>',
    unsafe_allow_html=True,
)

query = st.text_area(
    label="Maintenance question",
    label_visibility="collapsed",
    placeholder=(
        "Example: Motor starts but trips after 10–15 seconds.\n"
        "Example: What is the cause and troubleshooting procedure "
        "for Warning 1, 10 Volts Low?"
    ),
    height=115,
)

col1, col2 = st.columns([3.2, 1])

with col1:
    top_k = st.slider(
        "Evidence sources",
        min_value=1,
        max_value=10,
        value=5,
        help="Number of documentation chunks retrieved as evidence.",
    )

with col2:
    st.write("")
    diagnose = st.button(
        "🔍 Diagnose",
        type="primary",
        use_container_width=True,
    )


# ============================================================
# Diagnosis
# ============================================================

if diagnose:

    if not query.strip():
        st.warning("Please enter a maintenance or troubleshooting question.")
        st.stop()

    with st.spinner(
        "Retrieving engineering evidence and generating response..."
    ):

        try:
            rag = get_rag_service()

            result = rag.ask(
                query=query,
                top_k=top_k,
            )

        except Exception as exc:
            st.error(f"Application error: {exc}")
            st.stop()

    # --------------------------------------------------------
    # Answer
    # --------------------------------------------------------

    st.markdown(
        '<div class="answer-header">🧠 Engineering Assessment</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="answer-card">',
        unsafe_allow_html=True,
    )

    st.markdown(result["answer"])

    st.markdown(
        '</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Evidence
    # --------------------------------------------------------

    sources = result.get("sources", [])

    st.markdown(
        f'<div class="answer-header">📚 Evidence Sources ({len(sources)})</div>',
        unsafe_allow_html=True,
    )

    if not sources:
        st.info("No supporting documentation sources were returned.")

    for index, source in enumerate(sources, start=1):

        page_start = source.get("page_start")
        page_end = source.get("page_end")

        if page_start == page_end:
            page_label = str(page_start)
        else:
            page_label = f"{page_start}–{page_end}"

        with st.expander(
            f"Source {index}  •  Page {page_label}"
        ):

            st.write(
                f"**Document:** "
                f"{source.get('source') or 'Unknown'}"
            )

            st.write(
                f"**Pages:** {page_label}"
            )

            st.write(
                f"**Section:** "
                f"{source.get('section') or '—'}"
            )

            st.write(
                f"**Subsection:** "
                f"{source.get('subsection') or '—'}"
            )

            st.write(
                f"**Subsubsection:** "
                f"{source.get('subsubsection') or '—'}"
            )

            st.write(
                f"**Chunk ID:** "
                f"{source.get('chunk_id') or '—'}"
            )


# ============================================================
# Safety
# ============================================================

st.html(
    """
    <div class="safety-box">
        <div class="safety-title">⚠️ Safety Notice</div>
        This copilot provides evidence-based documentation guidance.
        It does not autonomously control machinery. Final maintenance,
        electrical, and safety decisions must be made by a qualified
        professional following applicable procedures.
    </div>
    """
)


# ============================================================
# Footer
# ============================================================

st.html(
    """
    <div class="footer">
        AI Manufacturing Troubleshooting Copilot ·
        Evidence-backed engineering assistance
    </div>
    """
)
