"""
Система управления задачами - Продвинутое ООП
Изучаем: ABC, множественное наследование, property, magic methods, context managers
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Dict, Any
import json


class TaskStatus(Enum):
    """Статусы задач"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class Priority(Enum):
    """Приоритеты задач"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


# Абстрактный базовый класс
class BaseTask(ABC):
    """Абстрактный базовый класс для всех задач"""
    
    def __init__(self, title: str, description: str = ""):
        self._title = title
        self._description = description
        self._created_at = datetime.now()
        self._status = TaskStatus.TODO
        self._id = id(self)  # Простой ID на основе адреса в памяти
    
    @property
    def title(self) -> str:
        """Геттер для заголовка"""
        return self._title
    
    @title.setter
    def title(self, value: str) -> None:
        """Сеттер для заголовка с валидацией"""
        if not value or not value.strip():
            raise ValueError("Заголовок не может быть пустым")
        self._title = value.strip()
    
    @property
    def description(self) -> str:
        return self._description
    
    @description.setter
    def description(self, value: str) -> None:
        self._description = value.strip()
    
    @property
    def status(self) -> TaskStatus:
        return self._status
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def id(self) -> int:
        return self._id
    
    @abstractmethod
    def get_priority(self) -> Priority:
        """Абстрактный метод - каждый тип задачи определяет свой приоритет"""
        pass
    
    @abstractmethod
    def estimate_duration(self) -> timedelta:
        """Абстрактный метод - оценка времени выполнения"""
        pass
    
    def start(self) -> None:
        """Начать выполнение задачи"""
        if self._status == TaskStatus.TODO:
            self._status = TaskStatus.IN_PROGRESS
        else:
            raise ValueError(f"Нельзя начать задачу со статусом {self._status.value}")
    
    def complete(self) -> None:
        """Завершить задачу"""
        if self._status == TaskStatus.IN_PROGRESS:
            self._status = TaskStatus.DONE
        else:
            raise ValueError(f"Нельзя завершить задачу со статусом {self._status.value}")
    
    def cancel(self) -> None:
        """Отменить задачу"""
        if self._status in [TaskStatus.TODO, TaskStatus.IN_PROGRESS]:
            self._status = TaskStatus.CANCELLED
        else:
            raise ValueError(f"Нельзя отменить задачу со статусом {self._status.value}")
    
    # Magic methods
    def __str__(self) -> str:
        """Строковое представление для пользователей"""
        return f"{self.title} ({self.status.value})"
    
    def __repr__(self) -> str:
        """Строковое представление для разработчиков"""
        return f"{self.__class__.__name__}(id={self.id}, title='{self.title}', status='{self.status.value}')"
    
    def __eq__(self, other) -> bool:
        """Сравнение задач по ID"""
        if not isinstance(other, BaseTask):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Хэш для использования в множествах и словарях"""
        return hash(self.id)


# Миксины для дополнительной функциональности
class TimestampMixin:
    """Миксин для отслеживания времени изменений"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._updated_at = datetime.now()
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    def _update_timestamp(self) -> None:
        """Обновить временную метку"""
        self._updated_at = datetime.now()


class AssigneeMixin:
    """Миксин для назначения исполнителя"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._assignee: Optional[str] = None
    
    @property
    def assignee(self) -> Optional[str]:
        return self._assignee
    
    @assignee.setter
    def assignee(self, value: Optional[str]) -> None:
        self._assignee = value
        if hasattr(self, '_update_timestamp'):
            self._update_timestamp()


# Конкретные классы задач с множественным наследованием
class SimpleTask(BaseTask, TimestampMixin):
    """Простая задача"""
    
    def __init__(self, title: str, description: str = "", priority: Priority = Priority.MEDIUM):
        super().__init__(title, description)
        self._priority = priority
    
    def get_priority(self) -> Priority:
        return self._priority
    
    def estimate_duration(self) -> timedelta:
        # Простая задача - от 30 минут до 2 часов в зависимости от приоритета
        base_hours = {
            Priority.LOW: 0.5,
            Priority.MEDIUM: 1,
            Priority.HIGH: 1.5,
            Priority.URGENT: 2
        }
        return timedelta(hours=base_hours[self._priority])


class WorkTask(BaseTask, TimestampMixin, AssigneeMixin):
    """Рабочая задача с исполнителем"""
    
    def __init__(self, title: str, description: str = "", assignee: Optional[str] = None):
        super().__init__(title, description)
        self.assignee = assignee
    
    def get_priority(self) -> Priority:
        # Рабочие задачи по умолчанию имеют высокий приоритет
        return Priority.HIGH
    
    def estimate_duration(self) -> timedelta:
        # Рабочие задачи обычно занимают больше времени
        return timedelta(hours=4)


class UrgentTask(BaseTask, TimestampMixin, AssigneeMixin):
    """Срочная задача"""
    
    def __init__(self, title: str, description: str = "", deadline: Optional[datetime] = None):
        super().__init__(title, description)
        self._deadline = deadline or (datetime.now() + timedelta(hours=24))
    
    @property
    def deadline(self) -> datetime:
        return self._deadline
    
    @property
    def is_overdue(self) -> bool:
        """Проверка просрочки"""
        return datetime.now() > self._deadline and self.status != TaskStatus.DONE
    
    def get_priority(self) -> Priority:
        return Priority.URGENT
    
    def estimate_duration(self) -> timedelta:
        return timedelta(hours=1)


# Context Manager для работы с задачами
class TaskManager:
    """Менеджер задач с context manager функциональностью"""
    
    def __init__(self, filename: str = "tasks.json"):
        self.filename = filename
        self.tasks: List[BaseTask] = []
        self._in_context = False
    
    def add_task(self, task: BaseTask) -> None:
        """Добавить задачу"""
        self.tasks.append(task)
    
    def get_task_by_id(self, task_id: int) -> Optional[BaseTask]:
        """Найти задачу по ID"""
        return next((task for task in self.tasks if task.id == task_id), None)
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[BaseTask]:
        """Получить задачи по статусу"""
        return [task for task in self.tasks if task.status == status]
    
    def get_overdue_tasks(self) -> List[UrgentTask]:
        """Получить просроченные задачи"""
        return [task for task in self.tasks 
                if isinstance(task, UrgentTask) and task.is_overdue]
    
    # Context Manager методы
    def __enter__(self):
        """Вход в контекст - загружаем задачи из файла"""
        print(f"📂 Загружаем задачи из {self.filename}")
        self._in_context = True
        try:
            self._load_tasks()
        except FileNotFoundError:
            print("📝 Файл не найден, создаем новый список задач")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Выход из контекста - сохраняем задачи в файл"""
        if exc_type is None:
            print(f"💾 Сохраняем задачи в {self.filename}")
            self._save_tasks()
        else:
            print(f"❌ Ошибка: {exc_val}, задачи не сохранены")
        self._in_context = False
        return False  # Не подавляем исключения
    
    def _load_tasks(self) -> None:
        """Загрузить задачи из файла (упрощенная версия)"""
        # В реальном проекте здесь была бы десериализация
        pass
    
    def _save_tasks(self) -> None:
        """Сохранить задачи в файл (упрощенная версия)"""
        # В реальном проекте здесь была бы сериализация
        task_data = []
        for task in self.tasks:
            task_data.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status.value,
                'type': task.__class__.__name__,
                'created_at': task.created_at.isoformat()
            })
        
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(task_data, f, ensure_ascii=False, indent=2)
    
    def __len__(self) -> int:
        """Количество задач"""
        return len(self.tasks)
    
    def __iter__(self):
        """Итерация по задачам"""
        return iter(self.tasks)


# Демонстрация всех возможностей
def demo():
    """Демонстрация продвинутого ООП"""
    print("🚀 Демонстрация продвинутого ООП в Python\n")
    
    # Создаем разные типы задач
    simple = SimpleTask("Изучить Python", "Основы ООП", Priority.HIGH)
    work = WorkTask("Написать отчет", "Квартальный отчет", "Иван Петров")
    urgent = UrgentTask("Исправить баг", "Критический баг в продакшене")
    
    print("📋 Созданные задачи:")
    print(f"1. {simple} - Приоритет: {simple.get_priority().name}")
    print(f"2. {work} - Исполнитель: {work.assignee}")
    print(f"3. {urgent} - Дедлайн: {urgent.deadline.strftime('%Y-%m-%d %H:%M')}")
    print()
    
    # Демонстрация Context Manager
    print("🔄 Работа с Context Manager:")
    with TaskManager("demo_tasks.json") as manager:
        manager.add_task(simple)
        manager.add_task(work)
        manager.add_task(urgent)
        
        print(f"Всего задач: {len(manager)}")
        
        # Работаем с задачами
        simple.start()
        work.start()
        work.complete()
        
        print("\n📊 Статистика:")
        print(f"TODO: {len(manager.get_tasks_by_status(TaskStatus.TODO))}")
        print(f"В работе: {len(manager.get_tasks_by_status(TaskStatus.IN_PROGRESS))}")
        print(f"Выполнено: {len(manager.get_tasks_by_status(TaskStatus.DONE))}")
        
        # Проверяем просроченные
        overdue = manager.get_overdue_tasks()
        if overdue:
            print(f"⚠️ Просроченных задач: {len(overdue)}")
    
    print("\n✅ Демонстрация завершена!")
    
    # Демонстрация magic methods
    print("\n🎭 Magic Methods:")
    print(f"str(simple): {str(simple)}")
    print(f"repr(simple): {repr(simple)}")
    print(f"simple == work: {simple == work}")
    print(f"hash(simple): {hash(simple)}")


if __name__ == "__main__":
    demo()