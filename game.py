import pygame
import random
import tkinter as tk
from tkinter import messagebox
from user import reset_coin_counter, connect_db, create_user, get_player_level, get_user_by_nickname, get_user_by_mail, update_coin_collections, create_achievement, update_achievement, get_achievement
import game_interface
import sys

pygame.init()

current_user_id = None  # Глобальна змінна для зберігання поточного user_id
bg_image = pygame.image.load("images/background.jpg")
bg_image = pygame.transform.scale(bg_image, (1000, 600))

pipe_spawn_delay = 300  # Відстань, яку повинна пройти пташка перед появою першої труби

def initialize_game():
    """Ініціалізація гри: очищення списків труб та монет, встановлення початкових значень пташки та фону."""
    global pipes, coins, bird_y, bird_velocity, background_x, pipe_spawn_delay
    pipes = []  # Очищення списку труб
    coins = []  # Очищення списку монет
    bird_y = 300  # Початкова позиція пташки
    bird_velocity = 0  # Початкова швидкість падіння пташки
    background_x = 0  # Початкова позиція фону
    pipe_spawn_delay = 300  # Затримка перед появою першої труби

def open_game_window(user_id):
    """Відкриває головне вікно гри з вказаним user_id."""
    global current_user_id, coin_counter, bird_y, bird_velocity, background_x, bg_image, pipe_spawn_delay
    current_user_id = user_id
    create_achievement(user_id)  # Встановлення життів і монет для користувача
    lives, coins = get_achievement(user_id)  # Отримуємо початкову кількість життів та монет
    coin_counter = coins  # Ініціалізуємо лічильник монет
    player_level = get_player_level(user_id)

    initialize_game()

    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Пернатий пілот")
    clock = pygame.time.Clock()

    gravity = 0.3  # Гравітація, яка впливає на падіння пташки

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    bird_velocity = -3  # Пташка підстрибує вгору

        bird_velocity += gravity  # Збільшення швидкості падіння пташки
        bird_y += bird_velocity  # Оновлення позиції пташки

        background_x -= 1  # Рух фону вліво
        if background_x <= -bg_image.get_width():
            background_x = 0  # Повернення фону на початкову позицію

        screen.fill((255, 255, 255))
        game_interface.draw_background(screen)
        if random.randint(1, 100) == 1:  # Рандомне додавання монет
            game_interface.add_coin()

        pipe_spawn_delay -= 2
        if pipe_spawn_delay <= 0:
            game_interface.add_pipe()
            pipe_spawn_delay = 300

        game_interface.draw_pipes(screen)
        game_interface.draw_bird(screen, bird_y)
        collected_coins = game_interface.collect_coins(bird_y)
        coins += collected_coins
        update_achievement(user_id, lives, coins)
        game_interface.draw_player_level(screen, player_level)
        game_interface.draw_coins(screen)
        game_interface.draw_coin_counter(screen)  # Передаємо лічильник монет
        game_interface.draw_lives(screen, lives)

        collision, collision_pipe_index = game_interface.check_collision(bird_y)
        if collision:
            lives -= 1
            update_achievement(user_id, lives, coins)
            if lives <= 0:
                running = False
                game_over_window()
                # initialize_game()  # Видаліть або закоментуйте цей рядок
            else:
                if 0 <= collision_pipe_index < len(pipes):
                    del pipes[collision_pipe_index]
                for pipe in pipes:
                    pipe['x'] += 300
                # initialize_game()  # Видаліть або закоментуйте цей рядок
                messagebox.showinfo("Життя втрачено", "У вас залишилось {} життів".format(lives))

        level = update_level(user_id, coins)  # Оновлення рівня гравця
        if level is not None:
            player_level = level
            coins = 0  # Скидання лічильника монет
            update_achievement(user_id, lives, coins)  # Оновлення досягнень в базі даних

        pygame.display.update()
        clock.tick(60)  # Обмеження кадрів на секунду (FPS)

    pygame.quit()

def game_over_window():
    """Відображення вікна "Гра завершена"."""
    def start_over():
        game_over.destroy()
        restart_game()

    game_over = tk.Tk()
    game_over.title("Гра завершена")
    center_window(game_over, 300, 200)
    game_over.configure(bg='#f0f0f0')

    pipes.clear()

    label = tk.Label(game_over, text="Гра завершена!", bg='#f0f0f0', font=("Arial", 14))
    label.pack(pady=10)

    restart_button = tk.Button(game_over, text="Почати заново", command=start_over, bg="#4CAF50", fg="black", width=15, height=2, relief="flat", cursor="hand2")
    restart_button.pack(pady=(0, 5))

    exit_button = tk.Button(game_over, text="Вихід", command=game_over.destroy, bg="#2196F3", fg="black", width=15, height=2, relief="flat", cursor="hand2")
    exit_button.pack()

    game_over.mainloop()

def restart_game():
    """Перезапуск гри."""
    pygame.init()  # Реініціалізація Pygame
    open_game_window(current_user_id)

def update_level(user_id, coins):
    """Оновлення рівня гравця в залежності від кількості зібраних монет."""
    if coins >= 5:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT level FROM progress WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            level = result[0]
            new_level = level + 1
            cursor.execute("UPDATE progress SET level = ? WHERE user_id = ?", (new_level, user_id))
            conn.commit()
            return new_level
        else:
            new_level = 1
            cursor.execute("INSERT INTO progress (user_id, level) VALUES (?, ?)", (user_id, new_level))
            conn.commit()
        conn.close()
        return new_level
    return None

def center_window(window, width, height):
    """Центрування вікна за розміром екрану."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f'{width}x{height}+{x}+{y}')

def register_user():
    """Реєстрація нового користувача."""
    nickname = entry_nickname.get()
    mail = entry_mail.get()

    if not nickname or not mail:
        messagebox.showerror("Помилка", "Будь ласка, заповніть усі поля.")
    elif get_user_by_nickname(nickname) or get_user_by_mail(mail):
        messagebox.showerror("Помилка", "Користувач з таким нікнеймом або емейлом вже існує.")
    else:
        user_id = create_user(nickname, mail)
        messagebox.showinfo("Успіх", "Реєстрація успішна.")
        window.destroy()
        open_game_window(user_id)

def login_user():
    """Вхід в гру."""
    nickname = entry_nickname.get()
    user = get_user_by_nickname(nickname)

    if user:
        messagebox.showinfo("Успіх", f"Вхід успішний. Вітаємо в грі, {user[1]}!")
        window.destroy()
        open_game_window(user[0])
    else:
        messagebox.showerror("Помилка", "Користувача з таким нікнеймом не знайдено.")

# Створення вікна
window = tk.Tk()
window.title("Вхід та Реєстрація")
center_window(window, 300, 300)
window.configure(bg='white')  # Зробити вікно білого кольору

# Створення та розміщення елементів інтерфейсу
frame = tk.Frame(window, padx=20, pady=20, bg='white')  # Зробити фрейм білого кольору
frame.pack(expand=True)

label_nickname = tk.Label(frame, text="Нікнейм:", bg='white')  # Зробити лейбл білого кольору
label_nickname.pack()

entry_nickname = tk.Entry(frame)
entry_nickname.pack(pady=5)

label_mail = tk.Label(frame, text="Емейл:", bg='white')  # Зробити лейбл білого кольору
label_mail.pack()

entry_mail = tk.Entry(frame)
entry_mail.pack(pady=5)

button_register = tk.Button(frame, text="Реєстрація", command=register_user, cursor="hand2", bg="#4CAF50", fg="black", width=20, height=2, relief="flat")
button_register.pack(pady=(20, 5))  # Додати відстань зверху над кнопкою

button_login = tk.Button(frame, text="Вхід", command=login_user, cursor="hand2", bg="#2196F3", fg="black", width=20, height=2, relief="flat")
button_login.pack(pady=5)

# Запуск головного циклу
window.mainloop()
