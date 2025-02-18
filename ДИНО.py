import pygame
import random
import sys
from os import path

pygame.init()
pygame.mixer.init()

# Настройки окна
WIDTH, HEIGHT = 700, 350
SCORE_FONT = pygame.font.SysFont('comicsans', 40)
INSTRUCTION_FONT = pygame.font.SysFont('comicsans', 30)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Динозаврик")

# Загрузка фоновой музыки
pygame.mixer.music.load("data/music/Динозаврик.mp3")
pygame.mixer.music.set_volume(0.05)
pygame.mixer.music.play(-1)  # Зацикливаем музыку

# Загрузка спрайтов
img_dir = path.join(path.dirname(__file__), 'data', 'assets')
dino_run1 = pygame.image.load(path.join(img_dir, 'dino_run2.1.png')).convert_alpha()
dino_run2 = pygame.image.load(path.join(img_dir, 'dino_run2.2.png')).convert_alpha()
duck_frames = [
    pygame.image.load(path.join(img_dir, 'dino_duck2.1.png')).convert_alpha(),
    pygame.image.load(path.join(img_dir, 'dino_duck2.2.png')).convert_alpha()]
bird_frames = [
    pygame.image.load(path.join(img_dir, 'bird1.png')).convert_alpha(),
    pygame.image.load(path.join(img_dir, 'bird2.png')).convert_alpha()]
cactus_small = pygame.image.load(path.join(img_dir, 'cactus1.2.png')).convert_alpha()
cactus_large = pygame.image.load(path.join(img_dir, 'cactus2.2.png')).convert_alpha()
road_img = pygame.image.load(path.join(img_dir, 'ground.png')).convert_alpha()

# Параметры дороги
road_height, road_width = road_img.get_height(), road_img.get_width()
road_x, road_y = 0, HEIGHT - road_height - 40
road2_x = road_width

# Настройки игровых объектов
PLAYER_HEIGHT = 50
PLAYER_Y = road_y - PLAYER_HEIGHT + 15  # Динозавр стоит на дороге
OBSTACLE_BASE_Y = road_y + 15  # Кактусы на дороге
BIRD_Y_RANGE = (HEIGHT - 150, HEIGHT - 120)  # Птички летают

# Таймеры
SPAWNOB = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWNOB, 1500)
BIRD_ANIM = pygame.USEREVENT + 2
pygame.time.set_timer(BIRD_ANIM, 150)

# Инициализация объектов
player = pygame.Rect(50, PLAYER_Y, 50, PLAYER_HEIGHT)
obstacles = []

# Переменные для анимации
run_frames = [dino_run1, dino_run2]
current_frame = 0
frame_time = 0
FRAME_RATE = 10  # Скорость смены кадров
duck_frame_time = 0
current_duck_frame = 0

# Переменные для игры
in_air = False
score = 0
jumping, jumping_speed = False, 10
game, game_started = False, False

class Obstacle:
    def __init__(self, type, rect):
        self.type = type  # 'cactus' или 'bird'
        self.rect = rect
        self.anim_frame = 0

def create_obstacle():
    if random.random() < 0.3:  # 30% шанс появления птицы
        height = 40
        y = random.randint(*BIRD_Y_RANGE)
        return Obstacle('bird', pygame.Rect(WIDTH, y, 60, height))
    else:  # Кактус
        cactus_type = random.choice(['small', 'large'])
        if cactus_type == 'small':
            height = 50
            return Obstacle('cactus', pygame.Rect(WIDTH, OBSTACLE_BASE_Y - height, 60, height))
        else:
            height = 70
            return Obstacle('cactus', pygame.Rect(WIDTH, OBSTACLE_BASE_Y - height, 60, height))

def handle_animation():
    for obstacle in obstacles:
        if obstacle.type == 'bird':
            obstacle.anim_frame = (obstacle.anim_frame + 1) % len(bird_frames)

# Основной игровой цикл
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.mixer.music.stop()  # Останавливаем музыку перед выходом
            pygame.quit()
            sys.exit()

        if event.type == SPAWNOB and game_started:
            obstacles.append(create_obstacle())
        if event.type == BIRD_ANIM:
            handle_animation()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not in_air:
                jumping = True
                game = True
                game_started = True

    if game:
        if jumping:
            player.y -= jumping_speed
            jumping_speed -= 0.5
            if jumping_speed <= 0:
                jumping = False
            in_air = True

        if pygame.key.get_pressed()[pygame.K_s] or pygame.key.get_pressed()[pygame.K_DOWN]:
            jumping = False
            if player.y < (PLAYER_Y - player.height):
                player.y += 8
            else:
                duck_frame_time += 1
                if duck_frame_time >= 10:
                    duck_frame_time = 0
                    current_duck_frame = (current_duck_frame + 1) % len(duck_frames)
                current_sprite = duck_frames[current_duck_frame]
                player.y = OBSTACLE_BASE_Y
            in_air = True
        elif not (pygame.key.get_pressed()[pygame.K_s] or pygame.key.get_pressed()[pygame.K_DOWN]):
            player.height = PLAYER_HEIGHT
            player.width = 50
            in_air = False

        if not jumping:
            if player.y < PLAYER_Y:
                player.y -= jumping_speed
                jumping_speed -= 0.5
            else:
                jumping_speed = 10
                player.y = PLAYER_Y
                if not player.height == 30:
                    in_air = False
        score += 1

    # Анимация дороги
    if game_started:
        road_speed = 10 if score // 10 < 500 else 12
        road_x -= road_speed
        road2_x -= road_speed

        if road_x < -road_width:
            road_x = road_width
        if road2_x < -road_width:
            road2_x = road_width

    screen.fill('white')
    screen.blit(road_img, (road_x, road_y))
    screen.blit(road_img, (road2_x, road_y))

    # Анимация динозавра
    if not in_air and not jumping:
        if pygame.key.get_pressed()[pygame.K_s] or pygame.key.get_pressed()[pygame.K_DOWN]:
            duck_frame_time += 1
            if duck_frame_time >= 10:
                duck_frame_time = 0
                current_duck_frame = (current_duck_frame + 1) % len(duck_frames)
            current_sprite = duck_frames[current_duck_frame]
        else:
            frame_time += 1
            if frame_time >= 10:
                frame_time = 0
                current_frame = (current_frame + 1) % len(run_frames)
            current_sprite = run_frames[current_frame]
    else:
        current_sprite = dino_run1

    scaled_dino = pygame.transform.scale(current_sprite, (player.width, player.height))
    screen.blit(scaled_dino, player.topleft)

    # Отрисовка препятствий
    for obstacle in obstacles:
        if game_started:
            obstacle.rect.x -= road_speed if score // 10 < 500 else road_speed + 2
            obstacle.rect.x = int(obstacle.rect.x)

            if obstacle.type == 'bird':
                frame = bird_frames[obstacle.anim_frame]
                screen.blit(pygame.transform.scale(frame, (obstacle.rect.width, obstacle.rect.height)), obstacle.rect.topleft)
            else:
                if obstacle.rect.height == 50:
                    cactus_sprite = pygame.transform.scale(cactus_small, (obstacle.rect.width, obstacle.rect.height))
                else:
                    cactus_sprite = pygame.transform.scale(cactus_large, (75, obstacle.rect.height))
                screen.blit(cactus_sprite, obstacle.rect.topleft)

        if player.colliderect(obstacle.rect):
            print("Ты проиграл, твой счёт:", score // 10)
            pygame.quit()
            sys.exit()

    # Отображение счёта
    score_text = SCORE_FONT.render("Счёт: " + str(score // 10), 1, 'black')
    screen.blit(score_text, (10, 10))

    # Отображение инструкций до начала игры
    if not game_started:
        instruction_text1 = INSTRUCTION_FONT.render("Нажмите ПРОБЕЛ, чтобы прыгать и начать игру", 1, 'black')
        instruction_text2 = INSTRUCTION_FONT.render("Используйте СТРЕЛКУ ВНИЗ, чтобы присесть", 1, 'black')
        screen.blit(instruction_text1, (WIDTH // 2 - instruction_text1.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(instruction_text2, (WIDTH // 2 - instruction_text2.get_width() // 2, HEIGHT // 2))

    pygame.display.update()
    pygame.time.Clock().tick(60)