"""
Практические задания по продвинутому ООП
Попробуй выполнить эти задания самостоятельно!
"""

from task_system import *
from datetime import datetime, timedelta


def practice_1_custom_task():
    """
    ЗАДАНИЕ 1: Создай свой тип задачи
    
    Создай класс PersonalTask, который:
    - Наследуется от BaseTask и TimestampMixin
    - Имеет дополнительное поле category (строка)
    - Приоритет зависит от категории:
      * "здоровье" -> URGENT
      * "семья" -> HIGH  
      * "хобби" -> LOW
      * остальное -> MEDIUM
    - Время выполнения: 2 часа для всех
    """
    print("🎯 ЗАДАНИЕ 1: Создай PersonalTask")
    print("Подсказка: class PersonalTask(BaseTask, TimestampMixin):")
    print("Нужно реализовать get_priority() и estimate_duration()")
    print()


def practice_2_custom_manager():
    """
    ЗАДАНИЕ 2: Расширь TaskManager
    
    Добавь методы:
    - get_tasks_by_priority(priority: Priority) -> List[BaseTask]
    - get_tasks_by_assignee(assignee: str) -> List[BaseTask]
    - get_completion_rate() -> float (процент выполненных задач)
    """
    print("🎯 ЗАДАНИЕ 2: Расширь TaskManager")
    print("Добавь новые методы для фильтрации и статистики")
    print()


def practice_3_decorators():
    """
    ЗАДАНИЕ 3: Создай декораторы для задач
    
    Создай декораторы:
    - @log_task_changes - логирует изменения статуса
    - @validate_task - проверяет валидность данных
    - @auto_assign - автоматически назначает исполнителя
    """
    print("🎯 ЗАДАНИЕ 3: Создай декораторы")
    print("Декораторы должны работать с методами start(), complete(), cancel()")
    print()


def practice_4_advanced_context():
    """
    ЗАДАНИЕ 4: Продвинутый Context Manager
    
    Создай DatabaseTaskManager, который:
    - Подключается к базе данных при входе в контекст
    - Начинает транзакцию
    - При успехе - коммитит транзакцию
    - При ошибке - откатывает транзакцию
    - Закрывает соединение при выходе
    """
    print("🎯 ЗАДАНИЕ 4: DatabaseTaskManager")
    print("Используй try/except в __exit__ для обработки транзакций")
    print()


# Решения (раскомментируй для проверки)

class PersonalTask(BaseTask, TimestampMixin):
    """Решение задания 1"""
    
    def __init__(self, title: str, description: str = "", category: str = "общее"):
        super().__init__(title, description)
        self.category = category
    
    def get_priority(self) -> Priority:
        priority_map = {
            "здоровье": Priority.URGENT,
            "семья": Priority.HIGH,
            "хобби": Priority.LOW
        }
        return priority_map.get(self.category.lower(), Priority.MEDIUM)
    
    def estimate_duration(self) -> timedelta:
        return timedelta(hours=2)


class ExtendedTaskManager(TaskManager):
    """Решение задания 2"""
    
    def get_tasks_by_priority(self, priority: Priority) -> List[BaseTask]:
        return [task for task in self.tasks if task.get_priority() == priority]
    
    def get_tasks_by_assignee(self, assignee: str) -> List[BaseTask]:
        return [task for task in self.tasks 
                if hasattr(task, 'assignee') and task.assignee == assignee]
    
    def get_completion_rate(self) -> float:
        if not self.tasks:
            return 0.0
        completed = len(self.get_tasks_by_status(TaskStatus.DONE))
        return (completed / len(self.tasks)) * 100


def log_task_changes(func):
    """Решение задания 3 - декоратор для логирования"""
    def wrapper(self, *args, **kwargs):
        old_status = self.status
        result = func(self, *args, **kwargs)
        new_status = self.status
        if old_status != new_status:
            print(f"📝 Задача '{self.title}': {old_status.value} -> {new_status.value}")
        return result
    return wrapper


def demo_solutions():
    """Демонстрация решений"""
    print("🎓 ДЕМОНСТРАЦИЯ РЕШЕНИЙ\n")
    
    # Задание 1
    print("✅ Задание 1 - PersonalTask:")
    health_task = PersonalTask("Пойти к врачу", category="здоровье")
    hobby_task = PersonalTask("Прочитать книгу", category="хобби")
    
    print(f"Здоровье: {health_task.get_priority().name}")
    print(f"Хобби: {hobby_task.get_priority().name}")
    print()
    
    # Задание 2
    print("✅ Задание 2 - ExtendedTaskManager:")
    with ExtendedTaskManager("extended_demo.json") as manager:
        manager.add_task(health_task)
        manager.add_task(hobby_task)
        
        work_task = WorkTask("Код ревью", assignee="Анна")
        manager.add_task(work_task)
        work_task.start()
        work_task.complete()
        
        print(f"Срочные задачи: {len(manager.get_tasks_by_priority(Priority.URGENT))}")
        print(f"Задачи Анны: {len(manager.get_tasks_by_assignee('Анна'))}")
        print(f"Процент выполнения: {manager.get_completion_rate():.1f}%")
    print()
    
    # Задание 3
    print("✅ Задание 3 - Декоратор логирования:")
    
    # Применяем декоратор к методам
    SimpleTask.start = log_task_changes(SimpleTask.start)
    SimpleTask.complete = log_task_changes(SimpleTask.complete)
    
    demo_task = SimpleTask("Демо задача")
    demo_task.start()
    demo_task.complete()


if __name__ == "__main__":
    print("📚 ПРАКТИЧЕСКИЕ ЗАДАНИЯ ПО ООП\n")
    
    practice_1_custom_task()
    practice_2_custom_manager()
    practice_3_decorators()
    practice_4_advanced_context()
    
    print("=" * 50)
    demo_solutions()