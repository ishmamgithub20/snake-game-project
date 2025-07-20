# Childhood nostalgic Snake 🐍 Xenzia game. On Nokia mobile phone.


# 🐍 Snake Xenzia (Nokia-style Snake Game)

A modern recreation of the classic Snake Xenzia game from old Nokia phones, built with [Kivy](https://kivy.org/) using Python.

Enjoy pixel-perfect movement, food pickups, score tracking, sounds, and support for both desktop and Android devices.

---

## 🎮 Gameplay Features

- 🟢 Snake grows as it eats food
- 🔊 Sound effects: eat, game over, and big food
- 🍎 Bonus big food appears every 5 steps
  - Eat it fast to get more points (up to 50)
- ⏸ Short pause with food blink after eating
- 🔄 Direction control via keyboard (desktop)
- 🧠 Smart collision detection and wraparound

---

## ▶️ How to Play

- **Move:** Use Arrow Keys (⬆️⬇️⬅️➡️)
- **Eat food** to grow longer
- **Avoid hitting yourself**
- Try to **eat big food within 3 seconds** to earn bonus

---

[![Watch the video](https://img.youtube.com/vi/EVg6gi0o9Ds/0.jpg)](https://www.youtube.com/watch?v=EVg6gi0o9Ds)

## 💻 Run on Desktop (Windows/Linux)

### 1. Clone the repo:
```bash
git clone https://github.com/azizur19/snake-xenzia.git
cd snake-xenzia
```

### 2. Install the  `kivy` library (If not already installed):
```bash
pip install kivy
```

### 3. Run the `snake.py`:
```bash
python snake.py
```



## Chat GPT Writen notes to convert to executable file(.exe) for windows
Awesome! 🐍 Your **Snake Xenzia** game is complete — now let’s package it as a **Windows `.exe` installer** so others can install and play it easily.

---

## ✅ Step-by-Step Guide: Convert Kivy Game to Windows `.exe`

We’ll use **PyInstaller** for this.

---

### 🔧 1. ✅ Install PyInstaller (if not already)

Open terminal and run:

```bash
pip install pyinstaller
```

---

### 📁 2. ✅ Make Sure Your Project Folder Has:

From your image, you already have:

```
SNAKE_XENZIA/
├── snake.py             # ✅ Your main game file
├── big_food.wav         # ✅ Game sounds
├── eat.wav
├── end_game.wav
├── README.md            # (optional)
```

✅ ✅ Good to go.

---

### ⚙️ 3. ✅ Create a `.spec` file (optional but useful for assets)

But first, just try this basic command:

```bash
pyinstaller --onefile --noconsole snake.py
```

* `--onefile` → builds a single `.exe`
* `--noconsole` → hides the terminal window (since it’s a GUI app)

After a few minutes, you’ll get:

```
dist/snake.exe
```

Run that `.exe`!

---

### 🎵 4. 🟠 If Your `.wav` Files Are Not Playing…

Add them to the build using a `.spec` file or `--add-data`.

Example with `--add-data`:

```bash
pyinstaller --onefile --noconsole snake.py --add-data "big_food.wav;." --add-data "eat.wav;." --add-data "end_game.wav;."
```

🔸 For Windows use **`;`** between source and destination
🔸 For Linux/macOS use **`:`**

---

### 📁 5. ✅ Your `.exe` will be found here:

```
SNAKE_XENZIA/
├── dist/
│   └── snake.exe      ✅ Final game executable
├── build/             🟡 Build cache
├── snake.spec         🟡 (optional, config)
```

---

### 🎁 6. (Optional) Create Installer with Inno Setup

If you want a **nice installer**, use [Inno Setup](https://jrsoftware.org/isinfo.php):

* Simple scripting tool to package your `.exe`
* Adds start menu shortcut, uninstall, etc.

---

## 🧪 Final Tips

✅ Test it on a clean PC (no Python installed)
🛠 If assets aren’t loading, try bundling as a **folder-based build** (`--onedir`)
🎮 You can even add an icon with:

```bash
--icon=myicon.ico
```

---


