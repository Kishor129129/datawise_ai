# 📸 Image Guide for README

This guide shows you what images to capture and add to make your GitHub README look professional and impressive to recruiters!

---

## 📁 Image Files Needed

Place all images in `docs/images/` folder:

```
docs/images/
├── banner.png              # Main project banner (REQUIRED)
├── demo.gif                # Short demo animation (HIGHLY RECOMMENDED)
├── architecture.png        # System architecture diagram
├── dashboard.png           # Main dashboard view
├── upload-step.png         # File upload interface
├── query-interface.png     # Ask Questions tab
├── query-step.png          # Query execution example
├── visualizations.png      # Chart visualizations
├── chat.png                # Chat interface
├── chat-step.png           # Chat conversation example
├── insights.png            # AI Insights display
├── insights-step.png       # Full insights page
├── reports.png             # Report generation interface
└── reports-step.png        # Generated report example
```

---

## 🎨 1. Banner Image (banner.png)

**What:** Eye-catching header image for your project

**How to create:**

1. Use Canva (free): https://www.canva.com/
2. Dimensions: 1200 x 400 pixels
3. Include:
   - Project name: "DataWise AI"
   - Tagline: "Your Intelligent Data Analysis Companion"
   - AI/Data icons
   - Modern gradient background (blue/purple)

**Alternative:** Use text-based banner:

```markdown
# 🚀 DataWise AI

### Your Intelligent Data Analysis Companion

Transform data into insights with natural language
```

---

## 🎥 2. Demo GIF (demo.gif) - HIGHLY RECOMMENDED!

**What:** 10-20 second screen recording showing the app in action

**How to create:**

### Option A: ScreenToGif (Windows)

1. Download: https://www.screentogif.com/
2. Record these steps:
   - Upload a file
   - Ask a question (e.g., "How many rows?")
   - Show AI response
   - Show chart generation
3. Keep it short (10-15 seconds)
4. Export as GIF (optimize to < 5MB)

### Option B: LICEcap (Windows/Mac)

1. Download: https://www.cockos.com/licecap/
2. Record same workflow
3. Save as GIF

### Option C: Use built-in tools

**Windows:** Xbox Game Bar (Win + G)
**Mac:** QuickTime + Convert to GIF online

**What to show:**

1. Start on Home page
2. Click "Upload Data"
3. Upload titanic.csv
4. Go to "Ask Questions"
5. Type: "How many passengers survived?"
6. Show result
7. Show auto-generated chart

**Tips:**

- Keep GIF under 5MB for GitHub
- Use 30 FPS
- Slow down cursor movements
- Show clear, readable text

---

## 🏗️ 3. Architecture Diagram (architecture.png)

**What:** Visual flowchart showing how the system works

**How to create:**

### Option A: Draw.io (Free, Easy)

1. Go to: https://app.diagrams.net/
2. Create flowchart:

```
┌─────────────┐
│   USER      │
│  Uploads    │
│   Data      │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Data Validator │
│   & Storage     │
│  (PostgreSQL)   │
└─────────┬───────┘
          │
          ▼
    ┌─────────────┐
    │  User asks  │
    │  question   │
    └──────┬──────┘
           │
           ▼
    ┌──────────────────┐
    │  Gemini AI       │
    │  NL → SQL        │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │  Query Executor  │
    │  Pandas/SQL      │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │  AI Insights     │
    │  Visualizations  │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │  PDF/Excel       │
    │  Reports         │
    └──────────────────┘
```

3. Add colors and icons
4. Export as PNG

### Option B: Excalidraw (Free, Beautiful)

1. Go to: https://excalidraw.com/
2. Draw boxes and arrows
3. Export as PNG

### Option C: Just use text diagram

Keep the ASCII diagram in README

---

## 📊 4. Feature Screenshots

### 4.1 Dashboard (dashboard.png)

**What to capture:**

1. Run `streamlit run app.py`
2. Open the Home tab
3. Make sure it shows:
   - All 8 feature cards
   - Progress indicators
   - Welcome message
4. Take full-page screenshot
5. Crop to show main content

### 4.2 Upload Step (upload-step.png)

**What to capture:**

1. Go to "Upload Data" tab
2. Upload `sample_data/titanic.csv`
3. Wait for preview to load
4. Screenshot showing:
   - File upload interface
   - Data preview table
   - Statistics
   - "Auto-Saved to Database" message

### 4.3 Query Interface (query-interface.png)

**What to capture:**

1. Go to "Ask Questions" tab
2. Type a question: "How many passengers survived?"
3. Before hitting Enter, take screenshot
4. Should show:
   - Input field with question
   - Suggested questions below
   - Clean interface

### 4.4 Query Results (query-step.png)

**What to capture:**

1. After query executes
2. Screenshot showing:
   - Natural language answer
   - Results table
   - Auto-generated chart
   - SQL query (in expander)

### 4.5 Visualizations (visualizations.png)

**What to capture:**

1. Same as above, but focus on the Visualization tab
2. Show an interesting chart (bar or pie chart)
3. Make sure chart is colorful and clear

### 4.6 Chat Interface (chat.png)

**What to capture:**

1. Go to "Chat" tab
2. Have a conversation:
   - "Hello"
   - "What data do I have?"
   - "Show me some statistics"
3. Screenshot showing multiple chat bubbles

### 4.7 Chat Example (chat-step.png)

**What to capture:**

1. Same as above
2. Full conversation flow
3. Include quick action buttons

### 4.8 Insights (insights.png)

**What to capture:**

1. Go to "Upload Data" tab
2. Upload data if not already
3. Scroll to "AI-Powered Insights"
4. Screenshot the 4-tab interface:
   - Key Insights
   - Statistics
   - Trends
   - Anomalies

### 4.9 Reports Interface (reports.png)

**What to capture:**

1. Go to "Reports" tab
2. Show the report configuration:
   - Title input
   - Checkboxes
   - Generate button
3. Don't click generate yet

### 4.10 Report Generated (reports-step.png)

**What to capture:**

1. After generating report
2. Show the download buttons
3. Maybe show a small preview of the PDF

---

## 🛠️ Screenshot Tools

### Windows:

- **Snipping Tool** (Win + Shift + S) - Built-in
- **ShareX** (Free) - Best for full-page screenshots
- **Greenshot** (Free)

### Mac:

- **Command + Shift + 4** - Built-in
- **Command + Shift + 5** - Screenshot toolbar

### Browser Extensions:

- **Awesome Screenshot** - For full-page captures
- **Nimbus Screenshot**

---

## 📐 Image Specifications

| Image Type   | Recommended Size | Format | Max File Size |
| ------------ | ---------------- | ------ | ------------- |
| Banner       | 1200 x 400 px    | PNG    | 500 KB        |
| Demo GIF     | 800 x 600 px     | GIF    | 5 MB          |
| Architecture | 800 x 600 px     | PNG    | 300 KB        |
| Screenshots  | 1200 x 800 px    | PNG    | 500 KB each   |

---

## 🎨 Styling Tips

1. **Consistent Colors:**

   - Primary: #2E86AB (blue)
   - Secondary: #A23B72 (purple)
   - Accent: #F18F01 (orange)

2. **Clean Backgrounds:**

   - Use white or light gray backgrounds
   - Avoid cluttered desktops in screenshots

3. **Highlight Key Features:**

   - Use arrows or circles to point out important parts
   - Add text annotations if needed

4. **Optimize File Sizes:**
   - Compress images: https://tinypng.com/
   - Keep total images < 10 MB

---

## ✅ Quick Priority List

**MUST HAVE (Top Priority):**

1. ✅ Banner image
2. ✅ Demo GIF
3. ✅ 3-4 key screenshots (upload, query, chat, insights)

**NICE TO HAVE:** 4. Architecture diagram 5. All feature screenshots 6. Report examples

**OPTIONAL:** 7. Logo 8. Custom graphics

---

## 🚀 Image Upload Instructions

### For GitHub:

1. **Option A: Upload via GitHub Web UI**

   ```
   1. Go to your repo on GitHub
   2. Navigate to docs/images/
   3. Click "Add file" > "Upload files"
   4. Drag and drop all images
   5. Commit changes
   ```

2. **Option B: Using Git Command Line**
   ```bash
   # Add images to docs/images/ folder
   git add docs/images/
   git commit -m "Add README images and documentation"
   git push origin main
   ```

---

## 💡 Pro Tips

1. **Take screenshots in light mode** - Better visibility
2. **Use sample data** - titanic.csv or sales_data.csv
3. **Clear cache** - Fresh, clean interface
4. **Zoom to 100%** - Best quality
5. **Hide personal info** - No real API keys visible
6. **Use consistent zoom level** - All screenshots same size

---

## 📝 Checklist

Before pushing to GitHub:

- [ ] Banner image created
- [ ] Demo GIF recorded (10-15 seconds)
- [ ] At least 4 feature screenshots
- [ ] All images optimized (< 500KB each)
- [ ] Images placed in `docs/images/` folder
- [ ] Images referenced correctly in README.md
- [ ] Tested image links on GitHub

---

## 🎬 If You Can't Create Images Right Now

**Temporary solution:**

1. Remove image tags from README:

   ```markdown
   <!-- Will add screenshot soon -->
   ```

2. Use text-based descriptions

3. Focus on making the text README amazing first

4. Add images later when you have time

**Your README will still look professional without images, but images make it 10x better for recruiters!**

---

## 🆘 Need Help?

**Free Design Resources:**

- Icons: https://www.flaticon.com/
- Colors: https://coolors.co/
- Fonts: https://fonts.google.com/
- Banners: https://www.canva.com/

**Quick Banner Templates:**

- Search "GitHub banner template" on Canva
- Customize with your project name
- Download and use!

---

Good luck! Your GitHub profile will look amazing! 🚀
