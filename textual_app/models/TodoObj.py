import json
import os

class TodoObj:
    def __init__(self, title, finished = False):
        self.title = title
        self.finished = finished

class TodoStorage:
    def __init__(self, path="todo.json"):
        self.path = path

    def save(self, todos):
        data = [{"title": todo.title, "finished": todo.finished} for todo in todos]
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self):
        if not os.path.exists(self.path):
            return []
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [TodoObj(item["title"], item["finished"]) for item in data]