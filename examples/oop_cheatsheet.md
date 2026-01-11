# 🐍 Продвинутое ООП в Python - Шпаргалка

## 🎯 Что мы изучили (9:00-10:30)

### 1. Абстрактные классы (ABC)
```python
from abc import ABC, abstractmethod

class BaseTask(ABC):
    @abstractmethod
    def get_priority(self):
        pass
```
**Зачем:** Определяет интерфейс, который должны реализовать наследники

### 2. Property декораторы
```python
@property
def title(self):
    return self._title

@title.setter  
def title(self, value):
    if not value:
        raise ValueError("Пустой заголовок")
    self._title = value
```
**Зачем:** Контролируемый доступ к атрибутам с валидацией

### 3. Magic Methods
```python
def __str__(self):      # Для пользователей
    return f"{self.title} ({self.status})"

def __repr__(self):     # Для разработчиков  
    return f"Task(id={self.id})"

def __eq__(self, other): # Сравнение
    return self.id == other.id

def __hash__(self):     # Для set/dict
    return hash(self.id)
```

### 4. Множественное наследование + Миксины
```python
class TimestampMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Важно!
        self._updated_at = datetime.now()

class WorkTask(BaseTask, TimestampMixin, AssigneeMixin):
    pass  # Получает функциональность от всех родителей
```
**Правило:** Всегда используй `super()` в миксинах!

### 5. Context Managers
```python
class TaskManager:
    def __enter__(self):
        # Подготовка ресурсов
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Очистка ресурсов
        if exc_type is None:
            self.save()  # Успех
        else:
            print(f"Ошибка: {exc_val}")  # Ошибка
        return False  # Не подавляем исключения
```

## 🔥 Ключевые принципы

### MRO (Method Resolution Order)
```python
class A: pass
class B(A): pass  
class C(A): pass
class D(B, C): pass

print(D.__mro__)  # Порядок поиска методов
```

### Композиция vs Наследование
- **Наследование:** "является" (Task IS-A BaseTask)
- **Композиция:** "содержит" (TaskManager HAS-A List[Task])

### SOLID принципы
- **S**ingle Responsibility - один класс = одна ответственность
- **O**pen/Closed - открыт для расширения, закрыт для изменения
- **L**iskov Substitution - наследники заменяют родителей
- **I**nterface Segregation - много маленьких интерфейсов
- **D**ependency Inversion - зависимость от абстракций

## ⚡ Практические советы

### 1. Когда использовать ABC
```python
# ✅ Хорошо - определяет контракт
class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount): pass

# ❌ Плохо - нет общего интерфейса
class Animal(ABC): pass
```

### 2. Property vs обычные атрибуты
```python
# ✅ Используй property для:
@property
def age(self):
    return (datetime.now() - self.birth_date).days // 365

# ❌ Не нужно для простых атрибутов
@property  
def name(self):
    return self._name  # Просто используй self.name
```

### 3. Миксины должны быть маленькими
```python
# ✅ Хорошо - одна функция
class TimestampMixin:
    def update_timestamp(self): pass

# ❌ Плохо - слишком много функций
class EverythingMixin:
    def timestamp(self): pass
    def validate(self): pass  
    def serialize(self): pass
```

## 🎯 Следующий шаг: Декораторы + Type Hints (10:30-12:00)

Готов продолжить? Переходим к созданию собственных декораторов! 🚀