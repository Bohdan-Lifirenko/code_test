from collections import deque

from flask import Blueprint, render_template, current_app

logs_data_bp = Blueprint('logs', __name__)

def tail(filename, n=50):
    """Повертає останні N рядків з файлу."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return deque(f, maxlen=n)
    except FileNotFoundError:
        return deque(['Логи не знайдено.'])

# Маршрут для відображення логів
@logs_data_bp.route('/last_logs')
def show_logs():
    last_lines = tail(current_app.config.get("LAST_LOG_FILE"), n=100)  # Останні 100 рядків
    logs = '\n'.join(last_lines).strip()  # Збираємо в рядок

    return render_template('last_logs.html', logs=logs)