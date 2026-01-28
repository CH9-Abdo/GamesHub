import pygame

# Screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "Retro Games Hub"

# Colors (Material Design / Retro Neon)
COLORS = {
    "BACKGROUND": (30, 30, 30),      # Dark Grey
    "TEXT": (230, 230, 230),         # Off-White
    "ACCENT": (0, 188, 212),         # Cyan
    "HIGHLIGHT": (255, 64, 129),     # Pink
    "SUCCESS": (0, 230, 118),        # Green
    "WARNING": (255, 193, 7),        # Amber
    "DANGER": (255, 82, 82),         # Red
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "GRID": (50, 50, 50)
}

# Fonts
FONT_NAME = "arial"  # Fallback
FONT_SIZE_TITLE = 64
FONT_SIZE_MENU = 32
FONT_SIZE_HUD = 24

# Game Specific Settings
# Tetris
TETRIS_COLS = 10
TETRIS_ROWS = 20
TETRIS_CELL_SIZE = 30
TETRIS_OFFSET_X = (SCREEN_WIDTH - (TETRIS_COLS * TETRIS_CELL_SIZE)) // 2
TETRIS_OFFSET_Y = (SCREEN_HEIGHT - (TETRIS_ROWS * TETRIS_CELL_SIZE)) // 2

# Snake
SNAKE_CELL_SIZE = 20
SNAKE_GRID_WIDTH = SCREEN_WIDTH // SNAKE_CELL_SIZE
SNAKE_GRID_HEIGHT = SCREEN_HEIGHT // SNAKE_CELL_SIZE

# Breakout
BREAKOUT_PADDLE_WIDTH = 100
BREAKOUT_PADDLE_HEIGHT = 15
BREAKOUT_BALL_RADIUS = 8
