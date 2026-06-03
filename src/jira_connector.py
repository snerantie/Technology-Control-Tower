"""
Jira Integration Module
Connects to Jira to pull projects, initiatives, issues, and actions
"""

from jira import JIRA
import pandas as pd
from datetime import datetime
from pathlib import Path
import yaml
import os
from typing import List, Dict, Optional
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class JiraConnector:
    """Handles connection and data extraction from Jira"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize Jira connector with configuration"""
        self.config = self._load_config(config_path)
        self.jira_client = None
        self.connected = False
        
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            example_path = "config/config.example.yaml"
            logger.warning(f"{config_path} not found, using {example_path}")
            with open(example_path, 'r') as f:
                return yaml.safe_load(f)
    
    def connect(self) -> bool:
        """Connect to Jira using credentials from environment variables"""
        try:
            jira_url = os.getenv('JIRA_URL', self.config['jira']['url'])
            jira_username = os.getenv('JIRA_USERNAME')
            jira_token = os.getenv('JIRA_API_TOKEN')
            
            if not jira_username or not jira_token:
                logger.error("Jira credentials not found in environment variables")
                logger.info("Please set JIRA_USERNAME and JIRA_API_TOKEN in .env file")
                return False
            
            logger.info(f"Connecting to Jira: {jira_url}")
            
            self.jira_client = JIRA(
                server=jira_url,
                basic_auth=(jira_username, jira_token)
            )
            
            # Test connection
            user = self.jira_client.current_user()
            logger.info(f"Successfully connected to Jira as: {user}")
            self.connected = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Jira: {e}")
            self.connected = False
            return False
    
    def get_projects(self, project_keys: Optional[List[str]] = None) -> List[Dict]:
        """Get list of projects from Jira"""
        if not self.connected:
            logger.error("Not connected to Jira. Call connect() first.")
            return []
        
        try:
            if project_keys is None:
                project_keys = self.config['jira'].get('projects', [])
            
            projects = []
            for project in self.jira_client.projects():
                if not project_keys or project.key in project_keys:
                    projects.append({
                        'key': project.key,
                        'name': project.name,
                        'lead': getattr(project.lead, 'displayName', 'Unknown')
                    })
            
            logger.info(f"Retrieved {len(projects)} projects from Jira")
            return projects
            
        except Exception as e:
            logger.error(f"Error fetching projects: {e}")
            return []
    
    def get_issues(self, jql: Optional[str] = None, max_results: int = 100) -> List[Dict]:
        """Get issues from Jira using JQL query"""
        if not self.connected:
            logger.error("Not connected to Jira. Call connect() first.")
            return []
        
        try:
            # Default JQL if none provided
            if jql is None:
                project_keys = self.config['jira'].get('projects', [])
                issue_types = self.config['jira'].get('issue_types', [])
                
                if project_keys:
                    projects_str = ', '.join(project_keys)
                    jql = f"project in ({projects_str})"
                else:
                    jql = "project is not EMPTY"
                
                if issue_types:
                    types_str = ', '.join([f'"{t}"' for t in issue_types])
                    jql += f" AND issuetype in ({types_str})"
            
            logger.info(f"Fetching issues with JQL: {jql}")
            issues = self.jira_client.search_issues(jql, maxResults=max_results)
            
            parsed_issues = []
            for issue in issues:
                parsed_issues.append(self._parse_issue(issue))
            
            logger.info(f"Retrieved {len(parsed_issues)} issues from Jira")
            return parsed_issues
            
        except Exception as e:
            logger.error(f"Error fetching issues: {e}")
            return []
    
    def _parse_issue(self, issue) -> Dict:
        """Parse a Jira issue into a dictionary"""
        try:
            # Extract basic fields
            data = {
                'ID': issue.key,
                'Name': issue.fields.summary,
                'Type': issue.fields.issuetype.name,
                'Status': issue.fields.status.name,
                'Priority': getattr(issue.fields.priority, 'name', 'Medium'),
                'Owner': getattr(issue.fields.assignee, 'displayName', 'Unassigned'),
                'Description': getattr(issue.fields, 'description', ''),
                'Created Date': issue.fields.created,
                'Updated Date': issue.fields.updated,
                'Source': 'Jira'
            }
            
            # Extract custom fields if available
            if hasattr(issue.fields, 'duedate'):
                data['Due Date'] = issue.fields.duedate
            
            if hasattr(issue.fields, 'components') and issue.fields.components:
                data['Component'] = ', '.join([c.name for c in issue.fields.components])
            
            if hasattr(issue.fields, 'labels') and issue.fields.labels:
                data['Labels'] = ', '.join(issue.fields.labels)
            
            # Try to map to TPR area based on labels or components
            data['TPR Area'] = self._map_to_tpr_area(issue)
            
            return data
            
        except Exception as e:
            logger.error(f"Error parsing issue {issue.key}: {e}")
            return {}
    
    def _map_to_tpr_area(self, issue) -> str:
        """Map Jira issue to TPR area based on labels, components, or project"""
        # Mapping logic - customize based on your Jira setup
        tpr_mapping = {
            'architecture': 'Architecture',
            'security': 'Cyber Security',
            'cost': 'AWS Cost Optimisation',
            'audit': 'Audits',
            'service': 'Service Management',
            'risk': 'Risk Management',
            'delivery': 'PI Delivery',
            'contract': '3rd Party Contracts Management',
            'resource': 'Resource Strategy',
            'assurance': 'Tech Assurance'
        }
        
        # Check labels
        if hasattr(issue.fields, 'labels') and issue.fields.labels:
            for label in issue.fields.labels:
                label_lower = label.lower()
                for key, tpr_area in tpr_mapping.items():
                    if key in label_lower:
                        return tpr_area
        
        # Check components
        if hasattr(issue.fields, 'components') and issue.fields.components:
            for component in issue.fields.components:
                component_lower = component.name.lower()
                for key, tpr_area in tpr_mapping.items():
                    if key in component_lower:
                        return tpr_area
        
        # Check issue type
        issue_type = issue.fields.issuetype.name.lower()
        if 'epic' in issue_type or 'initiative' in issue_type:
            return 'PI Delivery'
        
        # Default
        return 'Service Management'
    
    def get_epics(self, project_keys: Optional[List[str]] = None) -> List[Dict]:
        """Get all epics from specified projects"""
        if project_keys is None:
            project_keys = self.config['jira'].get('projects', [])
        
        projects_str = ', '.join(project_keys)
        jql = f"project in ({projects_str}) AND issuetype = Epic"
        
        return self.get_issues(jql=jql)
    
    def get_initiatives(self, project_keys: Optional[List[str]] = None) -> List[Dict]:
        """Get all initiatives from specified projects"""
        if project_keys is None:
            project_keys = self.config['jira'].get('projects', [])
        
        projects_str = ', '.join(project_keys)
        jql = f"project in ({projects_str}) AND issuetype = Initiative"
        
        return self.get_issues(jql=jql)
    
    def get_open_actions(self, max_results: int = 100) -> List[Dict]:
        """Get open actions/tasks from Jira"""
        project_keys = self.config['jira'].get('projects', [])
        projects_str = ', '.join(project_keys)
        
        jql = f"project in ({projects_str}) AND issuetype = Task AND status != Done AND status != Closed"
        
        issues = self.get_issues(jql=jql, max_results=max_results)
        
        # Convert to action tracker format
        actions = []
        for issue in issues:
            action = {
                'Action ID': issue.get('ID'),
                'Description': issue.get('Name'),
                'TPR Area': issue.get('TPR Area'),
                'Owner': issue.get('Owner'),
                'Due Date': issue.get('Due Date', ''),
                'Status': issue.get('Status'),
                'Priority': issue.get('Priority'),
                'Source': 'Jira',
                'Created Date': issue.get('Created Date', ''),
                'Completed Date': '',
                'Notes': issue.get('Component', '')
            }
            actions.append(action)
        
        return actions
    
    def export_to_master_register(self, output_path: str = "data/input/jira_data.xlsx") -> str:
        """Export Jira data in Master Register format"""
        if not self.connected:
            logger.error("Not connected to Jira")
            return None
        
        try:
            # Get all issues
            all_issues = self.get_issues(max_results=500)
            
            if not all_issues:
                logger.warning("No issues retrieved from Jira")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(all_issues)
            
            # Map to Master Register columns
            master_register_columns = [
                'ID', 'Name', 'Type', 'TPR Area', 'Owner', 'Status', 
                'Priority', 'Start Date', 'End Date', 'Budget', 'Risk Level',
                'Description', 'Source', 'Last Updated'
            ]
            
            # Add missing columns
            for col in master_register_columns:
                if col not in df.columns:
                    if col == 'Start Date':
                        df[col] = df.get('Created Date', '')
                    elif col == 'End Date':
                        df[col] = df.get('Due Date', '')
                    elif col == 'Budget':
                        df[col] = 0
                    elif col == 'Risk Level':
                        # Map priority to risk level
                        priority_risk_map = {
                            'Critical': 'High',
                            'High': 'High',
                            'Medium': 'Medium',
                            'Low': 'Low'
                        }
                        df[col] = df.get('Priority', 'Medium').map(priority_risk_map).fillna('Medium')
                    elif col == 'Last Updated':
                        df[col] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        df[col] = ''
            
            # Select only Master Register columns
            df = df[master_register_columns]
            
            # Export to Excel
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            df.to_excel(output_file, sheet_name='Jira Data', index=False)
            logger.info(f"Exported {len(df)} issues to {output_file}")
            
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error exporting to Master Register: {e}")
            return None
    
    def export_actions(self, output_path: str = "data/input/jira_actions.xlsx") -> str:
        """Export Jira actions in Action Tracker format"""
        if not self.connected:
            logger.error("Not connected to Jira")
            return None
        
        try:
            actions = self.get_open_actions(max_results=500)
            
            if not actions:
                logger.warning("No actions retrieved from Jira")
                return None
            
            df = pd.DataFrame(actions)
            
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            df.to_excel(output_file, sheet_name='Jira Actions', index=False)
            logger.info(f"Exported {len(df)} actions to {output_file}")
            
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error exporting actions: {e}")
            return None
    
    def run(self) -> None:
        """Main execution: Connect to Jira and export data"""
        logger.info("=" * 60)
        logger.info("Technology Control Tower - Jira Connector")
        logger.info("=" * 60)
        
        # Connect to Jira
        if not self.connect():
            logger.error("Failed to connect to Jira. Please check credentials.")
            logger.info("\nTo configure Jira connection:")
            logger.info("1. Copy .env.example to .env")
            logger.info("2. Set JIRA_URL, JIRA_USERNAME, and JIRA_API_TOKEN")
            logger.info("3. Run this script again")
            return
        
        # Export data
        logger.info("\nExporting Jira data...")
        
        master_register_file = self.export_to_master_register()
        if master_register_file:
            logger.info(f"✓ Master Register data: {master_register_file}")
        
        actions_file = self.export_actions()
        if actions_file:
            logger.info(f"✓ Action Tracker data: {actions_file}")
        
        # Get summary statistics
        projects = self.get_projects()
        logger.info(f"\nProjects tracked: {len(projects)}")
        for project in projects:
            logger.info(f"  - {project['key']}: {project['name']}")
        
        logger.info("\n" + "=" * 60)
        logger.info("Jira data extraction complete!")
        logger.info("=" * 60)


if __name__ == "__main__":
    connector = JiraConnector()
    connector.run()
