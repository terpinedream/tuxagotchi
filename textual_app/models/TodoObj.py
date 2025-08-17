import json
import os
from typing import List

class TodoObj:
    """
    Represents a single Todo item.
    
    Attributes:
        title (str): The title or description of the todo.
        finished (bool): Whether the todo is completed.
    """
    def __init__(self, title: str, finished: bool = False):
        self.title = title
        self.finished = finished


class TodoStorage:
    """
    Handles saving and loading a list of TodoObj instances to/from a JSON file.
    
    Attributes:
        path (str): File path for storing the todo list.
    """
    def __init__(self, path: str = "todo.json"):
        """
        Initialize the storage with a file path.

        Args:
            path (str): Path to the JSON file. Defaults to 'todo.json'.
        """
        self.path = path

    def save(self, todos: List[TodoObj]) -> None:
        """
        Save a list of TodoObj to a JSON file.

        Args:
            todos (List[TodoObj]): List of todo items to save.
        """
        data = [{"title": todo.title, "finished": todo.finished} for todo in todos]
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self) -> List[TodoObj]:
        """
        Load a list of TodoObj from the JSON file.

        Returns:
            List[TodoObj]: List of todo items loaded from the file.
            Returns an empty list if the file does not exist.
        """
        if not os.path.exists(self.path):
            return []
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [TodoObj(item["title"], item["finished"]) for item in data]