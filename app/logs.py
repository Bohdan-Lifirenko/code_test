import os
import json
import datetime
from collections import deque
from flask import Blueprint, render_template, current_app

logs_bp = Blueprint('logs', __name__)

def tail(filename, n=50):
    """Повертає останні N рядків з файлу."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return deque(f, maxlen=n)
    except FileNotFoundError:
        return deque(['Логи не знайдено.'])

# Маршрут для відображення логів
@logs_bp.route('/last_logs')
def last_logs():
    last_lines = tail(current_app.config.get("LAST_LOG_FILE"), n=100)  # Останні 100 рядків
    logs = '\n'.join(last_lines).strip()  # Збираємо в рядок

    return render_template('last_logs.html', logs=logs)

@logs_bp.route('/download_logs')
def download_logs():
    files = os.listdir(current_app.config.get("LOGS_DIR"))

    # Фільтруємо тільки валідні лог-файли
    valid_files = []
    has_current_log = False
    for file in files:
        if file == "app.log":
            has_current_log = True
        elif file.startswith("app.log.") and file.endswith("") and len(file.split('.')) == 3:
            # Перевіряємо формат app.log.YYYY-MM-DD
            suffix = file[8:]
            parts = suffix.split('-')
            if len(parts) == 3 and all(p.isdigit() for p in parts) and len(parts[0]) == 4 and len(
                    parts[1]) == 2 and len(parts[2]) == 2:
                valid_files.append(file)

    # Додаємо поточний лог, якщо є
    if has_current_log:
        valid_files.append("app.log")

    # Сортуємо файли: старі за датою descending, поточний на початку (як найновіший)
    valid_files.sort(key=lambda f: (f != "app.log", f.split('.')[-1] if f != "app.log" else "9999-99-99"), reverse=True)

    # Отримуємо поточну дату
    today = datetime.date.today()
    current_year = str(today.year)
    current_month = f"{today.month:02d}"

    return render_template('download_logs_single.html',
                           files_json=json.dumps(valid_files),
                           current_year=current_year,
                           current_month=current_month)