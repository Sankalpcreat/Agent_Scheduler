from datetime import datetime, timedelta
from agents.goal_tracker_agent import GoalTrackerAgent
from agents.knowledge_retrieval_agent import KnowledgeRetrievalAgent
from agents.reminder_agent import ReminderAgent
from agents.scheduler_agent import SchedulerAgent
from loguru import logger

def main():
    logger.info("Application started.")

    try:
        # Initialize agents
        goal_tracker = GoalTrackerAgent()
        knowledge_retriever = KnowledgeRetrievalAgent()
        reminder_agent = ReminderAgent()
        scheduler_agent = SchedulerAgent()

        # Calculate current and future dates
        current_datetime = datetime.now()
        one_week_later = current_datetime + timedelta(days=7)
        one_hour_duration = timedelta(hours=1)

        # Goal Tracker Agent
        goal_details = {
            'title': 'Launch new product by Q1',
            'description': 'Develop and launch the new software product by Q1',
            'milestones': []
        }
        goal_tracker.input_goal(goal_details)
        goal_tracker.log_milestone(goal_details['title'], 'Completed market research')
        goal_tracker.generate_progress_chart(goal_details['title'])
        goal_tracker.send_motivational_reminder(goal_details['title'])

        # Knowledge Retrieval Agent
        doc_title = f'Meeting Notes {current_datetime.strftime("%Y-%m-%d")}'
        content = 'Discussed the new product launch timeline and marketing strategies.'
        knowledge_retriever.store_document(doc_title, content)
        summary = knowledge_retriever.generate_summary(doc_title)
        logger.info(f"Document Summary:\n{summary}")

        # Scheduler Agent
        meeting_details = {
            'title': 'Product Launch Meeting',
            'participants': ['Alice', 'Bob', 'Charlie'],
            'participants_emails': ['alice@example.com', 'bob@example.com', 'charlie@example.com'],
            'time_zone': 'UTC'
        }
        optimal_slot = scheduler_agent.identify_optimal_slots(meeting_details)
        meeting_details['start_time'] = optimal_slot
        meeting_details['end_time'] = (datetime.fromisoformat(optimal_slot) + one_hour_duration).isoformat()
        meeting_details['description'] = summary
        agenda = scheduler_agent.generate_agenda(meeting_details)
        meeting_details['description'] += f"\nAgenda:\n{agenda}"
        event_result = scheduler_agent.add_event_to_google_calendar(meeting_details)
        scheduler_agent.send_notifications(meeting_details, agenda)
        scheduler_agent.adjust_schedule()

        # Reminder Agent
        task_details = {
            'title': 'Prepare marketing plan',
            'deadline': one_week_later.strftime('%Y-%m-%d'),
            'goal': 'Launch new product by Q1',
            'description': 'Develop a comprehensive marketing plan for the new product.'
        }
        reminder_agent.add_task(task_details)
        reminder_agent.adjust_reminders()
        reminder_agent.send_contextual_reminder(task_details['title'])

        # Add meeting as a task to Reminder Agent
        reminder_task = {
            'title': f"Attend {meeting_details['title']}",
            'deadline': one_week_later.strftime('%Y-%m-%d'),
            'goal': 'Participate in scheduled meetings',
            'description': meeting_details['description']
        }
        reminder_agent.add_task(reminder_task)

        logger.info("Application finished successfully.")

    except Exception as e:
        logger.exception("An error occurred in the main application.")

if __name__ == '__main__':
    main()
