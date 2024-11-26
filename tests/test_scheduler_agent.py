import unittest
from unittest.mock import MagicMock,patch
from datetime import datetime,timedelta
from agents.scheduler_agent import SchedulerAgent

class TestSchedulerAgent(unittest.TestCase):

    def setUp(self):

        self.mock_chroma_client=MagicMock()
        self.mock_langmem = MagicMock()
        self.mock.llm=MagicMock()
        self.mock_calendar_service=MagicMock()

        self.agent = SchedulerAgent(
            chroma_client=self.mock_chroma_client,
            langmem=self.mock_langmem,
            llm=self.mock_llm,
            calendar_service=self.mock_calendar_service
        )
    
    def test_retrieve_schedule_data(self):
        
        mock_schedules = [
            {'title': 'Meeting 1', 'start_time': '2024-12-01T10:00:00Z', 'end_time': '2024-12-01T11:00:00Z'},
            {'title': 'Meeting 2', 'start_time': '2024-12-02T12:00:00Z', 'end_time': '2024-12-02T13:00:00Z'}
        ]
        self.mock_chroma_client.get_all.return_value = mock_schedules

        schedules = self.agent.retrieve_schedule_data()
        self.assertEqual(len(schedules), 2, "Schedule data retrieval failed.")
        self.mock_chroma_client.get_all.assert_called_once()

    
    def test_identify_optimal_slots(self):
        
        meeting_details = {'duration': 60}
        self.agent._find_available_slot = MagicMock(return_value='2024-12-03T14:00:00Z')

        optimal_slot = self.agent.identify_optimal_slots(meeting_details)
        self.assertEqual(optimal_slot, '2024-12-03T14:00:00Z', "Failed to identify the optimal slot.")
        self.agent._find_available_slot.assert_called_once_with(meeting_details)

    def test_find_available_slot(self):
        
        mock_schedules = [
            {'start_time': '2024-12-01T10:00:00Z', 'end_time': '2024-12-01T11:00:00Z'},
            {'start_time': '2024-12-01T13:00:00Z', 'end_time': '2024-12-01T14:00:00Z'}
        ]
        self.mock_chroma_client.get_all.return_value = mock_schedules

        meeting_details = {'duration': 60}
        available_slot = self.agent._find_available_slot(meeting_details)

        expected_slot = '2024-12-01T11:15:00Z'  # 15 minutes after the last meeting
        self.assertEqual(available_slot, expected_slot, "Available slot calculation failed.")
    
    def test_generate_agenda(self):
        
        meeting_details = {'title': 'Project Discussion'}
        self.mock_llm.generate_text.return_value = "Agenda for Project Discussion:\n1. Updates\n2. Next Steps"

        agenda = self.agent.generate_agenda(meeting_details)
        self.assertIn("Agenda for Project Discussion", agenda, "Agenda generation failed.")
        self.mock_llm.generate_text.assert_called_once()

    def test_send_notifications(self):
        
        meeting_details = {
            'title': 'Project Discussion',
            'start_time': '2024-12-01T15:00:00Z'
        }
        agenda = "Agenda:\n1. Updates\n2. Next Steps"

        with patch("agents.scheduler_agent.logger") as mock_logger:
            self.agent.send_notifications(meeting_details, agenda)
            mock_logger.info.assert_called_with(
                f"Notification sent: Meeting 'Project Discussion' scheduled on 2024-12-01T15:00:00Z.\nAgenda:\n{agenda}"
            )
    

    def test_adjust_schedule(self):
       
        mock_events = [
            {'title': 'Meeting 1', 'start_time': '2024-12-01T10:00:00Z', 'end_time': '2024-12-01T11:00:00Z'},
            {'title': 'Meeting 2', 'start_time': '2024-12-01T10:30:00Z', 'end_time': '2024-12-01T11:30:00Z'}
        ]
        self.mock_chroma_client.get_all.return_value = mock_events

        self.agent.adjust_schedule()

       
        self.mock_chroma_client.update.assert_called()

    def test_add_event_to_google_calendar(self):
        
        event_details = {
            'title': 'Team Sync',
            'start_time': '2024-12-01T15:00:00Z',
            'end_time': '2024-12-01T16:00:00Z',
            'participants_emails': ['test@example.com']
        }

        self.agent.add_event_to_google_calendar(event_details)

        self.mock_calendar_service.events().insert.assert_called_once_with(
            calendarId='primary',
            body={
                'summary': 'Team Sync',
                'location': '',
                'description': '',
                'start': {'dateTime': '2024-12-01T15:00:00Z', 'timeZone': 'UTC'},
                'end': {'dateTime': '2024-12-01T16:00:00Z', 'timeZone': 'UTC'},
                'attendees': [{'email': 'test@example.com'}],
                'reminders': {'useDefault': True}
            }
        )


if __name__ == '__main__':
    unittest.main()
