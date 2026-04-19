from datetime import datetime

from sqlalchemy import ForeignKey, Integer, LargeBinary, String, UniqueConstraint
from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agent_connect_kit.db.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    connections: Mapped[list["Connection"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Connection(Base, TimestampMixin):
    __tablename__ = "connections"
    __table_args__ = (
        UniqueConstraint("user_id", "provider", name="uq_connection_user_provider"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    external_account_id: Mapped[str | None] = mapped_column(String(255))
    external_account_login: Mapped[str | None] = mapped_column(String(255))
    encrypted_access_token: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    encrypted_refresh_token: Mapped[bytes | None] = mapped_column(LargeBinary)
    scopes: Mapped[str | None] = mapped_column(String(1024))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="connections")


class ActionLog(Base):
    __tablename__ = "action_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    connection_id: Mapped[int | None] = mapped_column(
        ForeignKey("connections.id", ondelete="SET NULL"), index=True
    )
    action_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    args: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    result_summary: Mapped[str | None] = mapped_column(String(1024))
    error: Mapped[str | None] = mapped_column(String(2048))
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
