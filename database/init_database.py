"""
Database Initialization Script
Sets up database schema, creates tables, and adds seed data
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database.postgres_handler import db_handler, db_ops
from database.vector_store import vector_store
from loguru import logger
from config import settings


def check_database_connection():
    """Test database connection"""
    logger.info("🔍 Testing database connection...")
    if db_handler.test_connection():
        logger.info("✅ Database connection successful!")
        return True
    else:
        logger.error("❌ Database connection failed!")
        logger.error(f"Connection string: {settings.database_url}")
        logger.error("Please ensure PostgreSQL is running and credentials are correct in .env file")
        return False


def create_database_tables():
    """Create all database tables"""
    logger.info("🔨 Creating database tables...")
    try:
        db_handler.create_tables()
        logger.info("✅ All tables created successfully!")
        
        # List created tables
        from sqlalchemy import inspect
        inspector = inspect(db_handler.engine)
        tables = inspector.get_table_names()
        logger.info(f"📊 Created {len(tables)} tables: {', '.join(tables)}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        return False


def create_default_user():
    """Create default demo user"""
    logger.info("👤 Creating default user...")
    try:
        user = db_ops.get_or_create_user(
            username="demo_user",
            email="demo@datawise.ai"
        )
        if user:
            logger.info(f"✅ Default user ready: {user.username} ({user.email})")
            return user
        return None
    except Exception as e:
        logger.error(f"❌ Failed to create default user: {e}")
        return None


def initialize_vector_store():
    """Initialize ChromaDB vector store"""
    logger.info("🔍 Initializing vector store...")
    try:
        # Create a test collection
        collection = vector_store.create_collection(
            "test_collection",
            metadata={"description": "Test collection for DataWise AI"}
        )
        logger.info("✅ Vector store initialized successfully!")
        
        # List all collections
        collections = vector_store.list_collections()
        logger.info(f"📊 Available collections: {', '.join(collections)}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize vector store: {e}")
        return False


def get_database_info():
    """Display database information"""
    logger.info("\n" + "="*60)
    logger.info("DATABASE INFORMATION")
    logger.info("="*60)
    
    try:
        stats = db_ops.get_database_stats()
        logger.info(f"👥 Total Users: {stats['total_users']}")
        logger.info(f"📊 Total Datasets: {stats['total_datasets']}")
        logger.info(f"🔍 Total Queries: {stats['total_queries']}")
        logger.info(f"✅ Successful Queries: {stats['successful_queries']}")
        logger.info(f"💡 Total Insights: {stats['total_insights']}")
        logger.info(f"📈 Total Visualizations: {stats['total_visualizations']}")
        logger.info(f"💬 Total Conversations: {stats['total_conversations']}")
        logger.info(f"📄 Total Reports: {stats['total_reports']}")
        logger.info("="*60 + "\n")
    except Exception as e:
        logger.error(f"❌ Failed to get database info: {e}")


def main():
    """Main initialization function"""
    logger.info("\n" + "="*60)
    logger.info("🚀 DATAWISE AI - DATABASE INITIALIZATION")
    logger.info("="*60 + "\n")
    
    # Step 1: Check database connection
    if not check_database_connection():
        logger.error("❌ Database initialization failed!")
        logger.error("Please check your PostgreSQL installation and .env configuration")
        return False
    
    logger.info("")
    
    # Step 2: Create tables
    if not create_database_tables():
        logger.error("❌ Database initialization failed!")
        return False
    
    logger.info("")
    
    # Step 3: Create default user
    default_user = create_default_user()
    if not default_user:
        logger.warning("⚠️  Failed to create default user (non-critical)")
    
    logger.info("")
    
    # Step 4: Initialize vector store
    if not initialize_vector_store():
        logger.warning("⚠️  Failed to initialize vector store (non-critical)")
    
    logger.info("")
    
    # Step 5: Display database info
    get_database_info()
    
    logger.info("="*60)
    logger.info("✅ DATABASE INITIALIZATION COMPLETE!")
    logger.info("="*60)
    logger.info("\n✨ You can now start using DataWise AI!")
    logger.info("Run: streamlit run app.py\n")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

