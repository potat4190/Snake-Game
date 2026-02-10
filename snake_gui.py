# snake_gui.py
import tkinter as tk
import random
import math
from typing import Optional
from snake_logic import Game

# ---- Configuration ------------------------------------------------
CELL_SIZE = 24
GRID_WIDTH = 30
GRID_HEIGHT = 20
GAME_SPEED = 130  # ms between steps

# ---- Dark-mode palette -------------------------------------------
BG_COLOR    = "#1a1a2e"
PANEL_BG    = "#16213e"
TEXT_COLOR  = "#e0e0e0"
ACCENT      = "#0f3460"
BTN_BG      = "#0f3460"
BTN_FG      = "#e0e0e0"
BTN_HOVER   = "#1a5276"
SCORE_CLR   = "#00d4aa"

# ---- Grass palette ------------------------------------------------
GRASS_BASE   = "#2d5a27"
GRASS_COLORS = ["#1e4d2b", "#2d6a2e", "#3a7a3a", "#245522",
                "#1b4d1b", "#336633"]
GRASS_FLOWER = ["#dec04a", "#c776d5", "#bcd298"]

# ---- Snake palette ------------------------------------------------
SNAKE_HEAD       = "#7836e2"
SNAKE_BODY_START = "#7836e2"
SNAKE_BODY_END   = "#492386"
SNAKE_OUTLINE    = "#000000"
SNAKE_EYE_W      = "#ffffff"
SNAKE_EYE_P      = "#1a1a1a"
SNAKE_TONGUE     = "#ef4444"

# ---- Apple palette ------------------------------------------------
APPLE_BODY      = "#ef4444"
APPLE_DARK      = "#dc2626"
APPLE_HIGHLIGHT = "#fca5a5"
APPLE_STEM      = "#78350f"
APPLE_LEAF      = "#22c55e"

# ---- Effect colours ------------------------------------------------
EFFECT_COLORS = ["#fef08a", "#fde047", "#facc15", "#eab308",
                 "#ca8a04", "#a16207", "#854d0e", "#713f12"]


# ====================================================================
class SnakeGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("\U0001f40d Snake")
        self.root.configure(bg=BG_COLOR)

        canvas_w = GRID_WIDTH * CELL_SIZE
        canvas_h = GRID_HEIGHT * CELL_SIZE

        # --- Title ---
        tk.Label(root, text="S N A K E", font=("Consolas", 20, "bold"),
                 bg=BG_COLOR, fg=SCORE_CLR).pack(pady=(12, 4))

        # --- Canvas with accent border ---
        frame = tk.Frame(root, bg=ACCENT, padx=2, pady=2)
        frame.pack(padx=10)
        self.canvas = tk.Canvas(frame, width=canvas_w, height=canvas_h,
                                bg=GRASS_BASE, highlightthickness=0)
        self.canvas.pack()

        # --- HUD ---
        self.hud = tk.Label(root, text="Score: 0",
                            font=("Consolas", 16, "bold"),
                            bg=BG_COLOR, fg=SCORE_CLR)
        self.hud.pack(pady=8)

        # --- Buttons ---
        btn_frame = tk.Frame(root, bg=BG_COLOR)
        btn_frame.pack(pady=6)

        self.start_button = tk.Button(
            btn_frame, text="\u25B6  START",
            font=("Consolas", 12, "bold"),
            bg=BTN_BG, fg=BTN_FG,
            activebackground=BTN_HOVER, activeforeground="#fff",
            relief="flat", bd=0, padx=20, pady=6,
            cursor="hand2", command=self.start)
        self.start_button.pack(side="left", padx=6)

        # hover feedback
        self.start_button.bind("<Enter>",
            lambda e: self.start_button.config(bg=BTN_HOVER))
        self.start_button.bind("<Leave>",
            lambda e: self.start_button.config(bg=BTN_BG))

        tk.Label(root, text="Arrow keys or WASD to move",
                 font=("Consolas", 9), bg=BG_COLOR,
                 fg="#6b7280").pack(pady=(2, 10))

        # --- Key bindings ---
        for key, d in [("<Left>", "Left"), ("<Right>", "Right"),
                       ("<Up>", "Up"), ("<Down>", "Down"),
                       ("a", "Left"), ("d", "Right"),
                       ("w", "Up"), ("s", "Down")]:
            root.bind(key, lambda e, d=d: self.queue_direction(d))

        # --- Game model ---
        self.model = Game(GRID_WIDTH, GRID_HEIGHT, start_length=4)
        self.direction_queue: Optional[str] = None
        self.after_id = None

        # --- Effect bookkeeping ---
        self.growth_effects: list = []
        self.effect_after_id = None

        # --- Draw persistent grass layer ---
        self._draw_grass()

        # --- Initial draw ---
        self.draw()

    # ----------------------------------------------------------------
    #  GRASS BACKGROUND
    # ----------------------------------------------------------------
    def _draw_grass(self):
        """Render a textured grassy field (drawn once, kept behind game items)."""
        cw = GRID_WIDTH * CELL_SIZE
        ch = GRID_HEIGHT * CELL_SIZE

        # subtle checkerboard
        for gx in range(GRID_WIDTH):
            for gy in range(GRID_HEIGHT):
                x1 = gx * CELL_SIZE
                y1 = gy * CELL_SIZE
                color = "#2a5e2a" if (gx + gy) % 2 == 0 else "#276227"
                self.canvas.create_rectangle(
                    x1, y1, x1 + CELL_SIZE, y1 + CELL_SIZE,
                    fill=color, outline="", tags="grass")

        # random grass blades
        rng = random.Random(42)
        for _ in range(350):
            bx = rng.randint(0, cw - 1)
            by = rng.randint(0, ch - 1)
            bl = rng.randint(3, 8)
            dx = rng.choice([-2, -1, 0, 1, 2])
            self.canvas.create_line(
                bx, by, bx + dx, by - bl,
                fill=rng.choice(GRASS_COLORS), width=1, tags="grass")

        # small dot accents
        for _ in range(35):
            fx = rng.randint(4, cw - 4)
            fy = rng.randint(4, ch - 4)
            fs = rng.choice([1, 2])
            self.canvas.create_oval(
                fx - fs, fy - fs, fx + fs, fy + fs,
                fill=rng.choice(GRASS_FLOWER), outline="", tags="grass")

    # ----------------------------------------------------------------
    #  APPLE DRAWING
    # ----------------------------------------------------------------
    def _draw_apple(self, gx: int, gy: int):
        cx = gx * CELL_SIZE + CELL_SIZE // 2
        cy = gy * CELL_SIZE + CELL_SIZE // 2
        r = CELL_SIZE // 2 - 2

        # shadow
        self.canvas.create_oval(
            cx - r + 2, cy - r + 3, cx + r + 2, cy + r + 3,
            fill="#1a1a1a", outline="", stipple="gray25", tags="food")
        # body
        self.canvas.create_oval(
            cx - r, cy - r + 1, cx + r, cy + r + 1,
            fill=APPLE_BODY, outline=APPLE_DARK, width=1, tags="food")
        # highlight
        hr = r // 3
        self.canvas.create_oval(
            cx - r + 3, cy - r + 3,
            cx - r + 3 + hr * 2, cy - r + 3 + hr * 2,
            fill=APPLE_HIGHLIGHT, outline="", tags="food")
        # stem
        self.canvas.create_line(
            cx, cy - r + 1, cx + 1, cy - r - 4,
            fill=APPLE_STEM, width=2, tags="food")
        # leaf
        self.canvas.create_polygon(
            cx + 1, cy - r - 2,
            cx + 7, cy - r - 7,
            cx + 4, cy - r - 1,
            fill=APPLE_LEAF, outline="", smooth=True, tags="food")

    # ----------------------------------------------------------------
    #  SNAKE DRAWING
    # ----------------------------------------------------------------
    @staticmethod
    def _lerp_color(hex1: str, hex2: str, t: float) -> str:
        r1, g1, b1 = int(hex1[1:3], 16), int(hex1[3:5], 16), int(hex1[5:7], 16)
        r2, g2, b2 = int(hex2[1:3], 16), int(hex2[3:5], 16), int(hex2[5:7], 16)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _draw_snake_head(self, gx: int, gy: int, direction: str):
        x1 = gx * CELL_SIZE + 1
        y1 = gy * CELL_SIZE + 1
        x2 = x1 + CELL_SIZE - 2
        y2 = y1 + CELL_SIZE - 2
        cx = gx * CELL_SIZE + CELL_SIZE // 2
        cy = gy * CELL_SIZE + CELL_SIZE // 2

        # head oval
        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=SNAKE_HEAD, outline=SNAKE_OUTLINE, width=2, tags="snake")

        # eye positions by direction
        eye_r, pr = 3, 1.5
        offsets = {
            "Right": ((5, -4), (5,  4), ( 1, 0)),
            "Left":  ((-5, -4), (-5,  4), (-1, 0)),
            "Up":    ((-4, -5), ( 4, -5), ( 0, -1)),
            "Down":  ((-4,  5), ( 4,  5), ( 0,  1)),
        }
        (e1dx, e1dy), (e2dx, e2dy), (pdx, pdy) = offsets.get(direction,
                                                               offsets["Right"])
        for edx, edy in [(e1dx, e1dy), (e2dx, e2dy)]:
            ex, ey = cx + edx, cy + edy
            self.canvas.create_oval(
                ex - eye_r, ey - eye_r, ex + eye_r, ey + eye_r,
                fill=SNAKE_EYE_W, outline="", tags="snake")
            self.canvas.create_oval(
                ex + pdx - pr, ey + pdy - pr,
                ex + pdx + pr, ey + pdy + pr,
                fill=SNAKE_EYE_P, outline="", tags="snake")

        # tongue
        hs = CELL_SIZE // 2
        tongue_map = {
            "Right": (cx + hs, cy, cx + hs + 7, cy - 2, cx + hs + 7, cy + 2),
            "Left":  (cx - hs, cy, cx - hs - 7, cy - 2, cx - hs - 7, cy + 2),
            "Up":    (cx, cy - hs, cx - 2, cy - hs - 7, cx + 2, cy - hs - 7),
            "Down":  (cx, cy + hs, cx - 2, cy + hs + 7, cx + 2, cy + hs + 7),
        }
        pts = tongue_map.get(direction, tongue_map["Right"])
        # forked tongue: two thin lines
        self.canvas.create_line(pts[0], pts[1], pts[2], pts[3],
                                fill=SNAKE_TONGUE, width=1.5, tags="snake")
        self.canvas.create_line(pts[0], pts[1], pts[4], pts[5],
                                fill=SNAKE_TONGUE, width=1.5, tags="snake")

    def _draw_snake_body(self, i: int, gx: int, gy: int, total: int):
        x1 = gx * CELL_SIZE + 1
        y1 = gy * CELL_SIZE + 1
        x2 = x1 + CELL_SIZE - 2
        y2 = y1 + CELL_SIZE - 2
        cx = gx * CELL_SIZE + CELL_SIZE // 2
        cy = gy * CELL_SIZE + CELL_SIZE // 2

        t = i / max(total - 1, 1)
        body_clr = self._lerp_color(SNAKE_BODY_START, SNAKE_BODY_END, t)
        scale_clr = self._lerp_color(SNAKE_BODY_START, SNAKE_BODY_END,
                                     max(t - 0.15, 0))

        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=body_clr, outline=SNAKE_OUTLINE, width=2, tags="snake")

        # diamond scale pattern
        ds = 3
        self.canvas.create_polygon(
            cx, cy - ds, cx + ds, cy, cx, cy + ds, cx - ds, cy,
            fill=scale_clr, outline="", tags="snake")

    # ----------------------------------------------------------------
    #  GROWTH EFFECT
    # ----------------------------------------------------------------
    def _trigger_growth_effect(self, gx: int, gy: int):
        cx = gx * CELL_SIZE + CELL_SIZE // 2
        cy = gy * CELL_SIZE + CELL_SIZE // 2
        self.growth_effects.append({"cx": cx, "cy": cy, "frame": 0, "ids": []})
        if self.effect_after_id is None:
            self._animate_effects()

    def _animate_effects(self):
        still_active = []
        for eff in self.growth_effects:
            for eid in eff["ids"]:
                self.canvas.delete(eid)
            eff["ids"].clear()

            f = eff["frame"]
            if f >= 8:
                continue
            r = CELL_SIZE // 2 + f * 4
            color = EFFECT_COLORS[min(f, len(EFFECT_COLORS) - 1)]
            w = max(3 - f * 0.35, 0.5)

            ring = self.canvas.create_oval(
                eff["cx"] - r, eff["cy"] - r,
                eff["cx"] + r, eff["cy"] + r,
                outline=color, width=w, tags="effect")
            eff["ids"].append(ring)

            if f < 5:
                for a_deg in range(0, 360, 45):
                    a = math.radians(a_deg + f * 15)
                    px = eff["cx"] + int(r * 0.8 * math.cos(a))
                    py = eff["cy"] + int(r * 0.8 * math.sin(a))
                    sp = self.canvas.create_oval(
                        px - 2, py - 2, px + 2, py + 2,
                        fill="#fef08a", outline="", tags="effect")
                    eff["ids"].append(sp)

            eff["frame"] += 1
            still_active.append(eff)

        self.growth_effects = still_active
        if self.growth_effects:
            self.effect_after_id = self.root.after(40, self._animate_effects)
        else:
            self.effect_after_id = None

    # ----------------------------------------------------------------
    #  GAME CONTROL
    # ----------------------------------------------------------------
    def start(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        if self.effect_after_id:
            self.root.after_cancel(self.effect_after_id)
            self.effect_after_id = None

        self.model.reset()
        self.hud.config(text=f"Score: {self.model.score}")
        self.canvas.delete("snake")
        self.canvas.delete("food")
        self.canvas.delete("effect")
        self.canvas.delete("overlay")
        self.growth_effects = []
        self.direction_queue = None
        self.start_button.config(text="\u27F3  RESTART")
        self._game_loop()

    def queue_direction(self, d: str):
        self.direction_queue = d

    def _game_loop(self):
        if not self.model.is_running():
            self.game_over()
            return

        result = self.model.step(direction=self.direction_queue)
        self.direction_queue = None

        if result.get("ate"):
            head = self.model.get_snake_positions()[0]
            self._trigger_growth_effect(*head)

        self.draw()
        self.hud.config(text=f"Score: {self.model.score}")

        if result["game_over"]:
            self.game_over()
            return

        self.after_id = self.root.after(GAME_SPEED, self._game_loop)

    # ----------------------------------------------------------------
    #  DRAW (called every tick)
    # ----------------------------------------------------------------
    def draw(self):
        self.canvas.delete("snake")
        self.canvas.delete("food")

        # apple
        food = self.model.get_food_position()
        if food is not None:
            self._draw_apple(*food)

        # snake
        snake = self.model.get_snake_positions()
        direction = self.model.snake.direction if self.model.snake else "Right"
        for i, (gx, gy) in enumerate(snake):
            if i == 0:
                self._draw_snake_head(gx, gy, direction)
            else:
                self._draw_snake_body(i, gx, gy, len(snake))

    # ----------------------------------------------------------------
    #  GAME OVER OVERLAY
    # ----------------------------------------------------------------
    def game_over(self):
        w = GRID_WIDTH * CELL_SIZE
        h = GRID_HEIGHT * CELL_SIZE

        # dim overlay
        self.canvas.create_rectangle(
            0, 0, w, h, fill="#000000", stipple="gray50", tags="overlay")

        # panel
        bw, bh = 280, 110
        bx = w // 2 - bw // 2
        by = h // 2 - bh // 2
        self.canvas.create_rectangle(
            bx, by, bx + bw, by + bh,
            fill=PANEL_BG, outline=ACCENT, width=2, tags="overlay")

        self.canvas.create_text(
            w // 2, h // 2 - 25, text="GAME OVER",
            fill="#ef4444", font=("Consolas", 22, "bold"), tags="overlay")
        self.canvas.create_text(
            w // 2, h // 2 + 8, text=f"Score: {self.model.score}",
            fill=SCORE_CLR, font=("Consolas", 14), tags="overlay")
        self.canvas.create_text(
            w // 2, h // 2 + 32, text="Press RESTART to play again",
            fill="#6b7280", font=("Consolas", 9), tags="overlay")


# ====================================================================
def main():
    root = tk.Tk()
    SnakeGUI(root)
    root.resizable(False, False)
    root.mainloop()


if __name__ == "__main__":
    main()
