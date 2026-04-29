from random import randint

import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

SPEED = 20

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, position=None, body_color=None):
        """
        Инициализирует базовый игровой объект.

        Аргументы:
            position: Кортеж (x, y) с координатами объекта.
            body_color: Кортеж (r, g, b) с цветом объекта.
        """
        if position is None:
            self.position = (320, 240)
        else:
            self.position = position
        self.body_color = body_color

    def draw(self, surface):
        """
        Абстрактный метод для отрисовки объекта.
        Переопределяется в дочерних классах.

        Аргументы:
            surface: Поверхность pygame для рисования.
        """
        pass


class Apple(GameObject):
    """Класс яблока. Появляется в случайном месте поля."""

    def __init__(self, snake_positions=None):
        """
        Инициализирует яблоко.

        Аргументы:
            snake_positions: Список координат сегментов змейки.
        """
        super().__init__(position=None, body_color=APPLE_COLOR)
        self.randomize_position(snake_positions)

    def randomize_position(self, snake_positions=None):
        """
        Устанавливает случайные координаты для яблока.

        Аргументы:
            snake_positions: Список координат сегментов змейки.
        """
        if snake_positions is None:
            snake_positions = []
        while True:
            x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            self.position = (x, y)
            if self.position not in snake_positions:
                break

    def draw(self, surface):
        """Отрисовывает яблоко на игровой поверхности."""
        rect = pygame.Rect(
            self.position[0], self.position[1], GRID_SIZE, GRID_SIZE
        )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс змейки. Управляет движением, ростом и столкновениями."""

    def __init__(self):
        """Инициализирует змейку в начальном состоянии."""
        super().__init__(body_color=SNAKE_COLOR)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """
        Возвращает позицию головы змейки.

        Возвращает:
            tuple: Координаты (x, y) головы змейки.
        """
        return self.positions[0]

    def update_direction(self):
        """Обновляет направление движения после нажатия клавиши."""
        if self.next_direction:
            next_dx, next_dy = self.next_direction
            dx, dy = self.direction
            if next_dx != -dx or next_dy != -dy:
                self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """
        Перемещает змейку на одну клетку вперёд.
        Реализует прохождение сквозь стены и проверку на самопересечение.
        """
        head = self.get_head_position()
        dx, dy = self.direction
        new_x = (head[0] + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head[1] + dy * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_x, new_y)

        if new_head in self.positions:
            self.reset()
            return

        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def grow(self):
        """Увеличивает длину змейки при съедании яблока."""
        self.length += 1
        if self.last:
            self.positions.append(self.last)
            self.last = None

    def reset(self):
        """Сбрасывает змейку в начальное состояние после столкновения."""
        self.length = 1
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def draw(self, surface):
        """
        Отрисовывает змейку на игровой поверхности.
        Затирает последний сегмент, чтобы не было "следа".

        Аргументы:
            surface: Поверхность pygame для рисования.
        """
        if self.last:
            last_rect = pygame.Rect(
                self.last[0], self.last[1], GRID_SIZE, GRID_SIZE
            )
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

        for position in self.positions:
            rect = pygame.Rect(
                position[0], position[1], GRID_SIZE, GRID_SIZE
            )
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


def handle_keys(snake):
    """
    Обрабатывает нажатия клавиш и изменяет направление движения змейки.

    Аргументы:
        snake: Объект класса Snake.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake.direction != DOWN:
                snake.next_direction = UP
            elif event.key == pygame.K_DOWN and snake.direction != UP:
                snake.next_direction = DOWN
            elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                snake.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                snake.next_direction = RIGHT


def main():
    """Главная функция игры. Содержит основной игровой цикл."""
    snake = Snake()
    apple = Apple(snake.positions)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.grow()
            apple.randomize_position(snake.positions)

        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw(screen)
        snake.draw(screen)
        pygame.display.update()


if __name__ == '__main__':
    main()
