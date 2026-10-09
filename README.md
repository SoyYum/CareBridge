# DocuMind — Document Intelligence Assistant

DocuMind is a document-grounded AI assistant that lets users upload PDF documents, ask questions in natural language, and receive answers supported by relevant passages from their files.

It combines retrieval-augmented generation (RAG), hybrid search, and source citations to make document exploration more efficient and transparent.

## Features

- **Document question answering:** Ask questions about uploaded PDF files using natural language.
- **Retrieval-Augmented Generation (RAG):** Generate answers using relevant passages retrieved from the user's documents.
- **Hybrid retrieval:** Combine semantic vector search with keyword-based retrieval to improve relevance.
- **Source citations:** Display supporting document passages and page information alongside answers.
- **User authentication:** Register and log in to a personal workspace.
- **Document isolation:** Keep document retrieval scoped to the authenticated user.
- **Conversation history:** Save and revisit previous conversations.
- **Multilingual interaction:** Request answers in English or Hindi, or use automatic language selection. Hindi support is experimental.
- **Document management:** Upload, index, list, and delete PDFs through the interface.
- **Responsive interface:** A Streamlit dashboard with document management and an interactive chat interface.

## Tech Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Backend API | FastAPI |
| Language | Python |
| Language model | Google Gemini API |
| Embeddings | Gemini embedding model |
| Vector database | Qdrant Cloud |
| Relational database | PostgreSQL |
| Authentication | JWT and password hashing |
| Retrieval | Hybrid search with semantic and keyword retrieval |
| Deployment | Streamlit Community Cloud and Render |

## Architecture

1. **Upload:** A user uploads a PDF through the Streamlit interface.
2. **Ingestion:** The FastAPI backend extracts text and divides it into searchable chunks.
3. **Indexing:** Document chunks are embedded and stored in Qdrant, alongside metadata used to associate them with the correct user and document.
4. **Retrieval:** When a question is submitted, the backend searches for relevant passages.
5. **Generation:** The retrieved context and question are passed to Gemini to generate a grounded response.
6. **Citations:** The response includes references to the retrieved sources where available.
7. **Persistence:** PostgreSQL stores application records, while the frontend allows users to revisit saved conversations and manage documents.

## Getting Started

### Prerequisites

- Python 3.11 or a compatible version supported by the project's dependencies
- A Google Gemini API key
- A Qdrant instance and API key
- A PostgreSQL database for the deployed configuration

### 1. Clone the repository

```bash
git clone https://github.com/SoyYum/CareBridge.git
cd CareBridge
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

Install the dependencies declared in the repository:

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file using the variable names expected by the backend configuration.

Typical settings include:

```env
DATABASE_URL=your_postgresql_connection_string
JWT_SECRET=your_long_random_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_MINUTES=120

GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_configured_gemini_model
GEMINI_EMBEDDING_MODEL=your_configured_embedding_model
GEMINI_EMBEDDING_DIMENSIONS=768

QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION=carebridge_chunks
```

Use the exact environment variable names expected by your current configuration. Keep `.env` out of version control and never commit API keys, database credentials, or production secrets.

### 5. Start the backend

From the repository root, run:

```bash
uvicorn app.main:app --reload
```

The API should be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

### 6. Configure the frontend

Set the backend URL for Streamlit using the existing environment variable:

```env
CAREBRIDGE_API_URL=http://127.0.0.1:8000
```

For Streamlit Community Cloud, configure the equivalent value in the application's secrets settings. Use the deployed backend URL for a hosted frontend.

### 7. Start the frontend

```bash
streamlit run frontend.py
```

Open the local URL printed by Streamlit, create an account, upload a PDF, and start asking questions.

## Deployment

The application can be deployed using the following arrangement:

- **Frontend:** Streamlit Community Cloud
- **Backend:** Render
- **Vector storage:** Qdrant Cloud
- **Relational storage:** PostgreSQL
- **Model API:** Google Gemini

Configure all required credentials and service URLs in the respective hosting platforms' environment-variable or secrets settings. Do not commit production credentials to the repository.

Free hosting tiers may sleep after periods of inactivity, causing the first request to take longer while a service wakes up.

## Limitations

- PDF documents are supported by the current upload workflow.
- Scanned PDFs may require OCR before their contents can be retrieved.
- Answer quality depends on document quality, retrieval relevance, and model output.
- Citations help users verify responses but do not guarantee that every generated statement is correct.
- Hindi responses are experimental and may contain translation inaccuracies.
- Large documents may take longer to upload and index.
- The application is intended as a portfolio and demonstration project, not a production-grade document management platform.

## Security Notes

- Authentication is required to access a user's workspace.
- Document retrieval and deletion should remain scoped to the authenticated user.
- Use a strong, private JWT signing secret.
- Store API keys and database credentials in environment variables or hosting secrets.
- Use HTTPS for deployed services.
- Do not upload confidential documents to a demonstration deployment unless its data handling and access controls are appropriate for that information.

## Future Improvements

- Support for DOCX and TXT documents
- Improved retrieval evaluation and ranking
- Better document previews and citation navigation
- Additional language support
- More comprehensive automated tests
- Enhanced ingestion for scanned documents

## License

Add a license file if you intend to distribute this project under a specific open-source license. Until then, no open-source license is implied by this README.
