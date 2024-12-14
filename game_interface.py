import pygame
import random
from user import create_user, get_user_by_nickname, get_user_by_mail, update_coin_collections, create_achievement, update_achievement, get_achievement, connect_db

pygame.init()  # Ініціалізація Pygame

# Визначення розмірів пташки
bird_width = 50
bird_height = 50

# Завантаження зображень
bird_image = pygame.image.load("images/bird.png")
bird_image = pygame.transform.scale(bird_image, (bird_width, bird_height))

bg_image = pygame.image.load("images/background.jpg")
bg_image = pygame.transform.scale(bg_image, (1000, 600))

pipe_bottom = pygame.image.load("images/pipe_bottom.png")
pipe_top = pygame.image.load("images/pipe_top.png")
pipe_bottom = pygame.transform.scale(pipe_bottom, (60, 400))
pipe_top = pygame.transform.scale(pipe_top, (60, 400))

pipes = []
pipe_width = pipe_top.get_width()
pipe_height = pipe_top.get_height()
space_between_pipes = 200  # Відстань між верхньою та нижньою трубами

coin_image = pygame.image.load("images/coin.png")
coin_image = pygame.transform.scale(coin_image, (30, 30))
coin_width, coin_height = coin_image.get_size()
coins = []

font = pygame.font.SysFont(None, 30)

# Глобальна змінна для лічильника монет
coin_counter = 0

def draw_background(screen):
    """Функція для відображення фону."""
    screen.blit(bg_image, (0, 0))

def add_pipe():
    """Функція для додавання нової труби."""
    pipe_x = 800  # Початкова позиція труби (за межами екрану справа)
    pipe_y = random.randint(-pipe_height, 0)  # Випадкова позиція труби по вертикалі
    pipes.append({'x': pipe_x, 'top_y': pipe_y, 'bottom_y': pipe_y + pipe_height + space_between_pipes})

def draw_pipes(screen):
    """Функція для відображення труб."""
    for pipe in pipes:
        screen.blit(pipe_top, (pipe['x'], pipe['top_y']))
        screen.blit(pipe_bottom, (pipe['x'], pipe['bottom_y']))
        pipe['x'] -= 2  # Рух труб вліво

    # Видалення труб, які вийшли за межі екрану
    pipes[:] = [pipe for pipe in pipes if pipe['x'] > -pipe_width]

    # Додавання нової труби, якщо остання труба досягла певної позиції
    if not pipes or pipes[-1]['x'] < 400:
        add_pipe()

def add_coin():
    """Функція для додавання нової монети."""
    coin_x = random.randint(800, 1200)
    coin_y = random.randint(100, 500)
    # Перевірка, чи монета знаходиться на трубі
    for pipe in pipes:
        if pipe['x'] < coin_x < pipe['x'] + pipe_width:
            return  # Якщо монета на трубі, не додаємо її
    coins.append({'x': coin_x, 'y': coin_y})

def draw_coins(screen):
    """Функція для відображення монет."""
    for coin in coins:
        screen.blit(coin_image, (coin['x'], coin['y']))
        coin['x'] -= 2  # Рух монет вліво

def collect_coins(bird_y):
    """Функція для збору монет."""
    global coins, coin_counter
    bird_rect = pygame.Rect(100, bird_y, bird_width, bird_height)
    collected_coins = 0
    for coin in coins:
        if bird_rect.colliderect(pygame.Rect(coin['x'], coin['y'], coin_width, coin_height)):
            collected_coins += 1
            coin_counter += 1  # Оновлюйте coin_counter тут
    coins[:] = [coin for coin in coins if not bird_rect.colliderect(pygame.Rect(coin['x'], coin['y'], coin_width, coin_height))]
    return collected_coins

def draw_coin_counter(screen):
    """Функція для відображення лічильника монет."""
    global coin_counter
    font = pygame.font.SysFont(None, 30)
    text = font.render(f"Монети: {coin_counter}", True, (0, 0, 0))
    screen.blit(text, (10, 10))

def draw_bird(screen, bird_y):
    """Функція для відображення пташки."""
    screen.blit(bird_image, (100, bird_y))

def check_collision(bird_y):
    """Функція для перевірки зіткнення пташки з трубами."""
    bird_rect = pygame.Rect(100, bird_y, bird_width, bird_height)
    for i, pipe in enumerate(pipes):
        top_pipe_rect = pygame.Rect(pipe['x'], pipe['top_y'], pipe_width, pipe_height)
        bottom_pipe_rect = pygame.Rect(pipe['x'], pipe['bottom_y'], pipe_width, pipe_height)
        if bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect):
            del pipes[i]  # Видалення труби зі списку pipes
            return True, i  # Повертаємо індекс труби, з якою сталося зіткнення
    return False, -1  # Якщо немає зіткнення, повертаємо -1

def draw_lives(screen, lives):
    """Функція для відображення кількості життів."""
    text = font.render(f"Життя: {lives}", True, (0, 0, 0))
    screen.blit(text, (700, 10))
    
def draw_player_level(screen, level):
    """Функція для відображення рівня гравця."""
    font = pygame.font.SysFont(None, 30)
    text = font.render(f"Рівень: {level}", True, (0, 0, 0))
    screen.blit(text, (10, 40))
