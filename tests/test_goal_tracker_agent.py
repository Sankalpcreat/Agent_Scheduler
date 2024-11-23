import unittest
import os
import shutil
from agents.goal_tracker_agent import GoalTrackerAgent


class TestGoalTrackerAgent(unittest.TestCase):

    def setUp(self):
        self.agent=GoalTrackerAgent()
        self.goal_details={
            'title':'Test Goal',
            'description':'A goal for testing purpose',
            'milestones':[]
        }
        self.test_data_dir='data/goals'
        if os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)
        os.makedirs(self.test_data_dir,exist_ok=True)

    def tearDown(self):
        
        if os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)

    def test_input_goal(self):
        
        self.agent.input_goal(self.goal_details)
        goal_file = os.path.join(self.test_data_dir, f"{self.goal_details['title']}.txt")
        self.assertTrue(os.path.exists(goal_file), "Goal file was not created.")

        with open(goal_file, 'r') as f:
            content = f.read()
            self.assertIn(self.goal_details['title'], content, "Goal title not found in file.")
            self.assertIn(self.goal_details['description'], content, "Goal description not found in file.")
    

    def test_log_milestone(self):
        
        self.agent.input_goal(self.goal_details)
        milestone = 'Completed initial testing'
        self.agent.log_milestone(self.goal_details['title'], milestone)
        goal_file = os.path.join(self.test_data_dir, f"{self.goal_details['title']}.txt")

        with open(goal_file, 'r') as f:
            content = f.read()
            self.assertIn(f"Milestone: {milestone}", content, "Milestone not appended to goal file.")


    def test_generate_progress_chart(self):
        
        self.agent.input_goal(self.goal_details)
        milestones = ['Milestone 1', 'Milestone 2', 'Milestone 3']
        for milestone in milestones:
            self.agent.log_milestone(self.goal_details['title'], milestone)

        try:
            self.agent.generate_progress_chart(self.goal_details['title'])
            chart_file = os.path.join(self.test_data_dir, f"{self.goal_details['title']}_progress_chart.png")
            self.assertTrue(os.path.exists(chart_file), "Progress chart image was not created.")
        except Exception as e:
            self.fail(f"generate_progress_chart raised an exception {e}")


    def test_send_motivational_reminder(self):
        
        self.agent.input_goal(self.goal_details)
        milestones = ['Milestone 1', 'Milestone 2']
        for milestone in milestones:
            self.agent.log_milestone(self.goal_details['title'], milestone)

        try:
            self.agent.send_motivational_reminder(self.goal_details['title'])
          
        except Exception as e:
            self.fail(f"send_motivational_reminder raised an exception {e}")


if __name__ == '__main__':
    unittest.main()

