import pygame
import math
import tkinter as tk
from tkinter import filedialog

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1300, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Paint Pro")

# Цвета
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
BUTTON_COLOR, GRAY = (180, 180, 180), (200, 200, 200)

# Настройки
current_color = BLACK
brush_size = 5
current_tool, hex_input = "Кисть", ""
drawing = input_active = False
last_pos = temp_shape = None
history = []
his_index = -1
custom_colors = []

# Загрузка фоновой музыки
pygame.mixer.music.load("data/music/PAINT.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)  # Зацикливаем музыку

# Поверхности
preview_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
main_canvas = pygame.Surface((WIDTH, HEIGHT))
main_canvas.fill(WHITE)

# Шрифты
font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 24)

# Элементы интерфейса
UI_ELEMENTS = {
    "tools": {
        "rect": pygame.Rect(10, 10, 180, 360),
        "items": ["Кисть", "Ластик", "Заливка", "Прямоугольник",
                 "Круг", "Треугольник", "Линия", "Кривая"],
        "buttons": ["+", "-"]},
    "colors": {
        "rect": pygame.Rect(10, 380, 180, 200),
        "colors": [
            (0, 0, 0), (255, 0, 0), (0, 255, 0),
            (0, 0, 255), (255, 255, 0), (255, 165, 0),
            (255, 192, 203), (128, 0, 128), (255, 255, 255)],
        "buttons": ["Добавить"]},
    "controls": {
        "rect": pygame.Rect(10, 590, 180, 160),
        "buttons": ["Сохранить", "Загрузить", "Отменить", "Вперед"]}}


def draw_rounded_line(surface, color, start, end, width):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = max(abs(dx), abs(dy))
    for i in range(distance):
        x = int(start[0] + float(i)/distance * dx)
        y = int(start[1] + float(i)/distance * dy)
        pygame.draw.circle(surface, color, (x, y), width//2)


def calculate_triangle_points(start, end):
    return [start, (end[0], start[1]), ((start[0]+end[0])//2, end[1])]


def fill_area(x, y):
    target = main_canvas.get_at((x, y))
    stack = [(x, y)]
    while stack:
        x, y = stack.pop()
        if main_canvas.get_at((x, y)) == target:
            main_canvas.set_at((x, y), current_color)
            if x > 0: stack.append((x-1, y))
            if x < WIDTH-1: stack.append((x+1, y))
            if y > 0: stack.append((x, y-1))
            if y < HEIGHT-1: stack.append((x, y+1))
    push_history()


def save_image():
    root = tk.Tk()
    root.withdraw()
    try:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")])
        if file_path:
            pygame.image.save(main_canvas, file_path)
    except Exception as e:
        print(f"Ошибка сохранения: {e}")


def load_image():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
    if file_path:
        try:
            loaded_image = pygame.image.load(file_path)
            main_canvas.blit(loaded_image, (0, 0))
            push_history()
        except Exception as e:
            print(f"Ошибка загрузки: {e}")


def push_history():
    global his_index
    # Если после отмены сделано новое действие, удаляем будущие состояния
    if his_index < len(history)-1:
        history[his_index+1:] = []
    # Сохраняем текущее состояние
    history.append(main_canvas.copy())
    his_index = len(history)-1
    # Ограничиваем историю 50 последними действиями
    if len(history) > 50:
        history.pop(0)
        his_index -= 1


def undo():
    global his_index
    if his_index > 0:
        his_index -= 1
        main_canvas.blit(history[his_index], (0, 0))
        redraw_interface()


def redo():
    global his_index
    if his_index < len(history)-1:
        his_index += 1
        main_canvas.blit(history[his_index], (0, 0))
        redraw_interface()


def hex_to_rgb(hex):
    hex = hex.lstrip('#')
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))


def draw_interface():
    # Панель инструментов
    pygame.draw.rect(screen, BUTTON_COLOR, UI_ELEMENTS["tools"]["rect"])
    for i, tool in enumerate(UI_ELEMENTS["tools"]["items"]):
        rect = pygame.Rect(20, 20+i*40, 160, 30)
        color = WHITE if tool == current_tool else GRAY
        pygame.draw.rect(screen, color, rect)
        text = small_font.render(tool, True, BLACK)
        screen.blit(text, (30, 27+i*40))

    # Кнопки размеров
    for i, btn in enumerate(UI_ELEMENTS["tools"]["buttons"]):
        rect = pygame.Rect(20+i*80, 330, 70, 30)
        pygame.draw.rect(screen, GRAY, rect)
        text = small_font.render(btn, True, BLACK)
        screen.blit(text, (40+i*80, 337))

    # Палитра цветов
    pygame.draw.rect(screen, BUTTON_COLOR, UI_ELEMENTS["colors"]["rect"])
    all_colors = UI_ELEMENTS["colors"]["colors"] + custom_colors
    for i, color in enumerate(all_colors):
        x = 20 + (i%3)*50
        y = 390 + (i//3)*50
        pygame.draw.rect(screen, color, (x, y, 40, 40))
        if color == current_color:
            pygame.draw.rect(screen, WHITE, (x-2, y-2, 44, 44), 2)

    # Кнопка добавления цвета
    rect = pygame.Rect(20, 590, 160, 30)
    pygame.draw.rect(screen, GRAY, rect)
    text = small_font.render("Добавить цвет", True, BLACK)
    screen.blit(text, (30, 597))

    # Панель управления
    pygame.draw.rect(screen, BUTTON_COLOR, UI_ELEMENTS["controls"]["rect"])
    for i, btn in enumerate(UI_ELEMENTS["controls"]["buttons"]):
        rect = pygame.Rect(20, 600+i*40, 160, 30)
        pygame.draw.rect(screen, GRAY, rect)
        text = small_font.render(btn, True, BLACK)
        screen.blit(text, (30, 607+i*40))

    # HEX-ввод
    pygame.draw.rect(screen, WHITE, (210, 10, 150, 30))
    text = font.render(hex_input, True, BLACK)
    screen.blit(text, (220, 15))

    # Инфопанель
    info_text = f"Размер: {brush_size} | Цвет: {current_color}"
    text = small_font.render(info_text, True, BLACK)
    screen.blit(text, (WIDTH-300, 10))


def redraw_interface():
    screen.blit(main_canvas, (0, 0))
    draw_interface()
    pygame.display.update()

push_history()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.mixer.music.stop()
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if UI_ELEMENTS["tools"]["rect"].collidepoint(x, y):
                for i, tool in enumerate(UI_ELEMENTS["tools"]["items"]):
                    if 20+i*40 <= y <= 50+i*40:
                        current_tool = tool
                for i, btn in enumerate(UI_ELEMENTS["tools"]["buttons"]):
                    if 330 <= y <= 360 and 20+i*80 <= x <= 90+i*80:
                        if btn == "+": brush_size = min(20, brush_size+1)
                        elif btn == "-": brush_size = max(1, brush_size-1)

            elif UI_ELEMENTS["colors"]["rect"].collidepoint(x, y):
                all_colors = UI_ELEMENTS["colors"]["colors"] + custom_colors
                for i, color in enumerate(all_colors):
                    col_x = 20 + (i%3)*50
                    col_y = 390 + (i//3)*50
                    if col_x <= x <= col_x+40 and col_y <= y <= col_y+40:
                        current_color = color

            elif 20 <= x <= 180 and 590 <= y <= 620:
                if hex_input and len(hex_input) == 6:
                    custom_colors.append(hex_to_rgb(hex_input))
                    hex_input = ""

            elif UI_ELEMENTS["controls"]["rect"].collidepoint(x, y):
                for i, btn in enumerate(UI_ELEMENTS["controls"]["buttons"]):
                    if 600+i*40 <= y <= 630+i*40:
                        if btn == "Сохранить": save_image()
                        elif btn == "Загрузить": load_image()
                        elif btn == "Отменить": undo()
                        elif btn == "Вперед": redo()

            elif 210 <= x <= 360 and 10 <= y <= 40:
                input_active = True
                hex_input = ""
            else:
                input_active = False
                if current_tool == "Заливка":
                    fill_area(x, y)
                else:
                    drawing = True
                    last_pos = (x, y)
                    if current_tool in ["Прямоугольник", "Круг", "Треугольник", "Линия", "Кривая"]:
                        temp_shape = {"tool": current_tool, "start": (x, y), "end": (x, y), "points": [(x, y)]}

        if event.type == pygame.MOUSEBUTTONUP:
            drawing = False
            if temp_shape:
                push_history()
                s = temp_shape["start"]
                e = temp_shape["end"]
                if temp_shape["tool"] == "Прямоугольник":
                    pygame.draw.rect(main_canvas, current_color, (s[0], s[1], e[0]-s[0], e[1]-s[1]), brush_size)
                elif temp_shape["tool"] == "Круг":
                    radius = int(math.hypot(e[0]-s[0], e[1]-s[1]))
                    pygame.draw.circle(main_canvas, current_color, s, radius, brush_size)
                elif temp_shape["tool"] == "Треугольник":
                    points = calculate_triangle_points(s, e)
                    pygame.draw.polygon(main_canvas, current_color, points, brush_size)
                elif temp_shape["tool"] == "Линия":
                    pygame.draw.line(main_canvas, current_color, s, e, brush_size)
                elif temp_shape["tool"] == "Кривая":
                    if len(temp_shape["points"]) > 1:
                        pygame.draw.lines(main_canvas, current_color, False, temp_shape["points"], brush_size)
                temp_shape = None

        if event.type == pygame.MOUSEMOTION and drawing:
            if current_tool in ["Кисть", "Ластик"]:
                color = WHITE if current_tool == "Ластик" else current_color
                draw_rounded_line(main_canvas, color, last_pos, event.pos, brush_size)
                last_pos = event.pos
            elif temp_shape:
                temp_shape["end"] = event.pos
                if temp_shape["tool"] == "Кривая":
                    temp_shape["points"].append(event.pos)

        if event.type == pygame.KEYDOWN:
            if input_active:
                if event.key == pygame.K_RETURN:
                    if len(hex_input) == 6:
                        current_color = hex_to_rgb(hex_input)
                    hex_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    hex_input = hex_input[:-1]
                else:
                    if len(hex_input) < 6 and event.unicode.lower() in "0123456789abcdef":
                        hex_input += event.unicode

    # Отрисовка
    screen.fill(WHITE)
    screen.blit(main_canvas, (0, 0))

    # Предпросмотр фигур
    if temp_shape:
        preview_surface.fill((0,0,0,0))
        tool = temp_shape["tool"]
        points = temp_shape["points"]
        if tool == "Прямоугольник":
            pygame.draw.rect(preview_surface, current_color+(100,),
                           (temp_shape["start"][0], temp_shape["start"][1],
                            temp_shape["end"][0]-temp_shape["start"][0],
                            temp_shape["end"][1]-temp_shape["start"][1]),
                           brush_size)
        elif tool == "Круг":
            radius = int(math.hypot(temp_shape["end"][0]-temp_shape["start"][0],
                                  temp_shape["end"][1]-temp_shape["start"][1]))
            pygame.draw.circle(preview_surface, current_color+(100,),
                             temp_shape["start"], radius, brush_size)
        elif tool == "Треугольник":
            pygame.draw.polygon(preview_surface, current_color+(100,),
                              calculate_triangle_points(temp_shape["start"], temp_shape["end"]),
                              brush_size)
        elif tool == "Линия":
            pygame.draw.line(preview_surface, current_color+(100,),
                           temp_shape["start"], temp_shape["end"], brush_size)
        elif tool == "Кривая":
            if len(points) > 1:
                pygame.draw.lines(preview_surface, current_color+(100,), False, points, brush_size)
        screen.blit(preview_surface, (0,0))

    draw_interface()
    pygame.display.flip()

pygame.quit()
