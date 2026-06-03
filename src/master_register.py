"""
Master Register Module
Central registry for all technology assets, initiatives, and systems
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
import yaml
import os
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MasterRegister:
    """Manages the Master Register of technology items"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize Master Register with configuration"""
        self.config = self._load_config(config_path)
        self.register_data = pd.DataFrame()
        self.input_path = Path(self.config['data_sources']['input_path'])
        self.output_path = Path(self.config['data_sources']['output_path'])
        
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        # Try config.yaml first, fall back to config.example.yaml
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            example_path = "config/config.example.yaml"
            logger.warning(f"{config_path} not found, using {example_path}")
            with open(example_path, 'r') as f:
                return yaml.safe_load(f)
    
    def create_empty_register(self) -> pd.DataFrame:
        """Create an empty register with the standard columns"""
        columns = self.config['master_register']['columns']
        return pd.DataFrame(columns=columns)
    
    def load_from_excel(self, filepath: str) -> pd.DataFrame:
        """Load data from an Excel file"""
        try:
            logger.info(f"Loading data from {filepath}")
            df = pd.read_excel(filepath)
            logger.info(f"Loaded {len(df)} records from {filepath}")
            return df
        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
            return pd.DataFrame()
    
    def consolidate_excel_sources(self) -> pd.DataFrame:
        """Consolidate all Excel input files into the master register"""
        all_data = []
        
        # Get list of Excel files from config
        excel_files = self.config['data_sources'].get('excel_files', [])
        
        for excel_file in excel_files:
            filepath = self.input_path / excel_file
            if filepath.exists():
                df = self.load_from_excel(str(filepath))
                if not df.empty:
                    # Add source tracking
                    df['Source'] = excel_file
                    df['Last Updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    all_data.append(df)
            else:
                logger.warning(f"File not found: {filepath}")
        
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            logger.info(f"Consolidated {len(combined)} total records from {len(all_data)} sources")
            return combined
        else:
            logger.warning("No data consolidated. Creating empty register.")
            return self.create_empty_register()
    
    def add_item(self, item_data: Dict) -> None:
        """Add a single item to the register"""
        required_columns = self.config['master_register']['columns']
        
        # Ensure all required columns exist
        for col in required_columns:
            if col not in item_data:
                item_data[col] = None
        
        # Add metadata
        item_data['Last Updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        new_row = pd.DataFrame([item_data])
        self.register_data = pd.concat([self.register_data, new_row], ignore_index=True)
        logger.info(f"Added item: {item_data.get('Name', 'Unknown')}")
    
    def update_item(self, item_id: str, updates: Dict) -> bool:
        """Update an existing item in the register"""
        if 'ID' not in self.register_data.columns:
            logger.error("Register does not have ID column")
            return False
        
        mask = self.register_data['ID'] == item_id
        if mask.any():
            for key, value in updates.items():
                self.register_data.loc[mask, key] = value
            self.register_data.loc[mask, 'Last Updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"Updated item: {item_id}")
            return True
        else:
            logger.warning(f"Item not found: {item_id}")
            return False
    
    def filter_by_tpr_area(self, tpr_area: str) -> pd.DataFrame:
        """Filter register by TPR area"""
        if 'TPR Area' not in self.register_data.columns:
            logger.warning("TPR Area column not found")
            return pd.DataFrame()
        
        filtered = self.register_data[self.register_data['TPR Area'] == tpr_area]
        logger.info(f"Filtered {len(filtered)} items for TPR Area: {tpr_area}")
        return filtered
    
    def filter_by_status(self, status: str) -> pd.DataFrame:
        """Filter register by status"""
        if 'Status' not in self.register_data.columns:
            logger.warning("Status column not found")
            return pd.DataFrame()
        
        filtered = self.register_data[self.register_data['Status'] == status]
        logger.info(f"Filtered {len(filtered)} items with Status: {status}")
        return filtered
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics for the register"""
        stats = {
            'total_items': len(self.register_data),
            'by_tpr_area': {},
            'by_status': {},
            'by_risk_level': {},
            'by_priority': {}
        }
        
        if not self.register_data.empty:
            if 'TPR Area' in self.register_data.columns:
                stats['by_tpr_area'] = self.register_data['TPR Area'].value_counts().to_dict()
            
            if 'Status' in self.register_data.columns:
                stats['by_status'] = self.register_data['Status'].value_counts().to_dict()
            
            if 'Risk Level' in self.register_data.columns:
                stats['by_risk_level'] = self.register_data['Risk Level'].value_counts().to_dict()
            
            if 'Priority' in self.register_data.columns:
                stats['by_priority'] = self.register_data['Priority'].value_counts().to_dict()
        
        return stats
    
    def export_to_excel(self, filename: str = "master_register.xlsx") -> str:
        """Export the master register to Excel"""
        output_file = self.output_path / filename
        
        try:
            # Create output directory if it doesn't exist
            self.output_path.mkdir(parents=True, exist_ok=True)
            
            # Export to Excel with formatting
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                self.register_data.to_excel(writer, sheet_name='Master Register', index=False)
                
                # Get the xlsxwriter workbook and worksheet objects
                workbook = writer.book
                worksheet = writer.sheets['Master Register']
                
                # Add header format
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#4472C4',
                    'font_color': 'white',
                    'border': 1
                })
                
                # Write headers with format
                for col_num, value in enumerate(self.register_data.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                # Set column widths
                worksheet.set_column('A:A', 10)  # ID
                worksheet.set_column('B:B', 30)  # Name
                worksheet.set_column('C:C', 15)  # Type
                worksheet.set_column('D:D', 20)  # TPR Area
                worksheet.set_column('E:E', 20)  # Owner
                worksheet.set_column('F:F', 12)  # Status
                worksheet.set_column('G:G', 10)  # Priority
                worksheet.set_column('H:I', 12)  # Dates
                worksheet.set_column('J:J', 15)  # Budget
                worksheet.set_column('K:K', 12)  # Risk Level
                worksheet.set_column('L:L', 40)  # Description
                worksheet.set_column('M:N', 15)  # Source, Last Updated
            
            logger.info(f"Master Register exported to {output_file}")
            return str(output_file)
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            return None
    
    def generate_summary_report(self, filename: str = "master_register_summary.xlsx") -> str:
        """Generate a summary report with statistics"""
        output_file = self.output_path / filename
        
        try:
            self.output_path.mkdir(parents=True, exist_ok=True)
            
            stats = self.get_summary_stats()
            
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                # Summary sheet
                summary_data = {
                    'Metric': ['Total Items'],
                    'Value': [stats['total_items']]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # By TPR Area
                if stats['by_tpr_area']:
                    tpr_df = pd.DataFrame(list(stats['by_tpr_area'].items()), 
                                         columns=['TPR Area', 'Count'])
                    tpr_df.to_excel(writer, sheet_name='By TPR Area', index=False)
                
                # By Status
                if stats['by_status']:
                    status_df = pd.DataFrame(list(stats['by_status'].items()), 
                                            columns=['Status', 'Count'])
                    status_df.to_excel(writer, sheet_name='By Status', index=False)
                
                # By Risk Level
                if stats['by_risk_level']:
                    risk_df = pd.DataFrame(list(stats['by_risk_level'].items()), 
                                          columns=['Risk Level', 'Count'])
                    risk_df.to_excel(writer, sheet_name='By Risk Level', index=False)
            
            logger.info(f"Summary report exported to {output_file}")
            return str(output_file)
        except Exception as e:
            logger.error(f"Error generating summary report: {e}")
            return None
    
    def load_register(self) -> None:
        """Load the master register from all sources"""
        logger.info("Loading Master Register from all sources...")
        
        # Load from Excel files
        self.register_data = self.consolidate_excel_sources()
        
        logger.info(f"Master Register loaded with {len(self.register_data)} items")
    
    def run(self) -> None:
        """Main execution: Load data and generate reports"""
        logger.info("=" * 60)
        logger.info("Technology Control Tower - Master Register")
        logger.info("=" * 60)
        
        # Load data
        self.load_register()
        
        # Generate reports
        if not self.register_data.empty:
            self.export_to_excel()
            self.generate_summary_report()
            
            # Print summary stats
            stats = self.get_summary_stats()
            logger.info("\nMaster Register Summary:")
            logger.info(f"  Total Items: {stats['total_items']}")
            
            if stats['by_tpr_area']:
                logger.info("\n  By TPR Area:")
                for area, count in stats['by_tpr_area'].items():
                    logger.info(f"    {area}: {count}")
            
            if stats['by_status']:
                logger.info("\n  By Status:")
                for status, count in stats['by_status'].items():
                    logger.info(f"    {status}: {count}")
        else:
            logger.warning("No data found in Master Register")
            # Create empty template
            self.register_data = self.create_empty_register()
            self.export_to_excel()
            logger.info("Empty Master Register template created")
        
        logger.info("\n" + "=" * 60)
        logger.info("Master Register processing complete!")
        logger.info("=" * 60)


if __name__ == "__main__":
    register = MasterRegister()
    register.run()
