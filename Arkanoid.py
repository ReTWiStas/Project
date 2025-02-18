import pygame
import random
import math
import json
from enum import Enum

# Инициализация PyGame и звуковой системы
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Загрузка звуковых файлов
game_music = pygame.mixer.Sound("data/music/arkanoid музыка.mp3")
victory_music = pygame.mixer.Sound("data/music/arkanoid победа.mp3")
loss_music_1 = pygame.mixer.Sound("data/music/arkanoid проигрыш.mp3")
loss_music_2 = pygame.mixer.Sound("data/music/arkanoid проигрыш (2).mp3")
powerup_sound = pygame.mixer.Sound("data/music/arkanoid усиление.mp3")

# Установка громкости
game_music.set_volume(0.1)  # 10% громкости для фоновой музыки
victory_music.set_volume(0.7)  # 70% громкости для музыки победы
loss_music_1.set_volume(0.6)  # 60% громкости для проигрыша
loss_music_2.set_volume(0.6)  # 60% громкости для проигрыша
powerup_sound.set_volume(0.1)  # 10% громкости для звука бонуса

# Настройки окна
WIDTH, HEIGHT = 1200, 800

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arkanoid Ultimate")
pygame.mouse.set_visible(False)  # Скрываем курсор

# Цвета
WHITE = (255, 255, 255)
RED, GREEN, BLUE = (255, 0, 0), (0, 255, 0), (0, 0, 255)
PURPLE, ORANGE, YELLOW = (128, 0, 128), (255, 165, 0), (255, 255, 0)

CRIMSON, FIREBRICK, DARK_RED = (220, 20, 60), (178, 34, 34), (139, 0, 0)
HOT_PINK, DEEP_PINK, MEDIUM_VIOLET_RED = (255, 105, 180), (255, 20, 147), (199, 21, 133)
ORANGE_RED, DARK_ORANGE, GOLD = (255, 69, 0), (5, 140, 0), (255, 215, 0)
MEDIUM_ORCHID, MEDIUM_PURPLE, BLUE_VIOLET, DARK_VIOLET = (186, 85, 211), (147, 112, 219), (138, 43, 226), (148, 0, 211)
DARK_ORCHID, DARK_MAGENTA, INDIGO = (153, 50, 204), (139, 0, 139), (75, 0, 130)
LIME_GREEN, MEDIUM_SPRING_GREEN, SPRING_GREEN = (50, 205, 50), (0, 250, 154), (0, 255, 127)
MEDIUM_SEA_GREEN, SEA_GREEN, FOREST_GREEN = (60, 179, 113), (46, 139, 87), (34, 139, 34)
DARK_GREEN, DARK_CYAN, TEAL = (0, 100, 0), (0, 139, 139), (0, 128, 128)
AQUA, DEEP_SKY_BLUE, DODGER_BLUE, CORNFLOWER_BLUE = (0, 255, 255), (0, 191, 255), (30, 144, 255), (100, 149, 237)
MEDIUM_SLATE_BLUE, ROYAL_BLUE, DARK_BLUE, NAVY = (123, 104, 238), (65, 105, 225), (0, 0, 139), (0, 0, 128)

COLORS = [RED, GREEN, BLUE, PURPLE, ORANGE, YELLOW, CRIMSON, FIREBRICK, DARK_RED, HOT_PINK, DEEP_PINK,
          MEDIUM_VIOLET_RED, ORANGE_RED, DARK_ORANGE, GOLD, MEDIUM_ORCHID, MEDIUM_PURPLE, BLUE_VIOLET, DARK_VIOLET,
          DARK_ORCHID, DARK_MAGENTA, INDIGO, LIME_GREEN, MEDIUM_SPRING_GREEN, SPRING_GREEN, MEDIUM_SEA_GREEN, SEA_GREEN,
          FOREST_GREEN, DARK_GREEN, DARK_CYAN, TEAL, AQUA, DEEP_SKY_BLUE, DODGER_BLUE, CORNFLOWER_BLUE,
          MEDIUM_SLATE_BLUE, ROYAL_BLUE, DARK_BLUE, NAVY]

# Шрифты
font_large, font_medium, font_small = pygame.font.Font(None, 70), pygame.font.Font(None, 50), pygame.font.Font(None, 35)

# Параметры платформы и мяча
paddle_width, paddle_height = 150, 20
paddle_original_width, paddle_speed = paddle_width, 15

ball_radius, ball_speed, max_ball_speed = 12, 9, 18
MIN_BALL_SPEED, MAX_BALL_SPEED = 6, 18  # Минимальная скорость шарика и Максимальная скорость шарика

speed_up_count = 0
MAX_SPEED_UP = 2


# Состояния игры
class GameState(Enum):
    MENU, PLAYING, PAUSED, GAME_OVER, LEVEL_CHANGE, BUILDING_LEVEL = 0, 1, 2, 3, 4, 5


class BonusType(Enum):
    TRIPLE, EXTEND, SLOW, SPEED_UP, EXPLOSION = 1, 2, 3, 4, 5


class Particle(pygame.sprite.Sprite):
    def __init__(self, position, color):
        super().__init__()
        self.image = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (3, 3), 3)
        self.rect = self.image.get_rect(center=position)
        self.speed = [random.uniform(-3, 3), random.uniform(-3, 3)]
        self.lifetime = 20

    def update(self):
        self.rect.x += self.speed[0]
        self.rect.y += self.speed[1]
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()


class Ball:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - ball_radius,
                                HEIGHT - paddle_height - 50 - ball_radius * 2, ball_radius * 2, ball_radius * 2)
        angle = math.radians(random.randint(30, 150))
        self.speed = ball_speed
        self.dx = math.cos(angle) * self.speed
        self.dy = -abs(math.sin(angle)) * self.speed
        self.animation_frame = 0
        self.base_color = (0, 0, 255)

    def update_speed(self):
        # Ограничиваем скорость шарика
        self.speed = max(MIN_BALL_SPEED, min(self.speed, MAX_BALL_SPEED))
        speed = math.hypot(self.dx, self.dy)
        if speed != 0:
            self.dx = (self.dx / speed) * self.speed
            self.dy = (self.dy / speed) * self.speed

    def draw(self, surface):
        colors = [self.base_color, (self.base_color[0] // 2, self.base_color[1] // 2, 255),
                  (self.base_color[0] // 4, self.base_color[1] // 4, 255)]
        for i in range(3):
            radius = ball_radius - 2 * ((self.animation_frame + i) % 3)
            pygame.draw.circle(surface, colors[i], self.rect.center, radius, 2)


class Bonus:
    def __init__(self, position, bonus_type):
        self.rect = pygame.Rect(position[0], position[1], 30, 30)
        self.type = bonus_type
        self.speed, self.gravity = 1, 0.05

    def update(self):
        self.speed += self.gravity
        self.rect.y += self.speed

    def draw(self, surface):
        if self.type == BonusType.TRIPLE:
            for i in range(3):
                pygame.draw.circle(surface, BLUE, (self.rect.x + 10 + i * 10, self.rect.y + 15), 5)

        elif self.type == BonusType.EXTEND:
            pygame.draw.rect(surface, GREEN, self.rect)
            text = font_small.render("+", True, WHITE)
            surface.blit(text, (self.rect.x + 7, self.rect.y + 5))

        elif self.type == BonusType.SLOW:
            pygame.draw.rect(surface, ORANGE, self.rect)
            text = font_small.render("S", True, WHITE)
            surface.blit(text, (self.rect.x + 7, self.rect.y + 5))

        elif self.type == BonusType.SPEED_UP:
            pygame.draw.rect(surface, PURPLE, self.rect)
            text = font_small.render("F", True, WHITE)
            surface.blit(text, (self.rect.x + 7, self.rect.y + 5))


class LevelBuilder:
    def __init__(self):
        self.current_pixel, self.pixels, self.bricks = 0, [], []

    def create_level(self, bricks):
        self.bricks, self.pixels = bricks, []
        for brick, color in bricks:
            for x in range(brick.width):
                for y in range(brick.height):
                    self.pixels.append((brick.x + x, brick.y + y, color))
        random.shuffle(self.pixels)
        self.current_pixel = 0

    def update(self):
        if self.current_pixel < len(self.pixels):
            self.current_pixel += 80  # Увеличиваем скорость создания уровня в 4 раза
        return self.current_pixel >= len(self.pixels)

    def draw(self, surface):
        for x, y, color in self.pixels[:self.current_pixel]:
            surface.set_at((x, y), color)


# Создание объектов
paddle = pygame.Rect(WIDTH // 2 - paddle_width // 2, HEIGHT - paddle_height - 30, paddle_width, paddle_height)

balls = [Ball()]
particles = pygame.sprite.Group()
bonuses, current_level = [], 1
level_builder = LevelBuilder()

# Таймеры эффектов
powerup_timers = {'extend': 0, 'slow': 0, 'speed_up': 0}

# Игровые переменные
curr_state = GameState.MENU
running, score, lives = True, 0, 3
paddle_hit_animation = 0

# Флаги для управления звуком
loss_music_flag = False
music_playing = False


def create_bricks():
    bricks = []
    brick_width, brick_height = 50, 15
    for y in range(20):
        for x in range(WIDTH // brick_width):
            brick = pygame.Rect(x * brick_width + 2, y * brick_height + 50, brick_width, brick_height)
            bricks.append((brick, random.choice(COLORS)))
    return bricks


bricks = create_bricks()


def reset_game():
    global score, lives, current_level, bricks, balls, paddle, music_playing, speed_up_count
    score, lives, current_level, speed_up_count = 0, 3, 1, 0
    balls = [Ball()]
    bricks = create_bricks()
    bonuses.clear()
    for key in powerup_timers:
        powerup_timers[key] = 0
    # Возврат ракетки на начальную позицию
    paddle.x, paddle.y = WIDTH // 2 - paddle_width // 2, HEIGHT - paddle_height - 30
    # Остановка музыки и сброс флага
    pygame.mixer.stop()
    music_playing = False


def next_level():
    global current_level, bricks, balls, music_playing, speed_up_count
    speed_up_count = 0
    current_level += 1
    # Оставляем только один шарик
    balls = [Ball()]
    # Сбрасываем скорость шарика к начальной
    balls[0].speed = ball_speed
    # Сбрасываем позицию шарика
    balls[0].rect.center = (WIDTH // 2, HEIGHT - paddle_height - 50 - ball_radius * 2)
    # Создаем новый уровень
    bricks = create_bricks()
    bonuses.clear()
    level_builder.create_level(bricks)
    # Воспроизведение музыки победы
    victory_music.play()
    return GameState.BUILDING_LEVEL


def save_progress():
    if lives > 0:  # Сохраняем прогресс только если жизни больше 0
        data = {"score": score, "level": current_level, "lives": lives}
        with open("progress.json", "w") as file:
            json.dump(data, file)
    else:
        reset_game()


def load_progress():
    try:
        with open("progress.json", "r") as file:
            data = json.load(file)
            return data.get("score", 0), data.get("level", 1), data.get("lives", 3)
    except FileNotFoundError:
        return 0, 1, 3


def draw_text(surface, text, font, color, position, alpha):
    text_surface = font.render(text, True, color)
    text_surface.set_alpha(alpha)
    surface.blit(text_surface, position)


def draw_menu():
    screen.fill((0, 0, 0))
    alpha = int(255 * (1 + math.sin(pygame.time.get_ticks() / 500)) / 2)
    draw_text(screen, "ARKANOID", font_large, RED, (WIDTH // 2 - 125, 50), alpha)

    goal_text = font_medium.render("Цель: Разбейте все кирпичи, сохранив жизни!", True, GREEN)
    screen.blit(goal_text, (WIDTH // 2 - goal_text.get_width() // 2, 150))

    save_text = font_small.render("(Прогресс автоматически сохраняется в файл)", True, WHITE)
    screen.blit(save_text, (WIDTH // 2 - save_text.get_width() // 2, 200))

    y_start = HEIGHT - 280
    texts = [
        ("Управление:", YELLOW),
        ("ВЛЕВО и ВПРАВО - Движение", GREEN),
        ("ESC - Пауза", GREEN),
        ("Бонусы:", YELLOW),
        ("*** - Утроение мячей", BLUE),
        ("+ - Увеличение платформы", GREEN),
        ("S - Замедление мячей", ORANGE),
        ("F - Ускорение платформы", PURPLE)]

    for i, (text, color) in enumerate(texts):
        rendered = font_small.render(text, True, color)
        screen.blit(rendered, (20, y_start + i * 30))

        # Выбор сложности
    difficulty_text = font_medium.render("Выберите сложность:", True, WHITE)
    screen.blit(difficulty_text, (WIDTH // 2 - difficulty_text.get_width() // 2, HEIGHT // 2 - 50))

    for i, (text, color) in enumerate([("1 - Легкий", GREEN), ("2 - Средний", YELLOW), ("3 - Сложный", RED)]):
        rendered = font_medium.render(text, True, color)
        screen.blit(rendered, (WIDTH // 2 - rendered.get_width() // 2, HEIGHT // 2 + i * 40))

    # Выход
    quit_text = font_small.render("Нажмите Q для выхода", True, RED)
    screen.blit(quit_text, (WIDTH - quit_text.get_width() - 20, HEIGHT - 40))


def draw_pause():
    screen.fill((0, 0, 0))
    pause_text = font_large.render("ПАУЗА", True, WHITE)
    continue_text = font_medium.render("Нажмите SPACE для продолжения", True, GREEN)
    screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 3))
    screen.blit(continue_text, (WIDTH // 2 - continue_text.get_width() // 2, HEIGHT // 2))


def draw_game_over():
    screen.fill((0, 0, 0))
    game_over_text = font_large.render("ИГРА ОКОНЧЕНА", True, RED)
    score_text = font_medium.render(f"Ваш счет: {score}", True, WHITE)
    restart_text = font_medium.render("Нажмите SPACE для повторной игры", True, GREEN)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 3))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 100))

    # Проигрываем музыку проигрыша поочередно
    if not pygame.mixer.get_busy():
        global loss_music_flag
        if loss_music_flag:
            loss_music_1.play()
        else:
            loss_music_2.play()
        loss_music_flag = not loss_music_flag


def draw_level_change():
    screen.fill((0, 0, 0))
    level_text = font_large.render(f"Уровень {current_level}", True, WHITE)
    continue_text = font_medium.render("Нажмите SPACE для продолжения", True, GREEN)
    screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT // 3))
    screen.blit(continue_text, (WIDTH // 2 - continue_text.get_width() // 2, HEIGHT // 2))


# Загрузка прогресса
score, current_level, lives = load_progress()

# Игровой цикл
while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if curr_state == GameState.MENU:
                if event.key == pygame.K_1:
                    ball_speed, paddle_speed = 6, 10
                    curr_state = GameState.PLAYING
                    game_music.play(loops=-1)  # Запуск фоновой музыки с зацикливанием
                elif event.key == pygame.K_2:
                    ball_speed, paddle_speed = 9, 15
                    curr_state = GameState.PLAYING
                    game_music.play(loops=-1)
                elif event.key == pygame.K_3:
                    ball_speed, paddle_speed = 12, 20
                    curr_state = GameState.PLAYING
                    game_music.play(loops=-1)
                elif event.key == pygame.K_q:
                    running = False

            if curr_state == GameState.PLAYING and event.key == pygame.K_ESCAPE:
                curr_state = GameState.PAUSED
                game_music.stop()  # Остановка музыки при паузе

            if curr_state in [GameState.PAUSED, GameState.LEVEL_CHANGE] and event.key == pygame.K_SPACE:
                curr_state = GameState.PLAYING
                game_music.play(loops=-1)  # Возобновление музыки

            if curr_state == GameState.GAME_OVER and event.key == pygame.K_SPACE:
                reset_game()
                curr_state = GameState.PLAYING
                game_music.play(loops=-1)

            if curr_state == GameState.BUILDING_LEVEL and event.key == pygame.K_SPACE:
                curr_state = GameState.PLAYING
                game_music.play(loops=-1)

    if curr_state == GameState.MENU:
        draw_menu()

    elif curr_state == GameState.PAUSED:
        draw_pause()

    elif curr_state == GameState.GAME_OVER:
        draw_game_over()

    elif curr_state == GameState.LEVEL_CHANGE:
        draw_level_change()
        if level_builder.update():
            curr_state = GameState.PLAYING

    elif curr_state == GameState.BUILDING_LEVEL:
        if level_builder.update():
            curr_state = GameState.PLAYING
        level_builder.draw(screen)

    elif curr_state == GameState.PLAYING:
        # Обновление таймеров эффектов
        for key in powerup_timers:
            if powerup_timers[key] > 0:
                powerup_timers[key] -= 1
                if powerup_timers[key] == 0:
                    if key == 'extend':
                        paddle.width = paddle_original_width
                    elif key == 'slow':
                        for ball in balls:
                            ball.speed = ball_speed
                    elif key == 'speed_up':
                        speed_up_count = max(0, speed_up_count - 1)
                        paddle_speed = 15 + 5 * speed_up_count  # Возвращаем предыдущее значение скорости

        # Анимация платформы
        paddle_hit_animation = max(0, paddle_hit_animation - 1)
        current_paddle_color = (min(255, 100 + max(0, paddle_hit_animation - 1) * 20),
                                min(255, 100 + max(0, paddle_hit_animation - 1) * 20), 255)

        # Управление платформой
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle.left > 0:
            paddle.left -= paddle_speed
        if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
            paddle.right += paddle_speed

        # В методе обновления шарика добавляем улучшенную логику отскока
        for ball in balls:
            ball.rect.x += ball.dx
            ball.rect.y += ball.dy
            ball.animation_frame = (ball.animation_frame + 1) % 60

            # Столкновение со стенами
            if ball.rect.left <= 0 or ball.rect.right >= WIDTH:
                ball.dx = -ball.dx
            if ball.rect.top <= 0:
                ball.dy = -ball.dy

            # Физика отскока от платформы
            if ball.rect.colliderect(paddle):
                paddle_hit_animation = 10
                for _ in range(8):
                    particles.add(Particle(ball.rect.center, BLUE))

                ball.rect.bottom = paddle.top
                hit_pos = (ball.rect.centerx - paddle.left) / paddle.width
                # Ограничиваем угол отскока
                angle = math.radians(max(30, min(150, 45 * (1 - 2 * hit_pos))))
                angle += math.radians(random.uniform(-5, 5))  # Случайный угол
                speed = math.hypot(ball.dx, ball.dy)
                ball.dx = math.sin(angle) * speed
                ball.dy = -abs(math.cos(angle)) * speed

            # Столкновение с кирпичами
            for brick, color in bricks[:]:
                if ball.rect.colliderect(brick):
                    bricks.remove((brick, color))
                    ball.dy = -ball.dy
                    score += 100

                    # Генерация бонусов
                    if random.random() < 0.3:
                        bonus_type = random.choice(list(BonusType))
                        bonuses.append(Bonus(brick.center, bonus_type))

                    # Создаем частицы
                    for _ in range(10):
                        particles.add(Particle(brick.center, color))
                    break

        # Обновление бонусов
        for bonus in bonuses[:]:
            bonus.update()
            if bonus.rect.colliderect(paddle):
                powerup_sound.play()  # Звук получения бонуса
                if bonus.type == BonusType.TRIPLE:
                    new_balls = []
                    for ball in balls:
                        for _ in range(2):
                            new_ball = Ball()
                            new_ball.rect.center = ball.rect.center
                            angle = math.radians(random.randint(30, 150))
                            new_ball.dx = math.cos(angle) * new_ball.speed
                            new_ball.dy = -abs(math.sin(angle)) * new_ball.speed
                            new_balls.append(new_ball)
                    balls.extend(new_balls)

                elif bonus.type == BonusType.EXTEND:
                    paddle.width = paddle_original_width * 1.5
                    powerup_timers['extend'] = 600  # 10 секунд

                elif bonus.type == BonusType.SLOW:
                    for ball in balls:
                        ball.speed *= 0.5
                    powerup_timers['slow'] = 600  # 10 секунд

                elif bonus.type == BonusType.SPEED_UP:
                    if speed_up_count < MAX_SPEED_UP:
                        speed_up_count += 1
                        paddle_speed = 15 + 5 * speed_up_count  # Увеличиваем скорость на 5 за каждый уровень
                        powerup_timers['speed_up'] = 600
                        powerup_sound.play()
                bonuses.remove(bonus)
            elif bonus.rect.top > HEIGHT:
                bonuses.remove(bonus)

        # Проверка проигрыша
        balls = [ball for ball in balls if ball.rect.bottom < HEIGHT]
        if not balls:
            lives -= 1
            if lives <= 0:
                curr_state = GameState.GAME_OVER
                game_music.stop()  # Остановка фоновой музыки
            else:
                balls.append(Ball())

        if not bricks:
            curr_state = next_level()
            game_music.stop()  # Остановка фоновой музыки при переходе уровня
        particles.update()

        # Отрисовка объектов
        pygame.draw.rect(screen, current_paddle_color, paddle, border_radius=15)
        for ball in balls:
            ball.draw(screen)

        for brick, color in bricks:
            pygame.draw.rect(screen, color, brick)

        for bonus in bonuses:
            bonus.draw(screen)

        particles.draw(screen)

        # Панель информации
        score_text = font_small.render(f"Очки: {score}", True, WHITE)
        lives_text = font_small.render(f"Жизни: {lives}", True, WHITE)
        level_text = font_small.render(f"Уровень: {current_level}", True, WHITE)
        speed_text = font_small.render(f"Скорость: {paddle_speed}", True, WHITE)

        screen.blit(score_text, (20, 20))
        screen.blit(lives_text, (WIDTH - 150, 20))
        screen.blit(level_text, (WIDTH // 2 - 50, 20))
        screen.blit(speed_text, (WIDTH - 350, 20))
    pygame.display.flip()
    pygame.time.Clock().tick(60)
save_progress()
pygame.quit()
