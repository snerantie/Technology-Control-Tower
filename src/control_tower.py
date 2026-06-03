"""
Technology Control Tower - Main Orchestration Script
Runs all modules to generate complete Control Tower reports
"""

import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict

# Import all modules
from jira_connector import JiraConnector
from master_register import MasterRegister
from action_tracker import ActionTracker
from tpr_reporting import TPRReporting
from governance_cadence import GovernanceCadence

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ControlTower:
    """Main orchestrator for Technology Control Tower"""
    
    def __init__(self):
        """Initialize Control Tower"""
        self.start_time = datetime.now()
        self.jira_connector = None
        self.master_register = None
        self.action_tracker = None
        self.tpr_reporting = None
        self.governance_cadence = None
        
    def run_full_update(self) -> Dict[str, str]:
        """Run complete Control Tower update"""
        logger.info("=" * 80)
        logger.info("TECHNOLOGY CONTROL TOWER - FULL UPDATE")
        logger.info("=" * 80)
        logger.info(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)
        
        results = {
            'jira_data': None,
            'master_register': None,
            'action_tracker': None,
            'tpr_report': None,
            'governance_cadence': None
        }
        
        try:
            # Step 1: Connect to Jira and pull data
            logger.info("\n[1/5] Connecting to Jira and extracting data...")
            self.jira_connector = JiraConnector()
            if self.jira_connector.connect():
                self.jira_connector.export_to_master_register()
                self.jira_connector.export_actions()
                results['jira_data'] = 'Success'
                logger.info("✓ Jira data extracted")
            else:
                logger.warning("⚠ Jira connection failed - proceeding with existing data")
                results['jira_data'] = 'Skipped'
            
            # Step 2: Generate Master Register
            logger.info("\n[2/5] Generating Master Register...")
            self.master_register = MasterRegister()
            self.master_register.load_register()
            master_file = self.master_register.export_to_excel()
            self.master_register.generate_summary_report()
            results['master_register'] = master_file
            logger.info(f"✓ Master Register generated: {master_file}")
            
            # Step 3: Generate Action Tracker
            logger.info("\n[3/5] Generating Action Tracker...")
            self.action_tracker = ActionTracker()
            self.action_tracker.load_tracker()
            action_file = self.action_tracker.export_to_excel()
            self.action_tracker.generate_summary_report()
            results['action_tracker'] = action_file
            logger.info(f"✓ Action Tracker generated: {action_file}")
            
            # Step 4: Generate TPR Report
            logger.info("\n[4/5] Generating TPR Report...")
            self.tpr_reporting = TPRReporting()
            self.tpr_reporting.load_data()
            
            # Analyze all TPR areas
            for tpr_area in self.tpr_reporting.tpr_areas:
                area_name = tpr_area['name']
                analysis = self.tpr_reporting.analyze_tpr_area(area_name)
                self.tpr_reporting.report_data[area_name] = analysis
            
            tpr_file = self.tpr_reporting.export_report()
            results['tpr_report'] = tpr_file
            logger.info(f"✓ TPR Report generated: {tpr_file}")
            
            # Step 5: Generate Governance Cadence
            logger.info("\n[5/5] Generating Governance Cadence...")
            self.governance_cadence = GovernanceCadence()
            self.governance_cadence.generate_meeting_schedule(months_ahead=6)
            gov_file = self.governance_cadence.export_to_excel()
            results['governance_cadence'] = gov_file
            logger.info(f"✓ Governance Cadence generated: {gov_file}")
            
        except Exception as e:
            logger.error(f"Error during Control Tower update: {e}", exc_info=True)
            results['error'] = str(e)
        
        return results
    
    def print_summary(self, results: Dict[str, str]) -> None:
        """Print execution summary"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        logger.info("\n" + "=" * 80)
        logger.info("CONTROL TOWER UPDATE SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Completed: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info("\nGenerated Reports:")
        
        for report_type, filepath in results.items():
            if filepath and report_type != 'error':
                status = "✓" if filepath not in ['Skipped', None] else "⚠"
                logger.info(f"  {status} {report_type.replace('_', ' ').title()}: {filepath}")
        
        if 'error' in results:
            logger.error(f"\n⚠ Errors encountered: {results['error']}")
        
        logger.info("\n" + "=" * 80)
        logger.info("All reports available in: ./data/output/")
        logger.info("=" * 80)
        
        # Print key metrics
        if self.action_tracker and not self.action_tracker.actions_data.empty:
            stats = self.action_tracker.get_summary_stats()
            logger.info("\nKey Metrics:")
            logger.info(f"  Total Actions: {stats['total_actions']}")
            logger.info(f"  Overdue: {stats['overdue_count']}")
            logger.info(f"  Critical: {stats['critical_count']}")
        
        if self.tpr_reporting and self.tpr_reporting.report_data:
            red_count = sum(1 for area, data in self.tpr_reporting.report_data.items() 
                          if data.get('status') == 'Red')
            amber_count = sum(1 for area, data in self.tpr_reporting.report_data.items() 
                            if data.get('status') == 'Amber')
            green_count = sum(1 for area, data in self.tpr_reporting.report_data.items() 
                            if data.get('status') == 'Green')
            
            logger.info(f"\nTPR Status: Red: {red_count}, Amber: {amber_count}, Green: {green_count}")
        
        if self.governance_cadence:
            upcoming = self.governance_cadence.get_upcoming_meetings(7)
            logger.info(f"\nUpcoming Meetings (Next 7 Days): {len(upcoming)}")


def main():
    """Main entry point"""
    tower = ControlTower()
    results = tower.run_full_update()
    tower.print_summary(results)
    
    # Return exit code based on success
    if 'error' in results:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
