
import os
import requests
import streamlit as st


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="CareBridge | Healthcare Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================================================
# CLOUD CONFIGURATION
# ==================================================

DEFAULT_API_URL = "https://carebridge-gcfs.onrender.com"


def get_api_url():
    """Read the backend URL from Streamlit secrets or environment."""

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


# ==================================================
# SESSION STATE
# ==================================================

defaults = {
    "token": None,
    "session_id": None,
    "history": [],
    "language": "auto",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown(
    """
    <style>
    :root {
        --primary: #167D79;
        --primary-hover: #105E5A;
        --background: #F5F9F8;
        --surface: #FFFFFF;
        --sidebar: #EDF5F3;
        --text: #183332;
        --muted: #617875;
        --border: #DCE9E6;
    }

    html, body, .stApp,
    [data-testid="stAppViewContainer"] {
        background: var(--background) !important;
        color: var(--text) !important;
    }

    .block-container {
        max-width: 1250px;
        padding: 2rem 2.5rem 5rem;
    }

    [data-testid="stHeader"],
    [data-testid="stToolbar"] {
        background: var(--background) !important;
    }

    h1, h2, h3, h4, h5, h6,
    p, label, li, strong,
    .stMarkdown {
        color: var(--text) !important;
    }

    [data-testid="stCaptionContainer"] {
        color: var(--muted) !important;
    }

    [data-testid="stSidebar"] {
        background: var(--sidebar) !important;
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: var(--text) !important;
    }

    input, textarea,
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
        color: #81928F !important;
        -webkit-text-fill-color: #81928F !important;
    }

    [data-baseweb="select"] > div {
        background: #FFFFFF !important;
        border-color: var(--border) !important;
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
        background: #EAF3F1 !important;
    }

    [data-testid="stRadio"] label,
    [data-testid="stRadio"] p,
    [data-testid="stRadio"] span {
        color: var(--text) !important;
    }

    div.stButton > button,
    div.stFormSubmitButton > button {
        background: #FFFFFF !important;
        color: var(--primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        min-height: 2.65rem;
        font-weight: 600;
        transition: 0.2s ease;
    }

    div.stButton > button:hover {
        background: #EAF3F1 !important;
        border-color: var(--primary) !important;
    }

    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button[kind="primary"] {
        background: var(--primary) !important;
        color: #FFFFFF !important;
        border-color: var(--primary) !important;
    }

    div.stButton > button[kind="primary"]:hover,
    div.stFormSubmitButton > button[kind="primary"]:hover {
        background: var(--primary-hover) !important;
        color: #FFFFFF !important;
    }

    [data-testid="stMetric"] {
        background: #FFFFFF !important;
        border: 1px solid var(--border);
        border-radius: 15px;
        padding: 1rem 1.2rem;
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"],
    [data-testid="stMetricDelta"] {
        color: var(--text) !important;
    }

    [data-testid="stChatMessage"] {
        background: #FFFFFF !important;
        border: 1px solid var(--border);
        border-radius: 15px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }

    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li {
        color: var(--text) !important;
    }

    [data-testid="stBottom"],
    [data-testid="stBottomBlockContainer"] {
        background: var(--background) !important;
    }

    [data-testid="stChatInput"] {
        background: #FFFFFF !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
    }

    [data-testid="stChatInput"] textarea {
        background: #FFFFFF !important;
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
    }

    [data-testid="stFileUploader"] {
        background: #FFFFFF !important;
        border: 1px dashed #AFCBC5 !important;
        border-radius: 12px;
        padding: 0.5rem;
    }

    [data-testid="stFileUploader"] * {
        color: var(--text) !important;
    }

    [data-testid="stExpander"] {
        background: #FFFFFF !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px;
    }

    [data-testid="stAlert"] {
        border-radius: 12px;
    }

    [data-testid="stAlert"] p {
        color: var(--text) !important;
    }

    .cb-brand {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 0.3rem;
    }

    .cb-brand-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 54px;
        height: 54px;
        border-radius: 15px;
        background: #DFF0EC;
        font-size: 28px;
    }

    .cb-brand-name {
        color: var(--text) !important;
        font-size: 2rem;
        font-weight: 750;
        letter-spacing: -1px;
    }

    .cb-subtitle {
        color: var(--muted) !important;
        margin: 0.2rem 0 1.5rem 68px;
    }

    .cb-eyebrow {
        color: var(--primary) !important;
        font-size: 0.75rem;
        font-weight: 750;
        letter-spacing: 0.12em;
    }

    .cb-footer {
        color: var(--muted) !important;
        font-size: 0.82rem;
        text-align: center;
        padding-top: 1.5rem;
    }

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


# ==================================================
# API HELPER
# ==================================================

def api_call(method, path, *, timeout=120, **kwargs):
    """Make authenticated requests to the hosted FastAPI backend."""

    headers = dict(kwargs.pop("headers", {}) or {})

    if st.session_state.token:
        headers["Authorization"] = (
            f"Bearer {st.session_state.token}"
        )

    url = API_URL + path

    try:
        response = requests.request(
            method,
            url,
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
            "Render may be waking up after inactivity. "
            "Wait a little and try again."
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


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def reset_chat():
    st.session_state.session_id = None
    st.session_state.history = []


def render_brand():
    st.markdown(
        """
        <div class="cb-brand">
            <div class="cb-brand-icon">🩺</div>
            <div class="cb-brand-name">CareBridge</div>
        </div>
        <div class="cb-subtitle">
            Your healthcare document companion
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sources(sources):
    if not sources:
        return

    with st.expander(
        f"📚 Sources used ({len(sources)})",
        expanded=False,
    ):
        for index, source in enumerate(sources, start=1):
            source_label = source.get("id") or f"S{index}"
            document_name = source.get("document", "Document")
            page_number = source.get("page", "?")

            st.markdown(
                f"**[{source_label}] {document_name} · Page {page_number}**"
            )

            excerpt = source.get("excerpt", "")

            if excerpt:
                st.caption(excerpt)

            if index < len(sources):
                st.divider()


# ==================================================
# SIDEBAR BRANDING
# ==================================================

with st.sidebar:
    st.markdown("### 🩺 CareBridge")
    st.caption("Document intelligence workspace")
    st.caption("Connected to hosted FastAPI backend")


# ==================================================
# AUTHENTICATION
# ==================================================

if not st.session_state.token:

    render_brand()

    left, center, right = st.columns([1, 1.25, 1])

    with center:

        st.markdown(
            '<div class="cb-eyebrow">WELCOME</div>',
            unsafe_allow_html=True,
        )

        st.subheader("Sign in to your workspace")

        st.markdown(
            """
            <p style="color:#617875 !important;">
                Upload your documents, ask questions, and
                explore answers grounded in your files.
            </p>
            """,
            unsafe_allow_html=True,
        )

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
                placeholder="At least 10 characters",
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
                CareBridge is an educational document assistant,
                not a medical professional.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.stop()


# ==================================================
# LOAD USER DATA
# ==================================================

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


# ==================================================
# SIDEBAR: USER WORKSPACE
# ==================================================

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

    # DOCUMENT LIBRARY

    st.markdown("### 📄 Document library")

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

                st.markdown(f"**{filename}**")

                st.caption(
                    f"{document.get('chunks', 0)} indexed sections"
                )

            with delete_col:

                if st.button(
                    "✕",
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

    # LANGUAGE SELECTION

    st.markdown("### 🌐 Answer language")

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

    # CHAT HISTORY

    st.markdown("### 💬 Conversations")

    if st.button(
        "＋ Start a new chat",
        use_container_width=True,
    ):
        reset_chat()
        st.rerun()

    if sessions:

        session_options = {
            f"{item['title']} · #{item['id']}": item["id"]
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


# ==================================================
# MAIN DASHBOARD
# ==================================================

render_brand()

metric_col1, metric_col2, metric_col3 = st.columns(3)

with metric_col1:
    st.metric("Documents", len(documents))

with metric_col2:
    st.metric("Saved conversations", len(sessions))

with metric_col3:
    st.metric(
        "Answer language",
        language_labels[st.session_state.language],
    )

st.markdown("### Ask your documents")

st.markdown(
    """
    <p style="color:#617875 !important;">
        Ask a question about the PDFs in your library.
        CareBridge searches relevant passages and uses them
        to prepare a response.
    </p>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# EMPTY DOCUMENT STATE
# ==================================================

if not documents:
    st.info(
        "📄 Upload a text-based PDF from the sidebar "
        "before asking document questions."
    )


# ==================================================
# CONVERSATION HISTORY
# ==================================================

for item in st.session_state.history:

    with st.chat_message(item["role"]):

        st.markdown(item["content"])

        if item["role"] == "assistant":
            render_sources(item.get("sources", []))


# ==================================================
# CHAT INPUT
# ==================================================

question = st.chat_input(
    "Ask a question about your uploaded documents...",
    disabled=not bool(documents),
)


# ==================================================
# PROCESS QUESTION
# ==================================================

if question:

    st.session_state.history.append(
        {
            "role": "user",
            "content": question,
            "sources": [],
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):

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


# ==================================================
# MEDICAL DISCLAIMER
# ==================================================

st.divider()

st.markdown(
    """
    <div class="cb-footer">
        ⚕️ Educational use only. Do not use CareBridge for
        emergencies, diagnosis, treatment decisions, or
        medication changes. Always consult a qualified
        healthcare professional.
    </div>
    """,
    unsafe_allow_html=True,
)
