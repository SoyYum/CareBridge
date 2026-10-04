from app.services.ingestion import chunk_pages

def test_chunking_page_and_overlap():
    chunks = chunk_pages([{"page": 3, "text": "a" * 250}], size=120, overlap=20)
    assert len(chunks) == 3
    assert all(x["page"] == 3 for x in chunks)
    assert chunks[0]["text"][-20:] == chunks[1]["text"][:20]

def test_empty_page():
    assert chunk_pages([{"page": 1, "text": " "}]) == []
