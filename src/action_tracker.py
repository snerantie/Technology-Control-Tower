"""
Action Tracker Module
Track actions, owners, due dates, and status across all TPR areas
"""

import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import yaml
import os
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ActionTracker:
    """Manages tracking of actions across all technology areas"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize Action Tracker with configuration"""
        self.config = self._load_config(config_path)
        self.actions_data = pd.DataFrame()
        self.input_path = Path(self.config['data_sources']['input_path'])
        self.output_path = Path(self.config['data_sources']['output_path'])
        
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
    
    def create_empty_tracker(self) -> pd.DataFrame:
        """Create an empty tracker with standard columns"""
        columns = self.config['action_tracker']['columns']
        return pd.DataFrame(columns=columns)
    
    def load_from_excel(self, filepath: str) -> pd.DataFrame:
        """Load actions from an Excel file"""
        try:
            logger.info(f"Loading actions from {filepath}")
            df = pd.read_excel(filepath)
            logger.info(f"Loaded {len(df)} actions from {filepath}")
            return df
        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
            return pd.DataFrame()
    
    def consolidate_sources(self) -> pd.DataFrame:
        """Consolidate actions from all sources"""
        all_actions = []
        
        # Load from Jira export
        jira_file = self.input_path / "jira_actions.xlsx"
        if jira_file.exists():
            df = self.load_from_excel(str(jira_file))
            if not df.empty:
                all_actions.append(df)
        
        # Load from manual Excel files
        for excel_file in self.input_path.glob("*action*.xlsx"):
            if excel_file.name != "jira_actions.xlsx":
                df = self.load_from_excel(str(excel_file))
                if not df.empty:
                    all_actions.append(df)
        
        if all_actions:
            combined = pd.concat(all_actions, ignore_index=True)
            # Remove duplicates based on Action ID
            if 'Action ID' in combined.columns:
                combined = combined.drop_duplicates(subset=['Action ID'], keep='last')
            logger.info(f"Consolidated {len(combined)} total actions from {len(all_actions)} sources")
            return combined
        else:
            logger.warning("No actions found. Creating empty tracker.")
            return self.create_empty_tracker()
    
    def add_action(self, action_data: Dict) -> None:
        """Add a single action to the tracker"""
        required_columns = self.config['action_tracker']['columns']
        
        # Ensure all required columns exist
        for col in required_columns:
            if col not in action_data:
                if col == 'Created Date':
                    action_data[col] = datetime.now().strftime('%Y-%m-%d')
                elif col == 'Status':
                    action_data[col] = 'Not Started'
                elif col == 'Priority':
                    action_data[col] = 'Medium'
                else:
                    action_data[col] = ''
        
        # Generate Action ID if not provided
        if not action_data.get('Action ID'):
            action_data['Action ID'] = self._generate_action_id()
        
        new_row = pd.DataFrame([action_data])
        self.actions_data = pd.concat([self.actions_data, new_row], ignore_index=True)
        logger.info(f"Added action: {action_data.get('Action ID')}")
    
    def _generate_action_id(self) -> str:
        """Generate a unique action ID"""
        # Count existing actions
        if 'Action ID' in self.actions_data.columns and not self.actions_data.empty:
            existing_ids = self.actions_data['Action ID'].tolist()
            # Extract numbers from existing IDs
            numbers = []
            for aid in existing_ids:
                if isinstance(aid, str) and aid.startswith('ACT-'):
                    try:
                        numbers.append(int(aid.split('-')[1]))
                    except:
                        pass
            
            if numbers:
                next_num = max(numbers) + 1
            else:
                next_num = 1
        else:
            next_num = 1
        
        return f"ACT-{next_num:03d}"
    
    def update_action(self, action_id: str, updates: Dict) -> bool:
        """Update an existing action"""
        if 'Action ID' not in self.actions_data.columns:
            logger.error("Action Tracker does not have Action ID column")
            return False
        
        mask = self.actions_data['Action ID'] == action_id
        if mask.any():
            for key, value in updates.items():
                self.actions_data.loc[mask, key] = value
            logger.info(f"Updated action: {action_id}")
            return True
        else:
            logger.warning(f"Action not found: {action_id}")
            return False
    
    def complete_action(self, action_id: str) -> bool:
        """Mark an action as completed"""
        updates = {
            'Status': 'Completed',
            'Completed Date': datetime.now().strftime('%Y-%m-%d')
        }
        return self.update_action(action_id, updates)
    
    def get_overdue_actions(self) -> pd.DataFrame:
        """Get all overdue actions"""
        if self.actions_data.empty or 'Due Date' not in self.actions_data.columns:
            return pd.DataFrame()
        
        today = datetime.now()
        
        # Filter actions with due dates
        df = self.actions_data.copy()
        df = df[df['Due Date'].notna() & (df['Due Date'] != '')]
        
        # Convert Due Date to datetime
        df['Due Date'] = pd.to_datetime(df['Due Date'], errors='coerce')
        
        # Filter overdue and not completed
        overdue = df[
            (df['Due Date'] < today) & 
            (df['Status'] != 'Completed') & 
            (df['Status'] != 'Closed')
        ]
        
        logger.info(f"Found {len(overdue)} overdue actions")
        return overdue
    
    def get_actions_by_tpr_area(self, tpr_area: str) -> pd.DataFrame:
        """Get all actions for a specific TPR area"""
        if 'TPR Area' not in self.actions_data.columns:
            logger.warning("TPR Area column not found")
            return pd.DataFrame()
        
        filtered = self.actions_data[self.actions_data['TPR Area'] == tpr_area]
        logger.info(f"Found {len(filtered)} actions for TPR Area: {tpr_area}")
        return filtered
    
    def get_actions_by_owner(self, owner: str) -> pd.DataFrame:
        """Get all actions for a specific owner"""
        if 'Owner' not in self.actions_data.columns:
            logger.warning("Owner column not found")
            return pd.DataFrame()
        
        filtered = self.actions_data[self.actions_data['Owner'] == owner]
        logger.info(f"Found {len(filtered)} actions for Owner: {owner}")
        return filtered
    
    def get_actions_by_status(self, status: str) -> pd.DataFrame:
        """Get all actions with a specific status"""
        if 'Status' not in self.actions_data.columns:
            logger.warning("Status column not found")
            return pd.DataFrame()
        
        filtered = self.actions_data[self.actions_data['Status'] == status]
        logger.info(f"Found {len(filtered)} actions with Status: {status}")
        return filtered
    
    def get_critical_actions(self) -> pd.DataFrame:
        """Get all critical priority actions"""
        if 'Priority' not in self.actions_data.columns:
            return pd.DataFrame()
        
        critical = self.actions_data[self.actions_data['Priority'] == 'Critical']
        logger.info(f"Found {len(critical)} critical priority actions")
        return critical
    
    def get_upcoming_actions(self, days: int = 7) -> pd.DataFrame:
        """Get actions due in the next N days"""
        if self.actions_data.empty or 'Due Date' not in self.actions_data.columns:
            return pd.DataFrame()
        
        today = datetime.now()
        future_date = today + timedelta(days=days)
        
        df = self.actions_data.copy()
        df = df[df['Due Date'].notna() & (df['Due Date'] != '')]
        df['Due Date'] = pd.to_datetime(df['Due Date'], errors='coerce')
        
        upcoming = df[
            (df['Due Date'] >= today) & 
            (df['Due Date'] <= future_date) &
            (df['Status'] != 'Completed') & 
            (df['Status'] != 'Closed')
        ]
        
        logger.info(f"Found {len(upcoming)} actions due in next {days} days")
        return upcoming
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics for actions"""
        stats = {
            'total_actions': len(self.actions_data),
            'by_status': {},
            'by_tpr_area': {},
            'by_priority': {},
            'by_owner': {},
            'overdue_count': 0,
            'due_this_week': 0,
            'critical_count': 0
        }
        
        if not self.actions_data.empty:
            if 'Status' in self.actions_data.columns:
                stats['by_status'] = self.actions_data['Status'].value_counts().to_dict()
            
            if 'TPR Area' in self.actions_data.columns:
                stats['by_tpr_area'] = self.actions_data['TPR Area'].value_counts().to_dict()
            
            if 'Priority' in self.actions_data.columns:
                stats['by_priority'] = self.actions_data['Priority'].value_counts().to_dict()
            
            if 'Owner' in self.actions_data.columns:
                # Top 5 owners by action count
                owner_counts = self.actions_data['Owner'].value_counts().head(5).to_dict()
                stats['by_owner'] = owner_counts
            
            stats['overdue_count'] = len(self.get_overdue_actions())
            stats['due_this_week'] = len(self.get_upcoming_actions(7))
            stats['critical_count'] = len(self.get_critical_actions())
        
        return stats
    
    def export_to_excel(self, filename: str = "action_tracker.xlsx") -> str:
        """Export action tracker to Excel with formatting"""
        output_file = self.output_path / filename
        
        try:
            self.output_path.mkdir(parents=True, exist_ok=True)
            
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                # Main action tracker sheet
                self.actions_data.to_excel(writer, sheet_name='Action Tracker', index=False)
                
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
                for col_num, value in enumerate(self.actions_data.columns.values):
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
                
                # Add overdue actions sheet
                overdue = self.get_overdue_actions()
                if not overdue.empty:
                    overdue.to_excel(writer, sheet_name='Overdue Actions', index=False)
                
                # Add upcoming actions sheet
                upcoming = self.get_upcoming_actions(7)
                if not upcoming.empty:
                    upcoming.to_excel(writer, sheet_name='Due This Week', index=False)
                
                # Add critical actions sheet
                critical = self.get_critical_actions()
                if not critical.empty:
                    critical.to_excel(writer, sheet_name='Critical Actions', index=False)
            
            logger.info(f"Action Tracker exported to {output_file}")
            return str(output_file)
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            return None
    
    def generate_summary_report(self, filename: str = "action_tracker_summary.xlsx") -> str:
        """Generate summary report with statistics"""
        output_file = self.output_path / filename
        
        try:
            self.output_path.mkdir(parents=True, exist_ok=True)
            
            stats = self.get_summary_stats()
            
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                # Overall summary
                summary_data = {
                    'Metric': [
                        'Total Actions',
                        'Overdue Actions',
                        'Due This Week',
                        'Critical Actions'
                    ],
                    'Value': [
                        stats['total_actions'],
                        stats['overdue_count'],
                        stats['due_this_week'],
                        stats['critical_count']
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # By Status
                if stats['by_status']:
                    status_df = pd.DataFrame(list(stats['by_status'].items()),
                                           columns=['Status', 'Count'])
                    status_df.to_excel(writer, sheet_name='By Status', index=False)
                
                # By TPR Area
                if stats['by_tpr_area']:
                    tpr_df = pd.DataFrame(list(stats['by_tpr_area'].items()),
                                         columns=['TPR Area', 'Count'])
                    tpr_df.to_excel(writer, sheet_name='By TPR Area', index=False)
                
                # By Priority
                if stats['by_priority']:
                    priority_df = pd.DataFrame(list(stats['by_priority'].items()),
                                              columns=['Priority', 'Count'])
                    priority_df.to_excel(writer, sheet_name='By Priority', index=False)
                
                # By Owner (Top 5)
                if stats['by_owner']:
                    owner_df = pd.DataFrame(list(stats['by_owner'].items()),
                                           columns=['Owner', 'Count'])
                    owner_df.to_excel(writer, sheet_name='Top Owners', index=False)
            
            logger.info(f"Summary report exported to {output_file}")
            return str(output_file)
        except Exception as e:
            logger.error(f"Error generating summary report: {e}")
            return None
    
    def load_tracker(self) -> None:
        """Load the action tracker from all sources"""
        logger.info("Loading Action Tracker from all sources...")
        self.actions_data = self.consolidate_sources()
        logger.info(f"Action Tracker loaded with {len(self.actions_data)} actions")
    
    def run(self) -> None:
        """Main execution: Load data and generate reports"""
        logger.info("=" * 60)
        logger.info("Technology Control Tower - Action Tracker")
        logger.info("=" * 60)
        
        # Load data
        self.load_tracker()
        
        # Generate reports
        if not self.actions_data.empty:
            self.export_to_excel()
            self.generate_summary_report()
            
            # Print summary stats
            stats = self.get_summary_stats()
            logger.info("\nAction Tracker Summary:")
            logger.info(f"  Total Actions: {stats['total_actions']}")
            logger.info(f"  Overdue: {stats['overdue_count']}")
            logger.info(f"  Due This Week: {stats['due_this_week']}")
            logger.info(f"  Critical Priority: {stats['critical_count']}")
            
            if stats['by_status']:
                logger.info("\n  By Status:")
                for status, count in stats['by_status'].items():
                    logger.info(f"    {status}: {count}")
            
            if stats['by_tpr_area']:
                logger.info("\n  By TPR Area:")
                for area, count in list(stats['by_tpr_area'].items())[:5]:
                    logger.info(f"    {area}: {count}")
        else:
            logger.warning("No actions found in tracker")
            # Create empty template
            self.actions_data = self.create_empty_tracker()
            self.export_to_excel()
            logger.info("Empty Action Tracker template created")
        
        logger.info("\n" + "=" * 60)
        logger.info("Action Tracker processing complete!")
        logger.info("=" * 60)


if __name__ == "__main__":
    tracker = ActionTracker()
    tracker.run()
