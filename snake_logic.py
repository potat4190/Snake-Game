# snake_logic.py
import random
from typing import List, Tuple, Optional

Point = Tuple[int, int]


class Snake:
    DIRECTIONS = {
        "Left": (-1, 0),
        "Right": (1, 0),
        "Up": (0, -1),
        "Down": (0, 1),
    }

    OPPOSITE = {
        "Left": "Right",
        "Right": "Left",
        "Up": "Down",
        "Down": "Up",
    }

    def __init__(self, start: Point, start_length: int = 4, start_dir: str = "Right"):
        cx, cy = start
        self.body: List[Point] = [(cx - i, cy) for i in range(start_length)]  # head at index 0
        self.direction = start_dir
        self.next_direction = start_dir

    def set_direction(self, new_dir: str):
        if new_dir not in Snake.DIRECTIONS:
            return
        # Prevent instant 180-degree reversal when length > 1
        if Snake.OPPOSITE[new_dir] == self.direction and len(self.body) > 1:
            return
        self.next_direction = new_dir

    def next_head(self) -> Point:
        dx, dy = Snake.DIRECTIONS[self.next_direction]
        hx, hy = self.body[0]
        return (hx + dx, hy + dy)

    def advance(self, grow: bool = False):
        """Move snake forward, optionally growing (when `grow` is True)."""
        self.direction = self.next_direction
        new_head = self.next_head()
        self.body.insert(0, new_head)
        if not grow:
            self.body.pop()

    def collides_with_self(self) -> bool:
        head = self.body[0]
        return head in self.body[1:]


class Game:
    def __init__(self, grid_width: int, grid_height: int, start_length: int = 4):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.start_length = start_length
        self.score = 0
        self.snake: Optional[Snake] = None
        self.food: Optional[Point] = None
        self.running = False
        self.reset()

    def reset(self):
        cx = self.grid_width // 2
        cy = self.grid_height // 2
        self.snake = Snake((cx, cy), start_length=self.start_length, start_dir="Right")
        self.score = 0
        self.running = True
        self.place_food()

    def place_food(self):
        free_cells = [
            (x, y)
            for x in range(self.grid_width)
            for y in range(self.grid_height)
            if (x, y) not in self.snake.body
        ]
        if not free_cells:
            # No free cell: player wins / no food
            self.food = None
            return
        self.food = random.choice(free_cells)

    def step(self, direction: Optional[str] = None) -> dict:
        """
        Advance game by one tick.
        :param direction: optional direction requested by player (e.g., "Left")
        :return: dict with keys:
            - 'alive': bool
            - 'ate': bool
            - 'game_over': bool
            - 'score': int
        """
        if not self.running:
            return {"alive": False, "ate": False, "game_over": True, "score": self.score}

        if direction:
            self.snake.set_direction(direction)

        new_head = self.snake.next_head()
        nx, ny = new_head

        # Check wall collisions
        if nx < 0 or ny < 0 or nx >= self.grid_width or ny >= self.grid_height:
            self.running = False
            return {"alive": False, "ate": False, "game_over": True, "score": self.score}

        # Check self-collision (note tail will vacate unless growing)
        # We'll simulate growth check by seeing if new_head is in body except the tail
        body_without_tail = self.snake.body[:-1]
        if new_head in body_without_tail:
            self.running = False
            return {"alive": False, "ate": False, "game_over": True, "score": self.score}

        ate = (self.food is not None and new_head == self.food)

        # Advance snake (grow if ate)
        self.snake.advance(grow=ate)

        if ate:
            self.score += 10
            self.place_food()

        # Additional safety: detect self-collision after move
        if self.snake.collides_with_self():
            self.running = False
            return {"alive": False, "ate": ate, "game_over": True, "score": self.score}

        return {"alive": True, "ate": ate, "game_over": False, "score": self.score}

    # Helper accessors for GUI
    def get_snake_positions(self) -> List[Point]:
        return list(self.snake.body)

    def get_food_position(self) -> Optional[Point]:
        return self.food

    def is_running(self) -> bool:
        return self.running
