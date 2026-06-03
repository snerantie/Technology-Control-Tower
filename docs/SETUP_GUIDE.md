# Technology Control Tower - Setup Guide

## Quick Start (5 Minutes)

### Step 1: Install Python Dependencies
```bash
cd tech-control-tower
pip install -r requirements.txt
```

### Step 2: Create Configuration Files
```bash
# Copy example files
cp .env.example .env
cp config/config.example.yaml config/config.yaml
```

### Step 3: Test the System
```bash
# Generate sample templates
python src/create_templates.py

# Run a test update (will work without Jira)
python src/control_tower.py
```

That's it! Check `data/output/` for generated reports.

---

## Full Setup

### 1. System Requirements

**Software:**
- Python 3.9 or higher
- pip (Python package manager)
- Excel or LibreOffice (for viewing reports)

**Optional:**
- Jira account with API access
- SharePoint for report storage

**Operating Systems:**
- Linux
- macOS
- Windows

### 2. Installation

#### Clone or Download
```bash
# If using git
git clone <repository-url>
cd tech-control-tower

# Or download and extract the ZIP file
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

**Dependencies installed:**
- pandas - Data processing
- openpyxl - Excel file handling
- xlsxwriter - Excel formatting
- jira - Jira API client
- pyyaml - Configuration files
- python-dotenv - Environment variables

### 3. Configuration

#### A. Environment Variables (.env)

Create `.env` file from template:
```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Jira Configuration (Optional)
JIRA_URL=https://your-company.atlassian.net
JIRA_USERNAME=your.email@company.com
JIRA_API_TOKEN=your_jira_api_token

# Data Paths
INPUT_DATA_PATH=./data/input
OUTPUT_DATA_PATH=./data/output

# Organization
ORGANIZATION_NAME=VFS IT
REPORT_FREQUENCY=monthly
```

**Getting a Jira API Token:**
1. Log into Jira
2. Go to https://id.atlassian.com/manage-profile/security/api-tokens
3. Click "Create API token"
4. Name it "Control Tower"
5. Copy the token
6. Paste into `.env` file

**Security Note:** Never commit `.env` to version control!

#### B. System Configuration (config.yaml)

Create `config/config.yaml` from template:
```bash
cp config/config.example.yaml config/config.yaml
```

**Key Configuration Sections:**

##### Organization Details
```yaml
organization:
  name: "VFS IT"
  cio: "CIO Name"
  reporting_month: "June 2026"
```

##### Jira Connection
```yaml
jira:
  url: "https://your-company.atlassian.net"
  projects:
    - "TECH"      # Your project keys
    - "INFRA"
    - "SEC"
  issue_types:
    - "Epic"
    - "Story"
    - "Task"
    - "Initiative"
```

##### Data Sources
```yaml
data_sources:
  input_path: "./data/input"
  output_path: "./data/output"
  excel_files:
    - "service_management.xlsx"
    - "architecture.xlsx"
    # Add your input files here
```

##### TPR Areas
```yaml
tpr_areas:
  - id: 1
    name: "Service Management"
    owner: "John Doe"           # Add actual owner
    description: "Service delivery, SLAs"
  - id: 2
    name: "Architecture"
    owner: "Jane Smith"
    description: "Enterprise architecture"
  # ... (10 areas total)
```

##### Governance Meetings
```yaml
governance:
  meetings:
    - name: "Weekly Tech Leadership"
      frequency: "Weekly"
      day: "Monday"
      time: "10:00 AM"
      attendees: ["CIO", "Tech Leads"]
    - name: "Monthly TPR Review"
      frequency: "Monthly"
      day: "First Friday"
      time: "2:00 PM"
      attendees: ["CIO", "IT Leadership"]
```

### 4. Directory Structure

Ensure directories exist:
```bash
mkdir -p data/input
mkdir -p data/output
mkdir -p templates
```

**Directory Layout:**
```
tech-control-tower/
├── config/
│   ├── config.example.yaml
│   └── config.yaml              # Your config
├── data/
│   ├── input/                   # Place input Excel files here
│   └── output/                  # Generated reports go here
├── docs/
│   ├── SETUP_GUIDE.md
│   └── USER_GUIDE.md
├── src/
│   ├── control_tower.py         # Main orchestrator
│   ├── master_register.py
│   ├── action_tracker.py
│   ├── tpr_reporting.py
│   ├── governance_cadence.py
│   └── jira_connector.py
├── templates/
│   ├── master_register_template.xlsx
│   ├── action_tracker_template.xlsx
│   ├── tpr_report_template.xlsx
│   └── governance_cadence_template.xlsx
├── .env                         # Your environment variables
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

### 5. Testing the Installation

#### Test 1: Generate Templates
```bash
python src/create_templates.py
```

Expected output:
- 4 Excel templates created in `templates/`

#### Test 2: Run Individual Modules

**Master Register:**
```bash
python src/master_register.py
```
Expected: Empty template created in `data/output/`

**Action Tracker:**
```bash
python src/action_tracker.py
```
Expected: Empty template created in `data/output/`

**Governance Cadence:**
```bash
python src/governance_cadence.py
```
Expected: Meeting schedule created in `data/output/`

#### Test 3: Test Jira Connection (Optional)
```bash
python src/jira_connector.py
```

Expected output:
- Connection success message
- Data exported to `data/input/`

If this fails, the system will still work with manual data entry.

#### Test 4: Full System Test
```bash
python src/control_tower.py
```

Expected output:
- All modules execute
- Reports generated in `data/output/`
- Summary statistics displayed

### 6. Initial Data Setup

#### Option A: Using Jira (Recommended)

1. Configure Jira credentials in `.env`
2. Add your project keys to `config/config.yaml`
3. Run Jira connector:
   ```bash
   python src/jira_connector.py
   ```
4. Verify data in `data/input/`

#### Option B: Manual Data Entry

1. Copy templates to input directory:
   ```bash
   cp templates/master_register_template.xlsx data/input/
   cp templates/action_tracker_template.xlsx data/input/
   ```

2. Edit the files in Excel:
   - Add your initiatives/projects
   - Add your actions
   - Save files

3. Run the system:
   ```bash
   python src/control_tower.py
   ```

### 7. Customization

#### Customize TPR Area Mapping

Edit `src/jira_connector.py` to map your Jira labels/components to TPR areas:

```python
def _map_to_tpr_area(self, issue) -> str:
    tpr_mapping = {
        'architecture': 'Architecture',
        'security': 'Cyber Security',
        'cost': 'AWS Cost Optimisation',
        # Add your mappings here
    }
    # ... mapping logic
```

#### Customize Report Formatting

Each module has export functions you can customize:
- `master_register.py` - Line 260+
- `action_tracker.py` - Line 250+
- `tpr_reporting.py` - Line 200+

#### Customize Meeting Schedules

Edit `config/config.yaml`:
```yaml
governance:
  meetings:
    - name: "Your Meeting Name"
      frequency: "Weekly|Monthly|Quarterly"
      day: "Monday" or "First Friday"
      time: "10:00 AM"
      attendees: ["List", "Of", "Attendees"]
```

### 8. Automation (Optional)

#### Linux/Mac - Using Cron

Edit crontab:
```bash
crontab -e
```

Add daily update at 6 AM:
```
0 6 * * * cd /path/to/tech-control-tower && /usr/bin/python3 src/control_tower.py >> logs/control_tower.log 2>&1
```

#### Windows - Using Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Name: "Control Tower Update"
4. Trigger: Daily at 6:00 AM
5. Action: Start a Program
   - Program: `C:\Python39\python.exe`
   - Arguments: `src\control_tower.py`
   - Start in: `C:\path\to\tech-control-tower`

### 9. SharePoint Integration (Optional)

#### Manual Upload
1. Run Control Tower update
2. Navigate to `data/output/`
3. Upload Excel files to SharePoint document library

#### Automated Upload (Advanced)
Use SharePoint API or PowerShell scripts to automate uploads:

```python
# Example using Office365-REST-Python-Client
from office365.sharepoint.client_context import ClientContext
# ... implement upload logic
```

### 10. Troubleshooting Setup

#### Problem: "pip: command not found"
**Solution:** Install pip
```bash
# Mac/Linux
python3 -m ensurepip

# Windows
python -m ensurepip
```

#### Problem: "Permission denied" when creating directories
**Solution:** Create with sudo or adjust permissions
```bash
sudo mkdir -p data/input data/output
chmod -R 755 data/
```

#### Problem: "Module not found" errors
**Solution:** Ensure you're in the right directory and dependencies are installed
```bash
cd tech-control-tower
pip install -r requirements.txt
```

#### Problem: Jira connection times out
**Solution:** Check network/firewall settings
```bash
# Test connectivity
curl https://your-company.atlassian.net

# May need to configure proxy
export HTTPS_PROXY=http://proxy:port
```

#### Problem: Excel files won't open
**Solution:** Install openpyxl
```bash
pip install openpyxl xlsxwriter
```

---

## Post-Setup Checklist

- [ ] Python 3.9+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created and configured
- [ ] `config/config.yaml` created and customized
- [ ] Directories created (`data/input`, `data/output`)
- [ ] Templates generated (`python src/create_templates.py`)
- [ ] Jira connection tested (if using Jira)
- [ ] Full system test passed (`python src/control_tower.py`)
- [ ] Reports accessible in `data/output/`
- [ ] TPR area owners updated in config
- [ ] Meeting schedules customized
- [ ] (Optional) Automation configured

---

## Next Steps

1. Read the [User Guide](USER_GUIDE.md) for daily usage
2. Run your first full update
3. Review generated reports
4. Customize configurations as needed
5. Set up automation for regular updates
6. Share reports with your team

## Support

For setup issues:
1. Check troubleshooting section above
2. Review error messages in console
3. Verify configuration files
4. Test individual modules
5. Contact VFS IT Technology Team

---

## Advanced Setup

### Multiple Environments

Create separate config files for dev/test/prod:

```bash
config/
├── config.dev.yaml
├── config.test.yaml
└── config.prod.yaml
```

Run with specific config:
```bash
# Modify scripts to accept config parameter
python src/control_tower.py --config config/config.prod.yaml
```

### Virtual Environment (Recommended)

Use virtual environment to isolate dependencies:

```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Deactivate when done
deactivate
```

### Docker Deployment (Advanced)

Create `Dockerfile`:
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/control_tower.py"]
```

Build and run:
```bash
docker build -t control-tower .
docker run -v $(pwd)/data:/app/data control-tower
```

---

Setup complete! You're ready to use the Technology Control Tower. 🚀
