from letta import create_client, EmbeddingConfig, LLMConfig
from loguru import logger
import os
import matplotlib.pyplot as plt

class GoalTrackerAgent:
    def __init__(self):
        try:
            self.client = create_client()
            self.client.set_default_embedding_config(
                EmbeddingConfig.default_config(model_name="text-embedding-ada-002")
            )
            self.client.set_default_llm_config(
                LLMConfig.default_config(model_name="gpt-4")
            )
            self.agent_state = self.client.create_agent(
                name="GoalTrackerAgent",
                include_base_tools=True
            )
            os.makedirs('data/goals/', exist_ok=True)
            logger.info("GoalTrackerAgent initialized successfully.")
        except Exception as e:
            logger.exception("Failed to initialize GoalTrackerAgent.")
            raise e

    def input_goal(self, goal_details):
        try:
            goal_file = f"data/goals/{goal_details['title']}.txt"
            with open(goal_file, 'w') as f:
                f.write(str(goal_details))
            logger.info(f"Goal '{goal_details['title']}' saved.")
        except Exception as e:
            logger.exception("Error in input_goal.")
            raise e

    def log_milestone(self, goal_title, milestone):
        try:
            goal_file = f"data/goals/{goal_title}.txt"
            with open(goal_file, 'a') as f:
                f.write(f"\nMilestone: {milestone}")
            logger.info(f"Milestone '{milestone}' added to goal '{goal_title}'.")
        except Exception as e:
            logger.exception("Error in log_milestone.")
            raise e

    def generate_progress_chart(self, goal_title):
        try:
            goal_file = f"data/goals/{goal_title}.txt"
            with open(goal_file, 'r') as f:
                lines = f.readlines()

            milestones = [line.strip().split(': ')[1] for line in lines if line.startswith('Milestone')]

            plt.figure(figsize=(10, 5))
            plt.plot(range(1, len(milestones) + 1), milestones, marker='o')
            plt.title(f"Progress Chart for '{goal_title}'")
            plt.xlabel('Milestone Number')
            plt.ylabel('Milestone Description')
            plt.grid(True)
            plt.savefig(f"data/goals/{goal_title}_progress_chart.png")
            plt.show()
            logger.info(f"Progress chart for '{goal_title}' generated.")
        except Exception as e:
            logger.exception("Error in generate_progress_chart.")
            raise e

    def send_motivational_reminder(self, goal_title):
        try:
            goal_file = f"data/goals/{goal_title}.txt"
            with open(goal_file, 'r') as f:
                lines = f.readlines()

            total_milestones = len([line for line in lines if line.startswith('Milestone')])
            progress = (total_milestones / 10) * 100

            message = f"You're {progress}% closer to achieving '{goal_title}'!"
            logger.info(f"Motivational reminder sent: {message}")
        except Exception as e:
            logger.exception("Error in send_motivational_reminder.")
            raise e