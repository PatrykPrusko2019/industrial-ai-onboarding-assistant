import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.models.incident_report import IncidentReport


@dataclass
class RetrievedSource:
    source_type: str
    title: str
    reference: str
    snippet: str
    score: int


STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "near",
    "what",
    "should",
    "know",
    "before",
    "about",
    "from",
    "this",
    "that",
    "into",
    "have",
    "when",
    "where",
    "which",
    "employee",
    "engineer",
    "new",
}


def normalize_text(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9ąćęłńóśźżĄĆĘŁŃÓŚŹŻ\- ]", " ", text.lower())


def tokenize(text: str) -> set[str]:
    normalized = normalize_text(text)

    return {
        word
        for word in normalized.split()
        if len(word) > 2 and word not in STOPWORDS
    }


def score_text(query: str, text: str) -> int:
    query_tokens = tokenize(query)
    text_tokens = tokenize(text)

    return len(query_tokens.intersection(text_tokens))


def search_document_chunks(
    db: Session,
    query: str,
    limit: int = 4,
) -> list[RetrievedSource]:
    chunks = db.query(DocumentChunk).limit(1000).all()
    scored_sources: list[RetrievedSource] = []

    for chunk in chunks:
        score = score_text(query, f"{chunk.title} {chunk.content}")

        if score > 0:
            scored_sources.append(
                RetrievedSource(
                    source_type="company_document",
                    title=chunk.title,
                    reference=chunk.source_file,
                    snippet=chunk.content[:500].replace("\n", " ").strip(),
                    score=score,
                )
            )

    scored_sources.sort(key=lambda source: source.score, reverse=True)

    return scored_sources[:limit]


def search_incident_reports(
    db: Session,
    query: str,
    limit: int = 4,
) -> list[RetrievedSource]:
    incidents = db.query(IncidentReport).limit(10000).all()
    scored_sources: list[RetrievedSource] = []

    for incident in incidents:
        searchable_text = " ".join(
            [
                incident.title or "",
                incident.description or "",
                incident.industry or "",
                incident.incident_type or "",
                incident.severity or "",
                incident.recommended_training_topics or "",
            ]
        )

        score = score_text(query, searchable_text)

        if score > 0:
            scored_sources.append(
                RetrievedSource(
                    source_type="incident_report",
                    title=incident.title,
                    reference=f"incident_report_{incident.id}",
                    snippet=incident.description[:500].replace("\n", " ").strip(),
                    score=score,
                )
            )

    scored_sources.sort(key=lambda source: source.score, reverse=True)

    return scored_sources[:limit]


def retrieve_sources(
    db: Session,
    query: str,
    limit: int = 6,
) -> list[RetrievedSource]:
    document_sources = search_document_chunks(db=db, query=query, limit=4)
    incident_sources = search_incident_reports(db=db, query=query, limit=4)

    sources = document_sources + incident_sources
    sources.sort(key=lambda source: source.score, reverse=True)

    return sources[:limit]