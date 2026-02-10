# snake_gui.py
import tkinter as tk
import random
import math
from typing import Optional
from snake_logic import Game
from user_manager import load_users, create_user, update_high_score, get_high_score, has_users

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

        # --- Current user ---
        self.current_user: Optional[str] = None

        # --- Container for swappable screens ---
        self.main_container = tk.Frame(root, bg=BG_COLOR)
        self.main_container.pack(fill="both", expand=True)

        # --- Game model ---
        self.model = Game(GRID_WIDTH, GRID_HEIGHT, start_length=4)
        self.direction_queue: Optional[str] = None
        self.after_id = None

        # --- Effect bookkeeping ---
        self.growth_effects: list = []
        self.effect_after_id = None

        # --- Show user menu first ---
        self._show_user_menu()

    # ----------------------------------------------------------------
    #  USER MENU SCREENS
    # ----------------------------------------------------------------
    def _clear_container(self):
        """Remove all widgets from the main container."""
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def _show_user_menu(self):
        """Show the initial user selection / creation menu."""
        self._clear_container()
        f = self.main_container

        tk.Label(f, text="S N A K E", font=("Consolas", 24, "bold"),
                 bg=BG_COLOR, fg=SCORE_CLR).pack(pady=(40, 10))
        tk.Label(f, text="\U0001f40d", font=("Segoe UI Emoji", 36),
                 bg=BG_COLOR).pack(pady=(0, 20))

        users = load_users()

        if users:
            tk.Label(f, text="Welcome! Choose an option:",
                     font=("Consolas", 13), bg=BG_COLOR,
                     fg=TEXT_COLOR).pack(pady=(10, 16))

            btn_frame = tk.Frame(f, bg=BG_COLOR)
            btn_frame.pack(pady=6)

            btn_existing = tk.Button(
                btn_frame, text="\U0001f464  Select Existing User",
                font=("Consolas", 12, "bold"),
                bg=BTN_BG, fg=BTN_FG,
                activebackground=BTN_HOVER, activeforeground="#fff",
                relief="flat", bd=0, padx=20, pady=8,
                cursor="hand2", command=self._show_select_user)
            btn_existing.pack(pady=6)
            btn_existing.bind("<Enter>",
                lambda e: btn_existing.config(bg=BTN_HOVER))
            btn_existing.bind("<Leave>",
                lambda e: btn_existing.config(bg=BTN_BG))

            btn_new = tk.Button(
                btn_frame, text="\u2795  Create New User",
                font=("Consolas", 12, "bold"),
                bg=BTN_BG, fg=BTN_FG,
                activebackground=BTN_HOVER, activeforeground="#fff",
                relief="flat", bd=0, padx=20, pady=8,
                cursor="hand2", command=self._show_create_user)
            btn_new.pack(pady=6)
            btn_new.bind("<Enter>",
                lambda e: btn_new.config(bg=BTN_HOVER))
            btn_new.bind("<Leave>",
                lambda e: btn_new.config(bg=BTN_BG))
        else:
            tk.Label(f, text="No users found. Create one to start!",
                     font=("Consolas", 13), bg=BG_COLOR,
                     fg=TEXT_COLOR).pack(pady=(10, 16))

            btn_new = tk.Button(
                f, text="\u2795  Create New User",
                font=("Consolas", 12, "bold"),
                bg=BTN_BG, fg=BTN_FG,
                activebackground=BTN_HOVER, activeforeground="#fff",
                relief="flat", bd=0, padx=20, pady=8,
                cursor="hand2", command=self._show_create_user)
            btn_new.pack(pady=10)
            btn_new.bind("<Enter>",
                lambda e: btn_new.config(bg=BTN_HOVER))
            btn_new.bind("<Leave>",
                lambda e: btn_new.config(bg=BTN_BG))

        tk.Label(f, text="", bg=BG_COLOR).pack(pady=30)  # spacer

    def _show_select_user(self):
        """Show a screen listing all existing users and their high scores."""
        self._clear_container()
        f = self.main_container

        tk.Label(f, text="Select a User", font=("Consolas", 20, "bold"),
                 bg=BG_COLOR, fg=SCORE_CLR).pack(pady=(30, 16))

        users = load_users()

        # Scrollable list frame
        list_outer = tk.Frame(f, bg=ACCENT, padx=2, pady=2)
        list_outer.pack(padx=40, pady=(0, 10))

        list_canvas = tk.Canvas(list_outer, bg=PANEL_BG, highlightthickness=0,
                                width=380, height=min(len(users) * 48 + 10, 300))
        scrollbar = tk.Scrollbar(list_outer, orient="vertical",
                                 command=list_canvas.yview)
        scroll_frame = tk.Frame(list_canvas, bg=PANEL_BG)

        scroll_frame.bind("<Configure>",
            lambda e: list_canvas.configure(scrollregion=list_canvas.bbox("all")))
        list_canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        list_canvas.configure(yscrollcommand=scrollbar.set)

        list_canvas.pack(side="left", fill="both", expand=True)
        if len(users) * 48 + 10 > 300:
            scrollbar.pack(side="right", fill="y")

        # Header row
        hdr = tk.Frame(scroll_frame, bg=ACCENT)
        hdr.pack(fill="x", padx=4, pady=(6, 2))
        tk.Label(hdr, text="Username", font=("Consolas", 11, "bold"),
                 bg=ACCENT, fg=TEXT_COLOR, width=20, anchor="w").pack(side="left", padx=8)
        tk.Label(hdr, text="High Score", font=("Consolas", 11, "bold"),
                 bg=ACCENT, fg=SCORE_CLR, width=21, anchor="e").pack(side="right", padx=8)

        # User rows
        sorted_users = sorted(users.items(), key=lambda x: x[1], reverse=True)
        for i, (username, high_score) in enumerate(sorted_users):
            row_bg = "#1c2a4a" if i % 2 == 0 else PANEL_BG
            row = tk.Frame(scroll_frame, bg=row_bg, cursor="hand2")
            row.pack(fill="x", padx=4, pady=1)

            tk.Label(row, text=username, font=("Consolas", 11),
                     bg=row_bg, fg=TEXT_COLOR, width=20,
                     anchor="w").pack(side="left", padx=8, pady=6)
            tk.Label(row, text=str(high_score), font=("Consolas", 11, "bold"),
                     bg=row_bg, fg=SCORE_CLR, width=10,
                     anchor="e").pack(side="right", padx=8, pady=6)

            # Bind click to select user
            for widget in [row] + row.winfo_children():
                widget.bind("<Button-1>",
                    lambda e, u=username: self._select_user(u))
                widget.bind("<Enter>",
                    lambda e, r=row: r.config(bg=BTN_HOVER) or
                        [c.config(bg=BTN_HOVER) for c in r.winfo_children()])
                widget.bind("<Leave>",
                    lambda e, r=row, bg=row_bg: r.config(bg=bg) or
                        [c.config(bg=bg) for c in r.winfo_children()])

        # Back button
        btn_back = tk.Button(
            f, text="\u25C0  Back",
            font=("Consolas", 11, "bold"),
            bg=BTN_BG, fg=BTN_FG,
            activebackground=BTN_HOVER, activeforeground="#fff",
            relief="flat", bd=0, padx=16, pady=6,
            cursor="hand2", command=self._show_user_menu)
        btn_back.pack(pady=14)
        btn_back.bind("<Enter>",
            lambda e: btn_back.config(bg=BTN_HOVER))
        btn_back.bind("<Leave>",
            lambda e: btn_back.config(bg=BTN_BG))

    def _show_create_user(self):
        """Show the create-new-user screen."""
        self._clear_container()
        f = self.main_container

        tk.Label(f, text="Create New User", font=("Consolas", 20, "bold"),
                 bg=BG_COLOR, fg=SCORE_CLR).pack(pady=(40, 20))

        tk.Label(f, text="Enter your username:",
                 font=("Consolas", 12), bg=BG_COLOR,
                 fg=TEXT_COLOR).pack(pady=(0, 8))

        entry_frame = tk.Frame(f, bg=ACCENT, padx=2, pady=2)
        entry_frame.pack()
        self.username_entry = tk.Entry(
            entry_frame, font=("Consolas", 14),
            bg=PANEL_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
            relief="flat", width=22)
        self.username_entry.pack(padx=4, pady=4)
        self.username_entry.focus_set()

        self.create_error_label = tk.Label(
            f, text="", font=("Consolas", 10),
            bg=BG_COLOR, fg="#ef4444")
        self.create_error_label.pack(pady=(4, 0))

        btn_create = tk.Button(
            f, text="\u2714  Create & Play",
            font=("Consolas", 12, "bold"),
            bg=BTN_BG, fg=BTN_FG,
            activebackground=BTN_HOVER, activeforeground="#fff",
            relief="flat", bd=0, padx=20, pady=8,
            cursor="hand2", command=self._do_create_user)
        btn_create.pack(pady=14)
        btn_create.bind("<Enter>",
            lambda e: btn_create.config(bg=BTN_HOVER))
        btn_create.bind("<Leave>",
            lambda e: btn_create.config(bg=BTN_BG))

        # Allow Enter key to submit
        self.username_entry.bind("<Return>", lambda e: self._do_create_user())

        btn_back = tk.Button(
            f, text="\u25C0  Back",
            font=("Consolas", 11, "bold"),
            bg=BTN_BG, fg=BTN_FG,
            activebackground=BTN_HOVER, activeforeground="#fff",
            relief="flat", bd=0, padx=16, pady=6,
            cursor="hand2", command=self._show_user_menu)
        btn_back.pack(pady=4)
        btn_back.bind("<Enter>",
            lambda e: btn_back.config(bg=BTN_HOVER))
        btn_back.bind("<Leave>",
            lambda e: btn_back.config(bg=BTN_BG))

    def _do_create_user(self):
        """Handle the create-user action."""
        username = self.username_entry.get().strip()
        if not username:
            self.create_error_label.config(text="Username cannot be empty.")
            return
        if len(username) > 20:
            self.create_error_label.config(text="Username must be 20 characters or less.")
            return
        if not create_user(username):
            self.create_error_label.config(text=f'User "{username}" already exists.')
            return
        self._select_user(username)

    def _select_user(self, username: str):
        """Set current user and transition to the game screen."""
        self.current_user = username
        self._show_game_screen()

    # ----------------------------------------------------------------
    #  GAME SCREEN SETUP
    # ----------------------------------------------------------------
    def _show_game_screen(self):
        """Build the game UI (canvas, HUD, buttons) and show it."""
        self._clear_container()
        f = self.main_container

        canvas_w = GRID_WIDTH * CELL_SIZE
        canvas_h = GRID_HEIGHT * CELL_SIZE

        high = get_high_score(self.current_user)

        # --- Title ---
        tk.Label(f, text="S N A K E", font=("Consolas", 20, "bold"),
                 bg=BG_COLOR, fg=SCORE_CLR).pack(pady=(12, 4))

        # --- Canvas with accent border ---
        frame = tk.Frame(f, bg=ACCENT, padx=2, pady=2)
        frame.pack(padx=10)
        self.canvas = tk.Canvas(frame, width=canvas_w, height=canvas_h,
                                bg=GRASS_BASE, highlightthickness=0)
        self.canvas.pack()

        # --- HUD ---
        hud_frame = tk.Frame(f, bg=BG_COLOR)
        hud_frame.pack(pady=8)

        self.hud = tk.Label(hud_frame,
                            text=f"\U0001f464 {self.current_user}   |   "
                                 f"Score: 0   |   Best: {high}",
                            font=("Consolas", 14, "bold"),
                            bg=BG_COLOR, fg=SCORE_CLR)
        self.hud.pack()

        # --- Buttons ---
        btn_frame = tk.Frame(f, bg=BG_COLOR)
        btn_frame.pack(pady=6)

        self.start_button = tk.Button(
            btn_frame, text="\u25B6  START",
            font=("Consolas", 12, "bold"),
            bg=BTN_BG, fg=BTN_FG,
            activebackground=BTN_HOVER, activeforeground="#fff",
            relief="flat", bd=0, padx=20, pady=6,
            cursor="hand2", command=self.start)
        self.start_button.pack(side="left", padx=6)

        self.start_button.bind("<Enter>",
            lambda e: self.start_button.config(bg=BTN_HOVER))
        self.start_button.bind("<Leave>",
            lambda e: self.start_button.config(bg=BTN_BG))

        btn_switch = tk.Button(
            btn_frame, text="\U0001f464  Switch User",
            font=("Consolas", 11, "bold"),
            bg=BTN_BG, fg=BTN_FG,
            activebackground=BTN_HOVER, activeforeground="#fff",
            relief="flat", bd=0, padx=16, pady=6,
            cursor="hand2", command=self._back_to_menu)
        btn_switch.pack(side="left", padx=6)
        btn_switch.bind("<Enter>",
            lambda e: btn_switch.config(bg=BTN_HOVER))
        btn_switch.bind("<Leave>",
            lambda e: btn_switch.config(bg=BTN_BG))

        tk.Label(f, text="Arrow keys or WASD to move",
                 font=("Consolas", 9), bg=BG_COLOR,
                 fg="#6b7280").pack(pady=(2, 10))

        # --- Key bindings ---
        for key, d in [("<Left>", "Left"), ("<Right>", "Right"),
                       ("<Up>", "Up"), ("<Down>", "Down"),
                       ("a", "Left"), ("d", "Right"),
                       ("w", "Up"), ("s", "Down")]:
            self.root.bind(key, lambda e, d=d: self.queue_direction(d))

        # --- Draw persistent grass layer ---
        self._draw_grass()

        # --- Initial draw ---
        self.draw()

    def _back_to_menu(self):
        """Stop any active game and go back to the user menu."""
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        if self.effect_after_id:
            self.root.after_cancel(self.effect_after_id)
            self.effect_after_id = None
        self.growth_effects = []
        self.current_user = None
        self._show_user_menu()

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
        high = get_high_score(self.current_user) if self.current_user else 0
        self.hud.config(text=f"\U0001f464 {self.current_user}   |   "
                             f"Score: 0   |   Best: {high}")
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
        high = get_high_score(self.current_user) if self.current_user else 0
        self.hud.config(text=f"\U0001f464 {self.current_user}   |   "
                             f"Score: {self.model.score}   |   Best: {high}")

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
        # Save high score
        new_best = False
        if self.current_user:
            new_best = update_high_score(self.current_user, self.model.score)

        w = GRID_WIDTH * CELL_SIZE
        h = GRID_HEIGHT * CELL_SIZE

        # dim overlay
        self.canvas.create_rectangle(
            0, 0, w, h, fill="#000000", stipple="gray50", tags="overlay")

        # panel
        bw, bh = 300, 140
        bx = w // 2 - bw // 2
        by = h // 2 - bh // 2
        self.canvas.create_rectangle(
            bx, by, bx + bw, by + bh,
            fill=PANEL_BG, outline=ACCENT, width=2, tags="overlay")

        self.canvas.create_text(
            w // 2, h // 2 - 35, text="GAME OVER",
            fill="#ef4444", font=("Consolas", 22, "bold"), tags="overlay")
        self.canvas.create_text(
            w // 2, h // 2 - 5, text=f"Score: {self.model.score}",
            fill=SCORE_CLR, font=("Consolas", 14), tags="overlay")
        if new_best:
            self.canvas.create_text(
                w // 2, h // 2 + 18,
                text="\u2B50 NEW HIGH SCORE! \u2B50",
                fill="#fde047", font=("Consolas", 12, "bold"), tags="overlay")
        else:
            best = get_high_score(self.current_user) if self.current_user else 0
            self.canvas.create_text(
                w // 2, h // 2 + 18, text=f"Best: {best}",
                fill=TEXT_COLOR, font=("Consolas", 11), tags="overlay")
        self.canvas.create_text(
            w // 2, h // 2 + 42, text="Press RESTART to play again",
            fill="#6b7280", font=("Consolas", 9), tags="overlay")

        # Update HUD with latest high score
        high = get_high_score(self.current_user) if self.current_user else 0
        self.hud.config(text=f"\U0001f464 {self.current_user}   |   "
                             f"Score: {self.model.score}   |   Best: {high}")


# ====================================================================
def main():
    root = tk.Tk()
    SnakeGUI(root)
    root.resizable(False, False)
    root.mainloop()


if __name__ == "__main__":
    main()
