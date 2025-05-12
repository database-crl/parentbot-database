# ParentBot Database

Этот репозиторий содержит структуру базы данных для ParentBot на базе CSV файлов.

---

## Структура проекта

- `/db/` — все CSV файлы с данными.
- `init_db_folder.py` — создание папки `db/` и базовых CSV файлов с начальными данными.
- `create_database.py` — сборка базы данных SQLite (`database.sqlite3`) из файлов CSV.

---

## 🚀 Как начать работу

1. Склонируйте репозиторий:
    ```bash
    git clone https://github.com/ВАШ_АККАУНТ/parentbot-database.git
    cd parentbot-database
    ```

2. Инициализируйте папку `/db` и CSV файлы:
    ```bash
    python init_db_folder.py
    ```

3. Соберите базу данных SQLite:
    ```bash
    python create_database.py
    ```

После этого у вас появится `database.sqlite3`, готовая для работы с ботом.

---

## Что содержится в `/db`

| Файл | Назначение |
|:----|:-----------|
| parents.csv | Родители |
| students.csv | Ученики |
| schedule.csv | Расписание занятий |
| logs.csv | Логи действий пользователей |
| notifications_settings.csv | Настройки уведомлений |

---

## Примечания

- Файл `database.sqlite3` не коммитится в репозиторий (см. `.gitignore`).
- Вы можете онлайн редактировать CSV файлы на GitHub и пересобирать базу при необходимости.
