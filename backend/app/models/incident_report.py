from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base



class IncidentReport(Base):
    __tablename__ = "incident_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    source: Mapped[str] = mapped_column(
        String(100),
        default="kaggle",
        nullable=False,
    )

    source_record_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    event_date: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )


    industry: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    incident_type: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    severity: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )


    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    recommended_training_topics: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )