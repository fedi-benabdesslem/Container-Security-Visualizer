from sqlalchemy import Column, Integer, String, BigInteger, Boolean, Text, TIMESTAMP, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from backend.database import Base
class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp_ns = Column(BigInteger, nullable=False, index=True)
    timestamp_iso = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    pid = Column(Integer, nullable=False, index=True)
    tgid = Column(Integer)
    uid = Column(Integer)
    comm = Column(String(255))
    monitor_type = Column(String(20), nullable=False, index=True)
    container_id = Column(String(12), index=True)
    container_name = Column(String(255), index=True)
    container_image = Column(String(255))
    container_status = Column(String(20))
    argv = Column(Text)
    categories = Column(JSONB)
    risk_score = Column(Integer, index=True)
    is_security_relevant = Column(Boolean)
    source_ip = Column(String(45))
    dest_ip = Column(String(45))
    source_port = Column(Integer)
    dest_port = Column(Integer)
    event_type = Column(String(50))
    source_container_id = Column(String(12), index=True)
    dest_container_id = Column(String(12), index=True)
    source_container_name = Column(String(255))
    dest_container_name = Column(String(255))
    __table_args__ = (
        Index('idx_timestamp_desc', timestamp_ns.desc()),
        Index('idx_container_monitor', container_id, monitor_type),
        Index('idx_risk_timestamp', risk_score, timestamp_ns.desc()),
        Index('idx_created_at_desc', created_at.desc()),
    )
    def __repr__(self):
        return f"<Event(id={self.id}, type={self.monitor_type}, pid={self.pid}, container={self.container_name})>"
    def to_dict(self):
        return {
            "id": self.id,
            "timestamp_ns": self.timestamp_ns,
            "timestamp_iso": self.timestamp_iso.isoformat() if self.timestamp_iso else None,
            "pid": self.pid,
            "tgid": self.tgid,
            "uid": self.uid,
            "comm": self.comm,
            "monitor_type": self.monitor_type,
            "container_id": self.container_id,
            "container_name": self.container_name,
            "container_image": self.container_image,
            "container_status": self.container_status,
            "argv": self.argv,
            "categories": self.categories,
            "risk_score": self.risk_score,
            "is_security_relevant": self.is_security_relevant,
            "source_ip": self.source_ip,
            "dest_ip": self.dest_ip,
            "source_port": self.source_port,
            "dest_port": self.dest_port,
            "event_type": self.event_type,
            "source_container_id": self.source_container_id,
            "dest_container_id": self.dest_container_id,
            "source_container_name": self.source_container_name,
            "dest_container_name": self.dest_container_name,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
