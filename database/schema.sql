-- DataWise AI - PostgreSQL Database Schema
-- Phase 2: Database Setup

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- TABLE: users
-- Store user information and sessions
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- ============================================
-- TABLE: datasets
-- Store metadata about uploaded datasets
-- ============================================
CREATE TABLE IF NOT EXISTS datasets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    original_filename VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_type VARCHAR(50) NOT NULL,  -- csv, xlsx, json
    file_size_bytes BIGINT NOT NULL,
    row_count INTEGER,
    column_count INTEGER,
    columns JSONB,  -- Store column names and types
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT valid_file_type CHECK (file_type IN ('csv', 'xlsx', 'xls', 'json'))
);

-- ============================================
-- TABLE: queries
-- Store user queries and SQL execution history
-- ============================================
CREATE TABLE IF NOT EXISTS queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_id UUID REFERENCES datasets(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    question TEXT NOT NULL,  -- Natural language question
    generated_sql TEXT,  -- AI-generated SQL query
    execution_status VARCHAR(50) DEFAULT 'pending',  -- pending, success, error
    execution_time_ms INTEGER,
    result_rows INTEGER,
    result_data JSONB,  -- Store query results
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_status CHECK (execution_status IN ('pending', 'success', 'error'))
);

-- ============================================
-- TABLE: insights
-- Store AI-generated insights and analysis
-- ============================================
CREATE TABLE IF NOT EXISTS insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_id UUID REFERENCES datasets(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    insight_type VARCHAR(100) NOT NULL,  -- correlation, trend, anomaly, summary
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    confidence_score DECIMAL(3, 2),  -- 0.00 to 1.00
    insight_metadata JSONB,  -- Additional data (stats, values, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_bookmarked BOOLEAN DEFAULT FALSE,
    CONSTRAINT valid_insight_type CHECK (insight_type IN ('correlation', 'trend', 'anomaly', 'summary', 'recommendation'))
);

-- ============================================
-- TABLE: visualizations
-- Store generated charts and visualizations
-- ============================================
CREATE TABLE IF NOT EXISTS visualizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_id UUID REFERENCES queries(id) ON DELETE CASCADE,
    dataset_id UUID REFERENCES datasets(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    chart_type VARCHAR(100) NOT NULL,  -- bar, line, scatter, pie, heatmap
    chart_title VARCHAR(500),
    chart_config JSONB,  -- Plotly configuration
    chart_data JSONB,  -- Chart data
    chart_image_path VARCHAR(1000),  -- Path to saved PNG
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_chart_type CHECK (chart_type IN ('bar', 'line', 'scatter', 'pie', 'heatmap', 'histogram', 'box'))
);

-- ============================================
-- TABLE: conversations
-- Store chat conversation history
-- ============================================
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    dataset_id UUID REFERENCES datasets(id) ON DELETE CASCADE,
    title VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- ============================================
-- TABLE: messages
-- Store individual chat messages
-- ============================================
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,  -- user, assistant
    content TEXT NOT NULL,
    query_id UUID REFERENCES queries(id) ON DELETE SET NULL,  -- Link to executed query
    visualization_id UUID REFERENCES visualizations(id) ON DELETE SET NULL,  -- Link to chart
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_role CHECK (role IN ('user', 'assistant', 'system'))
);

-- ============================================
-- TABLE: reports
-- Store generated reports
-- ============================================
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    dataset_id UUID REFERENCES datasets(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    report_type VARCHAR(100) NOT NULL,  -- pdf, excel, html
    file_path VARCHAR(1000),
    file_size_bytes BIGINT,
    sections JSONB,  -- Report sections and content
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_report_type CHECK (report_type IN ('pdf', 'excel', 'html'))
);

-- ============================================
-- INDEXES for Performance
-- ============================================

-- Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Datasets
CREATE INDEX idx_datasets_user_id ON datasets(user_id);
CREATE INDEX idx_datasets_upload_date ON datasets(upload_date);
CREATE INDEX idx_datasets_is_active ON datasets(is_active);

-- Queries
CREATE INDEX idx_queries_dataset_id ON queries(dataset_id);
CREATE INDEX idx_queries_user_id ON queries(user_id);
CREATE INDEX idx_queries_created_at ON queries(created_at);
CREATE INDEX idx_queries_execution_status ON queries(execution_status);

-- Insights
CREATE INDEX idx_insights_dataset_id ON insights(dataset_id);
CREATE INDEX idx_insights_user_id ON insights(user_id);
CREATE INDEX idx_insights_insight_type ON insights(insight_type);
CREATE INDEX idx_insights_created_at ON insights(created_at);

-- Visualizations
CREATE INDEX idx_visualizations_query_id ON visualizations(query_id);
CREATE INDEX idx_visualizations_dataset_id ON visualizations(dataset_id);
CREATE INDEX idx_visualizations_user_id ON visualizations(user_id);

-- Conversations
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_dataset_id ON conversations(dataset_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);

-- Messages
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- Reports
CREATE INDEX idx_reports_user_id ON reports(user_id);
CREATE INDEX idx_reports_dataset_id ON reports(dataset_id);
CREATE INDEX idx_reports_created_at ON reports(created_at);

-- ============================================
-- VIEWS for Common Queries
-- ============================================

-- Recent datasets with stats
CREATE OR REPLACE VIEW v_recent_datasets AS
SELECT 
    d.id,
    d.name,
    d.original_filename,
    d.file_type,
    d.row_count,
    d.column_count,
    d.upload_date,
    d.last_accessed,
    u.username,
    COUNT(DISTINCT q.id) as query_count,
    COUNT(DISTINCT i.id) as insight_count
FROM datasets d
LEFT JOIN users u ON d.user_id = u.id
LEFT JOIN queries q ON d.id = q.dataset_id
LEFT JOIN insights i ON d.id = i.dataset_id
WHERE d.is_active = TRUE
GROUP BY d.id, d.name, d.original_filename, d.file_type, 
         d.row_count, d.column_count, d.upload_date, 
         d.last_accessed, u.username
ORDER BY d.upload_date DESC;

-- Query statistics
CREATE OR REPLACE VIEW v_query_stats AS
SELECT 
    dataset_id,
    COUNT(*) as total_queries,
    COUNT(CASE WHEN execution_status = 'success' THEN 1 END) as successful_queries,
    COUNT(CASE WHEN execution_status = 'error' THEN 1 END) as failed_queries,
    AVG(execution_time_ms) as avg_execution_time_ms,
    MAX(execution_time_ms) as max_execution_time_ms,
    MIN(execution_time_ms) as min_execution_time_ms
FROM queries
GROUP BY dataset_id;

-- ============================================
-- FUNCTIONS
-- ============================================

-- Update last_accessed timestamp for datasets
CREATE OR REPLACE FUNCTION update_dataset_last_accessed()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE datasets 
    SET last_accessed = CURRENT_TIMESTAMP 
    WHERE id = NEW.dataset_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update last_accessed on query
CREATE TRIGGER trigger_update_dataset_last_accessed
AFTER INSERT ON queries
FOR EACH ROW
EXECUTE FUNCTION update_dataset_last_accessed();

-- Update conversation updated_at timestamp
CREATE OR REPLACE FUNCTION update_conversation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update conversation timestamp on new message
CREATE TRIGGER trigger_update_conversation_timestamp
AFTER INSERT ON messages
FOR EACH ROW
EXECUTE FUNCTION update_conversation_timestamp();

-- ============================================
-- SEED DATA (Optional - for testing)
-- ============================================

-- Create default user
INSERT INTO users (username, email) 
VALUES ('demo_user', 'demo@datawise.ai')
ON CONFLICT (email) DO NOTHING;

-- ============================================
-- COMMENTS
-- ============================================

COMMENT ON TABLE users IS 'Store user account information';
COMMENT ON TABLE datasets IS 'Metadata for uploaded data files';
COMMENT ON TABLE queries IS 'Natural language queries and SQL execution history';
COMMENT ON TABLE insights IS 'AI-generated insights and analysis results';
COMMENT ON TABLE visualizations IS 'Generated charts and visual representations';
COMMENT ON TABLE conversations IS 'Chat conversation sessions';
COMMENT ON TABLE messages IS 'Individual messages in conversations';
COMMENT ON TABLE reports IS 'Generated analysis reports';

-- ============================================
-- END OF SCHEMA
-- ============================================

