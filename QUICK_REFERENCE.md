# 🎯 Quick Reference - Presentation Points

## ⚡ Setup (5 min before)
- [ ] Close unnecessary apps, disable notifications
- [ ] Run `START_DEMO.bat`
- [ ] Verify dashboard opens at `http://localhost:8000/web/dashboard.html`
- [ ] Check stats populated: Tokens, Scans, Detections, Alerts

## 🎤 Opening (30 sec)
**"Automated Honeytoken Detection System - fake credentials that act as security tripwires. No AI/ML, pure regex-based detection with full CI/CD integration and real-time dashboard."**

## 📊 Dashboard Demo (5 min)

### Stats Cards (30 sec)
- Hover each card for animation
- Point out: 30 tokens, 3 detections (red), 4 scans, 0 alerts

### Detections Panel (1 min)
- Red alert banner
- Table: Token ID, Type, Count, Timestamp
- Hover action buttons

### Scan History (1 min)
- Columns: Scan ID, Type, Target, Files, Findings
- Color badges: Green=clean, Orange=findings
- Duration metrics

### Activity Timeline (1 min)
- Chronological events with colored dots
- Blue=generation, Green=clean, Orange=findings, Red=alerts
- Relative timestamps ("5m ago")

### Live Features (30 sec)
- Auto-refresh every 30 seconds
- Manual refresh button
- Export Report, Run Scan buttons

## 🔧 Technical Points (2 min)

### Core Components
1. **Token Generator** - Realistic GitHub PAT, AWS, Slack tokens
2. **Scanner** - Regex-based, no ML needed
3. **Alert System** - Email, Slack, Discord, Teams
4. **Webhook Server** - Callback handler
5. **CI/CD Integration** - GitHub Actions, auto-scan on push
6. **Dashboard** - Real-time monitoring

### Key Features
- **Performance**: 24 files scanned <1 sec
- **Accuracy**: Entropy filtering, whitelist support
- **Scalability**: Handles 10,000+ files
- **Security**: Tokens never leak, audit logging
- **Docker**: One-command deployment

## 💡 Key Talking Points

1. **"Tripwire for credential leaks"**
2. **"Regex faster than ML for known patterns"**
3. **"CI/CD blocks commits before production"**
4. **"Enterprise-grade monitoring"**
5. **"Multi-channel alerts"**
6. **"Production-ready with Docker"**

## ❓ Quick Answers

**Why no ML?** Regex is faster and more accurate for known formats

**False positives?** Entropy checking + format validation + whitelist

**Detection flow?** Scan → Match → Alert → Log → Dashboard

**Scalability?** Parallel processing, tested on 10K+ files

**Production-ready?** Core yes, add auth + encryption for enterprise

**Next steps?** ML for unknown patterns, browser extension, K8s support

## 🎬 If Demo Fails
- Have screenshots ready
- Pivot to code walkthrough
- Show `src/honeytoken_generator.py`, `src/token_scanner.py`
- Run `python tests/test_suite.py`

## ⏱️ Timing
- Introduction: 30 sec
- Dashboard: 5 min
- Technical: 2 min
- Questions: 2-3 min
- **Total: 10-12 min**

## 🔑 File Shortcuts
- Demo: `START_DEMO.bat`
- Scanner: `python src/token_scanner.py --scan .`
- Stats: `python src/honeytoken_generator.py --stats`
- Tests: `python tests/test_suite.py`
