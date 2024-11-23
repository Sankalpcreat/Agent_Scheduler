from chromadb import Client
from langmem import LangMem
from loguru import logger
import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from agents.google_auth import authenticate_google_api

class ReminderAgent:

    def __init__(self, chroma_client=None, langmem=None, tasks_service=None):
        try:
            self.chroma_client = chroma_client or Client(path='data/tasks/')
            self.langmem = langmem or LangMem()
            if tasks_service:
                self.tasks_service = tasks_service
            else:
                self.creds = authenticate_google_api()
                self.tasks_service = build('tasks', 'v1', credentials=self.creds)
            logger.info("ReminderAgent initialized successfully with Google Tasks API.")
        except Exception as e:
            logger.exception("Failed to initialize ReminderAgent.")
            raise e
        
    
    def add_task(self,task_details):
        try:
            if not self.validate_task_details(task_details):
                raise ValueError("Invalid task details.")
            self.chroma_client.add(task_details['title'],task_details)
            self.langmem.update_context(task_details)
            logger.info(f"Task '{task_details['title']}' added.")
            self.add_task_to_google_task(task_details)
        except ValueError as ve:
            logger.error(f"Validation error: {ve}")
        except HttpError as he:
            logger.error(f"HTTP error occurred: {he}")
        except Exception as e:
            logger.exception("Unexpected error in add_task.")
        raise e
    
    def validate_task_details(self, task_details):
        required_keys = ['title', 'deadline', 'goal']
        for key in required_keys:
            if key not in task_details:
                logger.error(f"Task detail missing required key: {key}")
                return False
        try:
            datetime.datetime.strptime(task_details['deadline'], '%Y-%m-%d')
        except ValueError:
            logger.error("Deadline format should be YYYY-MM-DD.")
            return False
        return True
    

    def adjust_reminder(self):
        try:
            tasks=self.chroma_client.get_all()
            prioritized_tasks=self.langmem.prioritize(tasks)
            for task in prioritized_tasks:
                deadline = datetime.datetime.strptime(task['deadline'], '%Y-%m-%d').date()
            days_left = (deadline - datetime.date.today()).days
            message = f"Reminder: '{task['title']}' is due in {days_left} days."
            logger.info(message)
           
        except Exception as e:
            logger.exception("Error in adjust_reminders.")
            raise e
        
    def send_contextual_reminder(self, task_title):
        try:
            task = self.chroma_client.get(task_title)
            if not task:
                raise ValueError(f"Task '{task_title}' not found.")
            context = self.langmem.get_context(task)
            message = f"Reminder: Complete '{task_title}'. {context}"
            logger.info(message)
        
        except ValueError as ve:
            logger.error(f"Validation error: {ve}")
        except Exception as e:
            logger.exception("Unexpected error in send_contextual_reminder.")
            raise e
         

    def add_task_to_google_tasks(self,task_details):
        task={
            'title':task_details['title'],
            'notes':task_details.get('description',''),
            'due':task_details['deadline']+'T00:00:00Z',
        }
        try:
            result = self.tasks_service.tasks().insert(tasklist='@default', body=task).execute()
            logger.info(f"Task added to Google Tasks: {result.get('title')}")
            return result
        except HttpError as he:
            logger.error(f"HTTP error occurred while adding task to Google Tasks: {he}")
        except Exception as e:
            logger.exception("Unexpected error adding task to Google Tasks.")
        raise e