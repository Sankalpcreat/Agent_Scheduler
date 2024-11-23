import os
import datetime
from dotenv import load_dotenv
from loguru import logger
from chromadb import Client
from langchain.llms import OpenAI
from langmem import LangMem
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from agents.google_auth import authenticate_google_api

class SchedulerAgent:
    """
    Agent responsible for optimizing meeting schedules and handling notifications.
    """

    def __init__(self, chroma_client=None, langmem=None, llm=None, calendar_service=None):
        try:
            
            load_dotenv()
            self.chroma_client = chroma_client or Client(path='data/schedules/')
            self.langmem = langmem or LangMem()
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if not openai_api_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set.")
            self.llm = llm or OpenAI(api_key=openai_api_key)

            if calendar_service:
                self.calendar_service = calendar_service
            else:
                self.creds = authenticate_google_api()
                self.calendar_service = build('calendar', 'v3', credentials=self.creds)

            logger.info("SchedulerAgent initialized successfully with Google Calendar API.")
        except Exception as e:
            logger.exception("Failed to initialize SchedulerAgent.")
            raise e

    def retrieve_schedule_data(self):
        
        try:
            schedules = self.chroma_client.get_all()
            logger.info(f"Retrieved {len(schedules)} scheduled events.")
            return schedules
        except Exception as e:
            logger.exception("Error in retrieve_schedule_data.")
            raise e

    def identify_optimal_slots(self, meeting_details):
        
        try:
            optimal_slot = self._find_available_slot(meeting_details)
            logger.info(f"Optimal meeting slot identified: {optimal_slot}")
            return optimal_slot
        except Exception as e:
            logger.exception("Error in identify_optimal_slots.")
            raise e

    def _find_available_slot(self, meeting_details):
        
        try:
            events = self.retrieve_schedule_data()

            duration_minutes = meeting_details.get('duration', 60)

            sorted_events = sorted(events, key=lambda x: x['start_time'])
            available_slot = None
            for i in range(len(sorted_events) - 1):
                current_end = datetime.datetime.strptime(sorted_events[i]['end_time'], '%Y-%m-%dT%H:%M:%SZ')
                next_start = datetime.datetime.strptime(sorted_events[i + 1]['start_time'], '%Y-%m-%dT%H:%M:%SZ')

                if (next_start - current_end).total_seconds() / 60 >= duration_minutes:
                    available_slot = current_end + datetime.timedelta(minutes=15)
                    break

            if not available_slot:
                last_event_end = datetime.datetime.strptime(sorted_events[-1]['end_time'], '%Y-%m-%dT%H:%M:%SZ')
                available_slot = last_event_end + datetime.timedelta(minutes=15)

            available_slot_str = available_slot.strftime('%Y-%m-%dT%H:%M:%SZ')
            logger.info(f"Available slot identified: {available_slot_str}")
            return available_slot_str
        except Exception as e:
            logger.exception("Error in _find_available_slot.")
            raise e

    def generate_agenda(self, meeting_details):
        
        try:
            agenda_prompt = f"Create a detailed agenda for a meeting about {meeting_details['title']}."
            agenda = self.llm.generate_text(agenda_prompt)
            logger.info(f"Agenda generated for meeting '{meeting_details['title']}'.")
            return agenda
        except Exception as e:
            logger.exception("Error in generate_agenda.")
            raise e

    def send_notifications(self, meeting_details, agenda):
      
        try:
            notification_message = (
                f"Meeting '{meeting_details['title']}' scheduled on {meeting_details['start_time']}.\n"
                f"Agenda:\n{agenda}"
            )
            logger.info(f"Notification sent: {notification_message}")
            
        except Exception as e:
            logger.exception("Error in send_notifications.")
            raise e

    def adjust_schedule(self):
        
        try:
            events = self.retrieve_schedule_data()
            if not events:
                logger.info("No scheduled events found to adjust.")
                return
            
            adjusted_events = []
            for event in events:
                start_time = datetime.datetime.strptime(event['start_time'], '%Y-%m-%dT%H:%M:%SZ')
                end_time = datetime.datetime.strptime(event['end_time'], '%Y-%m-%dT%H:%M:%SZ')

                for other_event in events:
                    if event == other_event:
                        continue
                    other_start = datetime.datetime.strptime(other_event['start_time'], '%Y-%m-%dT%H:%M:%SZ')
                    other_end = datetime.datetime.strptime(other_event['end_time'], '%Y-%m-%dT%H:%M:%SZ')

                    if (start_time < other_end and end_time > other_start):
                        logger.warning(f"Conflict detected between '{event['title']}' and '{other_event['title']}'.")
                        adjusted_start = other_end + datetime.timedelta(minutes=15)
                        adjusted_end = adjusted_start + (end_time - start_time)
                        event['start_time'] = adjusted_start.strftime('%Y-%m-%dT%H:%M:%SZ')
                        event['end_time'] = adjusted_end.strftime('%Y-%m-%dT%H:%M:%SZ')
                        logger.info(f"Adjusted event '{event['title']}' to start at {event['start_time']} and end at {event['end_time']}.")
                        break
                adjusted_events.append(event)

            for adjusted_event in adjusted_events:
                self.chroma_client.update(adjusted_event['title'], adjusted_event)

            logger.info("Schedule adjustments completed.")
        except Exception as e:
            logger.exception("Error in adjust_schedule.")
            raise e

    def add_event_to_google_calendar(self, event_details):
        
        event = {
            'summary': event_details['title'],
            'location': event_details.get('location', ''),
            'description': event_details.get('description', ''),
            'start': {
                'dateTime': event_details['start_time'],
                'timeZone': event_details.get('time_zone', 'UTC'),
            },
            'end': {
                'dateTime': event_details['end_time'],
                'timeZone': event_details.get('time_zone', 'UTC'),
            },
            'attendees': [{'email': email} for email in event_details.get('participants_emails', [])],
            'reminders': {
                'useDefault': True,
            },
        }
        try:
            event_result = self.calendar_service.events().insert(calendarId='primary', body=event).execute()
            logger.info(f"Event created: {event_result.get('htmlLink')}")
            return event_result
        except HttpError as he:
            logger.error(f"HTTP error occurred while adding event to Google Calendar: {he}")
            raise he
        except Exception as e:
            logger.exception("Unexpected error adding event to Google Calendar.")
            raise e
