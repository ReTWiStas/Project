import pygame
import sys
import random

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Настройки экрана
WIDTH, HEIGHT = (1600, 900)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Пин-понг!")
SCORE_FONT = pygame.font.SysFont('comicsans', 50)

# Скрываем курсор мыши
pygame.mouse.set_visible(False)

# Загрузка фоновой музыки
pygame.mixer.music.load("data/music/Пин-понг.mp3")
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1)  # Зацикливаем музыку

# Игроки и мяч
player1 = pygame.Rect((10, (HEIGHT // 2) - 50), (10, 100))
player2 = pygame.Rect((WIDTH - 20, (HEIGHT // 2) - 50), (10, 100))
ball = pygame.Rect(((WIDTH / 2) - (20 / 2), (HEIGHT / 2) - (20 / 2)), (20, 20))
player1_score,  player2_score = 0, 0

game = False

# Скорость мяча
initial_speed = 5
ball_speed_y = initial_speed if random.randint(0, 1) else -initial_speed
ball_speed_x = initial_speed if random.randint(0, 1) else -initial_speed


def move_ball():
    global ball_speed_x, ball_speed_y, game, player2_score, player1_score
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    if ball.y <= 0 or ball.y + ball.height >= HEIGHT:
        ball_speed_y *= -1

    if ball.x <= 0:
        ball.x, ball.y = (WIDTH / 2) - (20 / 2), (HEIGHT / 2) - (20 / 2)
        player2_score += 1
        game = False
    elif ball.x + ball.width >= WIDTH:
        ball.x, ball.y = (WIDTH / 2) - (20 / 2), (HEIGHT / 2) - (20 / 2)
        player1_score += 1
        game = False

    if ball.colliderect(player1) and ball_speed_x < 0:
        ball_speed_x *= -1
    if ball.colliderect(player2) and ball_speed_x > 0:
        ball_speed_x *= -1


def move_players():
    keys_pressed = pygame.key.get_pressed()
    if keys_pressed[pygame.K_DOWN]:
        player2.y += 5
        if player2.y + player2.height > HEIGHT:
            player2.y = HEIGHT - player2.height
    elif keys_pressed[pygame.K_UP]:
        player2.y -= 5
        if player2.y < 0:
            player2.y = 0

    if keys_pressed[pygame.K_s]:
        player1.y += 5
        if player1.y + player1.height > HEIGHT:
            player1.y = HEIGHT - player1.height
    elif keys_pressed[pygame.K_w]:
        player1.y -= 5
        if player1.y < 0:
            player1.y = 0


def draw_score():
    score_text = SCORE_FONT.render(str(player1_score), 1, 'white')
    screen.blit(score_text, (WIDTH // 4, 10))
    score_text = SCORE_FONT.render(str(player2_score), 1, 'white')
    screen.blit(score_text, (3 * WIDTH // 4, 10))


def show_start_screen():
    screen.fill('black')
    font = pygame.font.Font(None, 100)
    title_surf = font.render("Пин-понг!!!", True, 'white')
    font = pygame.font.Font(None, 75)
    instruction_surf = font.render("Нажмите любую клавишу, чтобы играть", True, 'white')

    title_rect = title_surf.get_rect(center=(WIDTH / 2, HEIGHT / 3))
    instruction_rect = instruction_surf.get_rect(center=(WIDTH / 2, HEIGHT / 2))

    screen.blit(title_surf, title_rect)
    screen.blit(instruction_surf, instruction_rect)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False


# Показываем заставку
show_start_screen()

# Основной цикл
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.mixer.music.stop()
            pygame.quit()
            sys.exit()
        if not game and event.type == pygame.KEYDOWN:
            game = True

    if game:
        move_ball()
        move_players()

    screen.fill('black')
    pygame.draw.rect(screen, 'white', player1)
    pygame.draw.rect(screen, 'white', player2)
    pygame.draw.ellipse(screen, (200, 200, 200), ball)
    draw_score()
    pygame.display.update()
    pygame.time.Clock().tick(60)
