# CareBridge – Healthcare Document Intelligence Assistant

CareBridge is a document-grounded healthcare information assistant that allows users to upload healthcare PDF documents, search their contents, and ask questions using natural language.

It uses Retrieval-Augmented Generation (RAG) to retrieve relevant passages from uploaded documents and generate answers grounded in those passages. Responses include source citations to help users trace information back to the original documents.

**CareBridge is intended for educational and informational use only. It is not a medical diagnostic system and must not be used as a substitute for professional medical advice.**

## Live Demo

- **Frontend:** https://carebridge-v88or5uvp9vva8uhywungz.streamlit.app
- **Backend:** https://carebridge-gcfs.onrender.com
- **API Health Check:** https://carebridge-gcfs.onrender.com/health

## Features

- **User Authentication:** Secure registration and login using password hashing and JWT-based authentication.
- **PDF Upload:** Upload text-based healthcare PDF documents for processing.
- **Document Indexing:** Extract text, divide documents into smaller chunks, and generate vector embeddings.
- **Semantic Search:** Retrieve relevant document passages based on the meaning of a user's question.
- **Retrieval-Augmented Generation:** Generate answers using retrieved document context rather than relying solely on general model knowledge.
- **Source Citations:** Display references to the documents and passages used to generate an answer.
- **Document Management:** View uploaded documents and remove documents from the library.
- **Chat Interface:** Ask natural-language questions about uploaded documents.
- **Multilingual Responses:** Supports English and Hindi response modes.
- **Safety Notices:** Display educational-use disclaimers with generated responses.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Vector Database | Qdrant Cloud |
| Embeddings | Google Gemini Embedding API |
| Language Model | Google Gemini API |
| PDF Processing | PyPDF |
| Authentication | JWT and bcrypt |
| API Server | Uvicorn |
| Backend Hosting | Render |
| Frontend Hosting | Streamlit Community Cloud |

## Architecture

CareBridge follows a client-server architecture.

1. The user interacts with the Streamlit frontend.
2. The frontend communicates with the FastAPI backend through HTTP requests.
3. Uploaded PDFs are processed and divided into smaller text chunks.
4. Gemini generates embeddings for the document chunks.
5. The embeddings and associated metadata are stored in Qdrant Cloud.
6. When a user asks a question, the backend generates a query embedding and retrieves relevant passages from Qdrant.
7. The retrieved passages are provided to Gemini as context.
8. Gemini generates a document-grounded response.
9. The backend returns the answer and its source references to the frontend.

PostgreSQL stores user accounts, document metadata, chat sessions, and message history.

## Retrieval-Augmented Generation Pipeline

The application uses the following workflow:

**Document ingestion**

- Extract text from uploaded PDF files.
- Split extracted text into manageable chunks.
- Generate vector embeddings using the Gemini embedding model.
- Store embeddings and document metadata in Qdrant Cloud.

**Question answering**

- Accept a natural-language question.
- Generate an embedding for the question.
- Retrieve relevant chunks using semantic similarity.
- Combine retrieved context with the user's question.
- Generate an answer using Gemini.
- Return the answer with source references.

The generation instructions emphasize document grounding, relevance, citation accuracy, and avoiding unsupported medical claims.

## Project Structure

The main components are organized as follows. Adjust the paths below if your repository uses a different structure.

```text
CareBridge/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   │
│   └── services/
│       ├── ingestion.py
│       ├── vector_store.py
│       ├── retrieval.py
│       ├── rag.py
│       ├── generation.py
│       └── safety.py
│
├── frontend.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/SoyYum/CareBridge.git
cd CareBridge
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root or configure the corresponding environment variables in your hosting platform.

```env
DATABASE_URL=your_postgresql_connection_string

JWT_SECRET=your_secure_random_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_MINUTES=120

GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_configured_gemini_generation_model
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
GEMINI_EMBEDDING_DIMENSIONS=768

QDRANT_URL=your_qdrant_cluster_url
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION=carebridge_chunks
```

Do not commit `.env` files, API keys, database credentials, or other secrets to GitHub.

### 5. Start the backend

```bash
uvicorn app.main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### 6. Start the frontend

Open another terminal, activate the virtual environment, and run:

```bash
streamlit run frontend.py
```

The frontend will be available at:

```text
http://localhost:8501
```

## Deployment

CareBridge is deployed using separate hosting services:

- **Streamlit Community Cloud:** Hosts the frontend.
- **Render:** Hosts the FastAPI backend.
- **PostgreSQL hosting:** Stores application data.
- **Qdrant Cloud:** Stores vector embeddings and document chunks.
- **Google Gemini API:** Handles embedding generation and answer generation.

The frontend communicates with the deployed backend using its configured API URL. Deployment credentials and API keys are stored as environment variables rather than hardcoded in the source code.

Free hosting services may have usage limits, inactivity-related sleep, or resource restrictions.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check backend availability |
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Authenticate a user |
| GET | `/me` | Retrieve authenticated user information |
| POST | `/documents` | Upload and index a PDF |
| GET | `/documents` | List uploaded documents |
| DELETE | `/documents/{document_id}` | Delete a document |
| POST | `/chat` | Ask a question about uploaded documents |
| GET | `/sessions` | Retrieve chat sessions |
| GET | `/sessions/{session_id}/messages` | Retrieve messages from a chat session |

Protected endpoints require a valid bearer token.

## Security and Limitations

- Passwords are stored as hashes rather than plaintext.
- JWT authentication protects user-specific endpoints.
- Authentication endpoints use rate limiting.
- Uploaded documents are associated with their respective users.
- Vector retrieval applies user-level filtering.
- API credentials are configured through environment variables.

Current limitations:

- Scanned PDFs requiring OCR are not supported.
- Answer quality depends on the content and quality of uploaded documents.
- Semantic retrieval may occasionally return irrelevant passages.
- The application is designed as an educational demonstration, not a production healthcare system.
- Free hosting and API tiers may impose usage and availability restrictions.

Only public, synthetic, or otherwise non-sensitive sample documents should be used in the public demonstration.

## Future Improvements

- Add OCR support for scanned PDFs.
- Improve retrieval evaluation and answer-quality measurement.
- Add more advanced document filtering and search.
- Improve multilingual response quality.
- Introduce automated evaluation for citation accuracy and retrieval relevance.
- Add document preview and page-level navigation.

## Disclaimer

CareBridge provides educational information based on uploaded documents. It does not provide medical diagnoses, treatment recommendations, or emergency assistance.

Always consult a qualified healthcare professional for medical concerns.

## Author

**Soyam Bais**  
Indian Institute of Technology Patna

GitHub: https://github.com/SoyYum