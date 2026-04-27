import pandas as pd
import os

class TaskManager:
    def __init__(self, storage_path='smart_task_architect/data/tasks.csv'):
        self.storage_path = storage_path
        self._ensure_storage()
        self.load_tasks()

    def _ensure_storage(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

    def load_tasks(self):
        if os.path.exists(self.storage_path):
            try:
                self.tasks_df = pd.read_csv(self.storage_path)
            except Exception:
                self.tasks_df = self._get_empty_df()
        else:
            self.tasks_df = self._get_empty_df()

    def _get_empty_df(self):
        return pd.DataFrame(columns=['ID', 'Task', 'Priority', 'Status'])

    def add_task(self, task, priority):
        new_id = len(self.tasks_df) + 1
        new_task = pd.DataFrame([[new_id, task, priority, 'Pending']], 
                               columns=['ID', 'Task', 'Priority', 'Status'])
        self.tasks_df = pd.concat([self.tasks_df, new_task], ignore_index=True)
        self.save_tasks()

    def delete_task(self, task_id):
        self.tasks_df = self.tasks_df[self.tasks_df['ID'] != task_id]
        self.save_tasks()

    def save_tasks(self):
        self.tasks_df.to_csv(self.storage_path, index=False)

    def get_tasks(self):
        return self.tasks_df