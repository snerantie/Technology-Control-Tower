"""
Governance Cadence Module
Track meeting schedules, review cycles, and decision workflows
"""

import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import yaml
import os
from typing import List, Dict, Optional
import logging
import calendar

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GovernanceCadence:
    """Manages governance meetings, reviews, and decision tracking"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize Governance Cadence with configuration"""
        self.config = self._load_config(config_path)
        self.meetings = self.config['governance']['meetings']
        self.output_path = Path(self.config['data_sources']['output_path'])
        
        # Tracking data
        self.meeting_schedule = pd.DataFrame()
        self.upcoming_meetings = []
        
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
    
    def calculate_next_occurrence(self, meeting: Dict, reference_date: datetime = None) -> datetime:
        """Calculate next occurrence of a meeting"""
        if reference_date is None:
            reference_date = datetime.now()
        
        frequency = meeting['frequency'].lower()
        day = meeting['day']
        
        if frequency == 'weekly':
            # Map day names to weekday numbers
            weekdays = {
                'monday': 0, 'tuesday': 1, 'wednesday': 2, 
                'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
            }
            target_weekday = weekdays.get(day.lower(), 0)
            
            # Find next occurrence of target weekday
            days_ahead = target_weekday - reference_date.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            
            next_date = reference_date + timedelta(days=days_ahead)
            return next_date
        
        elif frequency == 'monthly':
            # Parse day (e.g., "First Friday", "Last Wednesday")
            parts = day.split()
            if len(parts) >= 2:
                position = parts[0].lower()  # first, second, last, etc.
                weekday_name = parts[1].lower()
                
                weekdays = {
                    'monday': 0, 'tuesday': 1, 'wednesday': 2,
                    'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
                }
                target_weekday = weekdays.get(weekday_name, 4)  # Default to Friday
                
                # Start with next month if we're past the likely date this month
                if reference_date.day > 28:
                    year = reference_date.year
                    month = reference_date.month + 1
                    if month > 12:
                        month = 1
                        year += 1
                else:
                    year = reference_date.year
                    month = reference_date.month
                
                # Find the target weekday occurrences in the month
                if position == 'first':
                    next_date = self._find_nth_weekday(year, month, target_weekday, 1)
                elif position == 'second':
                    next_date = self._find_nth_weekday(year, month, target_weekday, 2)
                elif position == 'third':
                    next_date = self._find_nth_weekday(year, month, target_weekday, 3)
                elif position == 'last':
                    next_date = self._find_last_weekday(year, month, target_weekday)
                else:
                    # Default to first occurrence
                    next_date = self._find_nth_weekday(year, month, target_weekday, 1)
                
                # If calculated date is in the past, move to next month
                if next_date < reference_date:
                    month += 1
                    if month > 12:
                        month = 1
                        year += 1
                    if position == 'last':
                        next_date = self._find_last_weekday(year, month, target_weekday)
                    else:
                        nth = 1 if position == 'first' else (2 if position == 'second' else 3)
                        next_date = self._find_nth_weekday(year, month, target_weekday, nth)
                
                return next_date
            else:
                # Fallback: next month, same day
                return reference_date + timedelta(days=30)
        
        elif frequency == 'quarterly':
            # Similar to monthly but every 3 months
            parts = day.split()
            if len(parts) >= 2:
                position = parts[0].lower()
                weekday_name = parts[1].lower()
                
                weekdays = {
                    'monday': 0, 'tuesday': 1, 'wednesday': 2,
                    'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
                }
                target_weekday = weekdays.get(weekday_name, 2)
                
                # Calculate next quarter
                current_quarter = (reference_date.month - 1) // 3
                next_quarter = current_quarter + 1
                if next_quarter > 3:
                    next_quarter = 0
                    year = reference_date.year + 1
                else:
                    year = reference_date.year
                
                # First month of next quarter
                month = (next_quarter * 3) + 1
                
                if position == 'last':
                    # Last month of the quarter
                    month = (next_quarter * 3) + 3
                    if month > 12:
                        month -= 12
                        year += 1
                    next_date = self._find_last_weekday(year, month, target_weekday)
                else:
                    next_date = self._find_nth_weekday(year, month, target_weekday, 1)
                
                return next_date
            else:
                # Fallback: 3 months ahead
                return reference_date + timedelta(days=90)
        
        else:
            # Default: 1 week ahead
            return reference_date + timedelta(days=7)
    
    def _find_nth_weekday(self, year: int, month: int, weekday: int, n: int) -> datetime:
        """Find the nth occurrence of a weekday in a month"""
        # First day of the month
        first_day = datetime(year, month, 1)
        
        # First occurrence of the target weekday
        days_ahead = weekday - first_day.weekday()
        if days_ahead < 0:
            days_ahead += 7
        
        first_occurrence = first_day + timedelta(days=days_ahead)
        
        # Nth occurrence
        nth_occurrence = first_occurrence + timedelta(weeks=n-1)
        
        # Make sure it's still in the same month
        if nth_occurrence.month != month:
            # Return first day of next month as fallback
            if month == 12:
                return datetime(year + 1, 1, 1)
            else:
                return datetime(year, month + 1, 1)
        
        return nth_occurrence
    
    def _find_last_weekday(self, year: int, month: int, weekday: int) -> datetime:
        """Find the last occurrence of a weekday in a month"""
        # Last day of the month
        last_day = calendar.monthrange(year, month)[1]
        last_date = datetime(year, month, last_day)
        
        # Find the last occurrence of the target weekday
        days_back = (last_date.weekday() - weekday) % 7
        last_occurrence = last_date - timedelta(days=days_back)
        
        return last_occurrence
    
    def generate_meeting_schedule(self, months_ahead: int = 3) -> pd.DataFrame:
        """Generate meeting schedule for the next N months"""
        logger.info(f"Generating meeting schedule for next {months_ahead} months...")
        
        schedule_data = []
        reference_date = datetime.now()
        
        for meeting in self.meetings:
            meeting_name = meeting['name']
            frequency = meeting['frequency']
            
            # Generate occurrences based on frequency
            if frequency.lower() == 'weekly':
                # Generate weekly meetings
                occurrences = []
                current_date = reference_date
                end_date = reference_date + timedelta(days=30 * months_ahead)
                
                while current_date <= end_date:
                    next_date = self.calculate_next_occurrence(meeting, current_date)
                    if next_date <= end_date:
                        occurrences.append(next_date)
                        current_date = next_date + timedelta(days=1)
                    else:
                        break
            
            elif frequency.lower() == 'monthly':
                # Generate monthly meetings
                occurrences = []
                for i in range(months_ahead):
                    future_date = reference_date + timedelta(days=30 * i)
                    next_date = self.calculate_next_occurrence(meeting, future_date)
                    occurrences.append(next_date)
            
            elif frequency.lower() == 'quarterly':
                # Generate quarterly meetings
                occurrences = []
                quarters = (months_ahead + 2) // 3  # Round up to cover quarters
                for i in range(quarters):
                    future_date = reference_date + timedelta(days=90 * i)
                    next_date = self.calculate_next_occurrence(meeting, future_date)
                    occurrences.append(next_date)
            
            else:
                # Default: generate one occurrence
                occurrences = [self.calculate_next_occurrence(meeting, reference_date)]
            
            # Add to schedule
            for occurrence in occurrences:
                schedule_data.append({
                    'Meeting Name': meeting_name,
                    'Date': occurrence.strftime('%Y-%m-%d'),
                    'Day': occurrence.strftime('%A'),
                    'Time': meeting['time'],
                    'Frequency': frequency,
                    'Attendees': ', '.join(meeting['attendees']),
                    'Status': 'Scheduled',
                    'Notes': ''
                })
        
        self.meeting_schedule = pd.DataFrame(schedule_data)
        self.meeting_schedule = self.meeting_schedule.sort_values('Date').reset_index(drop=True)
        
        logger.info(f"Generated {len(self.meeting_schedule)} meeting occurrences")
        return self.meeting_schedule
    
    def get_upcoming_meetings(self, days: int = 7) -> pd.DataFrame:
        """Get meetings scheduled in the next N days"""
        if self.meeting_schedule.empty:
            self.generate_meeting_schedule()
        
        today = datetime.now()
        future_date = today + timedelta(days=days)
        
        upcoming = self.meeting_schedule.copy()
        upcoming['Date'] = pd.to_datetime(upcoming['Date'])
        upcoming = upcoming[
            (upcoming['Date'] >= today) & 
            (upcoming['Date'] <= future_date)
        ]
        
        logger.info(f"Found {len(upcoming)} meetings in next {days} days")
        return upcoming
    
    def get_this_month_meetings(self) -> pd.DataFrame:
        """Get all meetings scheduled this month"""
        if self.meeting_schedule.empty:
            self.generate_meeting_schedule()
        
        today = datetime.now()
        
        meetings = self.meeting_schedule.copy()
        meetings['Date'] = pd.to_datetime(meetings['Date'])
        meetings = meetings[
            (meetings['Date'].dt.year == today.year) &
            (meetings['Date'].dt.month == today.month)
        ]
        
        logger.info(f"Found {len(meetings)} meetings this month")
        return meetings
    
    def export_to_excel(self, filename: str = "governance_cadence.xlsx") -> str:
        """Export governance cadence to Excel"""
        output_file = self.output_path / filename
        
        try:
            self.output_path.mkdir(parents=True, exist_ok=True)
            
            if self.meeting_schedule.empty:
                self.generate_meeting_schedule()
            
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                workbook = writer.book
                
                # Formats
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#FFC000',
                    'font_color': 'black',
                    'border': 1
                })
                
                # Full schedule
                self.meeting_schedule.to_excel(writer, sheet_name='Meeting Schedule', index=False)
                worksheet = writer.sheets['Meeting Schedule']
                
                for col_num, value in enumerate(self.meeting_schedule.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                worksheet.set_column('A:A', 25)
                worksheet.set_column('B:B', 12)
                worksheet.set_column('C:C', 12)
                worksheet.set_column('D:D', 10)
                worksheet.set_column('E:E', 12)
                worksheet.set_column('F:F', 35)
                worksheet.set_column('G:G', 12)
                worksheet.set_column('H:H', 30)
                
                # This month's meetings
                this_month = self.get_this_month_meetings()
                if not this_month.empty:
                    this_month.to_excel(writer, sheet_name='This Month', index=False)
                
                # Next week's meetings
                next_week = self.get_upcoming_meetings(7)
                if not next_week.empty:
                    next_week.to_excel(writer, sheet_name='Next Week', index=False)
                
                # Meeting types summary
                meeting_types = self.meeting_schedule.groupby('Meeting Name').agg({
                    'Date': 'count',
                    'Frequency': 'first',
                    'Attendees': 'first'
                }).reset_index()
                meeting_types.columns = ['Meeting Name', 'Occurrences', 'Frequency', 'Attendees']
                meeting_types.to_excel(writer, sheet_name='Meeting Types', index=False)
            
            logger.info(f"Governance Cadence exported to {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            return None
    
    def generate_calendar_summary(self) -> Dict:
        """Generate calendar summary statistics"""
        if self.meeting_schedule.empty:
            self.generate_meeting_schedule()
        
        summary = {
            'total_meetings': len(self.meeting_schedule),
            'this_month': len(self.get_this_month_meetings()),
            'next_week': len(self.get_upcoming_meetings(7)),
            'by_frequency': {},
            'by_meeting_type': {}
        }
        
        if not self.meeting_schedule.empty:
            summary['by_frequency'] = self.meeting_schedule['Frequency'].value_counts().to_dict()
            summary['by_meeting_type'] = self.meeting_schedule['Meeting Name'].value_counts().to_dict()
        
        return summary
    
    def run(self) -> None:
        """Main execution: Generate governance cadence schedule"""
        logger.info("=" * 60)
        logger.info("Technology Control Tower - Governance Cadence")
        logger.info("=" * 60)
        
        # Generate schedule
        self.generate_meeting_schedule(months_ahead=6)
        
        # Export to Excel
        output_file = self.export_to_excel()
        
        if output_file:
            logger.info(f"\n✓ Governance Cadence exported: {output_file}")
        
        # Print summary
        summary = self.generate_calendar_summary()
        logger.info("\nGovernance Cadence Summary:")
        logger.info(f"  Total Meetings Scheduled (6 months): {summary['total_meetings']}")
        logger.info(f"  This Month: {summary['this_month']}")
        logger.info(f"  Next Week: {summary['next_week']}")
        
        if summary['by_meeting_type']:
            logger.info("\n  By Meeting Type:")
            for meeting_type, count in summary['by_meeting_type'].items():
                logger.info(f"    {meeting_type}: {count} occurrences")
        
        # Show upcoming meetings
        upcoming = self.get_upcoming_meetings(14)
        if not upcoming.empty:
            logger.info("\n  Upcoming Meetings (Next 2 Weeks):")
            for _, meeting in upcoming.iterrows():
                logger.info(f"    {meeting['Date']} - {meeting['Meeting Name']} at {meeting['Time']}")
        
        logger.info("\n" + "=" * 60)
        logger.info("Governance Cadence tracking complete!")
        logger.info("=" * 60)


if __name__ == "__main__":
    cadence = GovernanceCadence()
    cadence.run()
