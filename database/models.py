"""
SQLAlchemy Models for DataWise AI
Defines ORM models for database tables
"""

from sqlalchemy import (
    Column, String, Integer, BigInteger, Boolean, 
    Text, DateTime, Numeric, ForeignKey, CheckConstraint,
    func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User account model"""
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    datasets = relationship("Dataset", back_populates="user", cascade="all, delete-orphan")
    queries = relationship("Query", back_populates="user", cascade="all, delete-orphan")
    insights = relationship("Insight", back_populates="user", cascade="all, delete-orphan")
    visualizations = relationship("Visualization", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"


class Dataset(Base):
    """Dataset metadata model"""
    __tablename__ = 'datasets'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    name = Column(String(255), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    row_count = Column(Integer)
    column_count = Column(Integer)
    columns = Column(JSONB)  # Column names and types
    upload_date = Column(DateTime, default=datetime.utcnow, index=True)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    description = Column(Text)
    is_active = Column(Boolean, default=True, index=True)
    
    __table_args__ = (
        CheckConstraint("file_type IN ('csv', 'xlsx', 'xls', 'json')", name='valid_file_type'),
    )
    
    # Relationships
    user = relationship("User", back_populates="datasets")
    queries = relationship("Query", back_populates="dataset", cascade="all, delete-orphan")
    insights = relationship("Insight", back_populates="dataset", cascade="all, delete-orphan")
    visualizations = relationship("Visualization", back_populates="dataset", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="dataset", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="dataset", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Dataset(name='{self.name}', type='{self.file_type}', rows={self.row_count})>"


class Query(Base):
    """Query execution history model"""
    __tablename__ = 'queries'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey('datasets.id', ondelete='CASCADE'), index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), index=True)
    question = Column(Text, nullable=False)  # Natural language question
    generated_sql = Column(Text)  # AI-generated SQL
    execution_status = Column(String(50), default='pending', index=True)
    execution_time_ms = Column(Integer)
    result_rows = Column(Integer)
    result_data = Column(JSONB)  # Query results
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        CheckConstraint("execution_status IN ('pending', 'success', 'error')", name='valid_status'),
    )
    
    # Relationships
    dataset = relationship("Dataset", back_populates="queries")
    user = relationship("User", back_populates="queries")
    visualizations = relationship("Visualization", back_populates="query", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="query")
    
    def __repr__(self):
        return f"<Query(question='{self.question[:50]}...', status='{self.execution_status}')>"


class Insight(Base):
    """AI-generated insights model"""
    __tablename__ = 'insights'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey('datasets.id', ondelete='CASCADE'), index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), index=True)
    insight_type = Column(String(100), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    confidence_score = Column(Numeric(3, 2))  # 0.00 to 1.00
    insight_metadata = Column(JSONB)  # Additional data
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    is_bookmarked = Column(Boolean, default=False)
    
    __table_args__ = (
        CheckConstraint("insight_type IN ('correlation', 'trend', 'anomaly', 'summary', 'recommendation')", 
                       name='valid_insight_type'),
    )
    
    # Relationships
    dataset = relationship("Dataset", back_populates="insights")
    user = relationship("User", back_populates="insights")
    
    def __repr__(self):
        return f"<Insight(type='{self.insight_type}', title='{self.title}')>"


class Visualization(Base):
    """Visualization/Chart model"""
    __tablename__ = 'visualizations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), ForeignKey('queries.id', ondelete='CASCADE'), index=True)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey('datasets.id', ondelete='CASCADE'), index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), index=True)
    chart_type = Column(String(100), nullable=False)
    chart_title = Column(String(500))
    chart_config = Column(JSONB)  # Plotly configuration
    chart_data = Column(JSONB)  # Chart data
    chart_image_path = Column(String(1000))  # Saved PNG path
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint("chart_type IN ('bar', 'line', 'scatter', 'pie', 'heatmap', 'histogram', 'box')", 
                       name='valid_chart_type'),
    )
    
    # Relationships
    query = relationship("Query", back_populates="visualizations")
    dataset = relationship("Dataset", back_populates="visualizations")
    user = relationship("User", back_populates="visualizations")
    messages = relationship("Message", back_populates="visualization")
    
    def __repr__(self):
        return f"<Visualization(type='{self.chart_type}', title='{self.chart_title}')>"


class Conversation(Base):
    """Chat conversation model"""
    __tablename__ = 'conversations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), index=True)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey('datasets.id', ondelete='CASCADE'), index=True)
    title = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    dataset = relationship("Dataset", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", 
                          order_by="Message.created_at")
    
    def __repr__(self):
        return f"<Conversation(title='{self.title}', messages={len(self.messages)})>"


class Message(Base):
    """Chat message model"""
    __tablename__ = 'messages'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey('conversations.id', ondelete='CASCADE'), 
                           index=True, nullable=False)
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    query_id = Column(UUID(as_uuid=True), ForeignKey('queries.id', ondelete='SET NULL'))
    visualization_id = Column(UUID(as_uuid=True), ForeignKey('visualizations.id', ondelete='SET NULL'))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant', 'system')", name='valid_role'),
    )
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    query = relationship("Query", back_populates="messages")
    visualization = relationship("Visualization", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(role='{self.role}', content='{self.content[:50]}...')>"


class Report(Base):
    """Generated report model"""
    __tablename__ = 'reports'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), index=True)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey('datasets.id', ondelete='CASCADE'), index=True)
    title = Column(String(500), nullable=False)
    report_type = Column(String(100), nullable=False)  # pdf, excel, html
    file_path = Column(String(1000))
    file_size_bytes = Column(BigInteger)
    sections = Column(JSONB)  # Report sections
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        CheckConstraint("report_type IN ('pdf', 'excel', 'html')", name='valid_report_type'),
    )
    
    # Relationships
    user = relationship("User", back_populates="reports")
    dataset = relationship("Dataset", back_populates="reports")
    
    def __repr__(self):
        return f"<Report(title='{self.title}', type='{self.report_type}')>"

