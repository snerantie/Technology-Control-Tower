"""
TPR Reporting Module
Generate Technology Performance Review reports across all 10 coverage areas
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
import yaml
import os
from typing import List, Dict, Optional
import logging
from master_register import MasterRegister
from action_tracker import ActionTracker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TPRReporting:
    """Generates TPR reports across all coverage areas"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize TPR Reporting with configuration"""
        self.config = self._load_config(config_path)
        self.output_path = Path(self.config['data_sources']['output_path'])
        self.tpr_areas = self.config['tpr_areas']
        
        # Initialize dependent modules
        self.master_register = MasterRegister(config_path)
        self.action_tracker = ActionTracker(config_path)
        
        # Report data
        self.report_data = {}
        
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
    
    def load_data(self) -> None:
        """Load data from Master Register and Action Tracker"""
        logger.info("Loading data for TPR Report...")
        
        # Load Master Register
        self.master_register.load_register()
        
        # Load Action Tracker
        self.action_tracker.load_tracker()
        
        logger.info("Data loaded successfully")
    
    def analyze_tpr_area(self, tpr_area_name: str) -> Dict:
        """Analyze data for a specific TPR area"""
        logger.info(f"Analyzing TPR Area: {tpr_area_name}")
        
        # Get items from Master Register
        register_items = self.master_register.filter_by_tpr_area(tpr_area_name)
        
        # Get actions for this TPR area
        area_actions = self.action_tracker.get_actions_by_tpr_area(tpr_area_name)
        
        # Calculate metrics
        analysis = {
            'tpr_area': tpr_area_name,
            'total_initiatives': len(register_items),
            'active_initiatives': len(register_items[register_items['Status'] == 'In Progress']) if not register_items.empty else 0,
            'completed_initiatives': len(register_items[register_items['Status'] == 'Completed']) if not register_items.empty else 0,
            'at_risk': len(register_items[register_items['Risk Level'] == 'High']) if not register_items.empty else 0,
            'total_actions': len(area_actions),
            'open_actions': len(area_actions[area_actions['Status'] != 'Completed']) if not area_actions.empty else 0,
            'overdue_actions': 0,
            'critical_actions': len(area_actions[area_actions['Priority'] == 'Critical']) if not area_actions.empty else 0,
            'status': 'Green',  # Default, can be customized based on rules
            'key_highlights': [],
            'key_risks': [],
            'recommendations': []
        }
        
        # Calculate overdue actions
        if not area_actions.empty and 'Due Date' in area_actions.columns:
            today = datetime.now()
            area_actions_copy = area_actions.copy()
            area_actions_copy['Due Date'] = pd.to_datetime(area_actions_copy['Due Date'], errors='coerce')
            overdue = area_actions_copy[
                (area_actions_copy['Due Date'] < today) & 
                (area_actions_copy['Status'] != 'Completed')
            ]
            analysis['overdue_actions'] = len(overdue)
        
        # Determine overall status (RAG)
        analysis['status'] = self._calculate_rag_status(analysis)
        
        # Generate insights
        analysis['key_highlights'] = self._generate_highlights(tpr_area_name, register_items, area_actions)
        analysis['key_risks'] = self._generate_risks(tpr_area_name, register_items, area_actions, analysis)
        analysis['recommendations'] = self._generate_recommendations(tpr_area_name, analysis)
        
        return analysis
    
    def _calculate_rag_status(self, analysis: Dict) -> str:
        """Calculate RAG (Red/Amber/Green) status"""
        # Red conditions
        if analysis['overdue_actions'] > 5:
            return 'Red'
        if analysis['at_risk'] > 3:
            return 'Red'
        if analysis['critical_actions'] > 5:
            return 'Red'
        
        # Amber conditions
        if analysis['overdue_actions'] > 2:
            return 'Amber'
        if analysis['at_risk'] > 1:
            return 'Amber'
        if analysis['critical_actions'] > 2:
            return 'Amber'
        
        # Green (default)
        return 'Green'
    
    def _generate_highlights(self, tpr_area: str, register_items: pd.DataFrame, actions: pd.DataFrame) -> List[str]:
        """Generate key highlights for the TPR area"""
        highlights = []
        
        if not register_items.empty:
            completed = len(register_items[register_items['Status'] == 'Completed'])
            if completed > 0:
                highlights.append(f"Completed {completed} initiative(s) this period")
            
            in_progress = len(register_items[register_items['Status'] == 'In Progress'])
            if in_progress > 0:
                highlights.append(f"{in_progress} active initiative(s) in progress")
        
        if not actions.empty:
            completed_actions = len(actions[actions['Status'] == 'Completed'])
            if completed_actions > 0:
                highlights.append(f"Closed {completed_actions} action(s)")
        
        if not highlights:
            highlights.append("No significant activity this period")
        
        return highlights
    
    def _generate_risks(self, tpr_area: str, register_items: pd.DataFrame, actions: pd.DataFrame, analysis: Dict) -> List[str]:
        """Generate key risks for the TPR area"""
        risks = []
        
        if analysis['overdue_actions'] > 0:
            risks.append(f"{analysis['overdue_actions']} overdue action(s) requiring attention")
        
        if analysis['at_risk'] > 0:
            risks.append(f"{analysis['at_risk']} high-risk initiative(s)")
        
        if analysis['critical_actions'] > 0:
            risks.append(f"{analysis['critical_actions']} critical priority action(s)")
        
        if not risks:
            risks.append("No significant risks identified")
        
        return risks
    
    def _generate_recommendations(self, tpr_area: str, analysis: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if analysis['overdue_actions'] > 2:
            recommendations.append("Review and update overdue actions with owners")
        
        if analysis['critical_actions'] > 3:
            recommendations.append("Prioritize critical actions for immediate attention")
        
        if analysis['at_risk'] > 1:
            recommendations.append("Develop mitigation plans for high-risk initiatives")
        
        if analysis['status'] == 'Red':
            recommendations.append("Schedule immediate review meeting with stakeholders")
        
        if not recommendations:
            recommendations.append("Continue monitoring and maintain current trajectory")
        
        return recommendations
    
    def generate_executive_summary(self) -> pd.DataFrame:
        """Generate executive summary across all TPR areas"""
        logger.info("Generating Executive Summary...")
        
        summary_data = []
        for tpr_area in self.tpr_areas:
            area_name = tpr_area['name']
            analysis = self.report_data.get(area_name, {})
            
            summary_data.append({
                'TPR Area': area_name,
                'Status': analysis.get('status', 'Green'),
                'Total Initiatives': analysis.get('total_initiatives', 0),
                'Active Initiatives': analysis.get('active_initiatives', 0),
                'Total Actions': analysis.get('total_actions', 0),
                'Open Actions': analysis.get('open_actions', 0),
                'Overdue Actions': analysis.get('overdue_actions', 0),
                'Key Highlights': '; '.join(analysis.get('key_highlights', [])),
                'Key Risks': '; '.join(analysis.get('key_risks', []))
            })
        
        return pd.DataFrame(summary_data)
    
    def generate_detailed_report(self, tpr_area_name: str) -> Dict[str, pd.DataFrame]:
        """Generate detailed report for a specific TPR area"""
        logger.info(f"Generating detailed report for: {tpr_area_name}")
        
        analysis = self.report_data.get(tpr_area_name, {})
        
        # Get detailed data
        register_items = self.master_register.filter_by_tpr_area(tpr_area_name)
        area_actions = self.action_tracker.get_actions_by_tpr_area(tpr_area_name)
        
        # Create summary metrics
        metrics_data = {
            'Metric': [
                'Total Initiatives',
                'Active Initiatives',
                'Completed Initiatives',
                'At Risk Initiatives',
                'Total Actions',
                'Open Actions',
                'Overdue Actions',
                'Critical Actions'
            ],
            'Value': [
                analysis.get('total_initiatives', 0),
                analysis.get('active_initiatives', 0),
                analysis.get('completed_initiatives', 0),
                analysis.get('at_risk', 0),
                analysis.get('total_actions', 0),
                analysis.get('open_actions', 0),
                analysis.get('overdue_actions', 0),
                analysis.get('critical_actions', 0)
            ]
        }
        metrics_df = pd.DataFrame(metrics_data)
        
        # Create insights
        insights_data = {
            'Type': ['Highlights'] * len(analysis.get('key_highlights', [])) +
                   ['Risks'] * len(analysis.get('key_risks', [])) +
                   ['Recommendations'] * len(analysis.get('recommendations', [])),
            'Details': analysis.get('key_highlights', []) +
                      analysis.get('key_risks', []) +
                      analysis.get('recommendations', [])
        }
        insights_df = pd.DataFrame(insights_data) if insights_data['Details'] else pd.DataFrame()
        
        return {
            'metrics': metrics_df,
            'insights': insights_df,
            'initiatives': register_items,
            'actions': area_actions
        }
    
    def export_report(self, filename: str = None) -> str:
        """Export complete TPR report to Excel"""
        if filename is None:
            report_month = self.config['organization'].get('reporting_month', datetime.now().strftime('%B %Y'))
            filename = f"TPR_Report_{report_month.replace(' ', '_')}.xlsx"
        
        output_file = self.output_path / filename
        
        try:
            self.output_path.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Exporting TPR Report to {output_file}...")
            
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                workbook = writer.book
                
                # Formats
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#C00000',
                    'font_color': 'white',
                    'border': 1
                })
                
                red_format = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
                amber_format = workbook.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C6500'})
                green_format = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
                
                # Executive Summary
                exec_summary = self.generate_executive_summary()
                exec_summary.to_excel(writer, sheet_name='Executive Summary', index=False)
                
                worksheet = writer.sheets['Executive Summary']
                for col_num, value in enumerate(exec_summary.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                # Apply conditional formatting for Status column
                status_col = exec_summary.columns.get_loc('Status')
                for row in range(1, len(exec_summary) + 1):
                    status = exec_summary.iloc[row - 1]['Status']
                    if status == 'Red':
                        worksheet.write(row, status_col, status, red_format)
                    elif status == 'Amber':
                        worksheet.write(row, status_col, status, amber_format)
                    else:
                        worksheet.write(row, status_col, status, green_format)
                
                worksheet.set_column('A:A', 25)
                worksheet.set_column('B:B', 12)
                worksheet.set_column('C:G', 15)
                worksheet.set_column('H:I', 45)
                
                # Detailed sheets for each TPR area
                for tpr_area in self.tpr_areas:
                    area_name = tpr_area['name']
                    detailed_report = self.generate_detailed_report(area_name)
                    
                    # Truncate sheet name if too long
                    sheet_name = area_name[:31]
                    
                    # Write metrics
                    start_row = 0
                    detailed_report['metrics'].to_excel(writer, sheet_name=sheet_name, 
                                                       startrow=start_row, index=False)
                    
                    # Write insights
                    if not detailed_report['insights'].empty:
                        start_row = len(detailed_report['metrics']) + 3
                        detailed_report['insights'].to_excel(writer, sheet_name=sheet_name,
                                                            startrow=start_row, index=False)
                    
                    # Format sheet
                    worksheet = writer.sheets[sheet_name]
                    worksheet.set_column('A:A', 25)
                    worksheet.set_column('B:B', 50)
                
                # Actions Summary
                action_stats = self.action_tracker.get_summary_stats()
                actions_summary_data = {
                    'Metric': ['Total Actions', 'Overdue', 'Due This Week', 'Critical'],
                    'Value': [
                        action_stats['total_actions'],
                        action_stats['overdue_count'],
                        action_stats['due_this_week'],
                        action_stats['critical_count']
                    ]
                }
                actions_summary_df = pd.DataFrame(actions_summary_data)
                actions_summary_df.to_excel(writer, sheet_name='Actions Summary', index=False)
            
            logger.info(f"TPR Report exported successfully to {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error exporting TPR report: {e}")
            return None
    
    def run(self) -> None:
        """Main execution: Generate complete TPR report"""
        logger.info("=" * 60)
        logger.info("Technology Control Tower - TPR Reporting")
        logger.info("=" * 60)
        
        # Load data
        self.load_data()
        
        # Analyze each TPR area
        logger.info("\nAnalyzing TPR Areas...")
        for tpr_area in self.tpr_areas:
            area_name = tpr_area['name']
            analysis = self.analyze_tpr_area(area_name)
            self.report_data[area_name] = analysis
            
            logger.info(f"\n{area_name}:")
            logger.info(f"  Status: {analysis['status']}")
            logger.info(f"  Initiatives: {analysis['total_initiatives']} (Active: {analysis['active_initiatives']})")
            logger.info(f"  Actions: {analysis['total_actions']} (Open: {analysis['open_actions']})")
        
        # Generate and export report
        logger.info("\nGenerating TPR Report...")
        report_file = self.export_report()
        
        if report_file:
            logger.info(f"\n✓ TPR Report generated: {report_file}")
            
            # Print executive summary
            logger.info("\nExecutive Summary:")
            exec_summary = self.generate_executive_summary()
            for _, row in exec_summary.iterrows():
                logger.info(f"  {row['TPR Area']}: {row['Status']} ({row['Open Actions']} open actions)")
        
        logger.info("\n" + "=" * 60)
        logger.info("TPR Reporting complete!")
        logger.info("=" * 60)


if __name__ == "__main__":
    reporting = TPRReporting()
    reporting.run()
