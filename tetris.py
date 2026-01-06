import tkinter as tk
import random
from tkinter import messagebox

# ================== CONSTANTS ==================
GAME_WIDTH = 400
GAME_HEIGHT = 600
GRID_SIZE = 30

BOARD_WIDTH = GAME_WIDTH // GRID_SIZE
BOARD_HEIGHT = GAME_HEIGHT // GRID_SIZE

BOARD_PIXEL_WIDTH = BOARD_WIDTH * GRID_SIZE
BOARD_PIXEL_HEIGHT = BOARD_HEIGHT * GRID_SIZE

BASE_SPEED = 500
MIN_SPEED = 100

SHAPES = [
    ([[1, 1, 1, 1]], "cyan"),
    ([[1, 1], [1, 1]], "yellow"),
    ([[1, 1, 0], [0, 1, 1]], "green"),
    ([[0, 1, 1], [1, 1, 0]], "red"),
    ([[1, 1, 1], [0, 1, 0]], "purple"),
    ([[1, 1, 1], [1, 0, 0]], "orange"),
    ([[1, 1, 1], [0, 0, 1]], "blue"),
]

# ================== GAME CLASS ==================
class Tetris(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Tetris")
        self.resizable(False, False)

        self.canvas = tk.Canvas(
            self,
            width=GAME_WIDTH + 140,
            height=GAME_HEIGHT,
            bg="black"
        )
        self.canvas.pack()

        self.info = tk.Label(self, font=("Helvetica", 12))
        self.info.pack()

        self.board = [[0]*BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        self.colors = [[None]*BOARD_WIDTH for _ in range(BOARD_HEIGHT)]

        self.score = 0
        self.level = 1
        self.lines = 0
        self.speed = BASE_SPEED
        self.paused = False

        self.current_shape, self.current_color = self.get_new_shape()
        self.next_shape, self.next_color = self.get_new_shape()
        self.current_position = [0, BOARD_WIDTH // 2 - len(self.current_shape[0]) // 2]

        # Controls
        self.bind("<Left>", lambda e: self.move(-1))
        self.bind("<Right>", lambda e: self.move(1))
        self.bind("<Down>", lambda e: self.soft_drop())
        self.bind("<Up>", lambda e: self.rotate())
        self.bind("<space>", lambda e: self.hard_drop())
        self.bind("p", lambda e: self.toggle_pause())

        self.update_info()
        self.after(self.speed, self.game_loop)

    # ================== GAME LOGIC ==================
    def get_new_shape(self):
        return random.choice(SHAPES)

    def toggle_pause(self):
        self.paused = not self.paused
        self.update_info()

    def update_info(self):
        status = "PAUSED" if self.paused else ""
        self.info.config(
            text=f"Score: {self.score}   Level: {self.level}   Lines: {self.lines}   {status}"
        )

    def valid(self, shape=None, pos=None):
        shape = shape or self.current_shape
        pos = pos or self.current_position

        for i, row in enumerate(shape):
            for j, val in enumerate(row):
                if val:
                    x = pos[1] + j
                    y = pos[0] + i
                    if x < 0 or x >= BOARD_WIDTH or y >= BOARD_HEIGHT:
                        return False
                    if y >= 0 and self.board[y][x]:
                        return False
        return True

    def move(self, dx):
        if self.paused:
            return
        self.current_position[1] += dx
        if not self.valid():
            self.current_position[1] -= dx

    def soft_drop(self):
        if self.paused:
            return
        self.current_position[0] += 1
        if not self.valid():
            self.current_position[0] -= 1
            self.lock()

    def hard_drop(self):
        if self.paused:
            return
        while self.valid():
            self.current_position[0] += 1
        self.current_position[0] -= 1
        self.lock()

    def rotate(self):
        if self.paused:
            return
        rotated = list(zip(*self.current_shape[::-1]))
        rotated = [list(r) for r in rotated]
        if self.valid(rotated):
            self.current_shape = rotated

    def lock(self):
        for i, row in enumerate(self.current_shape):
            for j, val in enumerate(row):
                if val:
                    y = self.current_position[0] + i
                    x = self.current_position[1] + j
                    if y < 0:
                        self.game_over()
                        return
                    self.board[y][x] = 1
                    self.colors[y][x] = self.current_color

        self.clear_lines()
        self.current_shape, self.current_color = self.next_shape, self.next_color
        self.next_shape, self.next_color = self.get_new_shape()
        self.current_position = [0, BOARD_WIDTH // 2 - len(self.current_shape[0]) // 2]

    def clear_lines(self):
        new_board = []
        new_colors = []
        cleared = 0

        for i in range(BOARD_HEIGHT):
            if all(self.board[i]):
                cleared += 1
            else:
                new_board.append(self.board[i])
                new_colors.append(self.colors[i])

        for _ in range(cleared):
            new_board.insert(0, [0]*BOARD_WIDTH)
            new_colors.insert(0, [None]*BOARD_WIDTH)

        self.board = new_board
        self.colors = new_colors

        if cleared:
            self.lines += cleared
            self.score += cleared * 100 * self.level
            self.level = self.lines // 10 + 1
            self.speed = max(MIN_SPEED, BASE_SPEED - (self.level - 1) * 40)

        self.update_info()

    # ================== DRAWING ==================
    def draw(self):
        self.canvas.delete("all")

        # Board border
        self.canvas.create_rectangle(
            0, 0,
            BOARD_PIXEL_WIDTH, BOARD_PIXEL_HEIGHT,
            outline="white",
            width=2
        )

        # Grid
        for x in range(0, BOARD_PIXEL_WIDTH, GRID_SIZE):
            self.canvas.create_line(x, 0, x, BOARD_PIXEL_HEIGHT, fill="#222")
        for y in range(0, BOARD_PIXEL_HEIGHT, GRID_SIZE):
            self.canvas.create_line(0, y, BOARD_PIXEL_WIDTH, y, fill="#222")

        # Locked blocks
        for i in range(BOARD_HEIGHT):
            for j in range(BOARD_WIDTH):
                if self.board[i][j]:
                    x, y = j * GRID_SIZE, i * GRID_SIZE
                    self.canvas.create_rectangle(
                        x, y, x+GRID_SIZE, y+GRID_SIZE,
                        fill=self.colors[i][j],
                        outline="black"
                    )

        # Ghost piece
        ghost_pos = self.current_position[:]
        while self.valid(pos=ghost_pos):
            ghost_pos[0] += 1
        ghost_pos[0] -= 1

        for i, row in enumerate(self.current_shape):
            for j, val in enumerate(row):
                if val:
                    x = (ghost_pos[1]+j) * GRID_SIZE
                    y = (ghost_pos[0]+i) * GRID_SIZE
                    self.canvas.create_rectangle(
                        x, y, x+GRID_SIZE, y+GRID_SIZE,
                        outline="white",
                        dash=(2, 2)
                    )

        # Current piece
        for i, row in enumerate(self.current_shape):
            for j, val in enumerate(row):
                if val:
                    x = (self.current_position[1]+j) * GRID_SIZE
                    y = (self.current_position[0]+i) * GRID_SIZE
                    self.canvas.create_rectangle(
                        x, y, x+GRID_SIZE, y+GRID_SIZE,
                        fill=self.current_color,
                        outline="black"
                    )

        # Divider
        self.canvas.create_line(
            BOARD_PIXEL_WIDTH + 10, 0,
            BOARD_PIXEL_WIDTH + 10, GAME_HEIGHT,
            fill="white"
        )

        # Next piece panel
        ox = BOARD_PIXEL_WIDTH + 40
        oy = 60
        self.canvas.create_text(
            ox, 30,
            text="NEXT",
            fill="white",
            font=("Helvetica", 12, "bold")
        )

        for i, row in enumerate(self.next_shape):
            for j, val in enumerate(row):
                if val:
                    self.canvas.create_rectangle(
                        ox + j*20, oy + i*20,
                        ox + j*20 + 20, oy + i*20 + 20,
                        fill=self.next_color,
                        outline="black"
                    )

    # ================== LOOP ==================
    def game_loop(self):
        if not self.paused:
            self.soft_drop()
            self.draw()
        self.after(self.speed, self.game_loop)

    def game_over(self):
        messagebox.showinfo("Game Over", f"Score: {self.score}")
        self.destroy()


# ================== RUN ==================
if __name__ == "__main__":
    Tetris().mainloop()
