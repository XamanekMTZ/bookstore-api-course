# Implementation Plan: Project Structure Cleanup

## Overview

Пошаговая реорганизация структуры проекта для очистки корневой директории и логической группировки файлов. Каждый шаг включает перемещение файлов, обновление ссылок и проверку функциональности.

## Tasks

- [-] 1. Подготовка к реорганизации
  - Создать резервную копию текущего состояния проекта
  - Проверить статус Git (отсутствие незафиксированных изменений)
  - Создать необходимые директории (config/, database/)
  - _Requirements: 2.1, 3.1_

- [ ]* 1.1 Write property test for directory creation
  - **Property 2: Required directories exist**
  - **Validates: Requirements 2.1, 3.1**

- [ ] 2. Перемещение конфигурационных файлов
  - [ ] 2.1 Переместить nginx конфигурации в config/
    - `git mv nginx.conf config/nginx.conf`
    - `git mv nginx-prod.conf config/nginx-prod.conf`
    - _Requirements: 2.2_

  - [ ] 2.2 Переместить мониторинг конфигурации в config/
    - `git mv prometheus.yml config/prometheus.yml`
    - `git mv loki.yml config/loki.yml`
    - `git mv promtail.yml config/promtail.yml`
    - _Requirements: 2.2_

  - [ ] 2.3 Переместить Redis конфигурацию в config/
    - `git mv redis.conf config/redis.conf`
    - _Requirements: 2.2_

- [ ]* 2.4 Write property test for config file preservation
  - **Property 3: Files are preserved during move**
  - **Validates: Requirements 2.2, 2.3**

- [ ] 3. Обновление ссылок на конфигурационные файлы
  - [ ] 3.1 Обновить docker-compose.yml
    - Обновить пути к nginx.conf, prometheus.yml, init.sql
    - _Requirements: 2.4, 5.2_

  - [ ] 3.2 Обновить docker-compose.prod.yml
    - Обновить пути к nginx-prod.conf, init-prod.sql
    - _Requirements: 2.4, 5.2_

  - [ ] 3.3 Обновить Kubernetes манифесты
    - Обновить ссылки в k8s/api-deployment.yaml и k8s/monitoring.yaml
    - _Requirements: 2.4, 5.1_

- [ ]* 3.4 Write property test for reference updates
  - **Property 4: All references are updated**
  - **Validates: Requirements 2.4, 5.1, 5.2**

- [ ] 4. Checkpoint - Проверка Docker конфигурации
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Перемещение SQL файлов
  - [ ] 5.1 Переместить SQL файлы в database/
    - `git mv init.sql database/init.sql`
    - `git mv init-prod.sql database/init-prod.sql`
    - _Requirements: 3.2_

  - [ ] 5.2 Обновить ссылки на SQL файлы в Docker файлах
    - Обновить пути в docker-compose.yml и docker-compose.prod.yml
    - _Requirements: 3.3, 5.2_

- [ ]* 5.3 Write property test for SQL file preservation
  - **Property 3: Files are preserved during move**
  - **Validates: Requirements 3.2**

- [ ] 6. Перемещение скриптов
  - [ ] 6.1 Переместить утилитарные скрипты в scripts/
    - `git mv backup-script.sh scripts/backup-script.sh`
    - _Requirements: 4.1, 4.2_

  - [ ] 6.2 Проверить и обновить права доступа к скриптам
    - Убедиться, что все скрипты имеют права на выполнение
    - _Requirements: 4.4, 5.4_

- [ ]* 6.3 Write property test for script organization
  - **Property 8: Scripts are properly organized**
  - **Validates: Requirements 4.1**

- [ ]* 6.4 Write property test for file permissions
  - **Property 5: File permissions are preserved**
  - **Validates: Requirements 4.4, 5.4**

- [ ] 7. Обновление документации
  - [ ] 7.1 Обновить README.md
    - Обновить пути к конфигурационным файлам и скриптам
    - Обновить структуру проекта в документации
    - _Requirements: 6.1, 6.2_

  - [ ] 7.2 Обновить README_RU.md
    - Синхронизировать с изменениями в README.md
    - _Requirements: 6.1, 6.4_

  - [ ] 7.3 Обновить документацию в docs/
    - Обновить docs/PROJECT_STRUCTURE.md и docs/СТРУКТУРА_ПРОЕКТА.md
    - Обновить пути в других документах при необходимости
    - _Requirements: 6.2, 6.3_

- [ ]* 7.4 Write property test for documentation updates
  - **Property 9: Documentation is updated**
  - **Validates: Requirements 6.1, 6.2, 6.3, 6.4**

- [ ] 8. Проверка функциональности
  - [ ] 8.1 Тестирование Docker compose
    - Запустить `docker-compose up --build` для проверки разработки
    - Запустить `docker-compose -f docker-compose.prod.yml up --build` для проверки продакшена
    - _Requirements: 3.4_

  - [ ] 8.2 Проверка работы скриптов
    - Запустить основные скрипты из scripts/ для проверки работоспособности
    - _Requirements: 4.3_

- [ ]* 8.3 Write property test for functionality preservation
  - **Property 7: Functionality is preserved**
  - **Validates: Requirements 3.4**

- [ ] 9. Проверка корневой директории
  - [ ] 9.1 Подсчет файлов в корне
    - Убедиться, что в корне не более 20 файлов
    - Проверить, что остались только essential файлы
    - _Requirements: 1.1, 1.4_

  - [ ] 9.2 Проверка Git истории
    - Убедиться, что Git показывает корректную историю перемещений
    - _Requirements: 5.5_

- [ ]* 9.3 Write property test for root directory cleanup
  - **Property 1: Root directory contains only essential files**
  - **Validates: Requirements 1.1, 1.2, 1.3, 1.4**

- [ ]* 9.4 Write property test for Git history
  - **Property 6: Git history is maintained**
  - **Validates: Requirements 5.5**

- [ ] 10. Final checkpoint - Полная проверка системы
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Задачи помеченные `*` являются опциональными и могут быть пропущены для быстрого MVP
- Каждая задача ссылается на конкретные требования для отслеживания
- Checkpoint'ы обеспечивают пошаговую валидацию
- Property тесты проверяют универсальные свойства корректности
- Unit тесты проверяют конкретные примеры и граничные случаи
- Используется `git mv` для сохранения истории Git
- Все изменения должны быть протестированы перед финализацией