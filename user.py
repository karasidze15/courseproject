import sqlite3

def connect_db():
    """Підключення до бази даних."""
    return sqlite3.connect('game_database.db')

def create_user(nickname, mail):
    """Створення нового користувача."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (nickname, mail) VALUES (?, ?)", (nickname, mail))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def get_user_by_nickname(nickname):
    """Отримання користувача за його ім'ям."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE nickname = ?", (nickname,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_mail(mail): 
    """Отримання користувача за його email."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE mail = ?", (mail,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_coin_collections(user_id, coins):
    """Оновлення кількості монет користувача."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE achievements SET coin_collections = coin_collections + ? WHERE user_id = ?", (coins, user_id))
    conn.commit()
    conn.close()
    
def create_achievement(user_id):
    """Створення досягнення для користувача."""
    conn = connect_db()
    cursor = conn.cursor()
    # Перевірка, чи існує запис про досягнення користувача
    cursor.execute("SELECT * FROM achievements WHERE user_id = ?", (user_id,))
    achievement = cursor.fetchone()
    if achievement is None:
        # Створення нового запису з трьома життями
        cursor.execute("INSERT INTO achievements (player_lives, coin_collections, user_id) VALUES (3, 0, ?)", (user_id,))
    else:
        # Встановлення трьох життів для існуючого користувача
        cursor.execute("UPDATE achievements SET player_lives = 3 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def update_achievement(user_id, lives, coins):
    """Оновлення досягнення користувача."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE achievements SET player_lives = ?, coin_collections = ? WHERE user_id = ?", (lives, coins, user_id))
    conn.commit()
    conn.close()

def get_achievement(user_id):
    """Отримання досягнення користувача."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT player_lives, coin_collections FROM achievements WHERE user_id = ?", (user_id,))
    achievement = cursor.fetchone()
    conn.close()
    return achievement

def get_player_level(user_id):
    """Отримання рівня гравця."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT level FROM progress WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return 0
