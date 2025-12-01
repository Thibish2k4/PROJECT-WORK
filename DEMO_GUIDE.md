# 🚀 One-Click Demo Launch

## Quick Start

### Windows Users (Easiest):

**Method 1: Double-Click the Batch File**
```
📁 Double-click: START_DEMO.bat
```

**Method 2: PowerShell (Right-click)**
```
📁 Right-click START_DEMO.ps1 → "Run with PowerShell"
```

**Method 3: Command Line**
```bash
python start_demo.py
```

### What Happens:

1. ✅ **Checks Dependencies** - Verifies Python packages
2. 🔑 **Generates Honeytokens** - Creates 18 sample tokens (GitHub PAT, AWS, Slack)
3. 📁 **Creates Demo Repo** - Sets up demo-presentation/ with injected tokens
4. 🔍 **Runs Scans** - Performs security scans to populate data
5. 🔔 **Generates Alerts** - Creates sample alert history
6. 🌐 **Starts Server** - Launches HTTP server on port 8000
7. 🎨 **Opens Dashboard** - Automatically opens in your default browser

### Dashboard Access:

```
http://localhost:8000/web/dashboard.html
```

The dashboard will show:
- 📊 **Real-time Statistics** - Tokens, scans, alerts
- 🔍 **Scan History** - Detailed scan results
- 🔔 **Alert Timeline** - Activity feed
- 🔄 **Auto-refresh** - Updates every 30 seconds

## For Examiner Presentation:

### Step 1: Launch Demo
```
Double-click START_DEMO.bat
```

### Step 2: Wait for Browser
The dashboard will automatically open in ~5 seconds

### Step 3: Show Features
- Hover over stat cards (animations)
- Scroll through scan history
- Point out activity timeline
- Explain color-coded badges

### Step 4: Run Additional Commands (Optional)
While demo is running, open another terminal:

```bash
# Show statistics
python src/honeytoken_generator.py --stats

# List detections
python src/token_scanner.py --detections

# View scan history
python src/token_scanner.py --history

# Run tests
python tests/test_suite.py
```

### Step 5: Stop Demo
Press **Ctrl+C** in the terminal to stop the server

## Troubleshooting:

### Port 8000 Already in Use
```bash
# The script will show an error
# Stop other servers or change port in start_demo.py
```

### Dashboard Not Opening
```bash
# Manually open browser to:
http://localhost:8000/web/dashboard.html
```

### Missing Dependencies
```bash
# Install required packages
pip install -r requirements.txt
```

### Python Not Found
```bash
# Install Python 3.7+ from python.org
# Make sure to check "Add to PATH" during installation
```

## What the Demo Creates:

```
📁 demo-presentation/    ← Sample repo with injected tokens
📁 config/              ← Populated with data
   ├── honeytokens.json     (18+ tokens)
   ├── scan_results.json    (Multiple scans)
   ├── alert_history.json   (8 alerts)
   └── latest-scan.json     (Latest report)
```

## After Demo:

### Clean Up (Optional)
```bash
# Remove demo repository
Remove-Item -Recurse demo-presentation

# Clear data (start fresh)
python src/setup_script.py
```

### Keep Server Running
Leave the terminal open to keep dashboard accessible

### Restart Demo
Simply run `START_DEMO.bat` again - it will refresh all data

## Pro Tips:

1. **Test Before Presentation**
   - Run the demo once before showing to examiner
   - Ensure browser opens correctly
   - Check dashboard loads data

2. **Full Screen**
   - Press F11 in browser for immersive view
   - Hide bookmarks bar for cleaner look

3. **Backup Plan**
   - If auto-open fails, have URL ready to type
   - Know where to find the batch file

4. **Impressive Stats**
   - The demo generates substantial data
   - ~18+ honeytokens, multiple scans
   - Shows system working at scale

5. **Keep Terminal Visible**
   - Position terminal and browser side-by-side
   - Show "live" server logs during demo

## System Requirements:

- ✅ Windows 10/11
- ✅ Python 3.7 or higher
- ✅ Internet connection (first run - to install packages)
- ✅ Modern web browser (Chrome, Edge, Firefox)

## Success Indicators:

When demo launches successfully, you'll see:

```
✅ DEMO ENVIRONMENT READY!

📊 System Status:
  🔑 Total Honeytokens: 18+
  🚨 Detections: 0
  🔍 Scans Completed: 2+
  🔔 Alerts Generated: 8

🌐 Dashboard:
  URL: http://localhost:8000/web/dashboard.html
  Status: ● LIVE

⏳ Server is running... Press Ctrl+C to stop
```

---

**🎓 You're now ready for your examiner presentation!**

The entire system is running with one click - professional, impressive, and production-ready! 🚀
