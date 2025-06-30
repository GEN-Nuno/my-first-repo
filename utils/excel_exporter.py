"""
Export data to Excel format
"""
import os
import datetime
import logging

# Check for required dependencies
EXCEL_AVAILABLE = True
MISSING_DEPENDENCIES = []

try:
    import pandas as pd
except ImportError:
    EXCEL_AVAILABLE = False
    MISSING_DEPENDENCIES.append("pandas")
    pd = None
    logging.error("pandas not installed. Excel export functionality unavailable.")

try:
    import openpyxl
except ImportError:
    EXCEL_AVAILABLE = False
    MISSING_DEPENDENCIES.append("openpyxl")
    logging.error("openpyxl not installed. Excel export functionality unavailable.")

# Fix the import to use the local config module
from .config import EXPORT_DIR

class ExcelExporter:
    """Exports task data to Excel"""
    
    @staticmethod
    def export_tasks(tasks, filename=None):
        """Export tasks to Excel file"""
        if not EXCEL_AVAILABLE:
            error_msg = f"Required packages for Excel export are missing: {', '.join(MISSING_DEPENDENCIES)}"
            logging.error(error_msg)
            return None
            
        if not filename:
            date_str = datetime.datetime.now().strftime("%Y%m%d")
            filename = os.path.join(EXPORT_DIR, f"tasks_{date_str}.xlsx")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Convert tasks to dataframe
        data = []
        for task in tasks:
            data.append({
                "Name": task.name,
                "Status": task.status,
                "Priority": task.get_priority_label(),
                "Days": ", ".join(task.days),
                "Tags": ", ".join(task.tags),
                "Details": task.details,
                "Completed Today": task.completed_today,
                "Perceived Effort": task.perceived_effort
            })
        
        if not data:
            data.append({
                "Name": "", "Status": "", "Priority": "", "Days": "", 
                "Tags": "", "Details": "", "Completed Today": "", "Perceived Effort": ""
            })
            
        df = pd.DataFrame(data)
        
        try:
            df.to_excel(filename, index=False)
            logging.info(f"Tasks exported to Excel: {filename}")
            return filename
        except Exception as e:
            logging.error(f"Failed to export to Excel: {str(e)}", exc_info=True)
            return None
    
    @staticmethod
    def export_work_time(work_time_data, filename=None):
        """Export work time data to Excel"""
        if not EXCEL_AVAILABLE:
            error_msg = f"Required packages for Excel export are missing: {', '.join(MISSING_DEPENDENCIES)}"
            logging.error(error_msg)
            return None
            
        if not filename:
            date_str = datetime.datetime.now().strftime("%Y%m%d")
            filename = os.path.join(EXPORT_DIR, f"work_time_{date_str}.xlsx")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        try:
            if isinstance(work_time_data, list):
                # Handle list of work time entries
                writer = pd.ExcelWriter(filename, engine='openpyxl')
                
                for idx, entry in enumerate(work_time_data):
                    date = entry.get("date", f"Sheet{idx+1}")
                    tasks = entry.get("tasks", [])
                    
                    data = [{
                        "Name": task.get("name", ""),
                        "Tags": ", ".join(task.get("tags", [])),
                        "Work Time": task.get("work_time", 0),
                        "Perceived Effort": task.get("perceived_effort", 0)
                    } for task in tasks]
                    
                    if data:
                        df = pd.DataFrame(data)
                        sheet_name = date.split()[0] if isinstance(date, str) else f"Sheet{idx+1}"
                        df.to_excel(writer, sheet_name=sheet_name[:31], index=False)  # Excel limits sheet names to 31 chars
                
                writer.save()
            else:
                # Handle single work time entry
                data = [{
                    "Name": task.name,
                    "Tags": ", ".join(task.tags),
                    "Work Time": task.calculated_work_time,
                    "Perceived Effort": task.perceived_effort
                } for task in work_time_data if hasattr(task, "calculated_work_time")]
                
                if data:
                    df = pd.DataFrame(data)
                    df.to_excel(filename, index=False)
            
            logging.info(f"Work time data exported to Excel: {filename}")
            return filename
        
        except Exception as e:
            logging.error(f"Failed to export work time data to Excel: {str(e)}", exc_info=True)
            return None
    
    @staticmethod
    def get_missing_dependencies():
        """Return list of missing dependencies for Excel export"""
        return MISSING_DEPENDENCIES
