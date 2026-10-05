from sqlalchemy import Column, String, Integer, DateTime, Float, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from database import Base

class FindingType(str, enum.Enum):
    DIAGNOSIS = "diagnosis"
    DRUG = "drug"
    RECOMMENDATION = "recommendation"
    LAB = "lab"

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id_hash = Column(String(255), nullable=False, index=True)
    doctor_id = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    turns = relationship("Turn", back_populates="conversation", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation(id={self.id}, patient_id_hash={self.patient_id_hash}, doctor_id={self.doctor_id})>"

class Turn(Base):
    __tablename__ = "turns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False, index=True)
    turn_number = Column(Integer, nullable=False)
    user_input = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    ai_response_json = Column(JSON, nullable=True)  # Parsed AI response
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    conversation = relationship("Conversation", back_populates="turns")
    findings = relationship("Finding", back_populates="turn", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="turn", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Turn(id={self.id}, conversation_id={self.conversation_id}, turn_number={self.turn_number})>"

class Finding(Base):
    __tablename__ = "findings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False, index=True)
    turn_id = Column(UUID(as_uuid=True), ForeignKey("turns.id"), nullable=False, index=True)
    finding_type = Column(Enum(FindingType), nullable=False, index=True)
    value = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)  # 0.0 to 1.0
    metadata = Column(JSON, nullable=True)  # Additional structured data
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    conversation = relationship("Conversation", back_populates="findings")
    turn = relationship("Turn", back_populates="findings")

    def __repr__(self):
        return f"<Finding(id={self.id}, finding_type={self.finding_type}, value={self.value})>"

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    turn_id = Column(UUID(as_uuid=True), ForeignKey("turns.id"), nullable=False, index=True)
    action = Column(String(255), nullable=False)  # e.g., "finding_extracted", "context_linked"
    details = Column(JSON, nullable=True)  # Additional details about the action
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    turn = relationship("Turn", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, timestamp={self.timestamp})>"
