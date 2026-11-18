# AniRush 🏃‍♂️💻

**A lane-runner game where you have to *code* your way to the next level.**

Pick a runner and sprint through a computer. Dodge the bugs and collect bits. When you hit the level's par score, the **Compile Gate** opens, and you have to solve a Python problem to unlock the next level.

<!-- Drag your gameplay video into this README in the GitHub editor and paste the link it generates here -->
https://github.com/user-attachments/assets/df050b6f-ef62-4651-a738-46b48498e4bf

---

## ✨ Features

- **6 playable characters** (Ani, DY, KK, JS, VS, PA), all drawn in code with running animations
- **10 levels.** Levels 6–10 are **HARD**: they're faster, give you fewer lives, add more bugs and bring in *fast bugs*
- **Compile Gate**: you hit the par score, then solve a Python question to move on
- **30 built-in Python problems** (15 easy, 15 hard) covering operators, strings, lists, dicts, sets, functions and exceptions
- **No repeats**: you won't see the same problem again until you've solved every problem in that set
- **Hints** after a wrong answer, with 3 attempts per gate
- **Progress is saved** automatically, including unlocked levels, used problems and your chosen character
- **Resizable window** that scales cleanly and can be maximized
- Pure Python + Pygame, in a **single file** with no image or sound assets

---

## 🎮 How to Play

| Item | Looks like | Effect |
|------|-----------|--------|
| **Bit** | 🟡 yellow coin | +10 score |
| **Bug** | 🟥 red block | −1 life |
| **Fast bug** | 🟧 orange block | −1 life, falls 1.5× faster (hard levels) |
| **Shield** | 🔵 cyan ring | blocks the next bug |

1. **Choose your runner** on the first screen.
2. **Pick a level** from the level menu.
3. **Survive the timer** and reach the **par score**.
4. **Pass the Compile Gate** by typing the answer to the Python problem.
5. **Unlock the next level** and keep going until you clear level 10.

Each spawn leaves at least one lane free of bugs, so every wave can be dodged.

### Controls

| Key | Action |
|-----|--------|
| `←` / `→` or `A` / `D` | Switch lane |
| `↑` / `↓` | Move through menus |
| `Enter` | Select / submit answer |
| `Backspace` | Delete a character of your answer |
| `Esc` | Back to the level menu (during a run) |
| `C` | Change character (on the level menu) |

---

## 🗺️ Levels

| # | Name | Par | Time | Lives | Difficulty |
|---|------|-----|------|-------|------------|
| 1 | Boot Up | 60 | 30s | 3 | Easy |
| 2 | Memory Lane | 80 | 30s | 3 | Easy |
| 3 | Cache Rush | 100 | 30s | 3 | Easy |
| 4 | Loop Tunnel | 120 | 30s | 3 | Easy |
| 5 | Syntax Storm | 140 | 30s | 3 | Easy |
| 6 | Stack Overflow | 300 | 35s | 2 | **Hard** |
| 7 | Null Pointer | 330 | 35s | 2 | **Hard** |
| 8 | Kernel Panic | 360 | 35s | 2 | **Hard** |
| 9 | Firewall | 390 | 35s | 2 | **Hard** |
| 10 | Root Access | 430 | 35s | 2 | **Hard** |

The speed also ramps up *during* each level. Levels 1–5 draw from the easy problem set and levels 6–10 from the hard set.

---

## 🚀 Getting Started

**Requirements:** Python 3.8+ and Pygame

```bash
# 1. Clone the repo
git clone https://github.com/anirudhr-05/AniRush_Game
cd AniRush_Game

# 2. Install Pygame (pygame-ce recommended)
pip install pygame-ce        # or: pip install pygame

# 3. Run
python AniRush.py
```

Progress is stored in `anirush_save.json` next to the game. Delete that file to start fresh.

---

## 🛠️ Customize It

Everything is configured at the top of `AniRush.py`.

**Add your own Python problems.** Append to `EASY_PROBLEMS` or `HARD_PROBLEMS`:

```python
{"question": ["What is the output?", "print(3 * 'ab')"],
 "answers": ["ababab"],
 "hint": "String repetition."},
```

Answers ignore case, spaces and quotes, and you can list several accepted answers.

**Tune a level.** Each entry in `LEVELS` controls `speed`, `spawn` rate, `par`, `time`, `lives`, how many objects spawn at once (`multi`), the bit/bug/shield mix (`weights`), the fast-bug chance (`fast`) and the in-level speed-up (`ramp`).

**Add a character.** Copy a line in `CHARACTERS` and change the colors or `style` (`hero`, `ponytail`, `robot`, `duck`, `headband`, `bunny`).

---

## 🧱 Built With

- [Python](https://www.python.org/)
- [Pygame](https://www.pygame.org/) / [pygame-ce](https://pyga.me/)

---

## 🤝 Contributing

New problems, levels and characters are welcome. Fork the repo, add your changes and open a pull request.

---

⭐ If you enjoyed AniRush, give the repo a star!
