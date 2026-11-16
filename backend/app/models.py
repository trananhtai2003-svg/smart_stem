from sqlalchemy import String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from .database import Base

class Module(Base):
    __tablename__ = "modules"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, default="")
    devices = relationship("Device", back_populates="module", cascade="all, delete-orphan")

class Device(Base):
    __tablename__ = "devices"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text, default="")
    function: Mapped[str] = mapped_column(Text, default="")
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"))
    image_path: Mapped[str] = mapped_column(String(500), default="")
    model3d_path: Mapped[str] = mapped_column(String(500), default="")
    video_path: Mapped[str] = mapped_column(String(500), default="")
    qr_path: Mapped[str] = mapped_column(String(500), default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    module = relationship("Module", back_populates="devices")

class DeviceEvent(Base):
    __tablename__ = "device_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    device_code: Mapped[str] = mapped_column(String(60), index=True)
    event_type: Mapped[str] = mapped_column(String(40))
    source: Mapped[str] = mapped_column(String(40), default="web")
    payload: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
