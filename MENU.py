import pygame
import sys
import subprocess

pygame.init()

# Инициализация микшера
pygame.mixer.init()

# Загрузка фоновой музыки
pygame.mixer.music.load("data/music/MENU.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)  # Зацикливаем музыку

WIDTH, HEIGHT = 1600, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Меню выбора игры")

# Цвета
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
BUTTON_COLOR = (0, 128, 255)
BUTTON_HOVER_COLOR = (0, 100, 200)

# Шрифты
FONT = pygame.font.Font(None, 50)

# Список игр и их названия
games = [
    ("Пин-понг", "Пин-понг.py"),
    ("Судоку", "Судоку.py"),
    ("Шарики", "ШАРИКИ.py"),
    ("Arkanoid", "Arkanoid.py"),
    ("Bomberman", "Bomberman.py"),
    ("Flappy bird", "Flappy bird.py"),
    ("PAINT", "PAINT.py"),
    ("Динозаврик", "Дино.py"),
    ("Лабиринт", "Лабиринт.py")]


def draw_text(text, font, color, x, y):
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=(x, y))
    screen.blit(text_surf, text_rect)


def draw_button(text, x, y, width, height):
    mouse_pos = pygame.mouse.get_pos()
    button_rect = pygame.Rect(x, y, width, height)

    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button_rect)
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, button_rect)

    draw_text(text, FONT, WHITE, x + width // 2, y + height // 2)
    return button_rect


def show_menu():
    while True:
        screen.fill(BLACK)
        draw_text("Выберите игру:", FONT, WHITE, WIDTH // 2, HEIGHT // 15)
        button_h, button_w = 60, 400

        for index, (game_name, script_name) in enumerate(games):
            button_y = HEIGHT // 2 - len(games) * (button_h + 20) // 2 + index * (button_h + 20)
            button = draw_button(game_name, WIDTH // 2 - button_w // 2, button_y, button_w, button_h)

            if pygame.mouse.get_pressed()[0] and button.collidepoint(pygame.mouse.get_pos()):
                return script_name

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()  # Останавливаем музыку перед выходом
                pygame.quit()
                sys.exit()


if __name__ == "__main__":
    while True:
        selected_game = show_menu()
        try:
            # Останавливаем музыку перед запуском игры
            pygame.mixer.music.stop()

            # Запускаем игру в отдельном процессе
            subprocess.run(["python", selected_game], check=True)

            # После выхода из игры, повторно инициализируем Pygame и запускаем музыку
            pygame.init()
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.mixer.music.play(-1)  # Возобновляем музыку
        except Exception as e:
            print(f"Ошибка при запуске игры {selected_game}: {e}")
            pygame.mixer.music.stop()  # Останавливаем музыку при ошибке
            pygame.quit()
            sys.exit()
