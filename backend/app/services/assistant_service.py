import re

from sqlalchemy.orm import Session

from app.services.retrieval_service import RetrievedSource, retrieve_sources


RISK_KEYWORDS = {
    "safety",
    "accident",
    "emergency",
    "high-voltage",
    "voltage",
    "certification",
    "certify",
    "lockout",
    "tagout",
    "evacuation",
    "danger",
    "hazard",
    "ppe",
    "quality",
    "non-conformance",
    "machine",
    "equipment",
    "injury",
    "near miss",
    "inspection",
    "maintenance",
    "tool",
    "welding",
    "electrical",
}

PROMPT_INJECTION_KEYWORDS = {
    "ignore previous instructions",
    "ignore all instructions",
    "reveal system prompt",
    "show hidden prompt",
    "bypass",
    "jailbreak",
    "developer message",
    "system message",
    "secret",
    "password",
    "api key",
}


def normalize_text(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9ąćęłńóśźżĄĆĘŁŃÓŚŹŻ\- ]", " ", text.lower())


def detect_prompt_injection(question: str) -> bool:
    normalized = normalize_text(question)

    return any(keyword in normalized for keyword in PROMPT_INJECTION_KEYWORDS)


def detect_risk_topic(question: str) -> bool:
    normalized = normalize_text(question)

    return any(keyword in normalized for keyword in RISK_KEYWORDS)


def build_context_summary(sources: list[RetrievedSource]) -> str:
    lines = []

    for source in sources[:4]:
        lines.append(f"- {source.title}: {source.snippet[:280]}")

    return "\n".join(lines)


def build_grounded_answer(question: str, db: Session) -> dict:
    if detect_prompt_injection(question):
        return {
            "answer": (
                "I cannot help with requests that try to bypass system rules, reveal hidden "
                "instructions, extract secrets or access protected data. Please ask a question "
                "related to onboarding, safety procedures, quality standards, tools or training."
            ),
            "confidence": 0.2,
            "requires_expert_review": True,
            "sources": [],
            "safety_notice": "Potential prompt injection or security-sensitive request detected.",
        }

    sources = retrieve_sources(db=db, query=question, limit=6)

    if not sources:
        return {
            "answer": (
                "I could not find enough verified information in the current company knowledge "
                "base or OSHA incident reports to answer this question reliably. Please consult "
                "a domain expert or add relevant documentation to the system."
            ),
            "confidence": 0.1,
            "requires_expert_review": True,
            "sources": [],
            "safety_notice": "No reliable source found in the knowledge base.",
        }

    requires_expert_review = detect_risk_topic(question)
    context_summary = build_context_summary(sources)

    answer = (
        "Based on the available company onboarding documents and similar OSHA incident reports, "
        "the employee should treat this topic as part of structured onboarding and follow approved "
        "internal procedures.\n\n"
        "Retrieved context suggests the following learning focus:\n"
        f"{context_summary}\n\n"
        "This answer is intended to support self-learning. It does not replace official company "
        "procedures, supervisor approval, certification requirements or expert decisions."
    )

    top_score = max(source.score for source in sources)
    confidence = min(0.88, 0.45 + len(sources) * 0.06 + top_score * 0.04)

    safety_notice = None

    if requires_expert_review:
        safety_notice = (
            "This question may involve safety, quality, tools, maintenance or certification. "
            "A qualified expert should review the final interpretation before the employee acts."
        )

    return {
        "answer": answer,
        "confidence": round(confidence, 2),
        "requires_expert_review": requires_expert_review,
        "sources": [
            {
                "source_type": source.source_type,
                "title": source.title,
                "reference": source.reference,
                "snippet": source.snippet,
            }
            for source in sources
        ],
        "safety_notice": safety_notice,
    }