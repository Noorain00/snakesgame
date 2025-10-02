🐍  Snake Game
A modern, feature-rich Snake game built with Python and Pygame, featuring smooth animations, particle effects, and a sleek dark theme UI.

---

✨ Features

🎨 Modern Dark Theme UI - Beautiful gradient effects and smooth animations
💫 Particle Effects - Dynamic particles for food collection and game events
🎮 Multiple Game States - Menu, Playing, Paused, Game Over, and Settings
⚙️ Customizable Settings - Adjust speed, toggle effects, and personalize gameplay
💾 Persistent Data - High scores and settings are saved automatically
🎯 Progressive Difficulty - Speed increases as you score more points
🖥️ Fullscreen Support - Press F11 to toggle fullscreen mode
📊 HUD Display - Real-time score, high score, and speed indicators

---

🚀 Installation
Prerequisites

Python 3.7 or higher
pip (Python package installer)

---

Setup

Clone the repository:

bashgit clone https://github.com/yourusername/snake-game.git
cd snake-game

---
Install dependencies:
bashpip install -r requirements.txt

---
Run the game:
bashpython snake_game.py

---
🎯 How to Play
Controls
Menu Navigation:

SPACE or ENTER - Start game
S - Open settings
Q or ESC - Quit game

---
Gameplay:

↑ or W - Move up
↓ or S - Move down
← or A - Move left
→ or D - Move right
ESC - Pause game
R - Restart game
F11 - Toggle fullscreen

---
Pause Menu:

SPACE or ESC - Resume
R - Restart
M - Return to main menu

---
Settings:

1 - Toggle grid visibility
2 - Toggle particle effects
3 - Toggle speed increase
4 - Toggle sound (placeholder)
+/- - Adjust base speed
ESC - Return to menu

---
Objective

Control the snake to eat the red food
Each food eaten increases your score by 1
The snake grows longer with each food eaten
Avoid hitting walls or yourself
Try to beat your high score!

---
⚙️ Settings
The game includes various customizable settings:

Grid Visibility - Show/hide the background grid
Particle Effects - Enable/disable visual particles
Speed Increase - Automatic speed increase with score
Base Speed - Adjust starting speed (4-20)
Sound - Sound effects toggle (placeholder for future feature)

---
Settings are automatically saved to snake_settings.json.
📁 Project Structure
snake-game/
│
├── snake_game.py           # Main game file
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .gitignore             # Git ignore rules
│
├── snake_settings.json    # Game settings (auto-generated)
└── snake_highscore.txt    # High score storage (auto-generated)

---
🛠️ Technical Details
Built With

Python - Core programming language
Pygame - Game development library

----
Architecture
The game uses a state machine pattern with the following states:

MENU - Main menu screen
PLAYING - Active gameplay
PAUSED - Game paused
GAME_OVER - Game over screen
SETTINGS - Settings configuration

---
Key Components

SnakeGame Class - Main game controller
GameState Enum - State management
Particle System - Visual effects engine
Settings Manager - Configuration persistence
High Score System - Score tracking and storage

---
⭐ If you enjoyed this game, please consider giving it a star on GitHub!
Made with ❤️ and Python
