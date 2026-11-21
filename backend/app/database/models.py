"""SQLAlchemy models for persisted AI predictions."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, JSON, String, Index
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.connection import Base


class PredictionHistory(Base):
    __tablename__ = "prediction_history"
    __table_args__ = (
        Index("ix_prediction_history_created_at_id", "created_at", "id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    predicted_class: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    predicted_label: Mapped[str] = mapped_column(String(255), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_percent: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_margin: Mapped[float] = mapped_column(Float, nullable=False)
    top_5_predictions: Mapped[list] = mapped_column(JSON, nullable=False)
    architecture: Mapped[str] = mapped_column(String(100), nullable=False)
    device: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
