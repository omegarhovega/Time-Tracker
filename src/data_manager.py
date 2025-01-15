import json
import os
from typing import Any, Dict


class DataManager:
    def __init__(self, filename="tasks.json"):
        self.filename = filename

    def load_top_tasks(self, date):
        data = self._load_data()
        date_str = date.strftime("%Y-%m-%d")
        return data.get(date_str, {}).get("top_tasks", [])

    def save_top_tasks(self, date, tasks):
        self._save_section(date, "top_tasks", tasks)

    def load_time_blocks(self, date):
        data = self._load_data()
        date_str = date.strftime("%Y-%m-%d")
        return data.get(date_str, {}).get("tasks", [])

    def save_time_blocks(self, date, blocks):
        self._save_section(date, "tasks", blocks)

    def _load_data(self) -> Dict[str, Any]:
        try:
            with open(self.filename, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save_section(self, date, section_name, data):
        all_data = self._load_data()
        date_str = date.strftime("%Y-%m-%d")
        if date_str not in all_data:
            all_data[date_str] = {}
        all_data[date_str][section_name] = data

        temp_file = f"{self.filename}.tmp"
        with open(temp_file, "w") as f:
            json.dump(all_data, f, indent=4)
        os.replace(temp_file, self.filename)
