import pygame
import sys
import numpy as np
import random

# Цвета
WHITE, BLACK, RED = (255, 255, 255), (0, 0, 0), (255, 0, 0)
BLUE = (0, 0, 255)  # Цвет выделения выбранной клетки

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Загрузка фоновой музыки
pygame.mixer.music.load("data/music/Судоку.mp3")
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)  # Зацикливаем музыку

# Настройки экрана
WIDTH, HEIGHT = 590, 590
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Судоку")
user_input = {}


def draw_grid():
    block_size = WIDTH // 9
    for i in range(10):
        thickness = 2 if i % 3 == 0 else 1
        pygame.draw.line(win, BLACK, (i * block_size, 0), (i * block_size, HEIGHT), thickness)
        pygame.draw.line(win, BLACK, (0, i * block_size), (WIDTH, i * block_size), thickness)


def draw_title_screen():
    win.fill(WHITE)
    font = pygame.font.Font(None, 75)
    title_text = font.render("Судоку", True, BLACK)
    instruction_text = font.render("Нажмите, чтобы играть", True, BLACK)

    win.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 50))
    win.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT // 2 + 20))
    pygame.display.flip()


def is_valid(num, row, col, grid):
    if num in grid[row]:
        return False
    if num in grid[:, col]:
        return False
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    if num in grid[start_row:start_row + 3, start_col:start_col + 3]:
        return False
    return True


def fill_grid(grid):
    for row in range(9):
        for col in range(9):
            if grid[row, col] == 0:
                nums = list(range(1, 10))
                random.shuffle(nums)
                for num in nums:
                    if is_valid(num, row, col, grid):
                        grid[row, col] = num
                        if fill_grid(grid):
                            return True
                        grid[row, col] = 0
                return False
    return True


def remove_numbers(grid, attempts):
    for _ in range(attempts):
        row, col = random.randint(0, 8), random.randint(0, 8)
        while grid[row, col] == 0:
            row, col = random.randint(0, 8), random.randint(0, 8)
        grid[row, col] = 0
    return grid


def generate_sudoku(difficulty=20):
    grid = np.zeros((9, 9), dtype=int)
    fill_grid(grid)
    return remove_numbers(grid, difficulty)


def draw_numbers(sudoku):
    font = pygame.font.Font(None, 50)
    block_size = WIDTH // 9
    for row in range(9):
        for col in range(9):
            # Рисуем пользовательский ввод красным цветом
            if (row, col) in user_input:
                num = user_input[(row, col)]
                text = font.render(num, True, RED)
                win.blit(text, (col * block_size + 20, row * block_size + 15))
            # Рисуем исходные числа черным цветом
            elif sudoku[row][col] != 0:
                num = sudoku[row][col]
                text = font.render(str(num), True, BLACK)
                win.blit(text, (col * block_size + 20, row * block_size + 15))


def draw_selected_cell():
    if selected_cell is not None:
        row, col = selected_cell
        block_size = WIDTH // 9
        pygame.draw.rect(win, BLUE, (col * block_size, row * block_size, block_size, block_size), 3)


def check_sudoku(grid):
    for row in grid:
        if sorted(row) != list(range(1, 10)):
            return False
    for col in grid.T:
        if sorted(col) != list(range(1, 10)):
            return False
    for i in range(0, 9, 3):
        for j in range(0, 9, 3):
            block = grid[i:i + 3, j:j + 3].flatten()
            if sorted(block) != list(range(1, 10)):
                return False
    return True


if __name__ == "__main__":
    selected_cell = None
    draw_title_screen()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

    sudoku = generate_sudoku(40)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                col = x // (WIDTH // 9)
                row = y // (HEIGHT // 9)
                if sudoku[row][col] == 0:
                    selected_cell = (row, col)
                else:
                    selected_cell = None

            if event.type == pygame.KEYDOWN:
                if selected_cell:
                    row, col = selected_cell
                    if event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                        if (row, col) in user_input:
                            del user_input[(row, col)]
                    elif event.unicode.isdigit() and event.unicode != '0':
                        user_input[(row, col)] = event.unicode
                    elif event.key == pygame.K_RETURN:
                        # Создаем временную сетку для проверки
                        temp_grid = np.copy(sudoku)
                        for (r, c), num in user_input.items():
                            temp_grid[r][c] = int(num)
                        if check_sudoku(temp_grid):
                            print("Поздравляем! Судоку решено правильно!")
                        else:
                            print("Есть ошибки! Попробуйте еще раз.")

        win.fill(WHITE)
        draw_grid()
        draw_selected_cell()
        draw_numbers(sudoku)
        pygame.display.update()

    pygame.quit()
    sys.exit()