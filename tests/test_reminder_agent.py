import unittest
from unittest import TestCase, mock
from agents.reminder_agent import ReminderAgent


class TestReminderAgent(unittest.TestCase):

    def setUp(self):
        self.mock_chroma_client = mock.MagicMock()
        self.mock_langmem = mock.MagicMock()
        self.mock_tasks_service = mock.MagicMock()

        # Initialize ReminderAgent with mocks
        self.agent = ReminderAgent(
            chroma_client=self.mock_chroma_client,
            langmem=self.mock_langmem,
            tasks_service=self.mock_tasks_service
        )


    def test_validate_task_details_valid(self):
        """Test validation of valid task details."""
        task_details = {
            "title": "Test Task",
            "deadline": "2024-12-01",
            "goal": "Test Goal"
        }
        result = self.agent.validate_task_details(task_details)
        self.assertTrue(result, "Valid task details failed validation.")

    def test_validate_task_details_invalid_date(self):
        """Test validation of task details with an invalid date."""
        task_details = {
            "title": "Test Task",
            "deadline": "InvalidDate",
            "goal": "Test Goal"
        }
        result = self.agent.validate_task_details(task_details)
        self.assertFalse(result, "Invalid date passed validation.")

    def test_add_task(self):
        """Test adding a task."""
        task_details = {
            "title": "Test Task",
            "deadline": "2024-12-01",
            "goal": "Test Goal",
            "description": "A test task description."
        }

        self.agent.add_task(task_details)

        # Verify that the chroma_client and langmem methods were called
        self.mock_chroma_client.add.assert_called_with(task_details["title"], task_details)
        self.mock_langmem.update_context.assert_called_with(task_details)

        # Verify the Google Tasks API call
        self.mock_tasks_service.tasks().insert.assert_called()

    def test_adjust_reminder(self):
        """Test adjusting reminders."""
        mock_tasks = [
            {"title": "Task 1", "deadline": "2024-12-01", "goal": "Test Goal"},
            {"title": "Task 2", "deadline": "2024-12-05", "goal": "Test Goal"}
        ]
        self.mock_chroma_client.get_all.return_value = mock_tasks

        self.agent.adjust_reminder()

        # Verify prioritization and deadline adjustment
        self.mock_langmem.prioritize.assert_called_with(mock_tasks)

    def test_send_contextual_reminder(self):
        """Test sending a contextual reminder."""
        task_title = "Test Task"
        mock_task = {"title": task_title, "deadline": "2024-12-01", "goal": "Test Goal"}
        self.mock_chroma_client.get.return_value = mock_task
        self.mock_langmem.get_context.return_value = "Context for the task."

        self.agent.send_contextual_reminder(task_title)

        # Verify interactions
        self.mock_chroma_client.get.assert_called_with(task_title)
        self.mock_langmem.get_context.assert_called_with(mock_task)

    def test_add_task_to_google_tasks(self):
        """Test adding a task to Google Tasks."""
        task_details = {
            "title": "Test Task",
            "deadline": "2024-12-01",
            "goal": "Test Goal",
            "description": "A test task description."
        }

        self.agent.add_task_to_google_tasks(task_details)

        # Verify the Google Tasks API call
        self.mock_tasks_service.tasks().insert.assert_called()


if __name__ == "__main__":
    unittest.main()