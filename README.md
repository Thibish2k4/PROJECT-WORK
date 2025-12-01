# 🍯 Automated Honeytoken Injection & Detection System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF)](https://github.com/features/actions)

A comprehensive **honeytoken detection system** designed for CI/CD pipelines, specifically targeting GitHub tokens and other sensitive credentials. This project provides automated token generation, injection, scanning, and alerting capabilities similar to GitGuardian, but without AI/ML dependencies.

## 🎯 Project Overview

This system is designed for **cybersecurity research and education**, demonstrating how organizations can detect credential leaks using honeytokens - deliberately planted fake credentials that trigger alerts when accessed or leaked.

### Key Features

- ✅ **Realistic Token Generation**: Generate GitHub PATs, OAuth tokens, AWS keys, Slack tokens, and more
- ✅ **Automated Scanning**: Regex-based detection (no ML required) of leaked tokens in repositories
- ✅ **CI/CD Integration**: GitHub Actions workflow for automated scanning on every push
- ✅ **Multi-Channel Alerts**: Email, Slack, Discord, MS Teams, and webhook notifications
- ✅ **Webhook Server**: Receive callbacks when honeytokens are used
- ✅ **Token Injection**: Automatically inject honeytokens into repositories and CI variables
- ✅ **Dashboard**: Web-based monitoring dashboard
- ✅ **Docker Support**: Containerized deployment with docker-compose

## 📁 Project Structure

```
honeytoken-project/
├── honeytoken_generator.py      # Generate realistic honeytokens
├── token_scanner.py              # Scan files for leaked tokens
├── github_integration.py         # GitHub API integration
├── alert_system.py               # Multi-channel alert notifications
├── webhook_server.py             # HTTP server for token callbacks
├── honeytoken_injector.py        # Inject tokens into repos/CI
├── ci_scanner.py                 # CI/CD pipeline integration
├── setup_script.py               # Automated setup and configuration
├── test_suite.py                 # Unit tests
├── requirements.txt              # Python dependencies
├── dashboard.html                # Monitoring dashboard
├── Dockerfile                    # Container image definition
├── docker-compose.yml            # Multi-container orchestration
├── .env                          # Environment configuration
├── .gitignore                    # Git ignore rules
├── README.md                     # This file
├── IMPLEMENTATION_GUIDE.txt      # Step-by-step implementation guide
└── .github/
    └── workflows/
        └── honeytoken-detection.yml  # GitHub Actions workflow
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Git
- Docker (optional, for containerized deployment)
- GitHub account with Personal Access Token

### Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd honeytoken-project
   ```

2. **Run the setup script**:
   ```bash
   python setup_script.py
   ```
   This will:
   - Create `.env` and `.gitignore` files
   - Initialize data directories
   - Validate dependencies

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Edit `.env` file with your settings:
   ```env
   GITHUB_TOKEN=your_github_token
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   ALERT_EMAIL_TO=security@example.com
   ```

## 💡 Usage Examples

### 1. Generate Honeytokens

```bash
# Generate a single GitHub PAT
python honeytoken_generator.py --type github_pat

# Generate multiple tokens
python honeytoken_generator.py --type github_pat --count 5

# Generate batch of different types
python honeytoken_generator.py --batch --count 3

# List all tokens
python honeytoken_generator.py --list

# Show statistics
python honeytoken_generator.py --stats
```

### 2. Scan for Leaked Tokens

```bash
# Scan a directory
python token_scanner.py /path/to/repository

# Scan a specific file
python token_scanner.py /path/to/file.py

# Scan text directly
python token_scanner.py --text "ghp_1234567890abcdefghijklmnopqrstuvwxyz"

# View scan history
python token_scanner.py --history

# Show honeytoken detections
python token_scanner.py --detections
```

### 3. Inject Honeytokens

```bash
# Create a honeypot file
python honeytoken_injector.py --create-file ./test-repo env_file

# Inject into a repository
python honeytoken_injector.py --inject-repo ./test-repo

# View injection history
python honeytoken_injector.py --history

# Clean up injected files
python honeytoken_injector.py --cleanup ./test-repo
```

### 4. Start Webhook Server

```bash
# Start on default port (8080)
python webhook_server.py

# Start on custom port
python webhook_server.py --port 9000

# Send test webhook
python webhook_server.py --test

# View webhook events
python webhook_server.py --events
```

### 5. Test Alert System

```bash
# Test email alerts
python alert_system.py --test-email

# Test Slack notifications
python alert_system.py --test-slack

# View alert history
python alert_system.py --history

# Show statistics
python alert_system.py --stats
```

### 6. CI/CD Scanning

```bash
# Scan workspace (for CI environments)
python ci_scanner.py --scan-workspace

# Scan only changed files
python ci_scanner.py --scan-diff --base-ref main --head-ref HEAD

# Generate markdown report
python ci_scanner.py --scan-workspace --format markdown --output-file report.md

# Fail build on findings
python ci_scanner.py --scan-workspace --fail-on-findings
```

### 7. GitHub Integration

```bash
# Test GitHub connection
python github_integration.py --test

# List repositories
python github_integration.py --list-repos

# Scan a GitHub repository
python github_integration.py --scan-repo owner repo-name

# List repository secrets
python github_integration.py --list-secrets owner repo-name
```

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services:
- **honeytoken-detector**: Webhook server on port 8080
- **dashboard**: Web dashboard on port 8081
- **scanner**: On-demand scanning (use profile)

### Run Scanner Service

```bash
docker-compose --profile scanner run scanner
```

## 🔧 GitHub Actions Integration

The included workflow (`.github/workflows/honeytoken-detection.yml`) automatically:

1. Scans repository on every push/PR
2. Detects leaked tokens using regex patterns
3. Creates issues for honeytoken detections
4. Comments on PRs with scan results
5. Fails builds if honeytokens are found

### Setup GitHub Actions

1. Add repository secrets in GitHub:
   - `GITHUB_TOKEN` (automatically available)
   - Add any additional secrets needed for alerts

2. The workflow runs automatically on:
   - Push to main/develop branches
   - Pull requests
   - Daily at 2 AM UTC
   - Manual trigger via workflow_dispatch

## 📊 Dashboard

Open `dashboard.html` in your browser to view:
- Total honeytokens generated
- Detection counts
- Scan history
- Alert statistics
- Activity timeline

When using Docker:
```
http://localhost:8081
```

## 🧪 Running Tests

```bash
# Run full test suite
python test_suite.py

# Run specific test
python -m unittest test_suite.TestHoneytokenGenerator

# Run with pytest (if installed)
pytest test_suite.py -v
```

## 🔐 Security Best Practices

1. **Never commit `.env` file** - Contains sensitive credentials
2. **Rotate honeytokens regularly** - Generate new tokens periodically
3. **Monitor alerts actively** - Respond to detections immediately
4. **Use secure channels** - Configure encrypted alert channels
5. **Limit access** - Restrict who can view honeytoken data
6. **Document incidents** - Keep records of all detections

## 📈 Use Cases

### 1. Security Research
- Study credential leak patterns
- Test detection capabilities
- Analyze attacker behavior

### 2. Education
- Demonstrate honeytoken concepts
- Teach secure coding practices
- CI/CD security integration

### 3. Internal Monitoring
- Detect accidental credential commits
- Monitor developer behavior
- Compliance verification

## 🛠️ Configuration

### Alert Channels

Configure in `.env`:

```env
# Email (SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=app_specific_password
ALERT_EMAIL_TO=security@example.com

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# Discord
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# Microsoft Teams
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...
```

### Scanning Patterns

Token patterns are defined in `token_scanner.py`. Supported types:
- GitHub PAT, OAuth, Fine-Grained tokens
- AWS Access Keys and Secret Keys
- Slack tokens and webhooks
- Stripe API keys
- Google API keys
- Private keys (RSA, EC)
- Generic API keys and secrets
- JWT tokens

## 📝 Academic Use

This project is suitable for:
- **Final year projects** in cybersecurity
- **Research papers** on credential leak detection
- **Master's thesis** topics
- **Conference presentations**

### Suggested Paper Topics:
1. "Honeytoken-Based Detection Systems in CI/CD Pipelines"
2. "Regex vs ML: Effectiveness in Credential Leak Detection"
3. "Automated Security Testing in DevOps Environments"
4. "Real-time Alert Systems for Credential Exposure"

## 🤝 Contributing

This is an educational project. Feel free to:
- Report issues
- Suggest improvements
- Add new token patterns
- Enhance detection logic

## 📄 License

MIT License - See LICENSE file for details

## ⚠️ Disclaimer

This tool is for **educational and authorized security testing only**. Users are responsible for:
- Obtaining proper authorization
- Complying with applicable laws
- Using ethically and responsibly
- Not using for malicious purposes

## 📚 Additional Resources

- [IMPLEMENTATION_GUIDE.txt](IMPLEMENTATION_GUIDE.txt) - Detailed setup instructions
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitGuardian Blog](https://blog.gitguardian.com/) - Inspiration and research

## 🆘 Support

For issues or questions:
1. Check `IMPLEMENTATION_GUIDE.txt`
2. Review test examples in `test_suite.py`
3. Examine configuration in `.env.example`

## 🎓 Academic Citation

If you use this project in academic work, please cite:

```
[Your Name], "Automated Honeytoken Injection and Detection System for CI/CD Pipelines",
[University Name], [Year]
```

---

**Built with ❤️ for cybersecurity education and research**
