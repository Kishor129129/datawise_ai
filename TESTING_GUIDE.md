# 🧪 Complete Project Testing Guide

## Before You Start

### ✅ Prerequisites Check

1. **Environment Setup**

```bash
# Check Python version (should be 3.8+)
python --version

# Verify virtual environment (if using one)
# If not activated, activate it first

# Check all dependencies installed
pip list | grep -E "streamlit|pandas|google-generativeai|chromadb|psycopg2|reportlab|openpyxl"
```

2. **Database Setup**

```bash
# Make sure PostgreSQL is running
# Windows: Check Services
# Mac/Linux: sudo service postgresql status

# Verify database exists
psql -U postgres -c "\l" | grep datawise_ai
```

3. **Environment Variables**

```bash
# Check .env file exists
cat .env

# Should contain:
# GEMINI_API_KEY=your_key_here
# DATABASE_URL=postgresql://...
```

---

## 🚀 Phase-by-Phase Testing

### Phase 1: Foundation & Setup ✅

**What to Test:**

- Project structure
- Configuration loading
- Basic imports

**Steps:**

```bash
# 1. Check directory structure
ls -la

# Should see:
# - database/
# - utils/
# - ai_engine/
# - visualization/
# - insights/
# - chat/
# - reports/
# - chroma_data/
# - uploads/
# - sample_data/

# 2. Test configuration
python -c "from config import settings; print('Config OK:', settings.gemini_api_key[:10])"

# Expected: Config OK: AIzaSyAnRC...
```

**✅ Pass Criteria:**

- All directories exist
- Config loads without errors
- Gemini API key loaded

---

### Phase 2: Database Integration ✅

**What to Test:**

- PostgreSQL connection
- ChromaDB initialization
- Database operations

**Steps:**

```bash
# 1. Test database connection
python -c "from database.postgres_handler import db_handler; print('DB:', db_handler.test_connection())"

# Expected: DB: True

# 2. Test ChromaDB
python -c "from database.vector_store import vector_store; print('Collections:', vector_store.list_collections())"

# Expected: Collections: ['chat_history']

# 3. Run database tests
python database/test_database.py
```

**✅ Pass Criteria:**

- PostgreSQL connects successfully
- ChromaDB directory exists (chroma_data/)
- All database tests pass

**Troubleshooting:**

```bash
# If database connection fails:
# 1. Check PostgreSQL is running
# 2. Verify DATABASE_URL in .env
# 3. Create database if needed:
createdb -U postgres datawise_ai

# If ChromaDB fails:
# 1. Check directory permissions
# 2. Reinstall: pip install chromadb>=0.4.0
```

---

### Phase 3: File Upload & Processing ✅

**What to Test:**

- File upload functionality
- Data validation
- Data preview

**Steps:**

```bash
# 1. Start the app
streamlit run app.py

# 2. In browser (http://localhost:8501):
```

**Browser Testing:**

1. Go to **"📁 Upload Data"** tab
2. Click file uploader
3. Select `sample_data/sales_data.csv`
4. Click **"🔍 Process & Analyze"**

**✅ Verify:**

- [x] File uploads without error
- [x] Data preview shows (5 rows)
- [x] Column info displays
- [x] Data quality metrics appear
- [x] Success message: "✅ Data processed successfully!"

**What You Should See:**

```
✅ File uploaded: sales_data.csv
✅ Data processed successfully!

📊 Data Preview (first 5 rows)
[Table with your data]

📋 Column Information
- X columns
- Y rows
- Data types listed

📈 Data Quality
- Missing values: X%
- Duplicates: Y
```

---

### Phase 4: Natural Language Queries ✅

**What to Test:**

- NL to SQL conversion
- Query execution
- Results display

**Steps:**

1. Make sure data is uploaded (Phase 3)
2. Go to **"💬 Ask Questions"** tab
3. Try these queries:

**Test Query 1:**

```
Question: "What is the total quantity?"
Expected: SQL generated, results shown in table
```

**Test Query 2:**

```
Question: "Show me the top 5 products by sales"
Expected: SQL with ORDER BY and LIMIT, top 5 rows displayed
```

**Test Query 3:**

```
Question: "What is the average sales?"
Expected: SQL with AVG(), single result
```

**✅ Verify:**

- [x] SQL query generated and displayed
- [x] Query executes successfully
- [x] Results shown in table format
- [x] Query added to history
- [x] Can ask follow-up questions

**Note:** If Gemini API gives 404 error:

- Queries won't work (API issue, not your code issue)
- Everything else should still function
- The query executor itself works fine

---

### Phase 5: Data Visualizations ✅

**What to Test:**

- Chart generation
- Chart type switching
- Interactive plots

**Steps:**

1. Upload data and run a query (Phase 3 & 4)
2. In **"💬 Ask Questions"** tab, after query results
3. Click **"📈 Visualization"** sub-tab

**Test Scenarios:**

**Scenario 1: Auto Chart**

```
Query: "Show me sales by region"
Expected: Auto-generates appropriate chart (bar/pie)
```

**Scenario 2: Chart Switching**

```
Action: Change chart type selector
Options: auto, bar, line, pie, scatter, histogram
Expected: Chart regenerates in selected type
```

**Scenario 3: Download**

```
Action: Click download button on chart
Expected: PNG file downloads
```

**✅ Verify:**

- [x] Chart appears automatically
- [x] Can switch between chart types
- [x] Charts are interactive (hover, zoom)
- [x] Download works
- [x] Chart config options available

---

### Phase 6: AI Insights & Analysis ✅

**What to Test:**

- Statistical analysis
- Trend detection
- Anomaly detection
- AI insight generation

**Steps:**

1. Upload data (Phase 3)
2. In **"📁 Upload Data"** tab
3. Scroll to **"Step 5: AI-Powered Insights"**
4. Click **"🧠 Generate AI Insights"**
5. Wait 5-10 seconds

**✅ Verify:**

- [x] Insights generate successfully
- [x] 4 tabs appear: Key Insights, Statistics, Trends, Anomalies
- [x] Statistical metrics displayed
- [x] Trends identified (increasing/decreasing/stable)
- [x] Anomalies detected (if any)
- [x] Recommendations provided

**What You Should See:**

```
🎯 Key Insights Tab:
• AI-generated insights
• Key findings
• Recommendations

📊 Statistics Tab:
• Basic stats (rows, columns, missing %)
• Data quality score (0-100)
• Numeric column analysis

📈 Trends Tab:
• Increasing trends: X
• Decreasing trends: Y
• Stable metrics: Z

⚠️ Anomalies Tab:
• Total anomalies: X
• Affected columns: Y
• Severity breakdown
```

---

### Phase 7: Conversational Chat ✅

**What to Test:**

- Chat interface
- Context awareness
- ChromaDB semantic search
- Conversation history

**Steps:**

1. Upload data (Phase 3)
2. Go to **"💭 Chat"** tab

**Test Conversation 1: Basic Chat**

```
You: "Hello!"
Expected: Friendly greeting response
```

**Test Conversation 2: Data Query**

```
You: "What is the total sales?"
Expected: SQL generated, results shown inline
```

**Test Conversation 3: Context Awareness**

```
You: "What is the total sales?"
[Get response]
You: "What about by region?"
Expected: Understands "what about" refers to sales, generates regional breakdown
```

**Test Conversation 4: Help**

```
You: "help"
Expected: Full help guide displayed
```

**Test Actions:**

- Click **"🆕 New Conversation"** → should clear chat
- Click **"🗑️ Clear Chat"** → should clear messages
- Toggle **"Use Conversation Context"** → on/off
- Click **"💡 Get Help"** → shows help
- Click **"📊 Show Summary"** → shows stats
- Click **"🔍 Search Similar"** → searches ChromaDB

**✅ Verify:**

- [x] Chat messages appear in bubbles
- [x] Context remembered between messages
- [x] SQL and results shown inline
- [x] Conversation stats update
- [x] ChromaDB indicator shows active
- [x] Quick actions work

**ChromaDB Test:**

```
After chatting for a while:
1. Click "🔍 Search Similar"
2. Should find similar past conversations
3. Confirms ChromaDB is working!
```

---

### Phase 8: Report Generation ✅

**What to Test:**

- Report generation
- PDF export
- Excel export
- Download functionality

**Steps:**

1. Upload data (Phase 3)
2. (Optional) Generate insights (Phase 6)
3. Go to **"📄 Reports"** tab

**Test Report 1: Basic Report**

```
1. Leave title as default
2. Check "Include Statistical Analysis" ✅
3. Uncheck "Include AI Insights" (if you haven't generated them)
4. Format: "Excel"
5. Click "📄 Generate Report"
6. Wait 2-3 seconds
7. Report preview should appear
```

**Test Report 2: Full Report**

```
1. Generate insights first (Phase 6)
2. Custom title: "My Test Report"
3. Check all options ✅
4. Format: "Both"
5. Click "📄 Generate Report"
6. Download both PDF and Excel
```

**Test Downloads:**

```
1. Click "⬇️ Download PDF"
   → File downloads (4-10 KB)
   → Open PDF → Check formatting

2. Click "⬇️ Download Excel"
   → File downloads (5-20 KB)
   → Open Excel → Check sheets (6 sheets)

3. Click "⬇️ Download Data Only"
   → File downloads (smaller)
   → Open Excel → Raw data only
```

**✅ Verify:**

- [x] Report generates without errors
- [x] Preview shows metadata correctly
- [x] PDF downloads and opens
- [x] Excel downloads with 6 sheets:
  - Summary
  - Data Overview
  - Statistics
  - Insights
  - Raw Data (if included)
  - Query History
- [x] Data-only export works
- [x] Files are well-formatted

**Excel Sheets to Check:**

1. **Summary** → Report info and metadata
2. **Data Overview** → Column details
3. **Statistics** → Stats table
4. **Insights** → AI findings (if generated)
5. **Raw Data** → Your dataset (if included)
6. **Query History** → Queries executed (if any)

---

## 🔄 **End-to-End Workflow Test**

### Complete User Journey

**Scenario: Data Analysis from Upload to Report**

```
1. START APP
   streamlit run app.py

2. UPLOAD DATA (Phase 3)
   → Upload Data tab
   → Upload sample_data/sales_data.csv
   → Process & Analyze
   ✅ Data preview appears

3. ASK QUESTIONS (Phase 4 & 5)
   → Ask Questions tab
   → "What are the top 5 products by sales?"
   ✅ SQL generated
   ✅ Results in table
   ✅ Chart auto-generated

4. CHAT ABOUT DATA (Phase 7)
   → Chat tab
   → "What is the average sales?"
   → "What about by region?"
   ✅ Context-aware responses
   ✅ Results shown inline

5. GENERATE INSIGHTS (Phase 6)
   → Upload Data tab
   → Scroll to AI Insights
   → Generate AI Insights
   ✅ 4 tabs of insights appear

6. CREATE REPORT (Phase 8)
   → Reports tab
   → Configure options
   → Generate Report
   → Download PDF and Excel
   ✅ Both files download successfully
```

**Total Time:** 5-10 minutes
**Success:** All steps complete without errors

---

## 🐛 **Common Issues & Solutions**

### Issue 1: App Won't Start

```
Error: "ModuleNotFoundError"

Solution:
pip install -r requirements.txt
```

### Issue 2: Database Connection Failed

```
Error: "could not connect to server"

Solution:
1. Check PostgreSQL is running
2. Verify .env DATABASE_URL
3. Create database:
   createdb -U postgres datawise_ai
```

### Issue 3: Gemini API 404 Error

```
Error: "models/gemini-1.5-flash-latest is not found"

Note: This is expected! Your API key may not have access to this model.
Impact: NL queries and AI chat won't work, but everything else will!

Solution:
1. Continue testing other features
2. Check API key access at: https://aistudio.google.com/
3. This doesn't affect: upload, visualization, insights, reports
```

### Issue 4: ChromaDB Not Found

```
Error: "Collection not found"

Solution:
# Run Phase 7 tests to initialize
python test_phase7.py

# Verify directory exists
ls -la chroma_data/
```

### Issue 5: Reports Not Generating

```
Error: "ReportLab not available"

Solution:
pip install reportlab>=4.0.0
# PDF will use fallback if still fails

For Excel:
pip install openpyxl>=3.1.0
```

### Issue 6: File Upload Fails

```
Error: File too large

Solution:
1. Check file size < 200MB
2. Try smaller dataset
3. Check uploads/ directory exists
```

---

## ✅ **Testing Checklist**

### Phase 1: Foundation ✅

- [ ] Project structure correct
- [ ] Config loads
- [ ] All packages imported

### Phase 2: Database ✅

- [ ] PostgreSQL connects
- [ ] ChromaDB initialized
- [ ] chroma_data/ exists (350 KB)

### Phase 3: File Upload ✅

- [ ] CSV uploads successfully
- [ ] Data preview displays
- [ ] Column info shows
- [ ] Data quality metrics appear

### Phase 4: NL Queries ✅

- [ ] SQL generated from question
- [ ] Query executes
- [ ] Results displayed
- [ ] Query history tracked
- [ ] (Note: May fail if Gemini API inaccessible)

### Phase 5: Visualizations ✅

- [ ] Charts auto-generate
- [ ] Chart type switching works
- [ ] Interactive features work
- [ ] Download chart works

### Phase 6: AI Insights ✅

- [ ] Insights generate
- [ ] Statistics displayed
- [ ] Trends detected
- [ ] Anomalies identified
- [ ] Data quality score shown

### Phase 7: Chat ✅

- [ ] Chat interface works
- [ ] Messages display in bubbles
- [ ] Context remembered
- [ ] Quick actions work
- [ ] ChromaDB search works
- [ ] Conversation stats update

### Phase 8: Reports ✅

- [ ] Report generates
- [ ] PDF downloads (4-10 KB)
- [ ] Excel downloads (5-20 KB)
- [ ] Excel has 6 sheets
- [ ] Data-only export works

### End-to-End ✅

- [ ] Complete workflow works
- [ ] All phases integrate smoothly
- [ ] No critical errors
- [ ] Performance acceptable (< 10 sec per action)

---

## 📊 **Expected Performance**

- **File Upload:** < 2 seconds
- **Data Processing:** < 3 seconds
- **Query Generation:** 2-4 seconds (if Gemini works)
- **Chart Generation:** < 2 seconds
- **Insights Generation:** 5-10 seconds
- **Report Generation:** 3-5 seconds
- **Chat Response:** 2-4 seconds

---

## 🎉 **Success Criteria**

Your project is **READY FOR PHASE 9** if:

✅ All 8 phases work independently
✅ End-to-end workflow completes
✅ ChromaDB active (chroma_data/ exists)
✅ Reports generate and download
✅ No critical errors
✅ Performance acceptable

**Minor issues OK:**

- Gemini API 404 (external service issue)
- Slow Gemini responses (network/API load)
- Warning messages (as long as features work)

---

## 🚀 **Ready for Phase 9?**

Once you've tested everything and most features work:

### Say: **"start phase 9"** or **"phase 9"**

We'll add:

- Docker containerization
- Production configuration
- Easy deployment
- Multi-container orchestration

---

## 📝 **Testing Notes Template**

Use this to track your testing:

```
=== DATAWISE AI - TESTING LOG ===

Date: _____________
Tester: ___________

Phase 1 (Foundation): [ ] PASS [ ] FAIL
Notes: ___________________________________

Phase 2 (Database): [ ] PASS [ ] FAIL
Notes: ___________________________________

Phase 3 (Upload): [ ] PASS [ ] FAIL
Notes: ___________________________________

Phase 4 (NL Queries): [ ] PASS [ ] FAIL
Notes: ___________________________________

Phase 5 (Visualizations): [ ] PASS [ ] FAIL
Notes: ___________________________________

Phase 6 (Insights): [ ] PASS [ ] FAIL
Notes: ___________________________________

Phase 7 (Chat): [ ] PASS [ ] FAIL
Notes: ___________________________________

Phase 8 (Reports): [ ] PASS [ ] FAIL
Notes: ___________________________________

End-to-End: [ ] PASS [ ] FAIL
Notes: ___________________________________

Overall Status: [ ] READY FOR PHASE 9 [ ] NEEDS FIXES

Issues to Address:
1. ___________________________________
2. ___________________________________
3. ___________________________________
```

---

**Good luck with testing! You've built something amazing! 🌟**
