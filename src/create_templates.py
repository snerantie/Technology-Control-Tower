"""
Create Excel templates for the Technology Control Tower
"""

import pandas as pd
from pathlib import Path
import yaml
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config():
    """Load configuration"""
    with open("config/config.example.yaml", 'r') as f:
        return yaml.safe_load(f)


def create_master_register_template():
    """Create Master Register Excel template with examples"""
    logger.info("Creating Master Register template...")
    
    config = load_config()
    columns = config['master_register']['columns']
    
    # Example data
    example_data = [
        {
            'ID': 'TECH-001',
            'Name': 'Cloud Migration Initiative',
            'Type': 'Initiative',
            'TPR Area': 'Architecture',
            'Owner': 'John Doe',
            'Status': 'In Progress',
            'Priority': 'High',
            'Start Date': '2026-01-15',
            'End Date': '2026-12-31',
            'Budget': '500000',
            'Risk Level': 'Medium',
            'Description': 'Migrate legacy applications to AWS cloud infrastructure',
            'Source': 'Manual Entry',
            'Last Updated': '2026-06-03'
        },
        {
            'ID': 'TECH-002',
            'Name': 'Security Audit Q2',
            'Type': 'Project',
            'TPR Area': 'Cyber Security',
            'Owner': 'Jane Smith',
            'Status': 'Completed',
            'Priority': 'Critical',
            'Start Date': '2026-04-01',
            'End Date': '2026-05-31',
            'Budget': '75000',
            'Risk Level': 'Low',
            'Description': 'Quarterly security audit and vulnerability remediation',
            'Source': 'Jira',
            'Last Updated': '2026-06-03'
        },
        {
            'ID': 'TECH-003',
            'Name': 'AWS Cost Optimization Review',
            'Type': 'Task',
            'TPR Area': 'AWS Cost Optimisation',
            'Owner': 'Mike Johnson',
            'Status': 'In Progress',
            'Priority': 'High',
            'Start Date': '2026-05-01',
            'End Date': '2026-07-31',
            'Budget': '0',
            'Risk Level': 'Low',
            'Description': 'Review and optimize AWS spending across all accounts',
            'Source': 'Manual Entry',
            'Last Updated': '2026-06-03'
        },
        {
            'ID': 'TECH-004',
            'Name': 'PI 2026.2 Delivery',
            'Type': 'Program Increment',
            'TPR Area': 'PI Delivery',
            'Owner': 'Sarah Lee',
            'Status': 'Planning',
            'Priority': 'High',
            'Start Date': '2026-06-01',
            'End Date': '2026-08-31',
            'Budget': '1200000',
            'Risk Level': 'Medium',
            'Description': 'Q3 Program Increment delivery across all agile teams',
            'Source': 'Jira',
            'Last Updated': '2026-06-03'
        },
        {
            'ID': 'TECH-005',
            'Name': 'Service Desk Enhancement',
            'Type': 'Project',
            'TPR Area': 'Service Management',
            'Owner': 'Tom Wilson',
            'Status': 'In Progress',
            'Priority': 'Medium',
            'Start Date': '2026-03-01',
            'End Date': '2026-09-30',
            'Budget': '150000',
            'Risk Level': 'Low',
            'Description': 'Upgrade service desk platform and improve SLA tracking',
            'Source': 'Manual Entry',
            'Last Updated': '2026-06-03'
        }
    ]
    
    df = pd.DataFrame(example_data, columns=columns)
    
    # Create templates directory
    templates_path = Path("templates")
    templates_path.mkdir(exist_ok=True)
    
    output_file = templates_path / "master_register_template.xlsx"
    
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Master Register', index=False)
        
        workbook = writer.book
        worksheet = writer.sheets['Master Register']
        
        # Formats
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#4472C4',
            'font_color': 'white',
            'border': 1
        })
        
        # Apply header format
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Set column widths
        worksheet.set_column('A:A', 12)   # ID
        worksheet.set_column('B:B', 35)   # Name
        worksheet.set_column('C:C', 18)   # Type
        worksheet.set_column('D:D', 22)   # TPR Area
        worksheet.set_column('E:E', 20)   # Owner
        worksheet.set_column('F:F', 15)   # Status
        worksheet.set_column('G:G', 12)   # Priority
        worksheet.set_column('H:I', 13)   # Dates
        worksheet.set_column('J:J', 15)   # Budget
        worksheet.set_column('K:K', 12)   # Risk Level
        worksheet.set_column('L:L', 50)   # Description
        worksheet.set_column('M:M', 15)   # Source
        worksheet.set_column('N:N', 18)   # Last Updated
    
    logger.info(f"Master Register template created: {output_file}")
    return output_file


def create_action_tracker_template():
    """Create Action Tracker Excel template"""
    logger.info("Creating Action Tracker template...")
    
    config = load_config()
    columns = config['action_tracker']['columns']
    
    # Example data
    example_data = [
        {
            'Action ID': 'ACT-001',
            'Description': 'Complete security vulnerability remediation',
            'TPR Area': 'Cyber Security',
            'Owner': 'Jane Smith',
            'Due Date': '2026-06-15',
            'Status': 'In Progress',
            'Priority': 'Critical',
            'Source': 'Audit Finding',
            'Created Date': '2026-05-20',
            'Completed Date': '',
            'Notes': 'Priority vulnerabilities identified in Q1 audit'
        },
        {
            'Action ID': 'ACT-002',
            'Description': 'Submit AWS cost optimization proposal',
            'TPR Area': 'AWS Cost Optimisation',
            'Owner': 'Mike Johnson',
            'Due Date': '2026-06-10',
            'Status': 'On Track',
            'Priority': 'High',
            'Source': 'TPR Review',
            'Created Date': '2026-05-15',
            'Completed Date': '',
            'Notes': 'Target 15% cost reduction'
        },
        {
            'Action ID': 'ACT-003',
            'Description': 'Update architecture documentation',
            'TPR Area': 'Architecture',
            'Owner': 'John Doe',
            'Due Date': '2026-06-30',
            'Status': 'Not Started',
            'Priority': 'Medium',
            'Source': 'Tech Assurance',
            'Created Date': '2026-06-01',
            'Completed Date': '',
            'Notes': 'Document cloud migration architecture decisions'
        },
        {
            'Action ID': 'ACT-004',
            'Description': 'Renew Oracle license agreement',
            'TPR Area': '3rd Party Contracts Management',
            'Owner': 'Lisa Brown',
            'Due Date': '2026-07-01',
            'Status': 'In Progress',
            'Priority': 'Critical',
            'Source': 'Contract Expiry',
            'Created Date': '2026-05-01',
            'Completed Date': '',
            'Notes': 'Contract expires July 31, negotiations underway'
        },
        {
            'Action ID': 'ACT-005',
            'Description': 'Complete PI 2026.2 sprint planning',
            'TPR Area': 'PI Delivery',
            'Owner': 'Sarah Lee',
            'Status': 'Completed',
            'Due Date': '2026-05-31',
            'Priority': 'High',
            'Source': 'Agile Process',
            'Created Date': '2026-05-15',
            'Completed Date': '2026-05-30',
            'Notes': 'All teams completed sprint planning for Q3'
        }
    ]
    
    df = pd.DataFrame(example_data, columns=columns)
    
    templates_path = Path("templates")
    templates_path.mkdir(exist_ok=True)
    
    output_file = templates_path / "action_tracker_template.xlsx"
    
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Action Tracker', index=False)
        
        workbook = writer.book
        worksheet = writer.sheets['Action Tracker']
        
        # Formats
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#70AD47',
            'font_color': 'white',
            'border': 1
        })
        
        # Apply header format
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Set column widths
        worksheet.set_column('A:A', 12)   # Action ID
        worksheet.set_column('B:B', 45)   # Description
        worksheet.set_column('C:C', 22)   # TPR Area
        worksheet.set_column('D:D', 20)   # Owner
        worksheet.set_column('E:E', 13)   # Due Date
        worksheet.set_column('F:F', 15)   # Status
        worksheet.set_column('G:G', 12)   # Priority
        worksheet.set_column('H:H', 18)   # Source
        worksheet.set_column('I:J', 13)   # Dates
        worksheet.set_column('K:K', 40)   # Notes
    
    logger.info(f"Action Tracker template created: {output_file}")
    return output_file


def create_tpr_report_template():
    """Create TPR Report Excel template"""
    logger.info("Creating TPR Report template...")
    
    config = load_config()
    tpr_areas = config['tpr_areas']
    
    templates_path = Path("templates")
    templates_path.mkdir(exist_ok=True)
    
    output_file = templates_path / "tpr_report_template.xlsx"
    
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Create Executive Summary sheet
        summary_data = {
            'TPR Area': [area['name'] for area in tpr_areas],
            'Status': ['Green'] * len(tpr_areas),
            'Key Highlights': [''] * len(tpr_areas),
            'Key Risks': [''] * len(tpr_areas),
            'Actions Required': [0] * len(tpr_areas)
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Executive Summary', index=False)
        
        # Format Executive Summary
        worksheet = writer.sheets['Executive Summary']
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#C00000',
            'font_color': 'white',
            'border': 1
        })
        
        for col_num, value in enumerate(summary_df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 12)
        worksheet.set_column('C:D', 40)
        worksheet.set_column('E:E', 15)
        
        # Create a sheet for each TPR area
        for area in tpr_areas:
            area_name = area['name']
            area_data = {
                'Metric': ['Active Initiatives', 'Completed This Month', 'At Risk', 'Budget Utilization', 'Key Performance Indicator'],
                'Value': ['', '', '', '', ''],
                'Target': ['', '', '', '', ''],
                'Status': ['', '', '', '', '']
            }
            area_df = pd.DataFrame(area_data)
            
            # Truncate sheet name if too long (Excel limit is 31 chars)
            sheet_name = area_name[:31]
            area_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Format area sheet
            worksheet = writer.sheets[sheet_name]
            for col_num, value in enumerate(area_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            worksheet.set_column('A:A', 30)
            worksheet.set_column('B:D', 20)
    
    logger.info(f"TPR Report template created: {output_file}")
    return output_file


def create_governance_template():
    """Create Governance Cadence tracking template"""
    logger.info("Creating Governance Cadence template...")
    
    config = load_config()
    meetings = config['governance']['meetings']
    
    # Meeting schedule data
    meeting_data = []
    for meeting in meetings:
        meeting_data.append({
            'Meeting Name': meeting['name'],
            'Frequency': meeting['frequency'],
            'Day': meeting['day'],
            'Time': meeting['time'],
            'Attendees': ', '.join(meeting['attendees']),
            'Next Meeting': '',
            'Status': 'Scheduled'
        })
    
    df = pd.DataFrame(meeting_data)
    
    templates_path = Path("templates")
    templates_path.mkdir(exist_ok=True)
    
    output_file = templates_path / "governance_cadence_template.xlsx"
    
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Meeting Schedule', index=False)
        
        workbook = writer.book
        worksheet = writer.sheets['Meeting Schedule']
        
        # Formats
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#FFC000',
            'font_color': 'black',
            'border': 1
        })
        
        # Apply header format
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Set column widths
        worksheet.set_column('A:A', 25)   # Meeting Name
        worksheet.set_column('B:B', 15)   # Frequency
        worksheet.set_column('C:C', 18)   # Day
        worksheet.set_column('D:D', 12)   # Time
        worksheet.set_column('E:E', 35)   # Attendees
        worksheet.set_column('F:F', 15)   # Next Meeting
        worksheet.set_column('G:G', 12)   # Status
    
    logger.info(f"Governance Cadence template created: {output_file}")
    return output_file


def main():
    """Create all templates"""
    logger.info("=" * 60)
    logger.info("Creating Technology Control Tower Templates")
    logger.info("=" * 60)
    
    create_master_register_template()
    create_action_tracker_template()
    create_tpr_report_template()
    create_governance_template()
    
    logger.info("\n" + "=" * 60)
    logger.info("All templates created successfully!")
    logger.info("=" * 60)
    logger.info("\nTemplates available in: ./templates/")
    logger.info("  - master_register_template.xlsx")
    logger.info("  - action_tracker_template.xlsx")
    logger.info("  - tpr_report_template.xlsx")
    logger.info("  - governance_cadence_template.xlsx")


if __name__ == "__main__":
    main()
