# Technology Control Tower - User Guide

## Overview
The Technology Control Tower is a comprehensive system for managing and reporting on technology operations at VFS IT. It provides centralized visibility across all technology areas and supports data-driven decision-making at the CIO level.

## Table of Contents
1. [Getting Started](#getting-started)
2. [System Components](#system-components)
3. [Common Tasks](#common-tasks)
4. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites
- Python 3.9 or higher
- Access to Jira (optional but recommended)
- Excel/SharePoint for viewing reports

### Installation

1. **Install Dependencies**
   ```bash
   cd tech-control-tower
   pip install -r requirements.txt
   ```

2. **Configure the System**
   
   Copy the example configuration files:
   ```bash
   cp .env.example .env
   cp config/config.example.yaml config/config.yaml
   ```

3. **Set Up Jira Connection (Optional)**
   
   Edit `.env` and add your Jira credentials:
   ```
   JIRA_URL=https://your-company.atlassian.net
   JIRA_USERNAME=your.email@company.com
   JIRA_API_TOKEN=your_api_token
   ```
   
   To get a Jira API token:
   - Go to https://id.atlassian.com/manage-profile/security/api-tokens
   - Click "Create API token"
   - Copy the token to your `.env` file

4. **Customize Configuration**
   
   Edit `config/config.yaml` to match your organization:
   - Update organization details
   - Configure Jira projects to track
   - Add TPR area owners
   - Customize meeting schedules

---

## System Components

### 1. Master Register
**Purpose:** Central registry of all technology initiatives, projects, and systems

**What it tracks:**
- Initiative/project names and IDs
- Owners and status
- TPR area assignment
- Dates, budgets, and risk levels
- Source (Jira or manual entry)

**How to use:**
```bash
python src/master_register.py
```

**Outputs:**
- `data/output/master_register.xlsx` - Complete registry
- `data/output/master_register_summary.xlsx` - Summary statistics

### 2. Action Tracker
**Purpose:** Track actions, owners, due dates, and status across all TPR areas

**What it tracks:**
- Action descriptions and IDs
- Owners and due dates
- Status and priority
- TPR area assignment
- Overdue and critical actions

**How to use:**
```bash
python src/action_tracker.py
```

**Outputs:**
- `data/output/action_tracker.xlsx` - Main tracker with multiple sheets:
  - Action Tracker (all actions)
  - Overdue Actions
  - Due This Week
  - Critical Actions
- `data/output/action_tracker_summary.xlsx` - Statistics

### 3. TPR Reporting
**Purpose:** Generate Technology Performance Review reports across all 10 coverage areas

**TPR Coverage Areas:**
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

**How to use:**
```bash
python src/tpr_reporting.py
```

**Outputs:**
- `data/output/TPR_Report_[Month_Year].xlsx` - Complete TPR report with:
  - Executive Summary (all areas with RAG status)
  - Detailed sheets for each TPR area
  - Actions Summary

**RAG Status:**
- 🟢 **Green:** On track, no significant issues
- 🟡 **Amber:** Some concerns, attention needed
- 🔴 **Red:** Significant issues, immediate action required

### 4. Governance Cadence
**Purpose:** Track meeting schedules, review cycles, and governance activities

**What it tracks:**
- Meeting schedules (weekly, monthly, quarterly)
- Attendees and meeting times
- Upcoming meetings
- Meeting frequency and types

**How to use:**
```bash
python src/governance_cadence.py
```

**Outputs:**
- `data/output/governance_cadence.xlsx` - Meeting calendar with:
  - Meeting Schedule (6 months)
  - This Month
  - Next Week
  - Meeting Types

### 5. Jira Integration
**Purpose:** Automatically pull data from Jira to populate Master Register and Action Tracker

**How to use:**
```bash
python src/jira_connector.py
```

**What it does:**
- Connects to Jira using API
- Retrieves projects, epics, initiatives, and tasks
- Maps issues to TPR areas
- Exports to Excel format for processing

**Outputs:**
- `data/input/jira_data.xlsx` - Issues in Master Register format
- `data/input/jira_actions.xlsx` - Tasks in Action Tracker format

---

## Common Tasks

### Running a Complete Control Tower Update

The easiest way to update all reports:

```bash
python src/control_tower.py
```

This will:
1. Connect to Jira and pull latest data
2. Generate Master Register
3. Generate Action Tracker
4. Generate TPR Report
5. Generate Governance Cadence

All reports will be saved in `data/output/`.

### Adding Manual Data

If you don't have Jira or want to add manual entries:

1. **For Master Register:**
   - Copy `templates/master_register_template.xlsx` to `data/input/`
   - Add your initiatives/projects
   - Run `python src/master_register.py`

2. **For Action Tracker:**
   - Copy `templates/action_tracker_template.xlsx` to `data/input/`
   - Add your actions
   - Run `python src/action_tracker.py`

### Generating Only Specific Reports

Run individual modules as needed:

```bash
# Master Register only
python src/master_register.py

# Action Tracker only
python src/action_tracker.py

# TPR Report only
python src/tpr_reporting.py

# Governance Cadence only
python src/governance_cadence.py
```

### Customizing TPR Areas

Edit `config/config.yaml` and update the `tpr_areas` section:

```yaml
tpr_areas:
  - id: 1
    name: "Service Management"
    owner: "John Doe"
    description: "Service delivery, SLAs, incident management"
```

### Customizing Meeting Schedules

Edit `config/config.yaml` and update the `governance.meetings` section:

```yaml
governance:
  meetings:
    - name: "Weekly Tech Leadership"
      frequency: "Weekly"
      day: "Monday"
      time: "10:00 AM"
      attendees: ["CIO", "Tech Leads"]
```

### Viewing Reports

All reports are generated as Excel files (.xlsx) in `data/output/`:

1. Open with Microsoft Excel or Google Sheets
2. Upload to SharePoint for team access
3. Use for presentations and decision-making

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'pandas'"

**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### "Jira connection failed"

**Possible causes:**
- Invalid credentials in `.env`
- Jira URL is incorrect
- API token expired
- Network connectivity issues

**Solution:**
1. Verify credentials in `.env`
2. Test Jira access in browser
3. Generate new API token if needed
4. Check network/firewall settings

### "No data found in Master Register"

**Possible causes:**
- No input files in `data/input/`
- Jira connection not configured

**Solution:**
1. Run `python src/jira_connector.py` to pull from Jira
2. OR add manual Excel files to `data/input/`
3. OR use the templates to create sample data

### "Config file not found"

**Solution:** Copy example config
```bash
cp config/config.example.yaml config/config.yaml
```

### Empty or Missing Reports

**Check:**
1. Run with verbose logging to see errors
2. Verify input data exists in `data/input/`
3. Check file permissions on `data/output/`

### Permission Errors

**Solution:** Ensure you have write permissions
```bash
chmod -R 755 data/
```

---

## Best Practices

### Weekly Routine
1. **Monday morning:** Run full Control Tower update
2. Review Action Tracker for overdue items
3. Check upcoming meetings in Governance Cadence
4. Share reports with leadership

### Monthly Routine
1. **First Friday:** Generate TPR Report
2. Review Executive Summary
3. Identify Red/Amber areas for focus
4. Present to CIO and IT Leadership
5. Update action owners and due dates

### Data Maintenance
- Update Jira regularly with latest information
- Review and close completed actions
- Archive old reports monthly
- Keep config.yaml updated with current owners

### Tips for Success
- Automate the full update with a cron job or scheduled task
- Store reports in SharePoint for team access
- Use Excel filters and pivot tables for deeper analysis
- Customize TPR area mappings based on your Jira labels/components
- Regularly review and refine governance meeting schedules

---

## Getting Help

### Resources
- **Configuration:** See `config/config.example.yaml` for all options
- **Templates:** Check `templates/` folder for Excel examples
- **Code:** Review Python modules in `src/` for customization

### Common Questions

**Q: Can I use this without Jira?**
A: Yes! Add manual Excel files to `data/input/` and the system will process them.

**Q: How do I change the report month?**
A: Edit `config/config.yaml` and update `organization.reporting_month`

**Q: Can I add more TPR areas?**
A: Yes! Edit the `tpr_areas` section in `config/config.yaml`

**Q: How do I schedule automatic updates?**
A: Use cron (Linux/Mac) or Task Scheduler (Windows) to run `python src/control_tower.py` daily

---

## Next Steps

### Q2 Enhancements (Planned)
- AI-assisted summarization of reports
- Automated action extraction from documents
- Natural language queries

### Q3 Enhancements (Planned)
- AI-generated insights and trend analysis
- Predictive analytics for risk and delivery
- Automated bottleneck detection

For questions or support, contact the VFS IT Technology Team.
