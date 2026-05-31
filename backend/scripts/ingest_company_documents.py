import hashlib
import re
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.append(str(BACKEND_ROOT))

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.company_document import CompanyDocument
from app.models.document_chunk import DocumentChunk


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCUMENTS_DIR = PROJECT_ROOT / "data" / "company_documents"


def build_title(file_path: Path) -> str:
    return file_path.stem.replace("_", " ").title()


def calculate_content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def split_into_chunks(content: str, max_chars: int = 700) -> list[str]:
    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", content)
        if paragraph.strip()
    ]

    chunks: list[str] = []
    current_chunk = ""

    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) + 2 <= max_chars:
            current_chunk = f"{current_chunk}\n\n{paragraph}".strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)

            current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def ingest_documents() -> int:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    processed_count = 0

    try:
        for file_path in DOCUMENTS_DIR.glob("*.md"):
            content = file_path.read_text(encoding="utf-8")
            file_hash = calculate_content_hash(content)

            existing_document = (
                db.query(CompanyDocument)
                .filter(CompanyDocument.file_name == file_path.name)
                .first()
            )

            if existing_document and existing_document.content_hash == file_hash:
                continue

            if existing_document:
                db.query(DocumentChunk).filter(
                    DocumentChunk.document_id == existing_document.id
                ).delete()

                existing_document.content_hash = file_hash
                document = existing_document
            else:
                document = CompanyDocument(
                    title=build_title(file_path),
                    file_name=file_path.name,
                    document_type="onboarding",
                    content_hash=file_hash,
                )

                db.add(document)
                db.flush()

            chunks = split_into_chunks(content)

            for index, chunk in enumerate(chunks):
                db.add(
                    DocumentChunk(
                        document_id=document.id,
                        chunk_index=index,
                        title=document.title,
                        source_file=file_path.name,
                        content=chunk,
                    )
                )

            processed_count += 1

        db.commit()

    finally:
        db.close()

    return processed_count


if __name__ == "__main__":
    count = ingest_documents()
    print(f"Ingested or updated company documents: {count}")