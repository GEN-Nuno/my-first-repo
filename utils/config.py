"""
Application configuration settings
"""
import os

# Application information
APP_NAME = "Task Scheduler"
APP_VERSION = "1.0.0"

# Base paths
BASE_DIR = "c:\\SH"
CONFIG_DIR = BASE_DIR
LOG_DIR = os.path.join(BASE_DIR, "logs")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
EXPORT_DIR = os.path.join(BASE_DIR, "exports")

# Ensure directories exist
for directory in [LOG_DIR, BACKUP_DIR, EXPORT_DIR]:
    os.makedirs(directory, exist_ok=True)

# Data file paths
DATA_FILES = {
    "tasks": os.path.join(CONFIG_DIR, "task_Lists.conf"),
    "tags": os.path.join(CONFIG_DIR, "tags.conf"),
    "work_time": os.path.join(CONFIG_DIR, "work_time.conf"),
    "today_tasks": os.path.join(CONFIG_DIR, "todaytask.conf")
}

# Language settings
DEFAULT_LANGUAGE = "en"  # 'en' for English, 'ja' for Japanese

# UI settings
UI_THEME = "light"  # 'light' or 'dark'

# Default hours in workday
DEFAULT_WORK_HOURS = 8.0
