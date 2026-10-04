
import os

import requests
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="CareBridge | Healthcare Assistant",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# BACKEND CONFIGURATION
# ============================================================

DEFAULT_API_URL = "https://carebridge-gcfs.onrender.com"


def get_api_url():
    """Get the hosted backend URL from Streamlit secrets or environment."""

    try:
        secret_url = st.secrets.get("CAREBRIDGE_API_URL", "")
    except Exception:
        secret_url = ""

    return (
        secret_url
        or os.getenv("CAREBRIDGE_API_URL")
        or DEFAULT_API_URL
    ).rstrip("/")


API_URL = get_api_url()


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "token": None,
    "session_id": None,
    "history": [],
    "language": "auto",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>

    :root {
        --primary: #167D79;
        --primary-dark: #105E5A;
        --background: #F5F8FA;
        --surface: #FFFFFF;
        --sidebar: #F0F5F6;
        --text: #172F3A;
        --muted: #647985;
        --border: #DCE5E9;
        --soft-teal: #E7F3F1;
    }

    /* Main application */

    .stApp {
        background: var(--background);
        color: var(--text);
    }

    [data-testid="stAppViewContainer"] {
        background: var(--background);
    }

    .block-container {
        max-width: 1350px;
        padding: 2rem 2.5rem 4rem;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    /* Typography */

    html, body, p, label, li,
    h1, h2, h3, h4, h5, h6 {
        color: var(--text);
    }

    h1 {
        font-weight: 750 !important;
        letter-spacing: -1.3px;
    }

    h2, h3 {
        font-weight: 650 !important;
        letter-spacing: -0.4px;
    }

    [data-testid="stCaptionContainer"] {
        color: var(--muted);
    }

    /* Sidebar */

    [data-testid="stSidebar"] {
        background: var(--sidebar);
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: var(--text);
    }

    /* Inputs */

    input,
    textarea,
    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea {
        background: #FFFFFF !important;
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
        border-color: var(--border) !important;
        border-radius: 9px !important;
    }

    input::placeholder,
    textarea::placeholder {
        color: #81919A !important;
        -webkit-text-fill-color: #81919A !important;
    }

    /* Select boxes */

    [data-baseweb="select"] > div {
        background: #FFFFFF !important;
        border-color: var(--border) !important;
        border-radius: 9px !important;
    }

    [data-baseweb="select"] *,
    [data-baseweb="select"] span {
        color: var(--text) !important;
    }

    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [role="listbox"] {
        background: #FFFFFF !important;
        border: 1px solid var(--border) !important;
    }

    [role="option"] {
        background: #FFFFFF !important;
        color: var(--text) !important;
    }

    [role="option"]:hover,
    [role="option"][aria-selected="true"] {
        background: var(--soft-teal) !important;
    }

    /* Buttons */

    div.stButton > button,
    div.stFormSubmitButton > button {
        background: #FFFFFF !important;
        color: var(--primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 9px !important;
        min-height: 2.65rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover {
        background: var(--soft-teal) !important;
        border-color: var(--primary) !important;
        color: var(--primary-dark) !important;
    }

    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button[kind="primary"] {
        background: var(--primary) !important;
        color: #FFFFFF !important;
        border-color: var(--primary) !important;
    }

    div.stButton > button[kind="primary"]:hover,
    div.stFormSubmitButton > button[kind="primary"]:hover {
        background: var(--primary-dark) !important;
        color: #FFFFFF !important;
    }

    /* Metrics */

    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 13px;
        padding: 1rem 1.2rem;
        box-shadow: 0 2px 8px rgba(23, 47, 58, 0.025);
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"],
    [data-testid="stMetricDelta"] {
        color: var(--text) !important;
    }

    /* Chat messages */

    [data-testid="stChatMessage"] {
        background: #FFFFFF !important;
        border: 1px solid var(--border);
        border-radius: 13px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.85rem;
        box-shadow: 0 2px 8px rgba(23, 47, 58, 0.025);
    }

    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li {
        color: var(--text) !important;
        line-height: 1.75;
    }

    /* Chat input */

    [data-testid="stBottom"],
    [data-testid="stBottomBlockContainer"] {
        background: var(--background) !important;
    }

    [data-testid="stChatInput"] {
        background: #FFFFFF !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        box-shadow: 0 3px 12px rgba(23, 47, 58, 0.04);
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 2px rgba(22, 125, 121, 0.10);
    }

    [data-testid="stChatInput"] textarea {
        background: #FFFFFF !important;
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
    }

    /* PDF uploader */

    [data-testid="stFileUploader"] {
        background: #FFFFFF !important;
        border: 1px dashed #AFC5CC !important;
        border-radius: 11px;
        padding: 0.65rem;
    }

    [data-testid="stFileUploader"] section {
        background: #FFFFFF !important;
    }

    [data-testid="stFileUploader"] button {
        background: #FFFFFF !important;
        color: var(--primary) !important;
        border: 1px solid var(--border) !important;
    }

    [data-testid="stFileUploader"] *,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] small {
        color: var(--text) !important;
    }

    /* Expanders and alerts */

    [data-testid="stExpander"] {
        background: #FFFFFF !important;
        border: 1px solid var(--border) !important;
        border-radius: 11px;
    }

    [data-testid="stAlert"] {
        border-radius: 10px;
    }

    [data-testid="stAlert"] p {
        color: var(--text) !important;
    }

    /* Dividers */

    hr {
        border-color: var(--border) !important;
    }

    /* Branding */

    .cb-brand {
        display: flex;
        align-items: center;
        gap: 13px;
        margin-bottom: 0.4rem;
    }

    .cb-brand-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        background: var(--soft-teal);
        color: var(--primary);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        font-weight: 800;
        border: 1px solid #D3E8E4;
    }

    .cb-brand-name {
        color: var(--text) !important;
        font-size: 2rem;
        font-weight: 750;
        letter-spacing: -1px;
    }

    .cb-subtitle {
        color: var(--muted) !important;
        font-size: 0.94rem;
        margin: 0.25rem 0 1.7rem 61px;
    }

    .cb-eyebrow {
        color: var(--primary) !important;
        font-size: 0.73rem;
        font-weight: 750;
        letter-spacing: 0.13em;
        margin-bottom: 0.5rem;
    }

    .cb-section-label {
        color: var(--primary) !important;
        font-size: 0.75rem;
        font-weight: 750;
        letter-spacing: 0.1em;
        margin-bottom: 0.45rem;
    }

    .cb-footer {
        color: var(--muted) !important;
        font-size: 0.82rem;
        line-height: 1.6;
        text-align: center;
        padding: 1.2rem 0 0.5rem;
    }

    .cb-sidebar-brand {
        font-size: 1.35rem;
        font-weight: 750;
        letter-spacing: -0.5px;
        color: var(--text);
        margin-bottom: 0.2rem;
    }

    .cb-sidebar-description {
        font-size: 0.85rem;
        color: var(--muted);
        margin-bottom: 1rem;
    }

    .cb-file-name {
        font-size: 0.9rem;
        font-weight: 600;
        overflow-wrap: anywhere;
    }

    .cb-login-card {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.5rem;
    }

    /* Mobile layout */

    @media (max-width: 700px) {
        .block-container {
            padding: 1rem 1rem 4rem;
        }

        .cb-brand-name {
            font-size: 1.7rem;
        }

        .cb-subtitle {
            margin-left: 0;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# API HELPER
# ============================================================

def api_call(method, path, *, timeout=120, **kwargs):
    """Send authenticated requests to the FastAPI backend."""

    headers = dict(kwargs.pop("headers", {}) or {})

    if st.session_state.token:
        headers["Authorization"] = (
            f"Bearer {st.session_state.token}"
        )

    try:
        response = requests.request(
            method,
            API_URL + path,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

        if response.status_code >= 400:

            try:
                detail = response.json().get(
                    "detail",
                    response.text,
                )
            except (ValueError, AttributeError):
                detail = response.text

            st.error(
                f"API error ({response.status_code}): {detail}"
            )

            return None

        if not response.content:
            return {}

        return response.json()

    except requests.Timeout:
        st.error(
            "The backend took too long to respond. "
            "It may be waking up after inactivity. "
            "Please wait and try again."
        )

    except requests.ConnectionError:
        st.error(
            "Could not connect to the CareBridge backend. "
            "Please try again in a moment."
        )

    except requests.RequestException as exc:
        st.error(f"Request failed: {exc}")

    except ValueError:
        st.error("The backend returned an invalid response.")

    return None


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def reset_chat():
    st.session_state.session_id = None
    st.session_state.history = []


def render_brand():
    st.markdown(
        """
        <div class="cb-brand">
            <div class="cb-brand-icon">CB</div>
            <div class="cb-brand-name">CareBridge</div>
        </div>
        <div class="cb-subtitle">
            Healthcare document intelligence
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sources(sources):
    """Display document references used to generate an answer."""

    if not sources:
        return

    with st.expander(
        f"Sources used ({len(sources)})",
        expanded=False,
    ):

        for index, source in enumerate(sources, start=1):

            source_label = source.get("id") or f"S{index}"
            document_name = source.get("document", "Document")
            page_number = source.get("page", "?")

            st.markdown(
                f"**[{source_label}] {document_name} - Page {page_number}**"
            )

            excerpt = source.get("excerpt", "")

            if excerpt:
                st.caption(excerpt)

            if index < len(sources):
                st.divider()


# ============================================================
# SIDEBAR BRANDING
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="cb-sidebar-brand">CareBridge</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="cb-sidebar-description">'
        'Healthcare document intelligence workspace'
        '</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# AUTHENTICATION
# ============================================================

if not st.session_state.token:

    render_brand()

    left, center, right = st.columns([1, 1.2, 1])

    with center:

        st.markdown(
            '<div class="cb-eyebrow">WELCOME</div>',
            unsafe_allow_html=True,
        )

        st.title("Your documents, understood.")

        st.markdown(
            """
            Upload healthcare documents, ask questions in natural
            language, and receive answers grounded in the content
            of your files.
            """
        )

        st.divider()

        mode = st.radio(
            "Account",
            ["Log in", "Create account"],
            horizontal=True,
            label_visibility="collapsed",
        )

        with st.form("auth_form", clear_on_submit=False):

            email = st.text_input(
                "Email address",
                placeholder="you@example.com",
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
            )

            submitted = st.form_submit_button(
                "Continue" if mode == "Log in" else "Create account",
                type="primary",
                use_container_width=True,
            )

        if submitted:

            if not email.strip() or not password:

                st.warning(
                    "Enter both your email address and password."
                )

            elif mode == "Create account" and len(password) < 10:

                st.warning(
                    "Your password must contain at least 10 characters."
                )

            else:

                endpoint = (
                    "/auth/login"
                    if mode == "Log in"
                    else "/auth/register"
                )

                result = api_call(
                    "POST",
                    endpoint,
                    timeout=60,
                    json={
                        "email": email.strip(),
                        "password": password,
                    },
                )

                if result and result.get("access_token"):

                    st.session_state.token = result["access_token"]

                    reset_chat()

                    st.rerun()

        st.markdown(
            """
            <div class="cb-footer">
                CareBridge is an educational document assistant.
                It does not replace professional medical advice.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.stop()


# ============================================================
# LOAD USER DATA
# ============================================================

documents = api_call(
    "GET",
    "/documents",
    timeout=60,
) or []

sessions = api_call(
    "GET",
    "/sessions",
    timeout=60,
) or []


# ============================================================
# SIDEBAR: USER WORKSPACE
# ============================================================

with st.sidebar:

    st.divider()

    user_col, logout_col = st.columns([3, 2])

    with user_col:

        st.caption("SIGNED IN")
        st.markdown("**Your workspace**")

    with logout_col:

        if st.button("Log out", use_container_width=True):

            st.session_state.token = None
            reset_chat()

            st.rerun()

    st.divider()

    # --------------------------------------------------------
    # DOCUMENT LIBRARY
    # --------------------------------------------------------

    st.markdown("### Document library")

    st.caption(
        "Upload a text-based PDF to make it searchable."
    )

    uploaded_pdf = st.file_uploader(
        "Choose a PDF",
        type=["pdf"],
        accept_multiple_files=False,
        help="Scanned PDFs without selectable text require OCR.",
    )

    if uploaded_pdf is not None:

        if st.button(
            "Upload and index",
            type="primary",
            use_container_width=True,
        ):

            with st.spinner(
                "Reading the PDF and building its search index..."
            ):

                result = api_call(
                    "POST",
                    "/documents",
                    timeout=300,
                    files={
                        "file": (
                            uploaded_pdf.name,
                            uploaded_pdf.getvalue(),
                            "application/pdf",
                        )
                    },
                )

            if result:

                if result.get("duplicate"):

                    st.info(
                        "This PDF is already in your library."
                    )

                else:

                    st.success(
                        f"Added {result.get('filename', uploaded_pdf.name)} "
                        f"({result.get('chunks', 0)} searchable sections)."
                    )

                st.rerun()

    st.markdown("#### Your files")

    if documents:

        for document in documents:

            file_col, delete_col = st.columns([5, 1])

            with file_col:

                filename = document.get("filename", "PDF")

                st.markdown(
                    f"**{filename}**"
                )

                st.caption(
                    f"{document.get('chunks', 0)} indexed sections"
                )

            with delete_col:

                if st.button(
                    "X",
                    key=f"delete_doc_{document['id']}",
                    help=f"Delete {filename}",
                ):

                    deleted = api_call(
                        "DELETE",
                        f"/documents/{document['id']}",
                        timeout=60,
                    )

                    if deleted:
                        st.success("Document deleted.")
                        st.rerun()

    else:

        st.caption(
            "Your library is empty. Upload a PDF to get started."
        )

    st.divider()

    # --------------------------------------------------------
    # LANGUAGE SELECTION
    # --------------------------------------------------------

    st.markdown("### Answer language")

    language_options = [
        "auto",
        "English",
        "Hindi",
    ]

    language_labels = {
        "auto": "Automatic",
        "English": "English",
        "Hindi": "Hindi (Experimental)",
    }

    if st.session_state.language not in language_options:
        st.session_state.language = "auto"

    st.session_state.language = st.selectbox(
        "Choose the language for new answers",
        options=language_options,
        format_func=lambda value: language_labels[value],
        index=language_options.index(
            st.session_state.language
        ),
        help=(
            "Automatic follows the language of your question. "
            "English and Hindi request that language explicitly."
        ),
    )

    if st.session_state.language == "Hindi":

        st.warning(
            "Hindi responses are experimental. Medical terminology "
            "and translations may contain inaccuracies. Please refer "
            "to the original document and verify important information "
            "with a healthcare professional."
        )

    st.divider()

    # --------------------------------------------------------
    # CHAT HISTORY
    # --------------------------------------------------------

    st.markdown("### Conversations")

    if st.button(
        "Start a new chat",
        use_container_width=True,
    ):

        reset_chat()
        st.rerun()

    if sessions:

        session_options = {
            f"{item['title']} - #{item['id']}": item["id"]
            for item in sessions
        }

        labels = list(session_options.keys())

        current_label = next(
            (
                label
                for label, sid in session_options.items()
                if sid == st.session_state.session_id
            ),
            None,
        )

        selected_label = st.selectbox(
            "Previous conversations",
            labels,
            index=(
                labels.index(current_label)
                if current_label in labels
                else None
            ),
            placeholder="Choose a conversation",
        )

        if selected_label:

            selected_id = session_options[selected_label]

            if selected_id != st.session_state.session_id:

                messages = api_call(
                    "GET",
                    f"/sessions/{selected_id}/messages",
                    timeout=60,
                )

                if messages is not None:

                    st.session_state.session_id = selected_id

                    st.session_state.history = [
                        {
                            "role": message["role"],
                            "content": message["content"],
                            "sources": [],
                        }
                        for message in messages
                        if message.get("role") in {
                            "user",
                            "assistant",
                        }
                    ]

                    st.rerun()


# ============================================================
# MAIN DASHBOARD
# ============================================================

render_brand()

st.markdown(
    '<div class="cb-eyebrow">YOUR WORKSPACE</div>',
    unsafe_allow_html=True,
)

st.title("Document intelligence")

st.markdown(
    """
    Search your uploaded healthcare documents and get
    answers supported by relevant passages from your files.
    """
)

st.write("")

# Dashboard metrics

metric_col1, metric_col2, metric_col3 = st.columns(3)

with metric_col1:
    st.metric(
        "Documents",
        len(documents),
    )

with metric_col2:
    st.metric(
        "Saved conversations",
        len(sessions),
    )

with metric_col3:
    st.metric(
        "Answer language",
        language_labels[st.session_state.language],
    )

st.write("")

st.divider()

# ============================================================
# DOCUMENT QUESTION ANSWERING
# ============================================================

st.markdown(
    '<div class="cb-eyebrow">DOCUMENT ASSISTANT</div>',
    unsafe_allow_html=True,
)

st.subheader("Ask your documents")

st.markdown(
    """
    Ask a question about the PDFs in your library.
    CareBridge retrieves relevant passages and uses them
    to prepare a document-grounded response.
    """
)

if not documents:

    st.info(
        "Upload a text-based PDF from the sidebar before "
        "asking questions."
    )


# ============================================================
# CONVERSATION HISTORY
# ============================================================

for item in st.session_state.history:

    if item["role"] == "user":

        with st.chat_message("user", avatar="U"):

            st.markdown(item["content"])

    else:

        with st.chat_message("assistant", avatar="C"):

            st.markdown(item["content"])

            render_sources(item.get("sources", []))


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask a question about your uploaded documents...",
    disabled=not bool(documents),
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:

    st.session_state.history.append(
        {
            "role": "user",
            "content": question,
            "sources": [],
        }
    )

    with st.chat_message("user", avatar="U"):

        st.markdown(question)

    with st.chat_message("assistant", avatar="C"):

        with st.spinner(
            "Searching your documents and preparing an answer..."
        ):

            result = api_call(
                "POST",
                "/chat",
                timeout=300,
                json={
                    "session_id": st.session_state.session_id,
                    "question": question,
                    "language": st.session_state.language,
                },
            )

        if result:

            st.session_state.session_id = result["session_id"]

            answer = result["answer"]

            st.markdown(answer)

            sources = result.get("sources") or []

            render_sources(sources)

            st.session_state.history.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                }
            )

        else:

            st.warning(
                "No answer was returned. The backend may be waking "
                "up or may have encountered an error. Please retry."
            )


# ============================================================
# MEDICAL DISCLAIMER
# ============================================================

st.divider()

st.markdown(
    """
    <div class="cb-footer">
        Educational use only. CareBridge does not provide medical
        diagnosis or treatment. Do not use it for emergencies,
        treatment decisions, or medication changes. Always consult
        a qualified healthcare professional.
    </div>
    """,
    unsafe_allow_html=True,
)
