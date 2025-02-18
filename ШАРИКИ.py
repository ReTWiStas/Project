import pygame
import sys
import random
import math
import os

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((1600, 900))
pygame.display.set_caption("ШАРИКИ")

# Загрузка фоновой музыки
pygame.mixer.music.load("data/music/ШАРИКИ.mp3")
pygame.mixer.music.set_volume(0.15)
pygame.mixer.music.play(-1)  # Зацикливаем музыку

# Скрываем курсор мыши
pygame.mouse.set_visible(False)

mouse_rect = pygame.Rect((0, 0), (23, 23))
flying_circles = []
score_rect = False
score = 0

increment = 1  # Скорость переливания
fade_amount = 0  # Переменная для изменения цвета


class FlyingCircle:
    def __init__(self):
        while True:
            self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            if self.color != (0, 0, 0):
                break
        self.rect = pygame.Rect((random.randint(0, screen.get_width()), random.randint(0, screen.get_height())), (20, 20))
        self.speed_x = random.choice([random.randint(5, 7), random.randint(-7, -5)])
        self.speed_y = random.choice([random.randint(5, 7), random.randint(-7, -5)])
        self.angle = 0

    def move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.x < 0 or (self.rect.x + self.rect.w) > screen.get_width():
            self.speed_x *= -1
        if self.rect.y < 0 or (self.rect.y + self.rect.h) > screen.get_height():
            self.speed_y *= -1

        self.angle += 5
        if self.angle >= 360:
            self.angle = 0

        self.draw()

    def draw(self):
        circle_surface = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        color = (
            max(0, min(255, self.color[0] + int(10 * math.sin(math.radians(self.angle))))),
            max(0, min(255, self.color[1] + int(10 * math.sin(math.radians(self.angle + 120))))),
            max(0, min(255, self.color[2] + int(10 * math.sin(math.radians(self.angle + 240))))))
        pygame.draw.ellipse(circle_surface, color, (0, 0, self.rect.w, self.rect.h))
        rotated_surface = pygame.transform.rotate(circle_surface, self.angle)
        rotated_rect = rotated_surface.get_rect(center=self.rect.center)
        screen.blit(rotated_surface, rotated_rect.topleft)


def show_start_screen():
    try:
        # Загрузка и масштабирование изображения
        start_image = pygame.image.load(os.path.join('data', 'image', 'ШАРИКИ.jpg')).convert()
        start_image = pygame.transform.scale(start_image, (1600, 900))
    except Exception as e:
        print(f"Ошибка загрузки изображения: {e}")
        pygame.quit()
        sys.exit()

    font = pygame.font.Font(None, 120)
    title_surf = font.render("ШАРИКИ", True, 'black')

    font = pygame.font.Font(None, 100)
    instruction_surf = font.render("Нажмите, чтобы играть", True, 'black')

    title_rect = title_surf.get_rect(center=(screen.get_width() / 2, screen.get_height() / 5 - 20))
    instruction_rect = instruction_surf.get_rect(center=(screen.get_width() / 2, screen.get_height() / 1.5 - 130))

    screen.blit(start_image, (0, 0))
    screen.blit(title_surf, title_rect)
    screen.blit(instruction_surf, instruction_rect)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False


show_start_screen()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.mixer.music.stop()
            pygame.quit()
            sys.exit()

    if not score_rect:
        score_rect = pygame.Rect((random.randint(0, (screen.get_width() - 25)),
                                  random.randint(0, (screen.get_height() - 25))), (25, 25))

    # Обновление позиции курсора
    mouse_rect.center = pygame.mouse.get_pos()

    # Ограничение движения шара игрока
    mouse_rect.clamp_ip(screen.get_rect())

    screen.fill('black')  # Черный фон
    pygame.draw.ellipse(screen, (255, 0, 0), mouse_rect)

    fade_amount += increment
    if fade_amount >= 255 or fade_amount <= 0:
        increment = -increment  # Меняем направление
    target_color = (255 - fade_amount, 0, fade_amount)  # Плавный переход от фиолетового к красному

    if score_rect:
        pygame.draw.rect(screen, target_color, score_rect)

    for flying_circle in flying_circles:
        flying_circle.move()
        if flying_circle.rect.colliderect(mouse_rect):
            print(score)
            pygame.quit()
            sys.exit()

    if mouse_rect.colliderect(score_rect):
        score += 1
        if score == 1 or not score % 5:
            circle = FlyingCircle()
            while circle.rect.colliderect(mouse_rect):
                circle = FlyingCircle()
            flying_circles.append(circle)
        score_rect = None
    score_surf = pygame.font.Font(None, 80).render("Счёт: " + str(score), False, 'white')
    score_r = score_surf.get_rect(topleft=(10, 10))
    screen.blit(score_surf, score_r)
    pygame.display.update()
    pygame.time.Clock().tick(60)
