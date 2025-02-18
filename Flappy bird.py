import pygame
import random
import math
import sys
import os

# Инициализация Pygame и микшера
pygame.init()
pygame.mixer.init()

# Настройки окна
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")
pygame.mouse.set_visible(False)

# Загрузка звуков и музыки
BG_MUSIC_PATH = pygame.mixer.Sound("data/music/Flappy bird музыка.mp3")
DEATH_SOUND_PATH = pygame.mixer.Sound("data/music/Flappy bird проигрыш.mp3")
WING_SOUND_PATH = pygame.mixer.Sound("data/music/Flappy bird взмах крыльев.mp3")

BG_MUSIC_PATH.set_volume(0.1)  # 10% громкости для фоновой музыки
DEATH_SOUND_PATH.set_volume(0.2)
WING_SOUND_PATH.set_volume(0.3)
# Загрузка спрайтов птицы
BIRD_SPRITE_SHEET = pygame.image.load(os.path.join("data", "assets", "birds.png"))  # Загружаем одно изображение

# Разделение спрайта на две части
BIRD_IMAGES = [BIRD_SPRITE_SHEET.subsurface(pygame.Rect(0, 0, 45, 40)),  # Левая половина (первая птица)
               BIRD_SPRITE_SHEET.subsurface(pygame.Rect(45, 0, 45, 40))]  # Правая половина (вторая птица)

# Цвета и Темы оформления
DARK_GREEN, DARK_GRAY = (0, 100, 0), (64, 64, 64)

themes = {'light': {'background': 'white', 'pipe': DARK_GREEN, 'text': 'black'},
          'dark': {'background': 'black', 'pipe': DARK_GRAY, 'text': 'white'}}


class Bird:
    def __init__(self):
        self.x, self.y = 50, HEIGHT // 2
        self.velocity = self.frame = self.animation_counter = 0

    def jump(self):
        self.velocity = -6
        WING_SOUND_PATH.play()  # Воспроизводим звук взмаха крыльев

    def update(self):
        self.velocity += 0.25
        self.y += self.velocity
        self.animation_counter += 1
        if self.animation_counter % 10 == 0:  # Замедление анимации
            self.frame = (self.frame + 1) % 2

    def draw(self):
        screen.blit(BIRD_IMAGES[self.frame], (self.x, int(self.y)))


class Pipe:
    def __init__(self, theme):
        self.width, self.x = 70, WIDTH
        self.gap_position = random.randint(150, HEIGHT - 350)
        self.scored, self.color = False, themes[theme]['pipe']
        self.top_rect = pygame.Rect(self.x, 0, self.width, self.gap_position)
        self.bottom_rect = pygame.Rect(self.x, self.gap_position + 200, self.width, HEIGHT)

    def update(self):
        self.x -= 3
        self.top_rect.x = self.bottom_rect.x = self.x

    def draw(self):
        pygame.draw.rect(screen, self.color, self.top_rect)
        pygame.draw.rect(screen, self.color, self.bottom_rect)

    def offscreen(self):
        return self.x < -self.width


def draw_text(text, font, color, y):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, text_surface.get_rect(center=(WIDTH // 2, y)))


def start_screen():
    running, current_theme = True, 'light'
    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return current_theme
                elif event.key == pygame.K_l:
                    current_theme = 'light'
                elif event.key == pygame.K_d:
                    current_theme = 'dark'

        # Настройка цветов в зависимости от темы
        bg_color = pygame.Color('white') if current_theme == 'light' else pygame.Color('black')
        text_color = pygame.Color('black') if current_theme == 'light' else pygame.Color('white')

        # Очистка экрана
        screen.fill(bg_color)

        # Анимированный заголовок
        current_time = pygame.time.get_ticks() / 1000.0
        factor = (math.sin(current_time * 3) + 1) / 2
        title_color = (int(255 * factor), 100, 0)  # Пульсирующий оранжевый

        # Рендер заголовка
        title_font = pygame.font.Font(None, 74)
        title_surface = title_font.render("Flappy Bird!", True, title_color)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title_surface, title_rect)

        # Основной шрифт
        info_font = pygame.font.Font(None, 36)

        # Блок с описанием цели игры
        objective = ["Цель игры:", "Пролетайте между трубами, набирая очки."]
        for i, line in enumerate(objective):
            text = info_font.render(line, True, text_color)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60 + i * 40))
            screen.blit(text, text_rect)

        # Блок с управлением
        controls = ["Управление:", "Пробел - прыжок", "Esc - пауза"]
        for i, line in enumerate(controls):
            text = info_font.render(line, True, text_color)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 40))
            screen.blit(text, text_rect)

        # Блок с выбором темы
        themes = ["Выберите тему:", "L - Светлая", "D - Темная"]
        for i, line in enumerate(themes):
            text = info_font.render(line, True, text_color)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120 + i * 40))
            screen.blit(text, text_rect)

        # Мигающая подсказка
        prompt_factor = (math.sin(current_time * 2) + 1) / 2
        prompt_color = (int(255 * prompt_factor),) * 3 if current_theme == 'light' else (int(255 * (
                1 - prompt_factor)),) * 3
        prompt = info_font.render("Нажмите Enter для начала игры", True, prompt_color)
        prompt_rect = prompt.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        screen.blit(prompt, prompt_rect)

        pygame.display.flip()
        pygame.time.Clock().tick(60)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:
                    return 'light'
                elif event.key == pygame.K_d:
                    return 'dark'


def game_over_screen(theme, score):
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)
    draw_text('Игра окончена!', font, themes[theme]['text'], HEIGHT // 2 - 100)
    draw_text(f'Счет: {score}', font, themes[theme]['text'], HEIGHT // 2 - 50)
    draw_text('Нажмите пробел, чтобы начать заново', small_font, themes[theme]['text'], HEIGHT // 2 + 50)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return


def main():
    current_theme = start_screen()

    # Запуск фоновой музыки
    BG_MUSIC_PATH.play(loops=-1)  # Зацикливаем фоновую музыку

    bird = Bird()
    pipes, score = [], 0
    last_pipe = pygame.time.get_ticks() - 1500
    running = game_active = True
    is_paused = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_active and not is_paused:
                        bird.jump()
                    elif not game_active:
                        main()
                elif event.key == pygame.K_ESCAPE:
                    is_paused = not is_paused

        if game_active and not is_paused:  # Игровая логика только когда нет паузы
            time_now = pygame.time.get_ticks()
            if time_now - last_pipe > 1500:
                pipes.append(Pipe(current_theme))
                last_pipe = time_now

            bird.update()
            for pipe in pipes:
                pipe.update()
            pipes = [pipe for pipe in pipes if not pipe.offscreen()]

            # Проверка столкновений
            bird_rect = pygame.Rect(bird.x, bird.y, 50, 50)
            for pipe in pipes:
                if bird_rect.colliderect(pipe.top_rect) or bird_rect.colliderect(pipe.bottom_rect):
                    DEATH_SOUND_PATH.play()  # Звук проигрыша
                    BG_MUSIC_PATH.stop()  # Останавливаем фоновую музыку
                    game_active = False
                    game_over_screen(current_theme, score)

            # Проверка границ экрана
            if bird.y + 50 > HEIGHT or bird.y < 0:
                DEATH_SOUND_PATH.play()  # Звук проигрыша
                BG_MUSIC_PATH.stop()  # Останавливаем фоновую музыку
                game_active = False
                game_over_screen(current_theme, score)

            # Обновление счета
            for pipe in pipes:
                if not pipe.scored and pipe.x + pipe.width < bird.x:
                    score += 1
                    pipe.scored = True

        # Отрисовка
        screen.fill(themes[current_theme]['background'])
        bird.draw()
        for pipe in pipes:
            pipe.draw()
        draw_text(str(score), pygame.font.Font(None, 75), themes[current_theme]['text'], 50)

        if is_paused:  # Показываем текст паузы
            draw_text("Пауза", pygame.font.Font(None, 75), themes[current_theme]['text'], HEIGHT // 2)
        pygame.display.update()
        pygame.time.Clock().tick(60)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
