import unittest
from unittest import mock
from agents.reminder_agent import ReminderAgent

class TestReminderAgent(unittest.TestCase):

    def setUp(self):
        
        self.mock_chroma_client = mock.MagicMock()
        self.mock_langmem_client = mock.MagicMock()
        self.mock_tasks_service = mock.MagicMock()

        
        self.agent = ReminderAgent(
            chroma_client=self.mock_chroma_client,
            langmem_client=self.mock_langmem_client,
            tasks_service=self.mock_tasks_service
        )

    def test_validate_task_details_valid(self):
        
        task_details = {
            "title": "Test Task",
            "deadline": "2024-12-01",
            "goal": "Test Goal"
        }
        result = self.agent.validate_task_details(task_details)
        self.assertTrue(result, "Valid task details failed validation.")

    def test_validate_task_details_invalid_date(self):
        
        task_details = {
            "title": "Test Task",
            "deadline": "InvalidDate",
            "goal": "Test Goal"
        }
        result = self.agent.validate_task_details(task_details)
        self.assertFalse(result, "Invalid date passed validation.")

    def test_add_task(self):
        
        task_details = {
            "title": "Test Task",
            "deadline": "2024-12-01",
            "goal": "Test Goal",
            "description": "A test task description."
        }

        self.agent.add_task(task_details)

        
        self.mock_chroma_client.add.assert_called_with(task_details["title"], task_details)
        self.mock_langmem_client.add_memory.assert_called_with(task_details)

        
        self.mock_tasks_service.tasks().insert.assert_called()

    def test_adjust_reminder(self):
        
        mock_tasks = [
            {"title": "Task 1", "deadline": "2024-12-01", "goal": "Test Goal"},
            {"title": "Task 2", "deadline": "2024-12-05", "goal": "Test Goal"}
        ]
        self.mock_chroma_client.get_all.return_value = mock_tasks

        self.agent.adjust_reminder()

        
        self.mock_langmem_client.prioritize.assert_called_with(mock_tasks)

    def test_send_contextual_reminder(self):
        
        task_title = "Test Task"
        mock_task = {"title": task_title, "deadline": "2024-12-01", "goal": "Test Goal"}
        self.mock_chroma_client.get.return_value = mock_task
        self.mock_langmem_client.get_context.return_value = "Context for the task."

        self.agent.send_contextual_reminder(task_title)

        
        self.mock_chroma_client.get.assert_called_with(task_title)
        self.mock_langmem_client.get_context.assert_called_with(mock_task)

    def test_add_task_to_google_tasks(self):
        
        task_details = {
            "title": "Test Task",
            "deadline": "2024-12-01",
            "goal": "Test Goal",
            "description": "A test task description."
        }

        self.agent.add_task_to_google_tasks(task_details)

        
        self.mock_tasks_service.tasks().insert.assert_called()

if __name__ == "__main__":
    unittest.main()