# 📁 Project Structure

```
honeytoken-project/
├── src/                          # Source code modules
│   ├── honeytoken_generator.py   # Generate fake credentials
│   ├── token_scanner.py          # Scan for leaked tokens
│   ├── honeytoken_injector.py    # Inject tokens into files
│   ├── github_integration.py     # GitHub API operations
│   ├── alert_system.py           # Multi-channel alerts
│   ├── webhook_server.py         # HTTP callback server
│   ├── ci_scanner.py             # CI/CD integration
│   └── setup_script.py           # Automated setup
│
├── web/                          # Web dashboard
│   └── dashboard.html            # Real-time monitoring UI
│
├── tests/                        # Unit tests
│   └── test_suite.py             # Complete test suite (22 tests)
│
├── config/                       # Configuration & data
│   ├── .env                      # Environment variables
│   ├── alert_config.json         # Alert settings
│   ├── honeytokens.json          # Generated tokens
│   ├── scan_results.json         # Scan history
│   ├── alert_history.json        # Alert logs
│   ├── injection_log.json        # Injection tracking
│   ├── webhook_events.json       # Webhook events
│   └── latest-scan.json          # Latest scan report
│
├── docs/                         # Documentation
│   ├── README.md                 # Main documentation
│   ├── IMPLEMENTATION_GUIDE.txt  # 16,000+ word guide
│   ├── PRESENTATION_GUIDE.md     # Examiner demo script
│   ├── DASHBOARD_FEATURES.md     # Dashboard documentation
│   ├── DASHBOARD_REFERENCE.md    # Quick reference
│   └── EXAMINER_CHECKLIST.md     # Presentation checklist
│
├── .github/                      # GitHub workflows
│   └── workflows/
│       └── honeytoken-detection.yml  # CI/CD automation
│
├── data/                         # Data directory (if needed)
├── logs/                         # Log files
├── reports/                      # Generated reports
│
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker image
├── docker-compose.yml            # Multi-service setup
└── PROJECT_STRUCTURE.md          # This file
```

## 🚀 Quick Start

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run setup script
python src/setup_script.py
```

### 2. Generate Honeytokens
```bash
# Generate GitHub PAT tokens
python src/honeytoken_generator.py --type github_pat --count 5

# Generate batch of mixed tokens
python src/honeytoken_generator.py --batch --count 3
```

### 3. Inject & Scan
```bash
# Inject into repository
python src/honeytoken_injector.py --inject-repo ./target-repo

# Scan for tokens
python src/token_scanner.py ./target-repo
```

### 4. View Dashboard
```bash
# Start HTTP server (from project root)
python -m http.server 8000

# Open browser
http://localhost:8000/web/dashboard.html
```

### 5. Run Tests
```bash
python tests/test_suite.py
```

## 📊 Data Files Location

All JSON data files are now in `config/` directory:
- **honeytokens.json** - Generated honeytoken database
- **scan_results.json** - Complete scan history
- **alert_history.json** - Alert delivery logs
- **injection_log.json** - Token injection tracking
- **webhook_events.json** - Webhook callback events

## 📝 Documentation

Comprehensive documentation is in `docs/`:
- **README.md** - Main project documentation
- **IMPLEMENTATION_GUIDE.txt** - Complete implementation guide
- **PRESENTATION_GUIDE.md** - 7-minute demo script for examiner
- **DASHBOARD_FEATURES.md** - Dashboard features and design
- **DASHBOARD_REFERENCE.md** - Quick reference card

## 🎓 For Examiner Presentation

1. Read `docs/PRESENTATION_GUIDE.md`
2. Start HTTP server: `python -m http.server 8000`
3. Open: `http://localhost:8000/web/dashboard.html`
4. Follow the 7-minute demo script

## 🔧 Configuration

Edit `config/.env` for:
- GitHub tokens
- Email/SMTP settings
- Slack/Discord webhooks
- Alert preferences

## 🐳 Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f
```

## ✅ Testing

```bash
# Run all 22 tests
python tests/test_suite.py

# Expected: All tests pass
```

## 📦 Production Deployment

1. Configure `config/.env` with production credentials
2. Run `docker-compose up -d` 
3. Access dashboard at configured port
4. Set up GitHub Actions workflow from `.github/workflows/`

---

**Note:** This structure keeps the project organized and professional for academic presentation and real-world deployment.
