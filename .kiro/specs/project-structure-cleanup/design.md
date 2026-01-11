# Design Document: Project Structure Cleanup

## Overview

Этот дизайн описывает реорганизацию структуры проекта bookstore для улучшения читаемости и профессионального вида. Основная цель - очистить корневую директорию от множества конфигурационных файлов, сгруппировав их логически в отдельные папки.

## Architecture

### Current Structure Analysis
Текущая корневая директория содержит:
- 15+ конфигурационных файлов (.yml, .conf, .sql)
- Основные файлы проекта (README, LICENSE, requirements)
- Docker файлы
- Скрипты и утилиты
- Документацию

### Target Structure
```
bookstore/
├── README.md                    # Основная документация
├── README_RU.md                # Русская документация  
├── LICENSE                     # Лицензия
├── CHANGELOG.md                # История изменений
├── CONTRIBUTING.md             # Руководство для контрибьюторов
├── requirements.txt            # Python зависимости
├── pyproject.toml             # Python конфигурация
├── pytest.ini                # Конфигурация тестов
├── Dockerfile                 # Docker образ
├── docker-compose.yml         # Docker композиция для разработки
├── docker-compose.prod.yml    # Docker композиция для продакшена
├── Makefile                   # Команды сборки
├── run_bookstore.py          # Точка входа приложения
├── create_test_data.py       # Утилита создания тестовых данных
├── bookstore/                # Основной код приложения
├── tests/                    # Тесты
├── docs/                     # Документация
├── examples/                 # Примеры кода
├── scripts/                  # Все скрипты
├── config/                   # Конфигурационные файлы
├── database/                 # SQL файлы и схемы БД
├── k8s/                      # Kubernetes манифесты
├── grafana/                  # Grafana конфигурация
└── .kiro/                    # Kiro спецификации
```

## Components and Interfaces

### Directory Structure Components

#### 1. Config Directory (`config/`)
**Purpose:** Централизованное хранение всех конфигурационных файлов
**Contents:**
- `nginx.conf` - Nginx конфигурация для разработки
- `nginx-prod.conf` - Nginx конфигурация для продакшена
- `prometheus.yml` - Конфигурация мониторинга Prometheus
- `loki.yml` - Конфигурация логирования Loki
- `promtail.yml` - Конфигурация сбора логов
- `redis.conf` - Конфигурация Redis

#### 2. Database Directory (`database/`)
**Purpose:** Хранение SQL файлов и схем базы данных
**Contents:**
- `init.sql` - Инициализация БД для разработки
- `init-prod.sql` - Инициализация БД для продакшена
- `migrations/` (будущее расширение)

#### 3. Scripts Directory (расширение существующего)
**Purpose:** Все исполняемые скрипты проекта
**Contents:**
- Существующие скрипты из `scripts/`
- `backup-script.sh` - Скрипт резервного копирования
- Другие утилитарные скрипты

### File Movement Strategy

#### Phase 1: Configuration Files
1. Создать директорию `config/`
2. Переместить конфигурационные файлы:
   - `nginx.conf` → `config/nginx.conf`
   - `nginx-prod.conf` → `config/nginx-prod.conf`
   - `prometheus.yml` → `config/prometheus.yml`
   - `loki.yml` → `config/loki.yml`
   - `promtail.yml` → `config/promtail.yml`
   - `redis.conf` → `config/redis.conf`

#### Phase 2: Database Files
1. Создать директорию `database/`
2. Переместить SQL файлы:
   - `init.sql` → `database/init.sql`
   - `init-prod.sql` → `database/init-prod.sql`

#### Phase 3: Scripts
1. Переместить скрипты в существующую директорию `scripts/`:
   - `backup-script.sh` → `scripts/backup-script.sh`

## Data Models

### File Reference Update Map
```python
file_moves = {
    "config/nginx.conf": [
        "docker-compose.yml",
        "docker-compose.prod.yml"
    ],
    "config/nginx-prod.conf": [
        "docker-compose.prod.yml",
        "k8s/api-deployment.yaml"
    ],
    "config/prometheus.yml": [
        "docker-compose.yml",
        "k8s/monitoring.yaml"
    ],
    "database/init.sql": [
        "docker-compose.yml"
    ],
    "database/init-prod.sql": [
        "docker-compose.prod.yml"
    ]
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

<function_calls>
<invoke name="prework">
<parameter name="featureName">project-structure-cleanup

### Property Reflection

После анализа всех свойств, выявлены следующие группы для объединения:
- Свойства 1.2 и 1.3 можно объединить в одно свойство о наличии essential файлов
- Свойства 2.1 и 3.1 можно объединить в одно свойство о создании необходимых директорий
- Свойства 5.1, 5.2, 5.3 можно объединить в одно свойство о обновлении всех ссылок
- Свойства 6.1, 6.2, 6.3 можно объединить в одно свойство о обновлении документации

Property 1: Root directory contains only essential files
*For any* project after reorganization, the root directory should contain only essential files (README, LICENSE, Docker files, Python package files) and no more than 20 files total
**Validates: Requirements 1.1, 1.2, 1.3, 1.4**

Property 2: Required directories exist
*For any* reorganized project, the config and database directories should exist and contain the appropriate files
**Validates: Requirements 2.1, 3.1**

Property 3: Files are preserved during move
*For any* file that is moved, the file should exist in the new location with identical content
**Validates: Requirements 2.2, 2.3, 3.2, 4.2**

Property 4: All references are updated
*For any* moved file, all references to that file in other files should point to the new location
**Validates: Requirements 2.4, 3.3, 4.3, 5.1, 5.2, 5.3**

Property 5: File permissions are preserved
*For any* moved file, the file permissions and executable flags should be identical to the original
**Validates: Requirements 4.4, 5.4**

Property 6: Git history is maintained
*For any* moved file, Git should show proper move history using git mv command
**Validates: Requirements 5.5**

Property 7: Functionality is preserved
*For any* Docker compose configuration, it should start successfully after file reorganization
**Validates: Requirements 3.4**

Property 8: Scripts are properly organized
*For any* shell script in the project, it should be located in the scripts directory
**Validates: Requirements 4.1**

Property 9: Documentation is updated
*For any* documentation file, it should contain correct paths to reorganized files and maintain consistency across languages
**Validates: Requirements 6.1, 6.2, 6.3, 6.4**

## Error Handling

### File Move Errors
- **Missing Source File**: Если исходный файл не существует, операция должна быть пропущена с предупреждением
- **Permission Denied**: Если нет прав на перемещение файла, операция должна быть прервана с ошибкой
- **Target Directory Missing**: Если целевая директория не существует, она должна быть создана автоматически

### Reference Update Errors
- **File Not Found**: Если файл для обновления ссылок не найден, это должно быть зафиксировано как предупреждение
- **Invalid Path**: Если путь в файле некорректен, он должен быть пропущен с предупреждением
- **Backup Creation**: Перед изменением файлов должны создаваться резервные копии

### Git Operation Errors
- **Uncommitted Changes**: Если есть незафиксированные изменения, операция должна быть прервана
- **Git Not Available**: Если Git недоступен, файлы должны быть перемещены обычным способом с предупреждением

## Testing Strategy

### Unit Tests
- Тестирование создания директорий
- Тестирование перемещения отдельных файлов
- Тестирование обновления ссылок в конкретных файлах
- Тестирование сохранения прав доступа

### Property-Based Tests
- Использование Hypothesis для Python
- Минимум 100 итераций для каждого property теста
- Каждый тест должен быть помечен комментарием: **Feature: project-structure-cleanup, Property N: [property text]**

### Integration Tests
- Тестирование полного процесса реорганизации
- Проверка работоспособности Docker compose после изменений
- Проверка целостности Git истории
- Проверка консистентности документации

### Manual Testing
- Визуальная проверка структуры директорий
- Проверка работы всех скриптов после перемещения
- Проверка доступности всех конфигурационных файлов