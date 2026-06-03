# Technology Control Tower - Quick Reference

## 🚀 Common Commands

### Run Everything
```bash
python src/control_tower.py
```
**Output:** All reports in `data/output/`

### Individual Reports
```bash
python src/master_register.py        # Master Register
python src/action_tracker.py         # Action Tracker
python src/tpr_reporting.py          # TPR Report
python src/governance_cadence.py     # Governance Calendar
python src/jira_connector.py         # Pull from Jira
python src/create_templates.py       # Generate templates
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `.env` | Jira credentials, API tokens |
| `config/config.yaml` | TPR areas, meetings, settings |
| `data/input/` | Place input Excel files here |
| `data/output/` | Generated reports appear here |
| `templates/` | Excel templates with examples |

---

## 🔧 Configuration Files

### .env (Credentials)
```env
JIRA_URL=https://your-company.atlassian.net
JIRA_USERNAME=your.email@company.com
JIRA_API_TOKEN=your_jira_api_token
```

### config/config.yaml (Settings)
```yaml
organization:
  name: "VFS IT"
  cio: "CIO Name"
  reporting_month: "June 2026"

jira:
  projects: ["TECH", "INFRA", "SEC"]

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
```

---

## 📊 Output Files

| File | Description |
|------|-------------|
| `master_register.xlsx` | All initiatives & projects |
| `master_register_summary.xlsx` | Statistics |
| `action_tracker.xlsx` | All actions (multiple sheets) |
| `action_tracker_summary.xlsx` | Action statistics |
| `TPR_Report_[Month].xlsx` | Full TPR report with Executive Summary |
| `governance_cadence.xlsx` | Meeting calendar (6 months) |

---

## 🎯 TPR Areas (10)

1. Service Management
2. Architecture  
3. Risk Management
4. PI Delivery
5. Tech Assurance
6. AWS Cost Optimisation
7. Cyber Security
8. Audits
9. Resource Strategy
10. 3rd Party Contracts Management

---

## 🚦 RAG Status

- 🟢 **Green** - On track, no issues
- 🟡 **Amber** - Some concerns, attention needed  
- 🔴 **Red** - Significant issues, immediate action required

**Auto-calculated based on:**
- Overdue actions (>5 = Red, >2 = Amber)
- High-risk initiatives (>3 = Red, >1 = Amber)
- Critical actions (>5 = Red, >2 = Amber)

---

## ⚡ Quick Setup (First Time)

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
cp config/config.example.yaml config/config.yaml
# Edit both files with your details

# 3. Run
python src/control_tower.py
```

---

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Module not found" | `pip install -r requirements.txt` |
| "Jira failed" | Check `.env` credentials |
| "No data" | Add Excel files to `data/input/` |
| "Config not found" | `cp config/config.example.yaml config/config.yaml` |
| "Permission denied" | `chmod -R 755 data/` |

---

## 📅 Recommended Schedule

### Daily
- No action needed (if automated)

### Weekly (Monday)
```bash
python src/control_tower.py
```
- Review Action Tracker (overdue items)
- Check Governance Cadence (upcoming meetings)

### Monthly (First Friday)
```bash
python src/tpr_reporting.py
```
- Generate TPR Report
- Review Executive Summary
- Present to CIO / IT Leadership
- Update action owners

---

## 🎓 Getting Help

1. **Setup issues?** → [Setup Guide](docs/SETUP_GUIDE.md)
2. **Usage questions?** → [User Guide](docs/USER_GUIDE.md)
3. **Need examples?** → Check `templates/` folder
4. **Still stuck?** → Contact VFS IT Technology Team

---

## 💡 Pro Tips

- **Automate it:** Set up cron job / Task Scheduler for daily updates
- **SharePoint:** Upload reports to SharePoint for team access
- **Filters:** Use Excel filters on reports for detailed analysis
- **Customize:** Edit `config.yaml` for your specific needs
- **Templates:** Use `create_templates.py` to see examples
- **Jira mapping:** Customize TPR area mapping in `jira_connector.py`

---

## 🔗 Quick Links

- [📖 Full Documentation](docs/USER_GUIDE.md)
- [🛠️ Setup Guide](docs/SETUP_GUIDE.md)
- [📝 README](README.md)

---

## 📞 Contact

**VFS IT Technology Team**

---

**Last Updated:** June 2026  
**Version:** 1.0.0 (Q1 MVP)
