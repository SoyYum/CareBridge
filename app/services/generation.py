
import re

from google import genai
from google.genai import types

from app.config import settings
from app.services.safety import NOTICE, emergency_prefix


SYSTEM = """
You are CareBridge, a document-grounded healthcare assistant.

Your ONLY task is to answer the user's exact question using
the supplied document excerpts.

STRICT RULES:

1. Never use outside knowledge.
2. Never add facts simply because they are related to the topic.
3. Answer only what the user explicitly asks.
4. Include all relevant information explicitly stated in the excerpts.
5. Do not confuse definitions, risk factors, symptoms, causes,
   treatments, and complications.
6. Do not invent symptoms, diseases, statistics or medical terms.
7. Every factual claim must have a supporting source citation.
8. Cite only the source that actually supports the claim.
9. If information is missing, say so.
10. Never diagnose or prescribe medication.
11. Never repeat information.
12. Preserve warnings and qualifications from the document.

Be concise, accurate and direct.
"""


_client = None


def get_gemini_client():

    global _client

    if _client is None:

        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is missing. "
                "Add it to your environment variables."
            )

        _client = genai.Client(
            api_key=settings.gemini_api_key
        )

    return _client


def _extract_context(contexts):

    formatted = []

    for index, item in enumerate(contexts, start=1):

        if not isinstance(item, dict):
            continue

        metadata = item.get("metadata") or {}

        content = (
            item.get("text")
            or item.get("page_content")
            or item.get("content")
            or ""
        ).strip()

        if not content:
            continue

        filename = (
            metadata.get("filename")
            or metadata.get("document")
            or item.get("filename")
            or "Uploaded document"
        )

        page = (
            metadata.get("page")
            or metadata.get("page_number")
            or item.get("page")
            or "Unknown"
        )

        source_id = metadata.get(
            "source_id",
            f"S{index}"
        )

        formatted.append(
            f"[{source_id}]\n"
            f"Document: {filename}\n"
            f"Page: {page}\n"
            f"Content:\n{content}"
        )

    return formatted


def _clean_answer(answer):

    """Remove exact duplicate lines without changing citations."""

    seen = set()
    result = []

    for line in answer.splitlines():

        normalized = re.sub(
            r"\s+",
            " ",
            line
        ).strip().lower()

        if normalized and normalized in seen:
            continue

        if normalized:
            seen.add(normalized)

        result.append(line)

    return "\n".join(result).strip()


def generate_answer(question, contexts, language="auto"):

    question = question.strip()

    if not question:
        return "Please enter a question."

    if not contexts:
        return (
            "The uploaded documents do not contain enough "
            "information to answer this question."
        )

    formatted_contexts = _extract_context(contexts)

    if not formatted_contexts:
        return (
            "The retrieved documents did not contain readable text. "
            "Please upload the PDF again."
        )

    context = "\n\n".join(formatted_contexts)

    if language and language.lower() in ("hindi", "hi"):

        language_instruction = """
LANGUAGE: Hindi.

Write entirely in natural, simple and grammatically correct Hindi.

Translate ONLY facts explicitly stated in the document.

Do not introduce additional medical information.

Preserve the exact meaning of the original statements.

Use English medical terms in parentheses only when necessary.
"""

    elif language and language.lower() in ("english", "en"):

        language_instruction = """
LANGUAGE: English.

Use clear, grammatically correct English.
"""

    else:

        language_instruction = """
Use the same language as the user's question.
"""

    prompt = f"""
{language_instruction}

USER QUESTION:
{question}

DOCUMENT EXCERPTS:
{context}

IMPORTANT ANSWERING RULES:

Before writing the answer, identify exactly what information
the question requests.

Consider each excerpt separately.

Use a fact only if that excerpt explicitly supports the answer.

Do not include other information merely because it discusses
the same disease or subject.

For example:
- A question about symptoms requires symptoms.
- A question about risk factors requires risk factors.
- A question about types requires the named types.
- A question about causes requires causes.

If the question asks for multiple items:
- Put each item on a separate bullet point.
- Include every supported item.
- Do not combine unrelated facts.
- Do not add an introduction or unnecessary conclusion.

Place the correct source citation immediately after each
factual statement.

If the excerpts do not contain the requested information,
say that the information is not available in the document.

Write complete sentences. Never stop in the middle of a sentence.

Return ONLY the answer.
"""

    try:

        client = get_gemini_client()

        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM,
                temperature=0.0,
                max_output_tokens=1024,
                top_p=0.8
            )
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty answer."
            )

        answer = response.text.strip()

        # Detect whether Gemini stopped because it reached
        # the configured output token limit.
        candidates = response.candidates or []

        if candidates:
            finish_reason = candidates[0].finish_reason

            if str(finish_reason).upper().endswith(
                "MAX_TOKENS"
            ):
                raise RuntimeError(
                    "Gemini reached its output token limit. "
                    "The response may be incomplete."
                )

        answer = _clean_answer(answer)

        if not answer:
            raise RuntimeError(
                "Gemini returned an empty answer after cleaning."
            )

        return (
            emergency_prefix(question)
            + answer
            + "\n\n"
            + NOTICE
        )

    except Exception as exc:

        raise RuntimeError(
            f"Gemini generation failed: {exc}"
        ) from exc
