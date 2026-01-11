# Requirements Document

## Introduction

Реорганизация структуры проекта для улучшения читаемости, удобства навигации и профессионального вида. Цель - очистить корневую директорию от "каши" конфигурационных файлов, оставив только самые важные файлы и логически сгруппировав остальные.

## Glossary

- **Root_Directory**: Корневая директория проекта
- **Config_Files**: Файлы конфигурации (yml, sql, conf и подобные)
- **Infrastructure_Directory**: Директория для инфраструктурных файлов
- **Database_Directory**: Директория для файлов базы данных
- **Deployment_Directory**: Директория для файлов развертывания

## Requirements

### Requirement 1: Очистка корневой директории

**User Story:** Как разработчик, я хочу видеть чистую корневую директорию, чтобы легко находить основные файлы проекта.

#### Acceptance Criteria

1. THE Root_Directory SHALL contain only essential project files (README, LICENSE, main application files)
2. THE Root_Directory SHALL contain Docker-related files (Dockerfile, docker-compose files) as they are frequently used
3. THE Root_Directory SHALL contain Python package files (requirements.txt, pyproject.toml, pytest.ini)
4. WHEN viewing the root directory, THE developer SHALL see no more than 15-20 files maximum

### Requirement 2: Создание директории для конфигурационных файлов

**User Story:** Как разработчик, я хочу иметь отдельную директорию для конфигурационных файлов, чтобы легко их находить и управлять ими.

#### Acceptance Criteria

1. THE system SHALL create a "config" directory for configuration files
2. WHEN moving config files, THE system SHALL preserve all nginx, prometheus, loki, redis configuration files
3. THE system SHALL maintain relative path references in moved files
4. THE system SHALL update any references to moved config files in other files

### Requirement 3: Создание директории для SQL файлов

**User Story:** Как разработчик, я хочу иметь отдельную директорию для SQL файлов базы данных, чтобы лучше организовать схему данных.

#### Acceptance Criteria

1. THE system SHALL create a "database" or "sql" directory
2. WHEN moving SQL files, THE system SHALL preserve init.sql and init-prod.sql files
3. THE system SHALL update Docker and docker-compose references to moved SQL files
4. THE system SHALL maintain database initialization functionality

### Requirement 4: Организация скриптов

**User Story:** Как разработчик, я хочу иметь все скрипты в одном месте, чтобы легко их находить и использовать.

#### Acceptance Criteria

1. THE system SHALL move all shell scripts to the existing "scripts" directory
2. WHEN moving scripts, THE system SHALL preserve backup-script.sh and other utility scripts
3. THE system SHALL update any references to moved scripts in documentation
4. THE system SHALL maintain script executable permissions

### Requirement 5: Сохранение функциональности

**User Story:** Как разработчик, я хочу, чтобы после реорганизации все функции проекта работали без изменений.

#### Acceptance Criteria

1. WHEN files are moved, THE system SHALL update all path references in configuration files
2. WHEN files are moved, THE system SHALL update all path references in Docker files
3. WHEN files are moved, THE system SHALL update all path references in documentation
4. THE system SHALL preserve all file permissions and executable flags
5. THE system SHALL maintain Git history for moved files using git mv command

### Requirement 6: Обновление документации

**User Story:** Как разработчик, я хочу, чтобы документация отражала новую структуру проекта.

#### Acceptance Criteria

1. WHEN structure is changed, THE system SHALL update README files with new paths
2. WHEN structure is changed, THE system SHALL update project structure documentation
3. THE system SHALL create or update a project structure guide
4. THE system SHALL maintain consistency between Russian and English documentation