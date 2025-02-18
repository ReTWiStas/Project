import pygame
import sys
import random
import time
import math

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 800  # Увеличили размер экрана
CELL_SIZE = 25
COLS = WIDTH // CELL_SIZE
ROWS = HEIGHT // CELL_SIZE

# Цвета для светлой и темной темы
THEMES = {
    'light': {
        'wall': (0, 0, 0),
        'player': (255, 215, 0),
        'exit': (0, 255, 0),
        'empty': (255, 255, 255),
        'spikes': (255, 0, 0),  # Красный цвет для шипов
        'background': (255, 255, 255),
        'text': (0, 0, 0)},
    'dark': {
        'wall': (50, 50, 50),
        'player': (255, 215, 0),
        'exit': (0, 200, 0),
        'empty': (30, 30, 30),
        'spikes': (200, 0, 0),  # Темно-красный цвет для шипов
        'background': (0, 0, 0),
        'text': (255, 255, 255)}}

# Текущая тема
current_theme = 'light'

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Лабиринт')

# Скрываем курсор мыши
pygame.mouse.set_visible(False)

# Загрузка фоновой музыки
pygame.mixer.music.load("data/music/Лабиринт.mp3")
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1)  # Зацикливаем музыку

# Шрифты
font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 72)


class Cell:
    """Класс для представления клетки лабиринта."""
    def __init__(self, x, y, cell_type):
        self.rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        self.type = cell_type


class Maze:
    """Класс для генерации и управления лабиринтом."""
    def __init__(self):
        self.grid = [[Cell(x, y, 'wall') for x in range(COLS)] for y in range(ROWS)]
        self.main_path = []  # Сохраняем путь генерации
        self.generate_maze()

    def generate_maze(self):
        """Генерация лабиринта с использованием алгоритма DFS."""
        stack = [(1, 1)]
        self.main_path = [(1, 1)]
        self.grid[1][1] = Cell(1, 1, 'empty')

        while stack:
            x, y = stack[-1]
            neighbors = []

            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                nx, ny = x + dx, y + dy
                if 0 < nx < COLS - 1 and 0 < ny < ROWS - 1 and self.grid[ny][nx].type == 'wall':
                    neighbors.append((nx, ny))

            if neighbors:
                nx, ny = random.choice(neighbors)
                wx, wy = (x + nx) // 2, (y + ny) // 2
                self.grid[wy][wx] = Cell(wx, wy, 'empty')
                self.grid[ny][nx] = Cell(nx, ny, 'empty')
                self.main_path.extend([(wx, wy), (nx, ny)])
                stack.append((nx, ny))
            else:
                stack.pop()

        # Добавляем выход и шипы
        self.add_exit()
        self.add_spikes()

    def add_exit(self):
        """Добавляет выход в случайной точке основного пути."""
        if self.main_path:
            # Выбираем случайную точку из основного пути, кроме стартовой позиции
            exit_pos = random.choice([pos for pos in self.main_path if pos != (1, 1)])
            self.grid[exit_pos[1]][exit_pos[0]] = Cell(*exit_pos, 'exit')

    def add_spikes(self):
        """Добавляет шипы, исключая стартовую позицию и выход."""
        for y in range(ROWS):
            for x in range(COLS):
                if (x, y) == (1, 1):
                    continue  # Пропускаем стартовую позицию
                if self.grid[y][x].type == 'exit':
                    continue  # Пропускаем выход
                if self.grid[y][x].type == 'empty' and random.random() < 0.1:
                    self.grid[y][x] = Cell(x, y, 'spikes')

    def draw(self, screen):
        """Отрисовка лабиринта."""
        for row in self.grid:
            for cell in row:
                if cell.type != 'empty':
                    pygame.draw.rect(screen, THEMES[current_theme][cell.type], cell.rect)

class Player:
    """Класс для управления игроком."""
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.target_x, self.target_y = x, y
        self.speed = 15  # Скорость перемещения
        self.is_moving = False  # Флаг для проверки движения
        self.on_spikes = False  # Флаг для проверки нахождения на шипах
        self.spike_start_time = 0  # Время начала нахождения на шипах

    def move(self, dx, dy, maze):
        """Движение игрока до ближайшей стены."""
        if self.is_moving:
            return  # Игрок уже движется, игнорируем новое движение

        new_x, new_y = self.x, self.y

        # Двигаемся по оси X
        if dx != 0:
            while True:
                new_x += dx
                if not (0 <= new_x < COLS):
                    new_x -= dx
                    break
                if maze.grid[int(self.y)][int(new_x)].type == 'wall':
                    new_x -= dx
                    break

        # Двигаемся по оси Y
        if dy != 0:
            while True:
                new_y += dy
                if not (0 <= new_y < ROWS):
                    new_y -= dy
                    break
                if maze.grid[int(new_y)][int(self.x)].type == 'wall':
                    new_y -= dy
                    break

        # Устанавливаем новую цель
        self.target_x, self.target_y = new_x, new_y
        self.is_moving = True

    def update(self, maze):
        """Обновление позиции игрока."""
        if self.is_moving:
            if abs(self.x - self.target_x) > 0.1:
                self.x += (self.target_x - self.x) * 0.5  # Увеличили скорость перемещения
            else:
                self.x = self.target_x

            if abs(self.y - self.target_y) > 0.1:
                self.y += (self.target_y - self.y) * 0.5  # Увеличили скорость перемещения
            else:
                self.y = self.target_y

            # Если игрок достиг цели, сбрасываем флаг движения
            if self.x == self.target_x and self.y == self.target_y:
                self.is_moving = False

        # Проверка нахождения на шипах
        current_cell = maze.grid[int(self.y)][int(self.x)]
        if current_cell.type == 'spikes':
            if not self.on_spikes:
                self.on_spikes = True
                self.spike_start_time = time.time()  # Засекаем время начала нахождения на шипах
            else:
                if time.time() - self.spike_start_time > 0.5:  # Если на шипах больше 0.5 секунды
                    print("СМЕРТЬ ОТ ШИПОВ!")
                    return True  # Игрок погиб
        else:
            self.on_spikes = False  # Сбрасываем флаг, если игрок ушел с шипов

        return False  # Игрок жив

    def draw(self, screen):
        """Отрисовка игрока."""
        pygame.draw.rect(screen, THEMES[current_theme]['player'],
                         (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))


class Game:
    """Класс для управления игровым циклом."""
    def __init__(self):
        self.maze = Maze()
        self.player = Player(1, 1)
        self.running = True
        self.paused = False
        self.start_time = time.time()

    def handle_events(self):
        """Обработка событий."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                if not self.paused:
                    if event.key == pygame.K_LEFT:
                        self.player.move(-1, 0, self.maze)
                    elif event.key == pygame.K_RIGHT:
                        self.player.move(1, 0, self.maze)
                    elif event.key == pygame.K_UP:
                        self.player.move(0, -1, self.maze)
                    elif event.key == pygame.K_DOWN:
                        self.player.move(0, 1, self.maze)
                    elif event.key == pygame.K_t:
                        global current_theme
                        current_theme = 'dark' if current_theme == 'light' else 'light'

    def update(self):
        """Обновление состояния игры."""
        if not self.paused:
            if self.player.update(self.maze):  # Если игрок погиб на шипах
                self.running = False
            current_cell = self.maze.grid[int(self.player.y)][int(self.player.x)]
            if current_cell.type == 'exit':
                print(f"ПОБЕДА! Время: {int(time.time() - self.start_time)} сек.")
                self.running = False

    def draw(self):
        """Отрисовка игры."""
        screen.fill(THEMES[current_theme]['background'])
        self.maze.draw(screen)
        self.player.draw(screen)

        if self.paused:
            pause_text = font.render("ПАУЗА", True, THEMES[current_theme]['text'])
            screen.blit(pause_text, (WIDTH // 2 - 50, HEIGHT // 2 - 20))

        pygame.display.flip()

    def run(self):
        """Запуск игрового цикла."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.time.Clock().tick(60)


def show_menu():
    """Отображение начального меню."""
    menu_running = True
    color_offset = 0  # Смещение для анимации цвета

    while menu_running:
        screen.fill(THEMES[current_theme]['background'])

        # Анимация цвета названия игры (плавное переливание)
        green_value = int(128 + 127 * (math.sin(color_offset) + 1))  # Плавное изменение от 128 до 255
        green_value = max(0, min(green_value, 255))  # Ограничиваем значение в диапазоне [0, 255]
        title_color = (0, green_value, 0)  # Зеленый цвет с плавным изменением
        title = title_font.render("Лабиринт", True, title_color)
        screen.blit(title, (WIDTH // 2 - 140, HEIGHT // 2 - 150))  # Подняли название выше

        # Остальной текст
        controls = font.render("Управление: Стрелки для движения, ESC для паузы", True, THEMES[current_theme]['text'])
        theme = font.render("T - Сменить тему", True, THEMES[current_theme]['text'])
        start = font.render("Нажмите SPACE чтобы начать", True, THEMES[current_theme]['text'])

        screen.blit(controls, (WIDTH // 2 - 250, HEIGHT // 2 - 50))
        screen.blit(theme, (WIDTH // 2 - 100, HEIGHT // 2))
        screen.blit(start, (WIDTH // 2 - 150, HEIGHT // 2 + 50))

        pygame.display.flip()

        # Обновление анимации цвета
        color_offset += 0.0002  # Уменьшили скорость изменения для плавности

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()  # Останавливаем музыку перед выходом
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    menu_running = False


# Запуск игры
if __name__ == "__main__":
    show_menu()
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()