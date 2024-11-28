import json
from flask import Flask, render_template, redirect, url_for, request, session
from datetime import datetime
from collections import defaultdict

# Создаем объект Flask
app = Flask(__name__)

# Устанавливаем секретный ключ для защиты данных сессии
app.secret_key = 'your_very_secure_secret_key'

# Словарь пользователей для авторизации
users = {
    "Ilya": "Kraken911"
}

# Пути к файлам для сохранения статистики
USER_STATS_FILE = "user_stats.json"
COMMAND_STATS_FILE = "command_stats.json"

# Хранилище статистики
user_stats = defaultdict(lambda: {"messages": 0, "actions": []})  # Статистика пользователей
command_stats = defaultdict(list)  # Статистика использования маршрутов


def save_stats_to_file():
    """Сохраняет статистику пользователей и маршрутов в файлы."""
    with open(USER_STATS_FILE, 'w', encoding='utf-8') as user_file:
        json.dump(user_stats, user_file, default=str, ensure_ascii=False, indent=4)

    with open(COMMAND_STATS_FILE, 'w', encoding='utf-8') as command_file:
        json.dump(command_stats, command_file, default=str, ensure_ascii=False, indent=4)


def load_stats_from_file():
    """Загружает статистику пользователей и маршрутов из файлов."""
    global user_stats, command_stats
    try:
        with open(USER_STATS_FILE, 'r', encoding='utf-8') as user_file:
            user_stats.update(json.load(user_file))
    except FileNotFoundError:
        pass

    try:
        with open(COMMAND_STATS_FILE, 'r', encoding='utf-8') as command_file:
            command_stats.update(json.load(command_file))
    except FileNotFoundError:
        pass


def log_user_activity(username, route):
    """Логирует активность пользователя: посещение страницы."""
    timestamp = datetime.now()
    user_stats[username]["actions"].append({
        "route": route,
        "timestamp": timestamp.isoformat()  # Сохраняем дату в формате ISO
    })
    user_stats[username]["messages"] += 1
    save_stats_to_file()


def log_command_usage(route):
    """Логирует использование маршрута."""
    timestamp = datetime.now()
    command_stats[route].append(timestamp.isoformat())  # Сохраняем дату в формате ISO
    save_stats_to_file()


@app.route('/')
def index():
    """
    Главная страница. Если пользователь авторизован,
    показываем приветствие, иначе просим авторизоваться.
    """
    if 'username' in session:
        username = session['username']
        log_user_activity(username, "index")
        log_command_usage("index")
        return render_template('index.html', username=username)
    log_command_usage("index")
    return redirect(url_for('authorization'))


@app.route('/authorization', methods=['GET', 'POST'])
def authorization():
    """
    Страница авторизации. Пользователь вводит логин и пароль.
    Если успешно, перенаправляется на главную страницу.
    """
    log_command_usage("authorization")
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in users and users[username] == password:
            session['username'] = username
            log_user_activity(username, "login")
            return redirect(url_for('index'))
        else:
            error = "Неправильный логин или пароль."
            return render_template('authorization.html', error=error)

    return render_template('authorization.html')


@app.route('/about')
def about():
    """Страница 'О нас'."""
    if 'username' in session:
        username = session['username']
        log_user_activity(username, "about")
    log_command_usage("about")
    return render_template('about.html')


@app.route('/moments')
def moments():
    """Страница с интересными моментами."""
    log_command_usage("moments")
    if 'username' in session:
        username = session['username']
        log_user_activity(username, "moments")
        return render_template('moments.html', username=username)
    return redirect(url_for('authorization'))


@app.route('/logout')
def logout():
    """Выход из системы."""
    if 'username' in session:
        username = session['username']
        log_user_activity(username, "logout")
        session.pop('username', None)
    log_command_usage("logout")
    return redirect(url_for('index'))


@app.route('/stats')
def stats():
    """
    Страница со статистикой.
    Выводит собранные данные о пользователях и командах.
    """
    if 'username' in session:
        username = session['username']
        log_user_activity(username, "stats")

    log_command_usage("stats")
    return render_template('stats.html', user_stats=user_stats, command_stats=command_stats)


if __name__ == "__main__":
    # Загружаем статистику при запуске
    load_stats_from_file()
    app.run(debug=True)
