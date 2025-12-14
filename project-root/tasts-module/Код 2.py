import json
import os
from datetime import datetime

# Файл для хранения задач
TASKS_FILE = "tasks.json"

class Task:
    """Класс, представляющий задачу"""
    def __init__(self, id, title, description, status="активная", created_at=None, updated_at=None):
        self.id = id
        self.title = title
        self.description = description
        self.status = status  # активная, в процессе, завершенная
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()

    def to_dict(self):
        """Преобразование задачи в словарь"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @staticmethod
    def from_dict(data):
        """Создание задачи из словаря"""
        return Task(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            status=data["status"],
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )

class TaskManager:
    """Менеджер задач"""
    def __init__(self):
        self.tasks = []
        self.load_tasks()

    def load_tasks(self):
        """Загрузка задач из файла"""
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                try:
                    tasks_data = json.load(f)
                    self.tasks = [Task.from_dict(task) for task in tasks_data]
                except json.JSONDecodeError:
                    self.tasks = []
        else:
            self.tasks = []

    def save_tasks(self):
        """Сохранение задач в файл"""
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump([task.to_dict() for task in self.tasks], f, ensure_ascii=False, indent=2)

    def create_task(self, title, description):
        """Создание новой задачи"""
        if not title.strip():
            return None, "Название задачи не может быть пустым"

        # Генерация ID
        new_id = max([task.id for task in self.tasks], default=0) + 1
        task = Task(id=new_id, title=title, description=description)
        self.tasks.append(task)
        self.save_tasks()
        return task, "Задача успешно создана"

    def get_task(self, task_id):
        """Получение задачи по ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def update_task(self, task_id, title=None, description=None, status=None):
        """Обновление задачи"""
        task = self.get_task(task_id)
        if not task:
            return False, "Задача не найдена"

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if status is not None:
            task.status = status

        task.updated_at = datetime.now().isoformat()
        self.save_tasks()
        return True, "Задача успешно обновлена"

    def delete_task(self, task_id):
        """Удаление задачи"""
        task = self.get_task(task_id)
        if not task:
            return False, "Задача не найдена"

        self.tasks = [t for t in self.tasks if t.id != task_id]
        self.save_tasks()
        return True, "Задача успешно удалена"

    def get_all_tasks(self):
        """Получение всех задач"""
        return self.tasks

    def filter_tasks(self, status=None, keyword=None):
        """Фильтрация задач по статусу и/или ключевому слову"""
        filtered = self.tasks

        if status:
            filtered = [task for task in filtered if task.status == status]

        if keyword:
            keyword_lower = keyword.lower()
            filtered = [
                task for task in filtered
                if keyword_lower in task.title.lower() or keyword_lower in task.description.lower()
            ]

        return filtered

    def change_status(self, task_id, new_status):
        """Изменение статуса задачи"""
        return self.update_task(task_id, status=new_status)

    def get_statistics(self):
        """Статистика по задачам"""
        total = len(self.tasks)
        active = len([t for t in self.tasks if t.status == "активная"])
        in_progress = len([t for t in self.tasks if t.status == "в процессе"])
        completed = len([t for t in self.tasks if t.status == "завершенная"])

        return {
            "total": total,
            "active": active,
            "in_progress": in_progress,
            "completed": completed
        }