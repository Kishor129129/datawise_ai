"""
DataWise AI - Your Intelligent Data Analysis Companion
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import google.generativeai as genai
from pathlib import Path
from datetime import datetime
import sys
from loguru import logger

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from config import settings
from database.postgres_handler import db_handler, db_ops
from database.vector_store import vector_store
from utils.file_processor import file_processor
from utils.data_validator import data_validator
from utils.data_preview import data_previewer
from ai_engine.gemini_handler import gemini_handler
from ai_engine.nl_to_sql import nl_to_sql_converter
from ai_engine.query_executor import query_executor
from visualization.chart_generator import chart_generator
from visualization.chart_customizer import chart_customizer
from chat.chat_handler import chat_handler
from chat.conversation_manager import conversation_manager
from insights.insight_generator import insight_generator
from reports.report_generator import report_generator
from reports.pdf_exporter import pdf_exporter
from reports.excel_exporter import excel_exporter

# Configure page settings
st.set_page_config(
    page_title="DataWise AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .feature-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .stAlert {
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_gemini():
    """Initialize Gemini AI with API key"""
    try:
        if settings.validate_gemini_key():
            genai.configure(api_key=settings.gemini_api_key)
            return True
        return False
    except Exception as e:
        st.error(f"Error initializing Gemini AI: {str(e)}")
        return False


def test_gemini_connection():
    """Test Gemini API connection"""
    try:
        model = genai.GenerativeModel(settings.gemini_model)
        response = model.generate_content("Say 'Hello, DataWise AI is ready!' in one sentence.")
        return True, response.text
    except Exception as e:
        return False, str(e)


def main():
    """Main application entry point"""
    
    # Header
    st.markdown('<div class="main-header">📊 DataWise AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Your Intelligent Data Analysis Companion</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/1f77b4/ffffff?text=DataWise+AI", use_container_width=True)
        st.markdown("---")
        st.markdown("### 🚀 Features")
        st.markdown("""
        - 📁 Upload CSV, Excel, JSON
        - 💬 Ask questions in natural language
        - 📊 Auto-generate visualizations
        - 🧠 AI-powered insights
        - 📄 Generate reports
        - 💾 Query history
        """)
        st.markdown("---")
        st.markdown("### ⚙️ Status")
        
        # Check configuration
        if settings.validate_gemini_key():
            st.success("✅ Gemini API: Connected")
        else:
            st.error("❌ Gemini API: Not configured")
        
        # Database status
        try:
            if db_handler.test_connection():
                st.success("✅ Database: Connected")
            else:
                st.error("❌ Database: Not connected")
        except:
            st.warning("⚠️  Database: Not initialized")
        
        st.markdown("---")
        st.markdown("### 📖 About")
        st.info("""
        **DataWise AI** helps you analyze data using natural language.
        
        Built with:
        - 🤖 Google Gemini AI
        - 📊 Streamlit
        - 🗄️ PostgreSQL
        - 🔍 ChromaDB
        """)
    
    # Main content area
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🏠 Home", 
        "📁 Upload Data", 
        "💬 Ask Questions", 
        "💭 Chat",
        "📄 Reports",
        "🔧 Setup Test", 
        "📚 How to Use"
    ])
    
    with tab1:
        st.markdown("## Welcome to DataWise AI! 👋")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <h3>📁 Upload Data</h3>
                <p>Easily upload CSV, Excel, or JSON files for analysis.</p>
                <p><em>✅ Now Available!</em></p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-card">
                <h3>💬 Ask Questions</h3>
                <p>Use natural language to query your data.</p>
                <p><em>✅ Now Available!</em></p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="feature-card">
                <h3>📊 Get Insights</h3>
                <p>AI-powered visualizations and analysis.</p>
                <p><em>✅ All Features Available!</em></p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.info("🚧 **Project Status:** Phase 8 Complete - Professional Report Generation!")
        
        # Project timeline
        st.markdown("### 📅 Development Timeline")
        progress_data = {
            "Phase 1": "✅ Complete - Foundation",
            "Phase 2": "✅ Complete - Database",
            "Phase 3": "✅ Complete - File Upload",
            "Phase 4": "✅ Complete - AI Integration",
            "Phase 5": "✅ Complete - Visualizations",
            "Phase 6": "✅ Complete - AI Insights",
            "Phase 7": "✅ Complete - Chat Interface",
            "Phase 8": "✅ Complete - Report Generation",
            "Phase 9": "⏳ Next - Docker",
        }
        
        for phase, status in progress_data.items():
            st.text(f"{phase}: {status}")
    
    with tab2:
        st.markdown("## 📁 Upload & Analyze Your Data")
        
        # Initialize session state for storing uploaded data
        if 'uploaded_data' not in st.session_state:
            st.session_state.uploaded_data = None
        if 'dataset_id' not in st.session_state:
            st.session_state.dataset_id = None
        
        # File upload section
        st.markdown("### Step 1: Upload File")
        
        uploaded_file = st.file_uploader(
            "Choose a file (CSV, Excel, or JSON)",
            type=['csv', 'xlsx', 'xls', 'json'],
            help="Maximum file size: 200MB"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name} ({uploaded_file.size / 1024:.2f} KB)")
            
            # Process button
            if st.button("🔍 Process & Analyze", type="primary"):
                with st.spinner("Processing file..."):
                    # Process file
                    result = file_processor.process_uploaded_file(uploaded_file)
                    
                    if result['success']:
                        df = result['dataframe']
                        file_info = result['file_info']
                        
                        # Store in session state
                        st.session_state.uploaded_data = {
                            'dataframe': df,
                            'file_info': file_info,
                            'file_path': result['file_path']
                        }
                        
                        st.success("✅ File processed successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Error processing file: {result['error']}")
        
        # Display processed data
        if st.session_state.uploaded_data is not None:
            df = st.session_state.uploaded_data['dataframe']
            file_info = st.session_state.uploaded_data['file_info']
            
            st.markdown("---")
            st.markdown("### Step 2: Data Overview")
            
            # Basic info
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Rows", f"{len(df):,}")
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                st.metric("File Size", f"{file_info['size_mb']} MB")
            with col4:
                st.metric("File Type", file_info['type'].upper())
            
            # Data quality summary
            st.markdown("#### Data Quality")
            summary = data_validator.get_data_summary(df)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Missing Values", f"{summary['missing_values'].get(df.columns[0], 0):,}" if len(df.columns) > 0 else "0")
            with col2:
                st.metric("Duplicate Rows", f"{summary['duplicate_rows']:,}")
            with col3:
                memory_color = "normal" if summary['memory_usage_mb'] < 100 else "inverse"
                st.metric("Memory Usage", f"{summary['memory_usage_mb']} MB")
            
            # Data issues
            issues = data_validator.detect_data_issues(df)
            if issues:
                st.markdown("#### ⚠️ Detected Issues")
                for issue in issues[:5]:  # Show top 5 issues
                    if issue['severity'] == 'error':
                        st.error(f"🔴 {issue['message']}")
                    elif issue['severity'] == 'warning':
                        st.warning(f"🟡 {issue['message']}")
                    else:
                        st.info(f"🔵 {issue['message']}")
            else:
                st.success("✅ No major data quality issues detected!")
            
            st.markdown("---")
            st.markdown("### Step 3: Data Preview")
            
            # Tabs for different views
            preview_tab1, preview_tab2, preview_tab3, preview_tab4 = st.tabs([
                "📊 Data Sample", "📈 Statistics", "🔍 Column Details", "📉 Visualizations"
            ])
            
            with preview_tab1:
                st.markdown("#### First 10 Rows")
                st.dataframe(df.head(10), use_container_width=True)
                
                with st.expander("Show Last 10 Rows"):
                    st.dataframe(df.tail(10), use_container_width=True)
            
            with preview_tab2:
                st.markdown("#### Statistical Summary")
                
                # Numeric summary
                numeric_summary = data_previewer.get_numeric_summary(df)
                if numeric_summary:
                    st.markdown("**Numeric Columns:**")
                    st.dataframe(pd.DataFrame(numeric_summary).T, use_container_width=True)
                
                # Categorical summary
                categorical_summary = data_previewer.get_categorical_summary(df)
                if categorical_summary:
                    st.markdown("**Categorical Columns:**")
                    for col, stats in list(categorical_summary.items())[:5]:
                        with st.expander(f"📋 {col}"):
                            st.write(f"Unique values: {stats['unique_count']}")
                            st.write(f"Most common: {stats['top_value']} ({stats['top_count']} times)")
                            if stats['value_counts']:
                                st.bar_chart(stats['value_counts'])
            
            with preview_tab3:
                st.markdown("#### Column Information")
                
                col_stats = data_validator.get_column_statistics(df)
                col_data = []
                for col, stats in col_stats.items():
                    col_data.append({
                        'Column': col,
                        'Type': stats['dtype'],
                        'Unique': stats['unique_count'],
                        'Missing': stats['null_count'],
                        'Missing %': f"{stats['null_percentage']}%"
                    })
                
                st.dataframe(pd.DataFrame(col_data), use_container_width=True)
            
            with preview_tab4:
                st.markdown("#### Data Visualizations")
                
                # Missing data chart
                missing_chart = data_previewer.create_missing_data_chart(df)
                if missing_chart:
                    st.plotly_chart(missing_chart, use_container_width=True)
                else:
                    st.success("✅ No missing data!")
                
                # Data type distribution
                dtype_chart = data_previewer.create_data_type_chart(df)
                st.plotly_chart(dtype_chart, use_container_width=True)
                
                # Correlation heatmap
                corr_chart = data_previewer.create_correlation_heatmap(df)
                if corr_chart:
                    st.plotly_chart(corr_chart, use_container_width=True)
                else:
                    st.info("ℹ️ Not enough numeric columns for correlation analysis")
            
            st.markdown("---")
            st.markdown("### Step 4: Auto-Saved to Database ✅")
            
            # Auto-save to database when file is uploaded
            if 'dataset_id' not in st.session_state or not st.session_state.dataset_id:
                try:
                    # Get or create default user
                    user = db_ops.get_or_create_user("demo_user", "demo@datawise.ai")
                    
                    if user:
                        # Prepare column info
                        column_info = {
                            'columns': list(df.columns),
                            'dtypes': df.dtypes.astype(str).to_dict()
                        }
                        
                        # Auto-generate dataset name from filename
                        dataset_name = Path(file_info['original_name']).stem
                        
                        # Save dataset metadata
                        dataset = db_ops.create_dataset(
                            user_id=str(user.id),
                            name=dataset_name,
                            original_filename=file_info['original_name'],
                            file_path=st.session_state.uploaded_data['file_path'],
                            file_type=file_info['type'],
                            file_size_bytes=file_info['size_bytes'],
                            row_count=len(df),
                            column_count=len(df.columns),
                            columns=column_info,
                            description=f"Uploaded on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        )
                        
                        if dataset:
                            st.session_state.dataset_id = str(dataset.id)
                except Exception as e:
                    logger.error(f"Auto-save failed: {e}")
            
            # Show saved status
            if st.session_state.dataset_id:
                st.success(f"✅ **Dataset automatically saved to database!**")
                st.info(f"📊 **Dataset ID:** `{st.session_state.dataset_id[:8]}...`  \n"
                       f"👤 **User:** demo_user  \n"
                       f"📁 **Name:** {Path(file_info['original_name']).stem}")
            else:
                st.warning("⚠️ Auto-save to database failed. Data is still available for analysis.")
            
            # AI Insights Section
            st.markdown("---")
            st.markdown("### Step 5: AI-Powered Insights")
            
            if st.button("🧠 Generate AI Insights", type="primary"):
                with st.spinner("🔍 Analyzing data and generating insights..."):
                    try:
                        # Generate comprehensive insights
                        insights = insight_generator.generate_comprehensive_insights(df)
                        
                        if insights:
                            # Store in session state
                            st.session_state.insights = insights
                            st.success("✅ Insights generated successfully!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error generating insights: {str(e)}")
            
            # Display insights if available
            if 'insights' in st.session_state and st.session_state.insights:
                insights = st.session_state.insights
                
                st.markdown("---")
                
                # Create tabs for different insight types
                insight_tab1, insight_tab2, insight_tab3, insight_tab4 = st.tabs([
                    "🎯 Key Insights",
                    "📊 Statistics",
                    "📈 Trends",
                    "⚠️  Anomalies"
                ])
                
                with insight_tab1:
                    st.markdown("#### AI-Generated Insights")
                    ai_insights = insights.get('ai_insights', 'No insights available')
                    st.info(ai_insights)
                    
                    # Key findings
                    key_findings = insights.get('key_findings', [])
                    if key_findings:
                        st.markdown("#### Key Findings")
                        for finding in key_findings:
                            st.markdown(f"• {finding}")
                    
                    # Recommendations
                    recommendations = insights.get('recommendations', [])
                    if recommendations:
                        st.markdown("#### Recommendations")
                        for rec in recommendations:
                            st.warning(f"💡 {rec}")
                
                with insight_tab2:
                    st.markdown("#### Statistical Summary")
                    
                    stats = insights.get('statistics', {})
                    basic = stats.get('basic_stats', {})
                    
                    # Basic stats
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Rows", f"{basic.get('row_count', 0):,}")
                    with col2:
                        st.metric("Columns", basic.get('column_count', 0))
                    with col3:
                        st.metric("Missing %", f"{basic.get('missing_percentage', 0):.1f}%")
                    with col4:
                        st.metric("Duplicates", basic.get('duplicate_rows', 0))
                    
                    # Data quality
                    quality = stats.get('data_quality', {})
                    if quality:
                        st.markdown("#### Data Quality Assessment")
                        score = quality.get('quality_score', 0)
                        grade = quality.get('grade', 'N/A')
                        
                        st.metric("Quality Score", f"{score:.1f}/100", delta=grade)
                        
                        issues = quality.get('issues', [])
                        if issues:
                            st.warning("**Issues Found:**")
                            for issue in issues:
                                st.markdown(f"• {issue}")
                    
                    # Numeric columns analysis
                    numeric_analysis = stats.get('numeric_analysis', {})
                    if numeric_analysis:
                        st.markdown("#### Numeric Columns")
                        
                        for col, col_stats in list(numeric_analysis.items())[:5]:  # Show first 5
                            with st.expander(f"📊 {col}"):
                                col_a, col_b, col_c = st.columns(3)
                                with col_a:
                                    st.metric("Mean", f"{col_stats.get('mean', 0):.2f}")
                                    st.metric("Std Dev", f"{col_stats.get('std', 0):.2f}")
                                with col_b:
                                    st.metric("Min", f"{col_stats.get('min', 0):.2f}")
                                    st.metric("Max", f"{col_stats.get('max', 0):.2f}")
                                with col_c:
                                    st.metric("Outliers", col_stats.get('outliers', {}).get('count', 0))
                                    st.metric("Missing", col_stats.get('missing_count', 0))
                
                with insight_tab3:
                    st.markdown("#### Trend Analysis")
                    
                    trends = insights.get('trends', {})
                    
                    if trends:
                        # Summary
                        increasing = [col for col, t in trends.items() if t.get('trend') == 'increasing']
                        decreasing = [col for col, t in trends.items() if t.get('trend') == 'decreasing']
                        stable = [col for col, t in trends.items() if t.get('trend') == 'stable']
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("📈 Increasing", len(increasing))
                        with col2:
                            st.metric("📉 Decreasing", len(decreasing))
                        with col3:
                            st.metric("➡️  Stable", len(stable))
                        
                        # Details
                        st.markdown("#### Trend Details")
                        
                        for col, trend_data in list(trends.items())[:10]:  # Show first 10
                            trend_type = trend_data.get('trend', 'unknown')
                            if trend_type == 'insufficient_data':
                                continue
                            
                            with st.expander(f"{col} - {trend_type.title()}"):
                                change_pct = trend_data.get('change_percentage', 0)
                                volatility = trend_data.get('volatility', 0)
                                
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    st.metric("Change", f"{change_pct:.1f}%")
                                    st.metric("First Value", f"{trend_data.get('first_value', 0):.2f}")
                                with col_b:
                                    st.metric("Volatility", f"{volatility:.1f}%")
                                    st.metric("Last Value", f"{trend_data.get('last_value', 0):.2f}")
                    else:
                        st.info("No trend data available")
                
                with insight_tab4:
                    st.markdown("#### Anomaly Detection")
                    
                    anomalies = insights.get('anomalies', {})
                    
                    if anomalies:
                        # Summary
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Total Anomalies", anomalies.get('total_anomalies', 0))
                        with col2:
                            st.metric("Affected Columns", anomalies.get('affected_columns', 0))
                        
                        # Column details
                        column_anomalies = anomalies.get('column_anomalies', {})
                        
                        if column_anomalies:
                            st.markdown("#### Anomaly Details by Column")
                            
                            for col, anom_data in list(column_anomalies.items())[:10]:
                                if anom_data.get('count', 0) > 0:
                                    severity = anom_data.get('severity', 'unknown')
                                    
                                    # Color code by severity
                                    if severity == 'critical':
                                        icon = "🔴"
                                    elif severity == 'high':
                                        icon = "🟠"
                                    elif severity == 'moderate':
                                        icon = "🟡"
                                    else:
                                        icon = "🟢"
                                    
                                    with st.expander(f"{icon} {col} - {severity.title()} ({anom_data['count']} outliers)"):
                                        col_a, col_b = st.columns(2)
                                        with col_a:
                                            st.metric("Outlier Count", anom_data['count'])
                                            st.metric("Lower Bound", f"{anom_data.get('lower_bound', 0):.2f}")
                                        with col_b:
                                            st.metric("Percentage", f"{anom_data.get('percentage', 0):.1f}%")
                                            st.metric("Upper Bound", f"{anom_data.get('upper_bound', 0):.2f}")
                                        
                                        # Show some outlier values
                                        outlier_vals = anom_data.get('outlier_values', [])
                                        if outlier_vals:
                                            st.markdown("**Sample Outlier Values:**")
                                            st.write(outlier_vals[:5])
                        
                        # Unusual patterns
                        patterns = insights.get('patterns', [])
                        if patterns:
                            st.markdown("#### Unusual Patterns Detected")
                            for pattern in patterns:
                                pattern_type = pattern.get('type', 'unknown')
                                description = pattern.get('description', 'No description')
                                st.warning(f"🔍 {description}")
                    else:
                        st.success("✅ No significant anomalies detected")
        
        else:
            st.info("👆 Upload a file above to get started!")
    
    with tab3:
        st.markdown("## 💬 Ask Questions About Your Data")
        
        # Check if data is available
        if 'uploaded_data' not in st.session_state or st.session_state.uploaded_data is None:
            st.warning("⚠️  Please upload a dataset first in the '📁 Upload Data' tab")
            st.info("""
            **To get started:**
            1. Go to the '📁 Upload Data' tab
            2. Upload a CSV, Excel, or JSON file
            3. Come back here to ask questions!
            """)
        else:
            df = st.session_state.uploaded_data['dataframe']
            file_info = st.session_state.uploaded_data['file_info']
            
            # Initialize session state for query history
            if 'query_history' not in st.session_state:
                st.session_state.query_history = []
            
            # Display current dataset info
            st.info(f"📊 **Current Dataset:** {file_info['original_name']} ({len(df)} rows, {len(df.columns)} columns)")
            
            # Show suggested questions
            with st.expander("💡 Suggested Questions", expanded=False):
                st.markdown("Here are some questions you can ask about your data:")
                
                if st.button("🔄 Generate AI Suggestions"):
                    with st.spinner("Generating suggestions..."):
                        suggestions = nl_to_sql_converter.suggest_questions(df)
                        if suggestions:
                            for i, question in enumerate(suggestions, 1):
                                st.markdown(f"**{i}.** {question}")
                        else:
                            st.warning("Could not generate suggestions")
                
                # Fallback suggestions
                st.markdown("""
                **Common Questions:**
                - Show me the first 10 rows
                - What is the average of [numeric column]?
                - Count the number of rows
                - Show me the top 5 rows by [column name]
                - What are the unique values in [column name]?
                """)
            
            st.markdown("---")
            
            # Query input section
            st.markdown("### Ask Your Question")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                user_question = st.text_input(
                    "Type your question in natural language:",
                    placeholder="e.g., What is the average sales by region?",
                    key="user_question_input"
                )
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                ask_button = st.button("🚀 Ask", type="primary", use_container_width=True)
            
            # Process query
            if ask_button and user_question:
                with st.spinner("🤔 Thinking..."):
                    # Convert NL to SQL
                    sql_query = nl_to_sql_converter.convert_to_sql(user_question, df)
                    
                    if sql_query:
                        # Execute query first
                        with st.spinner("⚙️  Executing query..."):
                            success, results, error = query_executor.execute_query(sql_query, df)
                            
                            if success and results is not None:
                                # Get AI explanation in natural language
                                analysis = nl_to_sql_converter.analyze_query_results(user_question, results)
                                
                                # Show natural language response
                                st.success("✅ Here's what I found:")
                                
                                if analysis:
                                    st.markdown(f"**💡 {analysis}**")
                                else:
                                    # Fallback explanation
                                    if len(results) == 1 and len(results.columns) == 1:
                                        # Single value result
                                        value = results.iloc[0, 0]
                                        st.markdown(f"**💡 The answer is: {value}**")
                                    else:
                                        st.markdown(f"**💡 I found {len(results)} results for your question.**")
                                
                                # Show SQL query in an expander (optional)
                                with st.expander("🔍 View SQL Query", expanded=False):
                                    st.code(sql_query, language="sql")
                                    explanation = nl_to_sql_converter.explain_query(sql_query, user_question)
                                    if explanation:
                                        st.caption(f"Technical explanation: {explanation}")
                                
                                # Display results
                                st.markdown("#### Results:")
                                st.markdown(f"**{len(results)} rows returned**")
                                
                                # Show results in tabs
                                result_tab1, result_tab2 = st.tabs(["📊 Data Table", "📈 Visualization"])
                                
                                with result_tab1:
                                    display_results = query_executor.format_results(results)
                                    st.dataframe(display_results, use_container_width=True, height=400)
                                
                                with result_tab2:
                                    # Auto-generate visualization
                                    if len(results) > 0 and len(results) <= 1000:
                                        with st.spinner("🎨 Generating visualization..."):
                                            fig, chart_type = chart_generator.auto_generate_chart(
                                                results,
                                                question=user_question
                                            )
                                            
                                            if fig:
                                                # Chart type selector
                                                col_chart1, col_chart2 = st.columns([1, 3])
                                                with col_chart1:
                                                    selected_chart_type = st.selectbox(
                                                        "Chart Type",
                                                        ["auto", "bar", "line", "pie", "scatter", "histogram"],
                                                        index=0,
                                                        key=f"chart_type_{len(st.session_state.query_history)}"
                                                    )
                                                
                                                # Regenerate if chart type changed
                                                if selected_chart_type != "auto" and selected_chart_type != chart_type:
                                                    fig, chart_type = chart_generator.auto_generate_chart(
                                                        results,
                                                        question=user_question,
                                                        chart_type=selected_chart_type
                                                    )
                                                
                                                # Display chart
                                                if fig:
                                                    st.plotly_chart(
                                                        fig,
                                                        use_container_width=True,
                                                        config=chart_generator.get_chart_config()
                                                    )
                                                    st.caption(f"📊 Chart Type: {chart_type.capitalize()}")
                                                else:
                                                    st.info("💡 This data is best viewed as a table")
                                            else:
                                                st.info("💡 Visualization not available for this result set")
                                    elif len(results) > 1000:
                                        st.warning(f"⚠️  Dataset too large ({len(results)} rows). Showing table view only.")
                                        st.info("💡 Try adding a LIMIT clause to your query or filter the data")
                                    else:
                                        st.info("💡 No data to visualize")
                                
                                # Analyze results
                                with st.spinner("🧠 Analyzing results..."):
                                    analysis = nl_to_sql_converter.analyze_query_results(user_question, results)
                                    if analysis:
                                        st.markdown("#### 🎯 Key Insights:")
                                        st.success(analysis)
                                
                                # Download option
                                col_a, col_b = st.columns([3, 1])
                                with col_b:
                                    csv_data = results.to_csv(index=False).encode('utf-8')
                                    st.download_button(
                                        label="📥 Download CSV",
                                        data=csv_data,
                                        file_name=f"query_results_{len(st.session_state.query_history) + 1}.csv",
                                        mime="text/csv",
                                        use_container_width=True
                                    )
                                
                                # Save to query history
                                st.session_state.query_history.append({
                                    'question': user_question,
                                    'sql': sql_query,
                                    'rows_returned': len(results),
                                    'timestamp': pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                                })
                                
                                # Save to database
                                try:
                                    query_record = db_ops.create_query(
                                        user_id=1,  # Default user
                                        dataset_id=None,  # Can be linked if dataset was saved
                                        query_text=user_question,
                                        sql_query=sql_query,
                                        results_count=len(results)
                                    )
                                    if query_record:
                                        st.caption(f"💾 Query saved to history (ID: {str(query_record.id)[:8]}...)")
                                except Exception as e:
                                    st.caption(f"⚠️  Could not save to database: {str(e)}")
                            
                            elif error and "column" in error.lower():
                                # Try to fix column name errors
                                st.warning("⚠️  Column name error detected. Attempting to fix...")
                                
                                with st.spinner("🔧 Fixing query..."):
                                    fixed_sql = nl_to_sql_converter.fix_sql_query(sql_query, error, df)
                                    
                                    if fixed_sql:
                                        st.info("✨ Query fixed! Executing corrected query...")
                                        st.code(fixed_sql, language="sql")
                                        
                                        success2, results2, error2 = query_executor.execute_query(fixed_sql, df)
                                        
                                        if success2 and results2 is not None:
                                            st.success("✅ Fixed query executed successfully!")
                                            st.markdown(f"**{len(results2)} rows returned**")
                                            display_results2 = query_executor.format_results(results2)
                                            st.dataframe(display_results2, use_container_width=True, height=400)
                                        else:
                                            st.error(f"❌ Fixed query also failed: {error2}")
                                    else:
                                        st.error(f"❌ Could not fix the query. Error: {error}")
                            
                            else:
                                st.error(f"❌ Query execution failed: {error}")
                                st.warning("💡 Try rephrasing your question or use simpler terms")
                    
                    else:
                        st.error("❌ Failed to generate SQL query from your question")
                        st.warning("💡 Try asking in a different way or check your Gemini API key")
            
            # Display query history
            if len(st.session_state.query_history) > 0:
                st.markdown("---")
                st.markdown("### 📜 Query History")
                
                with st.expander(f"View History ({len(st.session_state.query_history)} queries)", expanded=False):
                    for i, query in enumerate(reversed(st.session_state.query_history), 1):
                        st.markdown(f"""
                        **Query {len(st.session_state.query_history) - i + 1}** - {query['timestamp']}
                        - **Question:** {query['question']}
                        - **SQL:** `{query['sql']}`
                        - **Results:** {query['rows_returned']} rows
                        """)
                        st.markdown("---")
                    
                    if st.button("🗑️  Clear History"):
                        st.session_state.query_history = []
                        st.rerun()
            
            # Tips section
            st.markdown("---")
            st.markdown("### 💡 Tips for Asking Questions")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **✅ Good Questions:**
                - "What is the average price?"
                - "Show me the top 10 products"
                - "Count the total number of orders"
                - "Group sales by category"
                """)
            
            with col2:
                st.markdown("""
                **❌ Avoid:**
                - Too vague: "Show me data"
                - Wrong column names
                - Complex joins (use uploaded data as single table)
                - Multiple unrelated questions
                """)
    
    with tab4:
        st.markdown("## 💭 Chat with Your Data")
        st.caption("Have a conversation with your data - I'll remember the context!")
        
        # Initialize chat history in session state
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []
        if 'conversation_started' not in st.session_state:
            st.session_state.conversation_started = False
        
        # Check if data is uploaded
        if st.session_state.uploaded_data is None:
            st.warning("⚠️  Please upload data first in the 'Upload Data' tab!")
            st.info("💡 **What you can do with Chat:**\n\n"
                   "- Have natural conversations about your data\n"
                   "- Ask follow-up questions without repeating context\n"
                   "- Get AI-powered insights\n"
                   "- Search similar past conversations\n\n"
                   "Once you upload data, come back here to start chatting!")
        else:
            # Sidebar controls
            with st.sidebar:
                st.markdown("---")
                st.markdown("### 💭 Chat Controls")
                
                if st.button("🆕 New Conversation", use_container_width=True):
                    conversation_manager.start_new_conversation(title=f"Chat {len(st.session_state.chat_messages) + 1}")
                    st.session_state.chat_messages = []
                    st.session_state.conversation_started = True
                    st.success("✅ New conversation started!")
                    st.rerun()
                
                if st.button("🗑️ Clear Chat", use_container_width=True):
                    st.session_state.chat_messages = []
                    conversation_manager.clear_context()
                    st.success("✅ Chat cleared!")
                    st.rerun()
                
                # Context toggle
                use_context = st.checkbox("Use Conversation Context", value=True, 
                                        help="AI remembers previous messages")
                
                # Show conversation stats
                if st.session_state.conversation_started:
                    summary = conversation_manager.get_conversation_summary()
                    st.markdown("#### 📊 Stats")
                    st.metric("Messages", summary['message_count'])
                    st.metric("User", summary['user_messages'])
                    st.metric("Assistant", summary['assistant_messages'])
            
            # Main chat interface
            st.markdown("### 💬 Conversation")
            
            # Display chat history
            chat_container = st.container()
            with chat_container:
                for i, message in enumerate(st.session_state.chat_messages):
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
                        
                        # Show additional info for query results
                        if message.get("metadata"):
                            metadata = message["metadata"]
                            
                            if metadata.get("type") == "query_result":
                                # Show SQL in expander
                                with st.expander("🔍 View SQL Query"):
                                    st.code(metadata.get("sql", ""), language="sql")
                                
                                # Show results table
                                if metadata.get("results") is not None:
                                    st.dataframe(
                                        metadata["results"],
                                        use_container_width=True,
                                        height=300
                                    )
                                    st.caption(f"📊 Showing {len(metadata['results'])} rows")
            
            # Chat input
            st.markdown("---")
            user_message = st.chat_input("Ask me anything about your data...")
            
            if user_message:
                # Start conversation if not started
                if not st.session_state.conversation_started:
                    conversation_manager.start_new_conversation(title=f"Chat - {user_message[:30]}")
                    st.session_state.conversation_started = True
                
                # Add user message to display
                st.session_state.chat_messages.append({
                    "role": "user",
                    "content": user_message,
                    "metadata": {}
                })
                
                # Process with chat handler
                with st.spinner("🤔 Thinking..."):
                    response = chat_handler.process_chat_message(
                        message=user_message,
                        df=st.session_state.uploaded_data['dataframe'],
                        use_context=use_context
                    )
                
                # Add assistant response
                assistant_message = {
                    "role": "assistant",
                    "content": response.get("content", "I couldn't process that request."),
                    "metadata": response
                }
                st.session_state.chat_messages.append(assistant_message)
                
                # Rerun to show new messages
                st.rerun()
            
            # Quick actions
            if st.session_state.chat_messages:
                st.markdown("---")
                st.markdown("### ⚡ Quick Actions")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("💡 Get Help"):
                        help_response = chat_handler._handle_help()
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": help_response["content"],
                            "metadata": help_response
                        })
                        st.rerun()
                
                with col2:
                    if st.button("📊 Show Summary"):
                        summary_msg = f"You've asked {conversation_manager.get_conversation_summary()['user_messages']} questions in this conversation."
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": summary_msg,
                            "metadata": {"type": "summary"}
                        })
                        st.rerun()
                
                with col3:
                    if st.button("🔍 Search Similar"):
                        if st.session_state.chat_messages:
                            last_user_msg = conversation_manager.get_last_user_message()
                            if last_user_msg:
                                st.info("🔍 Searching for similar past conversations...")
                                similar = conversation_manager.search_similar_conversations(last_user_msg, n_results=3)
                                if similar:
                                    st.success(f"✅ Found {len(similar)} similar conversations!")
                                else:
                                    st.info("No similar conversations found yet.")
            
            # ChromaDB indicator
            st.markdown("---")
            st.caption("🔍 **ChromaDB Active**: Conversation history is being stored with semantic search capabilities")
    
    with tab5:
        st.markdown("## 📄 Generate Professional Reports")
        st.caption("Create and export comprehensive data analysis reports")
        
        # Check if data is uploaded
        if st.session_state.uploaded_data is None:
            st.warning("⚠️  Please upload data first in the 'Upload Data' tab!")
            st.info("💡 **Report Features:**\n\n"
                   "- 📄 Professional PDF reports with formatting\n"
                   "- 📊 Excel exports with multiple sheets\n"
                   "- 📈 Include statistics, insights, and visualizations\n"
                   "- 💾 Download and share with stakeholders\n\n"
                   "Once you upload data, come back here to generate reports!")
        else:
            st.markdown("### 📋 Report Configuration")
            
            # Report settings
            col1, col2 = st.columns(2)
            
            with col1:
                report_title = st.text_input(
                    "Report Title",
                    value=f"Data Analysis Report - {datetime.now().strftime('%Y-%m-%d')}",
                    help="Custom title for your report"
                )
                
                include_stats = st.checkbox("Include Statistical Analysis", value=True)
                include_insights = st.checkbox("Include AI Insights", value=True)
            
            with col2:
                export_format = st.selectbox(
                    "Export Format",
                    ["PDF", "Excel", "Both"],
                    help="Choose your preferred export format"
                )
                
                include_raw_data = st.checkbox(
                    "Include Raw Data (Excel only)",
                    value=False,
                    help="Add raw dataset as a separate sheet"
                )
            
            st.markdown("---")
            
            # Generate report button
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
            
            with col_btn1:
                if st.button("📄 Generate Report", type="primary", use_container_width=True):
                    with st.spinner("🔄 Generating report..."):
                        try:
                            # Get insights if requested (auto-generate if not available)
                            insights_data = None
                            if include_insights:
                                # Check both possible keys for insights
                                if 'insights' in st.session_state and st.session_state.insights:
                                    insights_data = st.session_state.insights
                                elif 'generated_insights' in st.session_state:
                                    insights_data = st.session_state.generated_insights
                                else:
                                    st.info("💡 Auto-generating AI insights for report...")
                                    insights_data = insight_generator.generate_comprehensive_insights(
                                        st.session_state.uploaded_data['dataframe']
                                    )
                                    # Store in both keys for consistency
                                    st.session_state.insights = insights_data
                                    st.session_state.generated_insights = insights_data
                            
                            # Get query history
                            query_history = st.session_state.get('query_history', [])
                            
                            # Create report
                            report = report_generator.create_report(
                                df=st.session_state.uploaded_data['dataframe'],
                                title=report_title,
                                include_statistics=include_stats,
                                include_insights=include_insights,
                                insights_data=insights_data,
                                query_history=query_history
                            )
                            
                            if report:
                                st.session_state.generated_report = report
                                st.success("✅ Report generated successfully!")
                            else:
                                st.error("❌ Failed to generate report")
                                
                        except Exception as e:
                            st.error(f"❌ Error generating report: {str(e)}")
            
            # Display generated report
            if 'generated_report' in st.session_state:
                st.markdown("---")
                st.markdown("### 📊 Report Preview")
                
                report = st.session_state.generated_report
                
                # Report summary
                with st.expander("📋 Report Summary", expanded=True):
                    st.markdown(f"**Title:** {report.get('title', 'N/A')}")
                    st.markdown(f"**Generated:** {report.get('generated_at', 'N/A')}")
                    
                    metadata = report.get('metadata', {})
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Total Rows", f"{metadata.get('total_rows', 0):,}")
                    with col_b:
                        st.metric("Total Columns", metadata.get('total_columns', 0))
                    with col_c:
                        st.metric("File Size", f"{metadata.get('file_size_mb', 0):.2f} MB")
                    
                    st.markdown(f"**Sections:** {len(report.get('sections', []))}")
                    for section in report.get('sections', []):
                        st.markdown(f"  - {section.get('title', 'Untitled')}")
                
                # Download buttons
                st.markdown("### 💾 Download Report")
                
                col_dl1, col_dl2, col_dl3 = st.columns(3)
                
                with col_dl1:
                    if st.button("⬇️ Download PDF", use_container_width=True):
                        with st.spinner("📄 Creating PDF..."):
                            success, pdf_bytes, error = pdf_exporter.export_to_pdf(
                                report,
                                filename=report_title.replace(' ', '_') + '.pdf'
                            )
                            
                            if success and pdf_bytes:
                                st.download_button(
                                    label="📥 Download PDF File",
                                    data=pdf_bytes,
                                    file_name=f"{report_title.replace(' ', '_')}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                                if error:
                                    st.info(error)
                            else:
                                st.error(f"❌ PDF export failed: {error}")
                
                with col_dl2:
                    if st.button("⬇️ Download Excel", use_container_width=True):
                        with st.spinner("📊 Creating Excel..."):
                            df_to_export = st.session_state.uploaded_data['dataframe'] if include_raw_data else None
                            success, excel_bytes, error = excel_exporter.export_to_excel(
                                report,
                                df=df_to_export,
                                filename=report_title.replace(' ', '_') + '.xlsx'
                            )
                            
                            if success and excel_bytes:
                                st.download_button(
                                    label="📥 Download Excel File",
                                    data=excel_bytes,
                                    file_name=f"{report_title.replace(' ', '_')}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                            else:
                                st.error(f"❌ Excel export failed: {error}")
                
                with col_dl3:
                    if st.button("⬇️ Download Data Only", use_container_width=True):
                        with st.spinner("📊 Creating Excel..."):
                            success, excel_bytes, error = excel_exporter.export_dataframe_to_excel(
                                st.session_state.uploaded_data['dataframe'],
                                filename="data_export.xlsx"
                            )
                            
                            if success and excel_bytes:
                                st.download_button(
                                    label="📥 Download Data Excel",
                                    data=excel_bytes,
                                    file_name="data_export.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                            else:
                                st.error(f"❌ Excel export failed: {error}")
    
    with tab6:
        st.markdown("## 🔧 Setup & Connection Test")
        
        st.markdown("### 1. Configuration Check")
        
        # Check directories
        st.write("**📁 Directory Structure:**")
        dirs_status = {
            "Upload Directory": settings.upload_dir.exists(),
            "Data Directory": settings.data_dir.exists(),
            "Reports Directory": settings.reports_dir.exists(),
            "Logs Directory": settings.logs_dir.exists(),
        }
        
        for dir_name, exists in dirs_status.items():
            if exists:
                st.success(f"✅ {dir_name}: Created")
            else:
                st.error(f"❌ {dir_name}: Missing")
        
        st.markdown("---")
        
        # Test Gemini connection
        st.markdown("### 2. Gemini AI Connection Test")
        
        if st.button("🧪 Test Gemini API", type="primary"):
            with st.spinner("Testing connection to Gemini AI..."):
                if initialize_gemini():
                    success, message = test_gemini_connection()
                    if success:
                        st.success("✅ Gemini API is working!")
                        st.info(f"**Response:** {message}")
                    else:
                        st.error(f"❌ Connection failed: {message}")
                else:
                    st.error("❌ Gemini API key not configured properly")
        
        st.markdown("---")
        
        # Test Database
        st.markdown("### 3. Database Connection Test")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🧪 Test Database Connection", type="primary"):
                with st.spinner("Testing database connection..."):
                    try:
                        if db_handler.test_connection():
                            st.success("✅ Database connection successful!")
                            
                            # Show stats
                            try:
                                stats = db_ops.get_database_stats()
                                st.info("**Database Statistics:**")
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    st.metric("Users", stats['total_users'])
                                    st.metric("Datasets", stats['total_datasets'])
                                    st.metric("Queries", stats['total_queries'])
                                with col_b:
                                    st.metric("Insights", stats['total_insights'])
                                    st.metric("Visualizations", stats['total_visualizations'])
                                    st.metric("Reports", stats['total_reports'])
                            except:
                                st.warning("Database connected but tables may not be initialized")
                        else:
                            st.error("❌ Database connection failed!")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.info("💡 Run: `python database/init_database.py` to initialize")
        
        with col2:
            if st.button("🔍 Test Vector Store"):
                with st.spinner("Testing vector store..."):
                    try:
                        collections = vector_store.list_collections()
                        st.success(f"✅ Vector store working!")
                        st.info(f"**Collections:** {len(collections)}")
                        if collections:
                            st.write("Available collections:", collections)
                    except Exception as e:
                        st.error(f"❌ Vector store error: {str(e)}")
        
        st.markdown("---")
        
        # Configuration details
        st.markdown("### 4. Current Configuration")
        
        with st.expander("Show Configuration Details"):
            config_info = {
                "Gemini Model": settings.gemini_model,
                "Database Name": settings.db_name,
                "Database Host": settings.db_host,
                "App Port": settings.app_port,
                "Debug Mode": settings.debug_mode,
                "Max Upload Size": f"{settings.max_upload_size_mb} MB",
                "Allowed Files": ", ".join(settings.allowed_extensions),
            }
            
            for key, value in config_info.items():
                st.text(f"{key}: {value}")
    
    with tab7:
        st.markdown("## 📚 How to Use DataWise AI")
        
        st.markdown("""
        ### Getting Started
        
        **DataWise AI** is your intelligent companion for data analysis. Here's how it works:
        
        #### Step 1: Upload Your Data 📁
        - Support for CSV, Excel, and JSON files
        - Automatic data validation and preview
        - Data stored securely in PostgreSQL
        
        #### Step 2: Ask Questions 💬
        - Use natural language: "What's the average sales?"
        - AI converts your question to SQL automatically
        - Get instant results in table format
        
        #### Step 3: Chat with Your Data 💭
        - **NEW!** Have a conversation with your data
        - Ask follow-up questions naturally
        - Context-aware responses (I remember what you asked before!)
        - Powered by ChromaDB for semantic search
        
        #### Step 4: Visualize Data 📊
        - Request charts: "Show me a bar chart of revenue by region"
        - AI chooses the best visualization
        - Interactive charts with zoom, pan, and export
        
        #### Step 5: Get Insights 🧠
        - Click "Generate Insights" for automatic analysis
        - Discover trends, correlations, and anomalies
        - AI explains findings in plain language
        
        #### Step 6: Generate Reports 📄
        - Create comprehensive reports with one click
        - Export to PDF or Excel
        - Professional formatting with charts and insights
        
        ---
        
        ### Example Questions You Can Ask:
        
        - "What are the top 5 products by revenue?"
        - "Show me sales trends over the last 6 months"
        - "Which region has the highest growth rate?"
        - "Are there any unusual patterns in the data?"
        - "Create a summary report of all key metrics"
        
        ---
        
        ### Now Available:
        - ✅ Phase 1: Project foundation & setup
        - ✅ Phase 2: PostgreSQL database integration
        - ✅ Phase 3: File upload & data processing
        - ✅ Phase 4: Natural language queries with Gemini AI
        - ✅ Phase 5: Interactive data visualizations
        - ✅ Phase 6: AI-powered insights & statistical analysis
        - ✅ Phase 7: Conversational chat with context & ChromaDB
        - ✅ Phase 8: Professional report generation & export
        
        ### Coming Soon:
        - ⏳ Phase 9: Docker containerization
        - ⏳ Phase 10: Cloud deployment & polish
        """)


if __name__ == "__main__":
    # Initialize Gemini on startup
    initialize_gemini()
    
    # Run main app
    main()

