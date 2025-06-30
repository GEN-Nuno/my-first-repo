import json
from datetime import datetime

class Task:
    """Model representing a task in the scheduler"""
    
    STATUS_OPTIONS = ["working", "planned", "closed"]
    DAYS_OPTIONS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Free"]
    PRIORITY_OPTIONS = [0, 1, 2, 3]  # 0: Low, 1: Normal, 2: High, 3: Critical
    
    def __init__(self, name="", status="planned", days=None, details="", tags=None, 
                 completed_today=False, perceived_effort=0, priority=1, recurring=None):
        self.name = name
        self.status = status if status in self.STATUS_OPTIONS else "planned"
        self.days = days if days else ["Free"]
        self.details = details
        self.tags = tags if tags else []
        self.completed_today = completed_today
        self.perceived_effort = perceived_effort
        self.calculated_work_time = 0
        self.priority = priority if priority in self.PRIORITY_OPTIONS else 1
        self.recurring = recurring if recurring else {}  # Dict with recurrence pattern
    
    def is_for_today(self, include_free=True):
        """Check if task is scheduled for today"""
        today = datetime.now().strftime("%A")
        if today in self.days:
            return True
        return include_free and "Free" in self.days
    
    def to_dict(self):
        """Convert task to dictionary for serialization"""
        return {
            "name": self.name,
            "status": self.status,
            "days": self.days,
            "details": self.details,
            "tags": self.tags,
            "completed_today": self.completed_today,
            "perceived_effort": self.perceived_effort,
            "priority": self.priority,
            "recurring": self.recurring,
            "save_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create task from dictionary"""
        return cls(
            name=data.get("name", ""),
            status=data.get("status", "planned"),
            days=data.get("days", ["Free"]),
            details=data.get("details", ""),
            tags=data.get("tags", []),
            completed_today=data.get("completed_today", False),
            perceived_effort=data.get("perceived_effort", 0),
            priority=data.get("priority", 1),
            recurring=data.get("recurring", {})
        )
    
    def get_priority_label(self):
        """Get a human-readable priority label"""
        priority_labels = {
            0: "Low",
            1: "Normal",
            2: "High",
            3: "Critical"
        }
        return priority_labels.get(self.priority, "Normal")
    
    def get_priority_color(self):
        """Get color associated with this priority level"""
        priority_colors = {
            0: "#CCCCCC",  # Light gray
            1: "#2196F3",  # Blue
            2: "#FFA726",  # Orange
            3: "#E53935"   # Red
        }
        return priority_colors.get(self.priority, "#2196F3")
