"""
ANIRUSH - a 10-level runner game where you must CODE your way to the next level.

Concept:
  Pick one of 6 characters and sprint through a computer. Dodge the BUGS (red),
  collect BITS (yellow), grab SHIELDS (cyan).
  Each level has a PAR SCORE. Reach it and the COMPILE GATE appears:
  solve a Python problem to unlock the next level.
  Levels 6-10 are HARD: faster, fewer lives, more bugs, fast bugs.

Controls:
  LEFT / RIGHT (or A / D)  - switch lane
  ENTER                    - select / submit answer
  ESC                      - back to level menu
  C                        - change character (on the level menu)
  The window can be resized or maximized.

Install:  pip install pygame-ce    (or pygame)
Run:      python anirush.py
"""

import json
import math
import random
import sys

import pygame

# ----------------------------------------------------------------------------
# SETTINGS
# ----------------------------------------------------------------------------
WIDTH, HEIGHT = 600, 700          # internal game size (scaled to the window)
START_WINDOW = (540, 630)         # first window size (same shape as the game)
FPS = 60
LANES = [150, 300, 450]           # x-position of the 3 lanes
PLAYER_Y = HEIGHT - 110
MAX_ATTEMPTS = 3                  # tries allowed at each Compile Gate
HARD_FROM = 5                     # index of the first hard level (level 6)
SAVE_FILE = "anirush_save.json"

# ----------------------------------------------------------------------------
# 10 LEVELS
#   speed   : how fast objects fall
#   spawn   : frames between spawns (smaller = more objects)
#   par     : score needed to reach the Compile Gate
#   time    : seconds in the level
#   lives   : starting lives
#   multi   : weights for 1 / 2 / 3 objects per spawn
#   weights : weights for bit / bug / shield
#   fast    : chance that a bug is a FAST bug (orange)
#   ramp    : how quickly the speed grows during the level
# ----------------------------------------------------------------------------
LEVELS = [
    {"name": "Boot Up",        "speed": 4.0, "spawn": 50, "par": 60,  "time": 30, "lives": 3,
     "multi": [100, 0, 0], "weights": [50, 40, 10], "fast": 0.0,  "ramp": 0.0015},
    {"name": "Memory Lane",    "speed": 4.5, "spawn": 46, "par": 80,  "time": 30, "lives": 3,
     "multi": [100, 0, 0], "weights": [50, 40, 10], "fast": 0.0,  "ramp": 0.0015},
    {"name": "Cache Rush",     "speed": 5.0, "spawn": 42, "par": 100, "time": 30, "lives": 3,
     "multi": [60, 40, 0], "weights": [45, 45, 10], "fast": 0.0,  "ramp": 0.0015},
    {"name": "Loop Tunnel",    "speed": 5.5, "spawn": 39, "par": 120, "time": 30, "lives": 3,
     "multi": [60, 40, 0], "weights": [45, 45, 10], "fast": 0.0,  "ramp": 0.0015},
    {"name": "Syntax Storm",   "speed": 6.0, "spawn": 36, "par": 140, "time": 30, "lives": 3,
     "multi": [55, 45, 0], "weights": [45, 45, 10], "fast": 0.0,  "ramp": 0.0015},
    # ---------------- HARD LEVELS ----------------
    {"name": "Stack Overflow", "speed": 7.0, "spawn": 27, "par": 300, "time": 35, "lives": 2,
     "multi": [20, 50, 30], "weights": [40, 55, 5], "fast": 0.15, "ramp": 0.002},
    {"name": "Null Pointer",   "speed": 7.5, "spawn": 25, "par": 330, "time": 35, "lives": 2,
     "multi": [20, 50, 30], "weights": [40, 55, 5], "fast": 0.20, "ramp": 0.002},
    {"name": "Kernel Panic",   "speed": 8.0, "spawn": 23, "par": 360, "time": 35, "lives": 2,
     "multi": [15, 50, 35], "weights": [38, 58, 4], "fast": 0.25, "ramp": 0.002},
    {"name": "Firewall",       "speed": 8.5, "spawn": 21, "par": 390, "time": 35, "lives": 2,
     "multi": [10, 50, 40], "weights": [38, 59, 3], "fast": 0.30, "ramp": 0.002},
    {"name": "Root Access",    "speed": 9.0, "spawn": 19, "par": 430, "time": 35, "lives": 2,
     "multi": [10, 45, 45], "weights": [38, 60, 2], "fast": 0.35, "ramp": 0.002},
]

# ----------------------------------------------------------------------------
# PYTHON PROBLEMS  <-- ADD YOUR OWN PROBLEMS TO THESE LISTS
# Levels 1-5 pick from EASY_PROBLEMS, levels 6-10 from HARD_PROBLEMS.
# A problem is never repeated until every problem in its list has been used
# (the used ones are remembered in the save file).
#   "question": list of lines shown on screen
#   "answers" : every answer you will accept (case and spaces are ignored)
#   "hint"    : shown after a wrong answer
# ----------------------------------------------------------------------------
EASY_PROBLEMS = [
    {"question": ["What is the output?", "print(2 ** 3)"],
     "answers": ["8"], "hint": "** means power."},
    {"question": ["What is the output?", "print(len('Python'))"],
     "answers": ["6"], "hint": "Count the letters."},
    {"question": ["What is the output?", "print(type(3.5))"],
     "answers": ["<class 'float'>", "float"], "hint": "3.5 is a decimal number."},
    {"question": ["What is the output?", "print('Hi' * 2)"],
     "answers": ["HiHi"], "hint": "String repetition."},
    {"question": ["What is the output?", "nums = [1, 2, 3]", "print(sum(nums))"],
     "answers": ["6"], "hint": "Add all the items."},
    {"question": ["What is the output?", "print(10 // 3)"],
     "answers": ["3"], "hint": "// is floor division."},
    {"question": ["What is the output?", "print(10 % 3)"],
     "answers": ["1"], "hint": "% gives the remainder."},
    {"question": ["What is the output?", "print('python'.upper())"],
     "answers": ["PYTHON"], "hint": "upper() makes capitals."},
    {"question": ["What is the output?", "print(max([4, 9, 2]))"],
     "answers": ["9"], "hint": "Largest item."},
    {"question": ["What is the output?", "x = 5", "x += 3", "print(x)"],
     "answers": ["8"], "hint": "+= adds to x."},
    {"question": ["What is the output?", "print('abc'[0])"],
     "answers": ["a"], "hint": "Index starts at 0."},
    {"question": ["What is the output?", "print(7 / 2)"],
     "answers": ["3.5"], "hint": "/ is normal division."},
    {"question": ["What is the output?", "print(bool(0))"],
     "answers": ["False"], "hint": "0 is falsy."},
    {"question": ["What is the output?", "print(int('12') + 3)"],
     "answers": ["15"], "hint": "int() converts text to a number."},
    {"question": ["What is the output?", "d = {'a': 1, 'b': 2}", "print(d['b'])"],
     "answers": ["2"], "hint": "Look up the key 'b'."},
]

HARD_PROBLEMS = [
    {"question": ["What is printed?", "try:", "    int('abc')",
                  "except ValueError:", "    print('Oops')"],
     "answers": ["Oops"], "hint": "int('abc') raises ValueError."},
    {"question": ["Which exception is raised by:", "print(1 / 0)"],
     "answers": ["ZeroDivisionError"], "hint": "Dividing by zero."},
    {"question": ["Which exception is raised by:", "print([1, 2, 3][5])"],
     "answers": ["IndexError"], "hint": "Index out of range."},
    {"question": ["Which exception is raised by:", "print({'a': 1}['b'])"],
     "answers": ["KeyError"], "hint": "Missing dictionary key."},
    {"question": ["Which exception is raised by:", "int('x')"],
     "answers": ["ValueError"], "hint": "Right type, wrong value."},
    {"question": ["How many lines are printed?", "try:", "    print(1 / 0)",
                  "except ZeroDivisionError:", "    print('A')",
                  "finally:", "    print('B')"],
     "answers": ["2"], "hint": "finally always runs."},
    {"question": ["What is the output?", "print('hello'[1:3])"],
     "answers": ["el"], "hint": "Start 1, stop before 3."},
    {"question": ["What is the output?", "print([1, 2, 3][-1])"],
     "answers": ["3"], "hint": "-1 is the last item."},
    {"question": ["What is the output?", "total = 0", "for i in range(4):",
                  "    total += i", "print(total)"],
     "answers": ["6"], "hint": "0 + 1 + 2 + 3."},
    {"question": ["What is the output?", "print('a,b,c'.split(','))"],
     "answers": ["['a', 'b', 'c']"], "hint": "split() returns a list."},
    {"question": ["What is the output?", "x = [1, 2, 3]", "x.append(4)", "print(len(x))"],
     "answers": ["4"], "hint": "append adds one item."},
    {"question": ["What is the output?", "def f(a, b=2):", "    return a * b", "print(f(3))"],
     "answers": ["6"], "hint": "b has a default of 2."},
    {"question": ["What is the output?", "print(3 > 2 and 2 > 5)"],
     "answers": ["False"], "hint": "and needs both True."},
    {"question": ["What is the output?", "s = {1, 2, 2, 3}", "print(len(s))"],
     "answers": ["3"], "hint": "Sets remove duplicates."},
    {"question": ["Which keyword runs code only if", "NO exception happened in try?"],
     "answers": ["else"], "hint": "try / except / ____ / finally."},
]

# ----------------------------------------------------------------------------
# COLORS
# ----------------------------------------------------------------------------
BG = (10, 12, 30)
WHITE = (240, 240, 240)
GREY = (90, 90, 110)
YELLOW = (255, 210, 40)
RED = (230, 60, 60)
ORANGE = (255, 130, 30)
CYAN = (60, 220, 230)
GREEN = (70, 220, 120)
BLUE = (80, 130, 255)
SKIN = (255, 205, 160)
PANTS = (50, 50, 110)

# ----------------------------------------------------------------------------
# CHARACTERS  (all drawn with shapes; pick one on the first screen)
#   style decides the head gear / face; add your own by copying a line
# ----------------------------------------------------------------------------
CHARACTERS = [
    {"name": "Ani",   "style": "hero",     "skin": (255, 205, 160), "body": (40, 90, 220),
     "legs": (30, 60, 170),   "accent": (220, 40, 50),   "hair": (35, 25, 25)},
    {"name": "DY",  "style": "ponytail", "skin": (255, 205, 160), "body": (240, 120, 190),
     "legs": (240, 120, 190), "accent": (255, 90, 150),  "hair": (110, 60, 30)},
    {"name": "KK",  "style": "robot",    "skin": (170, 180, 200), "body": (90, 110, 160),
     "legs": (90, 110, 160),  "accent": (255, 210, 40),  "hair": (60, 60, 60)},
    {"name": "JS",   "style": "duck",     "skin": (255, 225, 80),  "body": (255, 225, 80),
     "legs": (255, 150, 40),  "accent": (255, 150, 40),  "hair": (255, 225, 80)},
    {"name": "VS",   "style": "headband", "skin": (255, 205, 160), "body": (35, 35, 55),
     "legs": (35, 35, 55),    "accent": (220, 50, 50),   "hair": (25, 25, 30)},
    {"name": "PA", "style": "bunny",    "skin": (250, 245, 245), "body": (150, 200, 255),
     "legs": (150, 200, 255), "accent": (255, 170, 190), "hair": (250, 245, 245)},
]


# ----------------------------------------------------------------------------
# SAVE / LOAD  (try/except handles missing or corrupted files)
# ----------------------------------------------------------------------------
def load_save():
    """Return (unlocked level, used problem ids, chosen character)."""
    try:
        with open(SAVE_FILE, "r") as file:
            data = json.load(file)
        unlocked = max(1, min(int(data["unlocked"]), len(LEVELS)))
        used = [str(item) for item in data.get("used", [])]
        character = max(0, min(int(data.get("character", 0)), len(CHARACTERS) - 1))
        return unlocked, used, character
    except (FileNotFoundError, ValueError, KeyError, TypeError, AttributeError):
        return 1, [], 0


def write_save(unlocked, used, character):
    try:
        with open(SAVE_FILE, "w") as file:
            json.dump({"unlocked": unlocked, "used": used, "character": character}, file)
    except OSError:
        print("Could not save progress.")


def normalize(text):
    return text.strip().lower().replace('"', "").replace("'", "").replace(" ", "")


def check_answer(user_text, accepted):
    return any(normalize(user_text) == normalize(a) for a in accepted)


# ----------------------------------------------------------------------------
# GAME
# ----------------------------------------------------------------------------
class Game:
    def __init__(self):
        pygame.init()
        # RESIZABLE lets you maximize; the game is drawn on a fixed canvas
        # and scaled to fit the window.
        pygame.display.set_mode(START_WINDOW, pygame.RESIZABLE)
        pygame.display.set_caption("AniRush")
        self.screen = pygame.Surface((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 22)
        self.small = pygame.font.SysFont("consolas", 16)
        self.big = pygame.font.SysFont("consolas", 40, bold=True)

        self.unlocked, self.used, self.character = load_save()
        self.state = "pick"          # pick | menu | play | gate | result
        self.selected = 0
        self.level = 0
        self.result_text = ""
        self.result_color = WHITE

    # ---------- helpers ----------
    def text(self, msg, font, color, x, y, center=True):
        surface = font.render(msg, True, color)
        rect = surface.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.screen.blit(surface, rect)

    def present(self):
        """Scale the game canvas to the current window size (keeps the shape)."""
        window = pygame.display.get_surface()
        win_w, win_h = window.get_size()
        scale = min(win_w / WIDTH, win_h / HEIGHT)
        size = (max(1, int(WIDTH * scale)), max(1, int(HEIGHT * scale)))
        scaled = pygame.transform.smoothscale(self.screen, size)
        window.fill((0, 0, 0))
        window.blit(scaled, ((win_w - size[0]) // 2, (win_h - size[1]) // 2))
        pygame.display.flip()

    def draw_character(self, x, y, scale, char):
        """Draw a friendly animated running character (arms and legs swing)."""
        t = pygame.time.get_ticks() / 1000
        s = scale
        swing = math.sin(t * 14) * 10 * s
        y = y - abs(math.sin(t * 14)) * 3 * s       # little bounce while running
        screen = self.screen
        style = char["style"]
        accent = char["accent"]
        hair = char["hair"]
        dark = (40, 30, 30)
        hx, hy = x, y - 28 * s                      # head centre
        hr = 12 * s                                 # head radius

        def box(a, b, w, h):
            return pygame.Rect(int(a), int(b), max(1, int(w)), max(1, int(h)))

        thick = max(1, int(6 * s))
        thin = max(1, int(4 * s))
        shoe = max(1, int(4 * s))

        if style == "hero":                         # flowing cape behind the body
            flutter = swing * 0.8
            pygame.draw.polygon(screen, accent, [
                (x - 10 * s, y - 15 * s), (x + 10 * s, y - 15 * s),
                (x + 15 * s + flutter, y + 22 * s), (x - 15 * s + flutter, y + 24 * s)])

        # legs and shoes
        pygame.draw.line(screen, char["legs"], (x - 4 * s, y + 6 * s),
                         (x - 9 * s, y + 26 * s + swing), thick)
        pygame.draw.line(screen, char["legs"], (x + 4 * s, y + 6 * s),
                         (x + 9 * s, y + 26 * s - swing), thick)
        pygame.draw.circle(screen, (60, 40, 30), (int(x - 9 * s), int(y + 27 * s + swing)), shoe)
        pygame.draw.circle(screen, (60, 40, 30), (int(x + 9 * s), int(y + 27 * s - swing)), shoe)
        # arms (the hero has broader shoulders and stronger arms)
        sh = 13 if style == "hero" else 8
        arm_w = max(1, int((6 if style == "hero" else 4) * s))
        pygame.draw.line(screen, char["skin"], (x - sh * s, y - 12 * s),
                         (x - (sh + 7) * s, y + 2 * s - swing), arm_w)
        pygame.draw.line(screen, char["skin"], (x + sh * s, y - 12 * s),
                         (x + (sh + 7) * s, y + 2 * s + swing), arm_w)
        # body
        if style == "hero":                         # broad chest, narrow waist
            pygame.draw.polygon(screen, char["body"], [
                (x - 14 * s, y - 16 * s), (x + 14 * s, y - 16 * s),
                (x + 8 * s, y + 8 * s), (x - 8 * s, y + 8 * s)])
            pygame.draw.rect(screen, YELLOW, box(x - 8 * s, y + 5 * s, 16 * s, 3 * s))      # belt
            pygame.draw.polygon(screen, YELLOW, [                                         # emblem
                (x, y - 13 * s), (x + 5 * s, y - 8 * s), (x, y - 3 * s), (x - 5 * s, y - 8 * s)])
        else:
            pygame.draw.rect(screen, char["body"], box(x - 10 * s, y - 16 * s, 20 * s, 24 * s),
                             border_radius=max(1, int(7 * s)))
        if style == "robot":                        # chest light
            pygame.draw.circle(screen, accent, (int(x), int(y - 4 * s)), max(1, int(3 * s)))

        # bunny ears go behind the head
        if style == "bunny":
            for dx in (-6, 6):
                pygame.draw.ellipse(screen, char["skin"], box(hx + dx * s - 4 * s, hy - 32 * s, 8 * s, 22 * s))
                pygame.draw.ellipse(screen, accent, box(hx + dx * s - 2 * s, hy - 28 * s, 4 * s, 14 * s))

        # head
        if style == "robot":
            pygame.draw.rect(screen, char["skin"], box(hx - hr, hy - hr, 2 * hr, 2 * hr),
                             border_radius=max(1, int(4 * s)))
        else:
            pygame.draw.circle(screen, char["skin"], (int(hx), int(hy)), max(1, int(hr)))

        # hair / hats
        if style == "hero":                         # spiky hair + hero mask
            pygame.draw.ellipse(screen, hair, box(hx - hr, hy - hr - s, 2 * hr, 12 * s))
            for pts in ([(-8, -10), (-5, -19), (-1, -11)],
                        [(-3, -11), (1, -21), (5, -11)],
                        [(3, -11), (9, -18), (10, -9)]):
                pygame.draw.polygon(screen, hair, [(hx + px * s, hy + py * s) for px, py in pts])
            pygame.draw.rect(screen, accent, box(hx - hr + s, hy - s, 2 * hr - 2 * s, 6 * s),
                             border_radius=max(1, int(2 * s)))
        elif style == "ponytail":
            pygame.draw.ellipse(screen, hair, box(hx - hr, hy - hr - s, 2 * hr, 13 * s))
            pygame.draw.circle(screen, hair, (int(hx + hr + 3 * s), int(hy - 2 * s)), max(1, int(5 * s)))
            pygame.draw.circle(screen, accent, (int(hx + hr - s), int(hy - 8 * s)), max(1, int(3 * s)))
        elif style == "headband":
            pygame.draw.ellipse(screen, hair, box(hx - hr, hy - hr - s, 2 * hr, 12 * s))
            pygame.draw.rect(screen, accent, box(hx - hr, hy - 4 * s, 2 * hr, 4 * s))
            wave = swing * 0.5
            pygame.draw.line(screen, accent, (hx + hr, hy - 2 * s), (hx + hr + 9 * s, hy - 4 * s + wave), thin)
            pygame.draw.line(screen, accent, (hx + hr, hy - 2 * s), (hx + hr + 8 * s, hy + 2 * s + wave), thin)
        elif style == "duck":
            pygame.draw.circle(screen, char["skin"], (int(hx), int(hy - hr - s)), max(1, int(3 * s)))

        # face
        if style == "robot":
            for dx in (-7, 2):
                pygame.draw.rect(screen, accent, box(hx + dx * s, hy - 2 * s, 5 * s, 5 * s))
            pygame.draw.line(screen, dark, (hx - 5 * s, hy + 7 * s), (hx + 5 * s, hy + 7 * s), thin)
            pygame.draw.line(screen, GREY, (hx, hy - hr), (hx, hy - hr - 7 * s), max(1, int(2 * s)))
            pygame.draw.circle(screen, RED, (int(hx), int(hy - hr - 8 * s)), max(1, int(3 * s)))
        else:
            eye_y = int(hy + 2 * s)
            for dx in (-4, 4):
                if style == "hero":
                    pygame.draw.circle(screen, WHITE, (int(hx + dx * s), eye_y), max(1, int(3 * s)))
                pygame.draw.circle(screen, dark, (int(hx + dx * s), eye_y), max(1, int(2 * s)))
                pygame.draw.circle(screen, WHITE, (int(hx + dx * s + 0.7 * s), int(eye_y - 0.7 * s)),
                                   max(1, int(0.8 * s)))
            for dx in (-8, 8):                      # rosy cheeks
                pygame.draw.circle(screen, (255, 150, 150), (int(hx + dx * s), int(hy + 6 * s)),
                                   max(1, int(2 * s)))
            if style == "duck":                     # beak
                pygame.draw.ellipse(screen, accent, box(hx - 6 * s, hy + 4 * s, 12 * s, 6 * s))
            else:                                   # smile
                pygame.draw.arc(screen, dark, box(hx - 5 * s, hy + 2 * s, 10 * s, 8 * s),
                                math.pi + 0.4, 2 * math.pi - 0.4, max(1, int(1.5 * s)))
            if style == "bunny":
                pygame.draw.circle(screen, accent, (int(hx), int(hy + 5 * s)), max(1, int(1.5 * s)))

    # ---------- starting a level ----------
    def start_level(self, index):
        self.level = index
        self.config = LEVELS[index]
        self.score = 0
        self.lives = self.config["lives"]
        self.shield = False
        self.objects = []
        self.frame = 0
        self.lane = 1
        self.player_x = float(LANES[1])
        self.scroll = 0
        self.state = "play"

    def spawn(self):
        cfg = self.config
        count = random.choices([1, 2, 3], cfg["multi"])[0]
        lanes = random.sample(range(3), count)
        kinds = [random.choices(["bit", "bug", "shield"], cfg["weights"])[0]
                 for _ in lanes]
        if count == 3 and all(k == "bug" for k in kinds):
            kinds[0] = "bit"          # always leave one safe lane
        for lane, kind in zip(lanes, kinds):
            fast = kind == "bug" and random.random() < cfg["fast"]
            self.objects.append({"lane": lane, "y": -30.0, "kind": kind,
                                 "mult": 1.5 if fast else 1.0})

    # ---------- play state ----------
    def update_play(self):
        cfg = self.config
        self.frame += 1
        self.scroll = (self.scroll + cfg["speed"]) % 60

        # smooth lane movement
        self.player_x += (LANES[self.lane] - self.player_x) * 0.25

        if self.frame % cfg["spawn"] == 0:
            self.spawn()

        speed = cfg["speed"] + self.frame * cfg["ramp"]    # speeds up over time
        for obj in self.objects[:]:
            obj["y"] += speed * obj["mult"]
            if obj["lane"] == self.lane and abs(obj["y"] - PLAYER_Y) < 35:
                self.objects.remove(obj)
                if obj["kind"] == "bit":
                    self.score += 10
                elif obj["kind"] == "shield":
                    self.shield = True
                elif self.shield:
                    self.shield = False
                else:
                    self.lives -= 1
            elif obj["y"] > HEIGHT + 30:
                self.objects.remove(obj)

        if self.lives <= 0:
            self.finish("SYSTEM CRASHED!  Out of lives.", RED)
        elif self.frame >= cfg["time"] * FPS:
            if self.score >= cfg["par"]:
                self.start_gate()
            else:
                self.finish("Time up! Score %d / par %d" % (self.score, cfg["par"]), RED)

    def draw_play(self):
        cfg = self.config
        self.screen.fill(BG)
        for x in (225, 375):                       # moving lane lines
            for y in range(-60, HEIGHT, 60):
                pygame.draw.rect(self.screen, GREY, (x - 2, y + self.scroll, 4, 30))

        for obj in self.objects:
            x, y = LANES[obj["lane"]], int(obj["y"])
            if obj["kind"] == "bit":
                pygame.draw.circle(self.screen, YELLOW, (x, y), 18)
                self.text("1", self.font, BG, x, y)
            elif obj["kind"] == "shield":
                pygame.draw.circle(self.screen, CYAN, (x, y), 18, 4)
                self.text("S", self.font, CYAN, x, y)
            else:
                color = ORANGE if obj["mult"] > 1 else RED
                pygame.draw.rect(self.screen, color, (x - 20, y - 20, 40, 40), border_radius=8)
                self.text("bug", self.small, WHITE, x, y)

        px = int(self.player_x)
        self.draw_character(px, PLAYER_Y, 1.0, CHARACTERS[self.character])
        if self.shield:
            pygame.draw.circle(self.screen, CYAN, (px, PLAYER_Y), 40, 3)

        seconds_left = max(0, cfg["time"] - self.frame // FPS)
        tag = "  [HARD]" if self.level >= HARD_FROM else ""
        self.text("Level %d: %s%s" % (self.level + 1, cfg["name"], tag),
                  self.font, WHITE, 10, 10, center=False)
        self.text("Score %d / Par %d" % (self.score, cfg["par"]), self.font,
                  YELLOW if self.score < cfg["par"] else GREEN, 10, 38, center=False)
        self.text("Lives: " + "<3 " * self.lives, self.font, RED, 10, 66, center=False)
        self.text("Time %d" % seconds_left, self.font, WHITE, WIDTH - 110, 10, center=False)

    # ---------- compile gate (Python problem) ----------
    def pick_problem(self):
        """Pick a random problem that has not been used yet."""
        prefix, pool = ("H", HARD_PROBLEMS) if self.level >= HARD_FROM else ("E", EASY_PROBLEMS)
        ids = [prefix + str(i) for i in range(len(pool))]
        fresh = [i for i in range(len(pool)) if ids[i] not in self.used]
        if not fresh:                                   # all used: start over
            self.used = [u for u in self.used if not u.startswith(prefix)]
            fresh = list(range(len(pool)))
        choice = random.choice(fresh)
        self.used.append(ids[choice])
        write_save(self.unlocked, self.used, self.character)
        return pool[choice]

    def start_gate(self):
        self.problem = self.pick_problem()
        self.answer = ""
        self.attempts = MAX_ATTEMPTS
        self.gate_message = ""
        self.show_hint = False
        self.state = "gate"

    def submit_answer(self):
        if check_answer(self.answer, self.problem["answers"]):
            if self.level + 1 >= len(LEVELS):
                self.finish("YOU WIN! You mastered every level!", GREEN)
            else:
                self.unlocked = max(self.unlocked, self.level + 2)
                write_save(self.unlocked, self.used, self.character)
                self.finish("COMPILED! Level %d unlocked." % (self.level + 2), GREEN)
        else:
            self.attempts -= 1
            self.show_hint = True
            self.answer = ""
            if self.attempts <= 0:
                self.finish("Compile failed. Replay the level to try again.", RED)
            else:
                self.gate_message = "Wrong! Attempts left: %d" % self.attempts

    def draw_gate(self):
        self.screen.fill(BG)
        self.text("COMPILE GATE", self.big, GREEN, WIDTH // 2, 60)
        self.text("Par score reached! Solve to unlock the next level.",
                  self.small, WHITE, WIDTH // 2, 105)
        y = 170
        for line in self.problem["question"]:
            self.text(line, self.font, YELLOW, 60, y, center=False)
            y += 32
        pygame.draw.rect(self.screen, WHITE, (60, 460, 480, 50), 2, border_radius=6)
        self.text(self.answer + "_", self.font, WHITE, 72, 472, center=False)
        self.text("Type answer and press ENTER", self.small, GREY, WIDTH // 2, 540)
        self.text(self.gate_message, self.font, RED, WIDTH // 2, 580)
        if self.show_hint:
            self.text("Hint: " + self.problem["hint"], self.small, CYAN, WIDTH // 2, 620)

    # ---------- result screen ----------
    def finish(self, message, color):
        self.result_text = message
        self.result_color = color
        self.state = "result"

    def draw_result(self):
        self.screen.fill(BG)
        self.text(self.result_text, self.font, self.result_color, WIDTH // 2, 300)
        self.text("Press ENTER for level menu", self.small, WHITE, WIDTH // 2, 360)

    # ---------- level menu ----------
    def draw_menu(self):
        self.screen.fill(BG)
        self.draw_character(205, 82, 1.0, CHARACTERS[self.character])
        self.text("AniRush", self.big, BLUE, 340, 70)
        self.text("Hit the par score + solve the Python problem to advance",
                  self.small, WHITE, WIDTH // 2, 125)
        self.text("Levels 6-10 are HARD", self.small, RED, WIDTH // 2, 145)
        for i, level in enumerate(LEVELS):
            col, row = i % 2, i // 2
            x, y = 60 + col * 250, 175 + row * 85
            open_level = (i + 1) <= self.unlocked
            color = GREEN if open_level else GREY
            width = 4 if i == self.selected else 1
            pygame.draw.rect(self.screen, color, (x, y, 230, 72), width, border_radius=8)
            self.text("%d. %s" % (i + 1, level["name"]), self.small, color,
                      x + 10, y + 10, center=False)
            if open_level:
                info = "Par %d%s" % (level["par"], "  HARD" if i >= HARD_FROM else "")
            else:
                info = "LOCKED"
            self.text(info, self.small, color, x + 10, y + 40, center=False)
        self.text("Arrows: choose   ENTER: start   C: character", self.small, GREY, WIDTH // 2, 640)

    # ---------- character select ----------
    def draw_pick(self):
        self.screen.fill(BG)
        self.text("Choose your runner", self.big, BLUE, WIDTH // 2, 65)
        self.text("Arrows: choose   ENTER: play", self.small, GREY, WIDTH // 2, 112)
        for i, char in enumerate(CHARACTERS):
            col, row = i % 3, i // 3
            cx, cy = 100 + col * 200, 285 + row * 235
            chosen = i == self.character
            color = YELLOW if chosen else GREY
            pygame.draw.rect(self.screen, color, (cx - 85, cy - 115, 170, 225),
                             4 if chosen else 1, border_radius=12)
            self.draw_character(cx, cy + 5, 1.8, char)
            self.text(char["name"], self.font, color, cx, cy + 88)

    # ---------- events ----------
    def handle_key(self, event):
        key = event.key
        if self.state == "pick":
            if key == pygame.K_LEFT:
                self.character = max(0, self.character - 1)
            elif key == pygame.K_RIGHT:
                self.character = min(len(CHARACTERS) - 1, self.character + 1)
            elif key == pygame.K_UP:
                self.character = max(0, self.character - 3)
            elif key == pygame.K_DOWN:
                self.character = min(len(CHARACTERS) - 1, self.character + 3)
            elif key == pygame.K_RETURN:
                write_save(self.unlocked, self.used, self.character)
                self.state = "menu"
        elif self.state == "menu":
            if key == pygame.K_LEFT:
                self.selected = max(0, self.selected - 1)
            elif key == pygame.K_RIGHT:
                self.selected = min(len(LEVELS) - 1, self.selected + 1)
            elif key == pygame.K_UP:
                self.selected = max(0, self.selected - 2)
            elif key == pygame.K_DOWN:
                self.selected = min(len(LEVELS) - 1, self.selected + 2)
            elif key == pygame.K_RETURN and self.selected + 1 <= self.unlocked:
                self.start_level(self.selected)
            elif key == pygame.K_c:
                self.state = "pick"
        elif self.state == "play":
            if key in (pygame.K_LEFT, pygame.K_a):
                self.lane = max(0, self.lane - 1)
            elif key in (pygame.K_RIGHT, pygame.K_d):
                self.lane = min(2, self.lane + 1)
            elif key == pygame.K_ESCAPE:
                self.state = "menu"
        elif self.state == "gate":
            if key == pygame.K_RETURN and self.answer.strip():
                self.submit_answer()
            elif key == pygame.K_BACKSPACE:
                self.answer = self.answer[:-1]
            elif event.unicode.isprintable() and len(self.answer) < 30:
                self.answer += event.unicode
        elif self.state == "result":
            if key == pygame.K_RETURN:
                self.selected = min(self.unlocked, len(LEVELS)) - 1
                self.state = "menu"

    # ---------- main loop ----------
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    self.handle_key(event)

            if self.state == "play":
                self.update_play()

            if self.state == "pick":
                self.draw_pick()
            elif self.state == "menu":
                self.draw_menu()
            elif self.state == "play":
                self.draw_play()
            elif self.state == "gate":
                self.draw_gate()
            elif self.state == "result":
                self.draw_result()

            self.present()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Game().run()
