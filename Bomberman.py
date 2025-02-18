import random
import pygame
import time
import os
import math

# Глобальные настройки, которые можно менять через меню настроек
bomb_timer = 3.0  # время до взрыва (секунд)
enemy_move_delay = 0.66  # задержка между перемещениями врагов

# Цвета и настройки
LIGHT_BROWN = (210, 180, 140)
RED, GREEN, BLUE = (255, 0, 0), (0, 255, 0), (0, 0, 255)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
PANEL_COLOR = (113, 62, 91)
TEXT_COLOR = (143, 73, 239)

WIDTH, HEIGHT = 800, 610
CELL_SIZE = 40
ROWS, COLS = HEIGHT // CELL_SIZE - 1, WIDTH // CELL_SIZE
GAME_DURATION, UPGRADE_CHANCE = 120, 10

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bomberman")
pygame.mouse.set_visible(False)

# Фоновая музыка (зацикленная)
pygame.mixer.music.load("data/music/bomberman музыка.mp3")
pygame.mixer.music.set_volume(0.3)

# Звуки действий
bomb_sound = pygame.mixer.Sound("data/music/bomberman установка бомбы.mp3")
enemy_death_sound = pygame.mixer.Sound("data/music/bomberman враг.mp3")
victory_sound = pygame.mixer.Sound("data/music/bomberman победа.mp3")
defeat_sounds = [pygame.mixer.Sound("data/music/bomberman проигрыш.mp3"),
                 pygame.mixer.Sound("data/music/bomberman время истекло.mp3")]
for sound in defeat_sounds:
    sound.set_volume(0.5)

# В стартовое меню (после pygame.init()) добавить запуск музыки
pygame.mixer.music.play(-1)  # Зацикливаем фоновую музыку


# ======= Система рекордов =======
def load_record():
    try:
        with open("records.txt", "r") as f:
            line = f.readline().strip()
            if line:
                name, score_str = line.split(",")
                return name, int(score_str)
            else:
                return "", 0
    except:
        return "", 0


def save_record(name, score):
    with open("records.txt", "w") as f:
        f.write(f"{name},{score}")


def get_text_input(prompt, font_size=50, color='white'):
    input_text = ""
    active = True
    clock = pygame.time.Clock()
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode
        screen.fill('black')
        prompt_surface = pygame.font.Font(None, font_size).render(prompt, True, color)
        prompt_rect = prompt_surface.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        screen.blit(prompt_surface, prompt_rect)
        input_surface = pygame.font.Font(None, font_size).render(input_text, True, color)
        input_rect = input_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(input_surface, input_rect)
        pygame.display.flip()
        clock.tick(30)
    return input_text



# ======= Стартовое меню =======
def start_menu():
    menu_active = True
    clock = pygame.time.Clock()
    record_name, record_score = load_record()
    while menu_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    menu_active = False
                # Дополнительно можно реализовать просмотр рекордов по R
        screen.fill('black')
        # Анимация заголовка: переливание от красного к оранжевому
        factor = (math.sin(pygame.time.get_ticks() / 1000.0 * 3) + 1) / 2
        green_value = int(165 * factor)
        title_color = (255, green_value, 0)
        title_font = pygame.font.Font(None, 100)
        title_surface = title_font.render("Bomberman", True, title_color)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title_surface, title_rect)
        info_font = pygame.font.Font(None, 36)
        controls = [
            "Управление:",
            "Стрелки для перемещения, Пробел для установки бомбы,",
            "A, W, S, D - альтернативное управление,",
            "ЛКМ по игроку для установки бомбы"]
        for i, line in enumerate(controls):
            control_surface = info_font.render(line, True, 'white')
            control_rect = control_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 40))
            screen.blit(control_surface, control_rect)
        description = [
            "Описание: Игра в стиле Bomberman, где нужно уничтожать врагов",
            "и собирать улучшения, избегая взрывов.",
            "Цель игры: Набрать максимальное количество очков!"]
        for i, line in enumerate(description):
            desc_surface = info_font.render(line, True, 'white')
            desc_rect = desc_surface.get_rect(center=(WIDTH // 2, HEIGHT - 150 + i * 30))
            screen.blit(desc_surface, desc_rect)
        # Отображение лучшего результата
        record_text = f"Лучший результат: {record_name} - {record_score}"
        record_surface = info_font.render(record_text, True, 'white')
        record_rect = record_surface.get_rect(center=(WIDTH // 2, 30))
        screen.blit(record_surface, record_rect)
        pygame.display.flip()
        clock.tick(60)


# ======= Остальные функции =======
class Improvement:
    def __init__(self, x, y, type):
        self.x, self.y = x, y
        self.type = type  # 'bomb' или 'radius'


def show_text(text, size, color, y_offset=0):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    screen.blit(text_surface, text_rect)


def select_level():
    level = ""
    input_active = True
    error_message = ""
    while input_active:
        screen.fill('black')
        show_text("Введите номер уровня (1-5):", 50, 'white', -50)
        show_text(level, 50, 'white')
        if error_message:
            show_text(error_message, 30, RED, 50)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if level.isdigit() and 1 <= int(level) <= 5:
                        input_active = False
                    else:
                        error_message = "Доступны уровни 1-5!"
                        level = ""
                elif event.key == pygame.K_BACKSPACE:
                    level = level[:-1]
                elif event.unicode.isdigit():
                    level += event.unicode
    return int(level)


def load_level(level_num):
    filename = f"data/levels/level ({level_num}).txt"
    if not os.path.exists(filename):
        return None
    with open(filename, 'r') as file:
        return [[0 if char == '.' else 1 if char == '*' else 2 for char in line.strip()] for line in file]


def render_map(map_data, exploded_cells, improvements, explosion_time):
    for y in range(len(map_data)):
        for x in range(len(map_data[0])):
            rect = (x * CELL_SIZE, 50 + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if (x, y) in exploded_cells:
                # Анимированный эффект взрыва: круг, который сначала растёт, потом уменьшается
                t = time.time() - explosion_time[(x, y)]
                if t < 0.25:
                    radius = int(CELL_SIZE * (t / 0.25))
                else:
                    radius = int(CELL_SIZE * (1 - (t - 0.25) / 0.25))
                radius = max(radius, 5)
                pygame.draw.circle(screen, YELLOW, (x * CELL_SIZE + CELL_SIZE // 2, 50 + y * CELL_SIZE + CELL_SIZE // 2), radius)
            elif map_data[y][x] == 1:
                pygame.draw.rect(screen, GRAY, rect)
            elif map_data[y][x] == 2:
                pygame.draw.rect(screen, LIGHT_BROWN, rect)
                pygame.draw.line(screen, (139, 69, 19), (x * CELL_SIZE, 50 + y * CELL_SIZE),
                                 ((x + 1) * CELL_SIZE, 50 + (y + 1) * CELL_SIZE), 3)
                pygame.draw.line(screen, (139, 69, 19), ((x + 1) * CELL_SIZE, 50 + y * CELL_SIZE),
                                 (x * CELL_SIZE, 50 + (y + 1) * CELL_SIZE), 3)
            else:
                pygame.draw.rect(screen, LIGHT_BROWN, rect)
            pygame.draw.rect(screen, 'black', rect, 2)
    for upgrade in improvements:
        center = (upgrade.x * CELL_SIZE + 20, 50 + upgrade.y * CELL_SIZE + 20)
        color = GREEN if upgrade.type == 'bomb' else BLUE
        pygame.draw.circle(screen, color, center, 15)


# ======= Классы игрока и врагов =======
class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.bomb_limit = 3
        self.bombs = []
        self.explosion_radius = 2  # начальный радиус взрыва
        self.level, self.score, self.alive = 1, 0, True


    def draw(self):
        if self.alive:
            pygame.draw.rect(screen, RED, (self.x * CELL_SIZE, 50 + self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def can_place_bomb(self):
        current_pos = (self.x, self.y)
        return len(self.bombs) < self.bomb_limit and not any(bomb[0] == current_pos for bomb in self.bombs)

    def place_bomb(self):
        if self.can_place_bomb():
            self.bombs.append(((self.x, self.y), time.time()))
            bomb_sound.play()

    def move(self, direction, map_data):
        if not self.alive:
            return
        dx, dy = 0, 0
        if direction == "left":
            dx = -1
        elif direction == "right":
            dx = 1
        elif direction == "up":
            dy = -1
        elif direction == "down":
            dy = 1
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_x < COLS and 0 <= new_y < ROWS:
            if map_data[new_y][new_x] == 0:
                self.x, self.y = new_x, new_y

    def detonate_bombs(self, exploded_cells, explosion_time, map_data, improvements):
        current_time = time.time()
        new_bombs = []
        for bomb in self.bombs:
            pos, placed_time = bomb
            if current_time - placed_time > bomb_timer:
                directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                for dx, dy in directions:
                    for step in range(1, self.explosion_radius + 1):
                        x = pos[0] + dx * step
                        y = pos[1] + dy * step
                        if not (0 <= x < COLS and 0 <= y < ROWS):
                            break
                        if map_data[y][x] == 1:
                            break
                        elif map_data[y][x] == 2:
                            if random.randint(1, 100) <= UPGRADE_CHANCE:
                                upgrade_type = random.choice(['bomb', 'radius'])
                                improvements.append(Improvement(x, y, upgrade_type))
                            map_data[y][x] = 0
                            exploded_cells.add((x, y))
                            explosion_time[(x, y)] = current_time
                            break
                        exploded_cells.add((x, y))
                        explosion_time[(x, y)] = current_time
            else:
                new_bombs.append(bomb)
        self.bombs = new_bombs


class Enemy:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.move_delay = enemy_move_delay
        self.move_time = time.time()

    def move(self, enemies, map_data, bombs, player):
        if time.time() - self.move_time < self.move_delay:
            return
        self.move_time = time.time()
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        valid_moves = []
        for dx, dy in directions:
            new_x = self.x + dx
            new_y = self.y + dy
            if new_x < 0 or new_x >= COLS or new_y < 0 or new_y >= ROWS:
                continue
            if map_data[new_y][new_x] in (1, 2):
                continue
            if (new_x, new_y) in bombs:
                continue
            conflict = False
            for enemy in enemies:
                if enemy is not self and (enemy.x, enemy.y) == (new_x, new_y):
                    conflict = True
                    break
            if conflict:
                continue
            valid_moves.append((dx, dy))
        if not valid_moves:
            return
        best_move, best_distance = None, None
        for move in valid_moves:
            new_x, new_y = self.x + move[0], self.y + move[1]
            distance = abs(new_x - player.x) + abs(new_y - player.y)
            if best_distance is None or distance < best_distance:
                best_distance, best_move = distance, move
        if best_move is None:
            best_move = random.choice(valid_moves)
        self.x += best_move[0]
        self.y += best_move[1]

    def draw(self):
        pygame.draw.rect(screen, PURPLE, (self.x * CELL_SIZE, 50 + self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def respawn(self, player, map_data):
        while True:
            self.x = random.randint(0, COLS - 1)
            self.y = random.randint(1, ROWS - 1)
            if map_data[self.y][self.x] == 0 and (abs(self.x - player.x) > 3 or abs(self.y - player.y) > 3):
                break


# ======= Основной блок игры =======
start_menu()

# Выбор уровня
selected_level = select_level()
if not selected_level:
    pygame.quit()
    exit()

map_data = load_level(selected_level)
if not map_data:
    print("Ошибка загрузки уровня!")
    pygame.quit()
    exit()

player = Player(0, 0)
exploded_cells, explosion_time = set(), {}

# Генерация врагов
enemies = []
for _ in range(5):
    while True:
        x, y = random.randint(0, COLS - 1), random.randint(1, ROWS - 1)
        if map_data[y][x] == 0 and (abs(x - player.x) > 3 or abs(y - player.y) > 3):
            enemies.append(Enemy(x, y))
            break

improvements = []
start_time = time.time()
running, game_over, victory = True, False, False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # Меню паузы (ESC)
            if event.key == pygame.K_ESCAPE:
                paused = True
                pause_font = pygame.font.Font(None, 72)
                info_font = pygame.font.Font(None, 36)
                while paused:
                    for pevent in pygame.event.get():
                        if pevent.type == pygame.QUIT:
                            pygame.quit()
                            exit()
                        if pevent.type == pygame.KEYDOWN:
                            if pevent.key == pygame.K_RETURN or pevent.key == pygame.K_p:
                                paused = False
                            if pevent.key == pygame.K_q:
                                pygame.quit()
                                exit()
                    screen.fill('black')
                    pause_text = pause_font.render("Пауза", True, 'white')
                    pause_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
                    screen.blit(pause_text, pause_rect)
                    prompt_text = info_font.render("Нажмите Enter для продолжения, Q для выхода", True, 'white')
                    prompt_rect = prompt_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                    screen.blit(prompt_text, prompt_rect)
                    pygame.display.flip()
                    pygame.time.Clock().tick(15)
            elif event.key == pygame.K_SPACE:
                player.place_bomb()
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                player.move("left", map_data)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                player.move("right", map_data)
            elif event.key in (pygame.K_UP, pygame.K_w):
                player.move("up", map_data)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                player.move("down", map_data)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            grid_x = mouse_x // CELL_SIZE
            grid_y = (mouse_y - 50) // CELL_SIZE
            if grid_x == player.x and grid_y == player.y:
                player.place_bomb()

    # Проверка улучшений
    for upgrade in improvements[:]:
        if player.x == upgrade.x and player.y == upgrade.y:
            if upgrade.type == 'bomb':
                player.bomb_limit += 1
            elif upgrade.type == 'radius':
                player.explosion_radius += 1
            improvements.remove(upgrade)

    # Проверка столкновений с врагами
    for enemy in enemies:
        if player.alive and enemy.x == player.x and enemy.y == player.y:
            player.alive = False
            game_over = True

    # Проверка: погиб ли игрок от собственного взрыва
    if (player.x, player.y) in exploded_cells:
        player.alive = False
        game_over = True

    # Проверка времени игры и набранных очков
    remaining_time = max(0, GAME_DURATION - int(time.time() - start_time))
    if remaining_time == 0 or player.score >= 5000:
        game_over = True
        victory = player.score >= 5000

    current_time = time.time()
    for cell in list(explosion_time.keys()):
        if current_time - explosion_time[cell] > 0.5:
            exploded_cells.discard(cell)
            del explosion_time[cell]

    bombs_pos = [bomb[0] for bomb in player.bombs]

    # Перемещение врагов с улучшенным обходом препятствий и погоней за игроком
    for enemy in enemies[:]:
        enemy.move(enemies, map_data, bombs_pos, player)
        if (enemy.x, enemy.y) in exploded_cells:
            enemies.remove(enemy)
            enemy_death_sound.play()
            player.score += 1000
            new_enemy = Enemy(0, 0)
            new_enemy.respawn(player, map_data)
            enemies.append(new_enemy)

    # Обновление задержки движения врагов (в случае изменения настроек)
    for enemy in enemies:
        enemy.move_delay = enemy_move_delay

    screen.fill(LIGHT_BROWN)
    # Отрисовка панели информации
    pygame.draw.rect(screen, PANEL_COLOR, (0, 0, WIDTH, 50))
    font = pygame.font.Font(None, 36)
    timer_text = f"Время: {remaining_time // 60:02}:{remaining_time % 60:02}"
    info_text = (f"Уровень: {selected_level}  Бомбы: {player.bomb_limit - len(player.bombs)}  "
                 f"Радиус: {player.explosion_radius}  Очки: {player.score}")
    screen.blit(font.render(timer_text, True, TEXT_COLOR), (10, 10))
    screen.blit(font.render(info_text, True, TEXT_COLOR), (WIDTH // 3, 10))

    render_map(map_data, exploded_cells, improvements, explosion_time)
    player.detonate_bombs(exploded_cells, explosion_time, map_data, improvements)

    # Анимация бомб: пульсирующий эффект
    for bomb in player.bombs:
        x, y = bomb[0]
        dt = time.time() - bomb[1]
        pulsate = 5 * math.sin((dt / bomb_timer) * math.pi * 2)
        radius = 15 + int(pulsate)
        pygame.draw.circle(screen, 'black', (x * CELL_SIZE + 20, 50 + y * CELL_SIZE + 20), radius)

    player.draw()
    for enemy in enemies:
        enemy.draw()

    if game_over:
        pygame.mixer.music.stop()
        screen.fill('black')
        if victory:
            show_text("Победа!", 75, GREEN, -50)
            victory_sound.play()
        elif not player.alive:
            show_text("Игрок погиб!", 75, RED, -50)
            defeat_sounds[1].play()
        else:
            show_text("Время вышло!", 75, 'white', -50)
            defeat_sounds[2].play()
        show_text(f"Ваш счёт: {player.score}", 50, 'white', 50)
        pygame.display.flip()
        pygame.time.wait(3000)
        # Если рекорд побит, предложить ввести имя и сохранить новый рекорд
        record_name, record_score = load_record()
        if player.score > record_score:
            new_name = get_text_input("Новый рекорд! Введите имя:")
            save_record(new_name, player.score)
        running = False

    pygame.display.flip()
    pygame.time.Clock().tick(60)
pygame.quit()
