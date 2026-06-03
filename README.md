# Technology Control Tower - VFS IT

> **Central orchestration system for CIO-level visibility and decision-making across all technology management areas**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Internal-green.svg)]()

---

## 🎯 Overview

The Technology Control Tower is a comprehensive automation system that provides unified operational visibility across VFS IT's technology landscape. It integrates data from multiple sources (Jira, spreadsheets, manual inputs) and generates executive-ready reports for informed decision-making.

### Key Benefits
- 🎯 **Unified Visibility** - Single source of truth for all technology initiatives
- ⚡ **Automated Reporting** - Eliminate manual report compilation
- 📊 **Data-Driven Decisions** - Real-time insights across 10 TPR areas
- 🔴🟡🟢 **RAG Status** - Clear visual indicators for risk and performance
- 📅 **Governance Tracking** - Never miss a meeting or deadline
- 🤖 **AI-Ready** - Foundation for Q2/Q3 AI enhancements

---

## 🚀 Quick Start

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Configure
```bash
cp .env.example .env
cp config/config.example.yaml config/config.yaml
# Edit .env and config.yaml with your settings
```

### 3. Run
```bash
python src/control_tower.py
```

**That's it!** Check `data/output/` for your reports.

📖 **Detailed Setup:** See [Setup Guide](docs/SETUP_GUIDE.md)  
📚 **Usage Instructions:** See [User Guide](docs/USER_GUIDE.md)

---

## 📦 Q1 MVP Components

### 1. 📋 Master Register
Central registry of all technology assets, initiatives, and systems
- Track initiatives across 10 TPR areas
- Monitor status, owners, budgets, and risk levels
- Consolidate data from Jira and Excel sources
- **Output:** `master_register.xlsx`, `master_register_summary.xlsx`

### 2. ✅ Action Tracker
Comprehensive action management across all technology areas
- Track actions with owners, due dates, and status
- Identify overdue and critical actions
- Filter by TPR area, owner, or priority
- **Output:** `action_tracker.xlsx` (with Overdue, Due This Week, Critical sheets)

### 3. 📊 TPR Reporting Model
Technology Performance Review reports across 10 coverage areas
- Executive summary with RAG status indicators
- Detailed reports for each TPR area
- Automated highlights, risks, and recommendations
- **Output:** `TPR_Report_[Month_Year].xlsx`

### 4. 📅 Governance Cadence
Meeting schedules, review cycles, and decision workflows
- Track weekly, monthly, and quarterly meetings
- Generate 6-month meeting calendar
- Identify upcoming meetings and deadlines
- **Output:** `governance_cadence.xlsx`

### 5. 🔗 Jira Integration
Automated data collection from Jira
- Pull projects, epics, initiatives, and tasks
- Map issues to TPR areas automatically
- Export to Master Register and Action Tracker formats
- **Output:** `jira_data.xlsx`, `jira_actions.xlsx`

---

## 📊 TPR Coverage Areas

The system tracks performance across 10 technology domains:

| # | Area | Description |
|---|------|-------------|
| 1 | **Service Management** | Service delivery, SLAs, incident management |
| 2 | **Architecture** | Enterprise architecture, technical standards |
| 3 | **Risk Management** | Technology risks, mitigation strategies |
| 4 | **PI Delivery** | Program Increment delivery, agile metrics |
| 5 | **Tech Assurance** | Quality assurance, compliance |
| 6 | **AWS Cost Optimisation** | Cloud cost management |
| 7 | **Cyber Security** | Security posture, vulnerabilities, threats |
| 8 | **Audits** | Audit findings, remediation tracking |
| 9 | **Resource Strategy** | Staffing, skills, capacity planning |
| 10 | **3rd Party Contracts** | Vendor relationships, contract tracking |

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Language** | Python 3.9+ | Core automation and processing |
| **Data Processing** | pandas, numpy | Data transformation and analysis |
| **Excel** | openpyxl, xlsxwriter | Read/write/format Excel files |
| **Jira** | jira-python | API integration |
| **Config** | pyyaml, python-dotenv | Configuration management |
| **Output** | Excel, SharePoint | Report distribution |

---

## 📁 Project Structure

```
tech-control-tower/
├── 📂 config/                          # Configuration files
│   ├── config.example.yaml            # Template configuration
│   └── config.yaml                    # Your configuration (create this)
├── 📂 data/
│   ├── 📂 input/                      # Input data (Excel, CSV, Jira exports)
│   └── 📂 output/                     # Generated reports
├── 📂 docs/                           # Documentation
│   ├── SETUP_GUIDE.md                 # Detailed setup instructions
│   └── USER_GUIDE.md                  # User manual
├── 📂 src/                            # Source code
│   ├── control_tower.py               # 🎯 Main orchestrator - RUN THIS
│   ├── master_register.py             # Master Register module
│   ├── action_tracker.py              # Action Tracker module
│   ├── tpr_reporting.py               # TPR Reporting module
│   ├── governance_cadence.py          # Governance Cadence module
│   ├── jira_connector.py              # Jira integration module
│   └── create_templates.py            # Generate Excel templates
├── 📂 templates/                      # Excel templates
│   ├── master_register_template.xlsx
│   ├── action_tracker_template.xlsx
│   ├── tpr_report_template.xlsx
│   └── governance_cadence_template.xlsx
├── .env.example                       # Environment variables template
├── .gitignore                         # Git ignore rules
├── README.md                          # This file
└── requirements.txt                   # Python dependencies
```

---

## 💻 Usage Examples

### Run Full Control Tower Update
```bash
python src/control_tower.py
```
Generates all reports in one go.

### Run Individual Modules
```bash
# Master Register only
python src/master_register.py

# Action Tracker only
python src/action_tracker.py

# TPR Report only
python src/tpr_reporting.py

# Governance Cadence only
python src/governance_cadence.py

# Pull data from Jira
python src/jira_connector.py
```

### Generate Templates
```bash
python src/create_templates.py
```
Creates Excel templates with example data.

---

## 🔧 Configuration

### Jira Connection
Edit `.env`:
```env
JIRA_URL=https://your-company.atlassian.net
JIRA_USERNAME=your.email@company.com
JIRA_API_TOKEN=your_api_token
```

### TPR Areas & Meetings
Edit `config/config.yaml`:
```yaml
tpr_areas:
  - id: 1
    name: "Service Management"
    owner: "John Doe"

governance:
  meetings:
    - name: "Weekly Tech Leadership"
      frequency: "Weekly"
      day: "Monday"
      time: "10:00 AM"
      attendees: ["CIO", "Tech Leads"]
```

See [Setup Guide](docs/SETUP_GUIDE.md) for full configuration details.

---

## 📈 Roadmap

### ✅ Q1 (Apr-Jun 2026) - MVP COMPLETE
- [x] Master Register
- [x] Action Tracker
- [x] TPR Reporting Model (10 areas)
- [x] Governance Cadence
- [x] Jira Integration
- [x] Automated report generation

### 🔄 Q2 (Jul-Sep 2026) - AI Automation
- [ ] AI-assisted report summarization
- [ ] Automated action extraction from documents
- [ ] Natural language insights generation
- [ ] Smart recommendations engine

### 🚀 Q3 (Oct-Dec 2026) - AI Intelligence
- [ ] Predictive analytics for delivery and risk
- [ ] Trend analysis across all TPR areas
- [ ] Automated bottleneck detection
- [ ] AI-powered decision support

---

## 📊 Sample Output

### Executive Summary (TPR Report)
```
TPR Area              | Status | Active | Open Actions | Overdue
---------------------|--------|--------|--------------|--------
Service Management   | Green  | 5      | 3            | 0
Architecture         | Amber  | 8      | 12           | 2
Cyber Security       | Red    | 3      | 15           | 8
AWS Cost Optimisation| Green  | 2      | 1            | 0
...
```

### Action Tracker Highlights
```
Total Actions: 127
Overdue: 15
Due This Week: 23
Critical Priority: 8
```

### Governance Cadence
```
Upcoming Meetings (Next 7 Days):
- 2026-06-05: Weekly Tech Leadership at 10:00 AM
- 2026-06-07: Monthly TPR Review at 2:00 PM
```

---

## 🎓 Documentation

| Document | Description |
|----------|-------------|
| [Setup Guide](docs/SETUP_GUIDE.md) | Detailed installation and configuration |
| [User Guide](docs/USER_GUIDE.md) | Daily usage, common tasks, troubleshooting |
| [README](README.md) | This file - project overview |

---

## ✅ Features

### Current (Q1)
- ✅ Automated data collection from Jira
- ✅ Excel spreadsheet consolidation
- ✅ Master Register with full technology inventory
- ✅ Action tracking with owners and due dates
- ✅ TPR report generation across 10 areas
- ✅ RAG status indicators (Red/Amber/Green)
- ✅ Governance cadence tracking
- ✅ Overdue and critical action identification
- ✅ Executive summary generation
- ✅ Configurable meeting schedules

### Planned (Q2/Q3)
- 🔄 SharePoint integration
- 🔄 AI-assisted summarization
- 🔄 AI-generated insights and trends
- 🔄 Predictive analytics
- 🔄 Natural language queries
- 🔄 Automated recommendations

---

## 🤝 Contributing

This is an internal VFS IT project. For improvements or issues:
1. Document the issue or enhancement
2. Discuss with the Technology Team
3. Update configuration or code as needed
4. Update documentation

---

## 📞 Support

**VFS IT Technology Team**

For questions or issues:
1. Check the [User Guide](docs/USER_GUIDE.md) troubleshooting section
2. Review [Setup Guide](docs/SETUP_GUIDE.md) for configuration help
3. Contact the Technology Team

---

## 📝 License

Internal use only - VFS IT

---

## 🏆 Project Status

**Status:** ✅ Q1 MVP Complete  
**Version:** 1.0.0  
**Last Updated:** June 2026  
**Maintained by:** VFS IT Technology Team

---

**Built with ❤️ for VFS IT**
