import csv
import sys
from pathlib import Path

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.incident_report import IncidentReport


def get_value(row: dict[str, str], *names: str) -> str | None:
    normalized_row = {
        key.strip().lower(): value.strip()
        for key, value in row.items()
        if key is not None and value is not None
    }

    for name in names:
        value = normalized_row.get(name.lower())

        if value:
            return value

    return None


def build_title(description: str, event_title: str | None, nature_title: str | None) -> str:
    if event_title and nature_title:
        return f"{event_title} - {nature_title}"[:500]

    if event_title:
        return event_title[:500]

    if nature_title:
        return nature_title[:500]

    return description[:90].strip() + "..."


def build_training_topics(row: dict[str, str]) -> str | None:
    topics = []

    event_title = get_value(row, "EventTitle")
    source_title = get_value(row, "SourceTitle")
    nature_title = get_value(row, "NatureTitle")
    body_part = get_value(row, "Part of Body Title")

    if event_title:
        topics.append(event_title)

    if source_title:
        topics.append(source_title)

    if nature_title:
        topics.append(nature_title)

    if body_part:
        topics.append(body_part)

    if not topics:
        return None

    return "; ".join(topics)


def build_severity(row: dict[str, str]) -> str:
    hospitalized = get_value(row, "Hospitalized")
    amputation = get_value(row, "Amputation")

    if amputation and amputation not in {"0", "0.0"}:
        return "High - amputation"

    if hospitalized and hospitalized not in {"0", "0.0"}:
        return "High - hospitalization"

    return "Unknown"


def import_incidents(csv_path: Path, max_rows: int | None = None) -> int:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    imported_count = 0

    try:
        with csv_path.open("r", encoding="latin1", newline="") as csv_file:
            reader = csv.DictReader(csv_file)

            for row in reader:
                if max_rows is not None and imported_count >= max_rows:
                    break

                description = get_value(row, "Final Narrative")

                if not description:
                    continue

                source_record_id = get_value(row, "ID")

                existing = None

                if source_record_id:
                    existing = (
                        db.query(IncidentReport)
                        .filter(IncidentReport.source_record_id == source_record_id)
                        .first()
                    )

                if existing:
                    continue

                event_title = get_value(row, "EventTitle")
                nature_title = get_value(row, "NatureTitle")

                incident = IncidentReport(
                    source="OSHA Severe Injury Reports",
                    source_record_id=source_record_id,
                    event_date=get_value(row, "EventDate"),
                    industry=get_value(row, "Primary NAICS"),
                    incident_type=event_title,
                    severity=build_severity(row),
                    title=build_title(
                        description=description,
                        event_title=event_title,
                        nature_title=nature_title,
                    ),
                    description=description,
                    recommended_training_topics=build_training_topics(row),
                )

                db.add(incident)
                imported_count += 1

                if imported_count % 1000 == 0:
                    db.commit()
                    print(f"Imported so far: {imported_count}")

            db.commit()

    finally:
        db.close()

    return imported_count


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/import_incidents.py <path_to_csv> [max_rows]")
        raise SystemExit(1)

    csv_path = Path(sys.argv[1])

    if not csv_path.exists():
        print(f"File not found: {csv_path}")
        raise SystemExit(1)

    max_rows = None

    if len(sys.argv) >= 3:
        max_rows = int(sys.argv[2])

    count = import_incidents(csv_path=csv_path, max_rows=max_rows)
    print(f"Imported incident reports: {count}")