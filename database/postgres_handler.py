"""
PostgreSQL Connection Handler and CRUD Operations
Manages database connections and provides data access layer
"""

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from loguru import logger
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import settings
from database.models import Base, User, Dataset, Query, Insight, Visualization, Conversation, Message, Report


class PostgreSQLHandler:
    """
    PostgreSQL database handler with connection pooling
    """
    
    def __init__(self):
        """Initialize database connection"""
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Create database engine with connection pooling"""
        try:
            self.engine = create_engine(
                settings.database_url,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,  # Verify connections before using
                echo=settings.debug_mode  # Log SQL queries in debug mode
            )
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info(f"✅ Database engine initialized: {settings.db_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize database engine: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Session:
        """
        Context manager for database sessions
        
        Usage:
            with db_handler.get_session() as session:
                # Your database operations
                pass
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("✅ Database connection test successful")
                return True
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {e}")
            return False
    
    def create_tables(self):
        """Create all tables defined in models"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ Database tables created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            raise
    
    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("⚠️  All database tables dropped")
        except Exception as e:
            logger.error(f"❌ Failed to drop tables: {e}")
            raise
    
    def execute_sql_file(self, sql_file_path: str):
        """Execute SQL from a file (e.g., schema.sql)"""
        try:
            with open(sql_file_path, 'r') as file:
                sql_commands = file.read()
            
            with self.engine.connect() as conn:
                # Split by semicolon and execute each command
                for command in sql_commands.split(';'):
                    command = command.strip()
                    if command:
                        conn.execute(text(command))
                conn.commit()
            
            logger.info(f"✅ SQL file executed: {sql_file_path}")
        except Exception as e:
            logger.error(f"❌ Failed to execute SQL file: {e}")
            raise
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database"""
        inspector = inspect(self.engine)
        return table_name in inspector.get_table_names()
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get information about a table"""
        inspector = inspect(self.engine)
        
        if not self.table_exists(table_name):
            return {"error": f"Table '{table_name}' does not exist"}
        
        columns = inspector.get_columns(table_name)
        pk_constraint = inspector.get_pk_constraint(table_name)
        foreign_keys = inspector.get_foreign_keys(table_name)
        indexes = inspector.get_indexes(table_name)
        
        return {
            "table_name": table_name,
            "columns": columns,
            "primary_key": pk_constraint,
            "foreign_keys": foreign_keys,
            "indexes": indexes
        }


class DatabaseOperations:
    """
    CRUD operations for all models
    """
    
    def __init__(self, db_handler: PostgreSQLHandler):
        self.db = db_handler
    
    # ==================== USER OPERATIONS ====================
    
    def create_user(self, username: str, email: str) -> Optional[User]:
        """Create a new user"""
        try:
            with self.db.get_session() as session:
                user = User(username=username, email=email)
                session.add(user)
                session.flush()
                session.refresh(user)
                # Make object accessible after session closes
                session.expunge(user)
                logger.info(f"✅ User created: {username}")
                return user
        except Exception as e:
            logger.error(f"❌ Failed to create user: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        with self.db.get_session() as session:
            user = session.query(User).filter(User.email == email).first()
            if user:
                # Make object accessible after session closes
                session.expunge(user)
            return user
    
    def get_or_create_user(self, username: str, email: str) -> User:
        """Get existing user or create new one"""
        user = self.get_user_by_email(email)
        if not user:
            user = self.create_user(username, email)
        return user
    
    # ==================== DATASET OPERATIONS ====================
    
    def create_dataset(self, user_id: str, name: str, original_filename: str,
                      file_path: str, file_type: str, file_size_bytes: int,
                      row_count: int = None, column_count: int = None,
                      columns: Dict = None, description: str = None) -> Optional[Dataset]:
        """Create a new dataset record"""
        try:
            with self.db.get_session() as session:
                dataset = Dataset(
                    user_id=user_id,
                    name=name,
                    original_filename=original_filename,
                    file_path=file_path,
                    file_type=file_type,
                    file_size_bytes=file_size_bytes,
                    row_count=row_count,
                    column_count=column_count,
                    columns=columns,
                    description=description
                )
                session.add(dataset)
                session.flush()
                session.refresh(dataset)
                # Make object accessible after session closes
                session.expunge(dataset)
                logger.info(f"✅ Dataset created: {name}")
                return dataset
        except Exception as e:
            logger.error(f"❌ Failed to create dataset: {e}")
            return None
    
    def get_dataset(self, dataset_id: str) -> Optional[Dataset]:
        """Get dataset by ID"""
        with self.db.get_session() as session:
            return session.query(Dataset).filter(Dataset.id == dataset_id).first()
    
    def get_user_datasets(self, user_id: str, active_only: bool = True) -> List[Dataset]:
        """Get all datasets for a user"""
        with self.db.get_session() as session:
            query = session.query(Dataset).filter(Dataset.user_id == user_id)
            if active_only:
                query = query.filter(Dataset.is_active == True)
            return query.order_by(Dataset.upload_date.desc()).all()
    
    def update_dataset(self, dataset_id: str, **kwargs) -> bool:
        """Update dataset fields"""
        try:
            with self.db.get_session() as session:
                dataset = session.query(Dataset).filter(Dataset.id == dataset_id).first()
                if dataset:
                    for key, value in kwargs.items():
                        if hasattr(dataset, key):
                            setattr(dataset, key, value)
                    logger.info(f"✅ Dataset updated: {dataset_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"❌ Failed to update dataset: {e}")
            return False
    
    def delete_dataset(self, dataset_id: str) -> bool:
        """Soft delete a dataset (set is_active=False)"""
        return self.update_dataset(dataset_id, is_active=False)
    
    # ==================== QUERY OPERATIONS ====================
    
    def create_query(self, dataset_id: str, user_id: str, question: str,
                    generated_sql: str = None, execution_status: str = 'pending',
                    execution_time_ms: int = None, result_rows: int = None,
                    result_data: Dict = None, error_message: str = None) -> Optional[Query]:
        """Create a new query record"""
        try:
            with self.db.get_session() as session:
                query = Query(
                    dataset_id=dataset_id,
                    user_id=user_id,
                    question=question,
                    generated_sql=generated_sql,
                    execution_status=execution_status,
                    execution_time_ms=execution_time_ms,
                    result_rows=result_rows,
                    result_data=result_data,
                    error_message=error_message
                )
                session.add(query)
                session.flush()
                session.refresh(query)
                logger.info(f"✅ Query created: {question[:50]}...")
                return query
        except Exception as e:
            logger.error(f"❌ Failed to create query: {e}")
            return None
    
    def get_dataset_queries(self, dataset_id: str, limit: int = 50) -> List[Query]:
        """Get queries for a dataset"""
        with self.db.get_session() as session:
            return session.query(Query)\
                .filter(Query.dataset_id == dataset_id)\
                .order_by(Query.created_at.desc())\
                .limit(limit)\
                .all()
    
    def update_query_result(self, query_id: str, execution_status: str,
                           execution_time_ms: int = None, result_rows: int = None,
                           result_data: Dict = None, error_message: str = None) -> bool:
        """Update query with execution results"""
        try:
            with self.db.get_session() as session:
                query = session.query(Query).filter(Query.id == query_id).first()
                if query:
                    query.execution_status = execution_status
                    query.execution_time_ms = execution_time_ms
                    query.result_rows = result_rows
                    query.result_data = result_data
                    query.error_message = error_message
                    return True
                return False
        except Exception as e:
            logger.error(f"❌ Failed to update query result: {e}")
            return False
    
    # ==================== INSIGHT OPERATIONS ====================
    
    def create_insight(self, dataset_id: str, user_id: str, insight_type: str,
                      title: str, description: str, confidence_score: float = None,
                      insight_metadata: Dict = None) -> Optional[Insight]:
        """Create a new insight"""
        try:
            with self.db.get_session() as session:
                insight = Insight(
                    dataset_id=dataset_id,
                    user_id=user_id,
                    insight_type=insight_type,
                    title=title,
                    description=description,
                    confidence_score=confidence_score,
                    insight_metadata=insight_metadata
                )
                session.add(insight)
                session.flush()
                session.refresh(insight)
                logger.info(f"✅ Insight created: {title}")
                return insight
        except Exception as e:
            logger.error(f"❌ Failed to create insight: {e}")
            return None
    
    def get_dataset_insights(self, dataset_id: str, insight_type: str = None) -> List[Insight]:
        """Get insights for a dataset"""
        with self.db.get_session() as session:
            query = session.query(Insight).filter(Insight.dataset_id == dataset_id)
            if insight_type:
                query = query.filter(Insight.insight_type == insight_type)
            return query.order_by(Insight.created_at.desc()).all()
    
    # ==================== CONVERSATION OPERATIONS ====================
    
    def create_conversation(self, user_id: str, title: str = None, 
                           context_data: Dict = None) -> Optional[Conversation]:
        """Create a new conversation"""
        try:
            with self.db.get_session() as session:
                conversation = Conversation(
                    user_id=user_id,
                    title=title or "New Conversation",
                    context_data=context_data or {}
                )
                session.add(conversation)
                session.flush()
                session.refresh(conversation)
                session.expunge(conversation)
                logger.info(f"✅ Conversation created: {title}")
                return conversation
        except Exception as e:
            logger.error(f"❌ Failed to create conversation: {e}")
            return None
    
    def create_message(self, conversation_id: str, role: str, content: str,
                      message_metadata: Dict = None) -> Optional['Message']:
        """Create a new message in conversation"""
        try:
            with self.db.get_session() as session:
                message = Message(
                    conversation_id=conversation_id,
                    role=role,
                    content=content,
                    message_metadata=message_metadata or {}
                )
                session.add(message)
                session.flush()
                session.refresh(message)
                session.expunge(message)
                logger.info(f"✅ Message created: {role}")
                return message
        except Exception as e:
            logger.error(f"❌ Failed to create message: {e}")
            return None
    
    def get_conversation_messages(self, conversation_id: str) -> List['Message']:
        """Get all messages in a conversation"""
        with self.db.get_session() as session:
            return session.query(Message)\
                .filter(Message.conversation_id == conversation_id)\
                .order_by(Message.created_at.asc())\
                .all()
    
    def get_user_conversations(self, user_id: str, limit: int = 50) -> List[Conversation]:
        """Get all conversations for a user"""
        with self.db.get_session() as session:
            return session.query(Conversation)\
                .filter(Conversation.user_id == user_id)\
                .order_by(Conversation.created_at.desc())\
                .limit(limit)\
                .all()
    
    # ==================== VISUALIZATION OPERATIONS ====================
    
    def create_visualization(self, dataset_id: str, chart_type: str,
                            config_data: Dict, chart_data: Dict = None) -> Optional[Visualization]:
        """Create a new visualization"""
        try:
            with self.db.get_session() as session:
                viz = Visualization(
                    dataset_id=dataset_id,
                    chart_type=chart_type,
                    config_data=config_data,
                    chart_data=chart_data or {}
                )
                session.add(viz)
                session.flush()
                session.refresh(viz)
                session.expunge(viz)
                logger.info(f"✅ Visualization created: {chart_type}")
                return viz
        except Exception as e:
            logger.error(f"❌ Failed to create visualization: {e}")
            return None
    
    # ==================== REPORT OPERATIONS ====================
    
    def create_report(self, dataset_id: str, title: str, report_type: str,
                     content_data: Dict, file_path: str = None) -> Optional[Report]:
        """Create a new report"""
        try:
            with self.db.get_session() as session:
                report = Report(
                    dataset_id=dataset_id,
                    title=title,
                    report_type=report_type,
                    content_data=content_data,
                    file_path=file_path
                )
                session.add(report)
                session.flush()
                session.refresh(report)
                session.expunge(report)
                logger.info(f"✅ Report created: {title}")
                return report
        except Exception as e:
            logger.error(f"❌ Failed to create report: {e}")
            return None
    
    # ==================== HELPER METHODS ====================
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self.db.get_session() as session:
            stats = {
                "total_users": session.query(User).count(),
                "total_datasets": session.query(Dataset).filter(Dataset.is_active == True).count(),
                "total_queries": session.query(Query).count(),
                "successful_queries": session.query(Query).filter(Query.execution_status == 'success').count(),
                "total_insights": session.query(Insight).count(),
                "total_visualizations": session.query(Visualization).count(),
                "total_conversations": session.query(Conversation).count(),
                "total_reports": session.query(Report).count()
            }
            return stats


# Global instance
db_handler = PostgreSQLHandler()
db_ops = DatabaseOperations(db_handler)

