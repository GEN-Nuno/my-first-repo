import os
import json
import datetime
import logging
from .task_model import Task
from patterns.observer import Subject
from utils.config import DATA_FILES

class ScheduleModel(Subject):
    """Model representing the schedule containing tasks"""
    
    def __init__(self):
        Subject.__init__(self)
        self.tasks = []
        self.tags = ["Work", "Personal", "Meeting", "Development", "Documentation"]
        self.load_tasks()
        self.load_tags()
    
    def add_task(self, task):
        """Add a new task to the schedule"""
        self.tasks.append(task)
        self.notify()
    
    def delete_task(self, task):
        """Remove a task from the schedule"""
        if task in self.tasks:
            self.tasks.remove(task)
            self.notify()
    
    def delete_closed_tasks(self):
        """Delete all tasks with 'closed' status"""
        self.tasks = [task for task in self.tasks if task.status != "closed"]
        self.notify()
    
    def get_today_tasks(self, include_exceptions=False, include_free=True):
        """
        Get tasks for today
        
        Args:
            include_exceptions: If True, return all tasks regardless of day
            include_free: If True, also include tasks with 'Free' attribute
        """
        today = datetime.datetime.now().strftime("%A")
        
        # Get today's tasks from the loaded tasks
        if include_exceptions:
            return self.tasks
        else:
            if include_free:
                filtered_tasks = [task for task in self.tasks if today in task.days or "Free" in task.days]
            else:
                filtered_tasks = [task for task in self.tasks if today in task.days]
    
        return filtered_tasks
    
    def add_tag(self, tag):
        """Add a new tag"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.save_tags()
            self.notify()
    
    def delete_tag(self, tag):
        """Remove a tag"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.save_tags()
            self.notify()
    
    def save_tasks(self):
        """Save tasks to configuration file"""
        data = [task.to_dict() for task in self.tasks]
        os.makedirs(os.path.dirname(DATA_FILES["tasks"]), exist_ok=True)
        with open(DATA_FILES["tasks"], "w") as file:
            json.dump(data, file, indent=4)
        logging.info(f"Saved {len(self.tasks)} tasks to {DATA_FILES['tasks']}")
        return True
    
    def load_tasks(self):
        """Load tasks from configuration file"""
        try:
            if os.path.exists(DATA_FILES["tasks"]):
                with open(DATA_FILES["tasks"], "r") as file:
                    data = json.load(file)
                    self.tasks = [Task.from_dict(task_dict) for task_dict in data]
                    logging.info(f"Loaded {len(self.tasks)} tasks from {DATA_FILES['tasks']}")
        except Exception as e:
            logging.error(f"Error loading tasks: {e}", exc_info=True)
            self.tasks = []
    
    def save_tags(self):
        """Save tags to configuration file"""
        os.makedirs(os.path.dirname(DATA_FILES["tags"]), exist_ok=True)
        with open(DATA_FILES["tags"], "w") as file:
            json.dump(self.tags, file, indent=4)
        logging.info(f"Saved {len(self.tags)} tags to {DATA_FILES['tags']}")
        return True
    
    def load_tags(self):
        """Load tags from configuration file"""
        try:
            if os.path.exists(DATA_FILES["tags"]):
                with open(DATA_FILES["tags"], "r") as file:
                    self.tags = json.load(file)
                    logging.info(f"Loaded {len(self.tags)} tags from {DATA_FILES['tags']}")
        except Exception as e:
            logging.error(f"Error loading tags: {e}", exc_info=True)
            # Use default tags
    
    def save_work_time(self, calculated_tasks):
        """Save calculated work time to configuration file"""
        # Use full ISO format to include date and time
        today_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "date": today_date,
            "tasks": [
                {
                    "name": task.name,
                    "tags": task.tags,
                    "work_time": task.calculated_work_time,
                    "perceived_effort": task.perceived_effort
                }
                for task in calculated_tasks
            ]
        }
        
        # Load existing data if file exists
        all_data = []
        if os.path.exists(DATA_FILES["work_time"]):
            try:
                with open(DATA_FILES["work_time"], "r") as file:
                    all_data = json.load(file)
            except Exception as e:
                logging.error(f"Error reading work time data: {e}", exc_info=True)
                all_data = []
        
        # Append new data
        if not isinstance(all_data, list):
            all_data = []
        all_data.append(data)
        
        # Save back to file
        os.makedirs(os.path.dirname(DATA_FILES["work_time"]), exist_ok=True)
        with open(DATA_FILES["work_time"], "w") as file:
            json.dump(all_data, file, indent=4)
        
        logging.info(f"Saved work time data for {len(calculated_tasks)} tasks")
        return True
    
    def save_today_tasks(self, tasks):
        """Save today's tasks to todaytask.conf with date information"""
        if not tasks:
            logging.warning("No tasks to save for today")
            return False  # Return False if there are no tasks to save
        
        today_date = datetime.datetime.now().strftime("%Y-%m-%d")
        data = {
            "date": today_date,
            "tasks": [task.to_dict() for task in tasks]
        }
        
        try:
            # Make sure the directory exists
            os.makedirs(os.path.dirname(DATA_FILES["today_tasks"]), exist_ok=True)
            
            # Save directly to file - don't append, replace with new data
            with open(DATA_FILES["today_tasks"], "w") as file:
                json.dump(data, file, indent=4)
        
            logging.info(f"Saved {len(tasks)} today's tasks to {DATA_FILES['today_tasks']}")
            return True
        except Exception as e:
            logging.error(f"Error saving today's tasks: {str(e)}", exc_info=True)
            return False
            logging.error(f"Error saving today's tasks: {str(e)}")
            return False
