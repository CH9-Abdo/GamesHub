import pygame
import random
from settings import *
from games.base_game import BaseGame

# Tetromino Definitions
SHAPES = [
    [[1, 1, 1, 1]], # I
    [[1, 1], [1, 1]], # O
    [[0, 1, 0], [1, 1, 1]], # T
    [[1, 0, 0], [1, 1, 1]], # J
    [[0, 0, 1], [1, 1, 1]], # L
    [[0, 1, 1], [1, 1, 0]], # S
    [[1, 1, 0], [0, 1, 1]]  # Z
]

COLORS_LIST = [
    (0, 255, 255), # Cyan (I)
    (255, 255, 0), # Yellow (O)
    (128, 0, 128), # Purple (T)
    (0, 0, 255),   # Blue (J)
    (255, 127, 0), # Orange (L)
    (0, 255, 0),   # Green (S)
    (255, 0, 0)    # Red (Z)
]

class TetrisGame(BaseGame):
    def __init__(self, screen, return_to_menu_callback):
        super().__init__(screen)
        self.return_to_menu = return_to_menu_callback
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE_HUD)
        self.reset()

    def reset(self):
        self.grid = [[0 for _ in range(TETRIS_COLS)] for _ in range(TETRIS_ROWS)]
        self.current_piece = self._get_new_piece()
        self.next_piece = self._get_new_piece()
        self.score = 0
        self.game_over = False
        self.drop_timer = 0
        self.drop_interval = 500
        self.fast_drop = False

    def _get_new_piece(self):
        shape_idx = random.randint(0, len(SHAPES) - 1)
        shape = SHAPES[shape_idx]
        color = COLORS_LIST[shape_idx]
        return {
            'shape': shape,
            'color': color,
            'x': TETRIS_COLS // 2 - len(shape[0]) // 2,
            'y': 0
        }

    def handle_events(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.reset()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.return_to_menu()
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self._move(-1, 0)
            elif event.key == pygame.K_RIGHT:
                self._move(1, 0)
            elif event.key == pygame.K_DOWN:
                self.fast_drop = True
            elif event.key == pygame.K_UP:
                self._rotate()
            elif event.key == pygame.K_SPACE:
                self._hard_drop()
            elif event.key == pygame.K_ESCAPE:
                self.return_to_menu()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                self.fast_drop = False

    def update(self):
        if self.game_over:
            return

        current_time = pygame.time.get_ticks()
        interval = 50 if self.fast_drop else self.drop_interval
        
        if current_time - self.drop_timer > interval:
            self.drop_timer = current_time
            if not self._move(0, 1):
                self._lock_piece()

    def _move(self, dx, dy):
        new_x = self.current_piece['x'] + dx
        new_y = self.current_piece['y'] + dy
        if not self._check_collision(self.current_piece['shape'], new_x, new_y):
            self.current_piece['x'] = new_x
            self.current_piece['y'] = new_y
            return True
        return False

    def _rotate(self):
        shape = self.current_piece['shape']
        new_shape = [list(row) for row in zip(*shape[::-1])] # Rotate matrix
        if not self._check_collision(new_shape, self.current_piece['x'], self.current_piece['y']):
            self.current_piece['shape'] = new_shape

    def _check_collision(self, shape, x, y):
        for r, row in enumerate(shape):
            for c, val in enumerate(row):
                if val:
                    grid_x = x + c
                    grid_y = y + r
                    if grid_x < 0 or grid_x >= TETRIS_COLS or grid_y >= TETRIS_ROWS:
                        return True
                    if grid_y >= 0 and self.grid[grid_y][grid_x]:
                        return True
        return False

    def _lock_piece(self):
        for r, row in enumerate(self.current_piece['shape']):
            for c, val in enumerate(row):
                if val:
                    grid_y = self.current_piece['y'] + r
                    grid_x = self.current_piece['x'] + c
                    if grid_y < 0:
                        self.game_over = True
                        return
                    self.grid[grid_y][grid_x] = self.current_piece['color']
        
        self._clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self._get_new_piece()
        
        if self._check_collision(self.current_piece['shape'], self.current_piece['x'], self.current_piece['y']):
            self.game_over = True

    def _clear_lines(self):
        lines_cleared = 0
        new_grid = [row for row in self.grid if any(cell == 0 for cell in row)]
        lines_cleared = TETRIS_ROWS - len(new_grid)
        for _ in range(lines_cleared):
            new_grid.insert(0, [0 for _ in range(TETRIS_COLS)])
        self.grid = new_grid
        self.score += lines_cleared * 100

    def _hard_drop(self):
        while self._move(0, 1):
            pass
        self._lock_piece()

    def _get_ghost_position(self):
        ghost_y = self.current_piece['y']
        while not self._check_collision(self.current_piece['shape'], self.current_piece['x'], ghost_y + 1):
            ghost_y += 1
        return ghost_y

    def draw(self):
        self.screen.fill(COLORS["BACKGROUND"])

        # Draw Grid Board
        pygame.draw.rect(self.screen, COLORS["GRID"], 
                         (TETRIS_OFFSET_X - 2, TETRIS_OFFSET_Y - 2, 
                          TETRIS_COLS * TETRIS_CELL_SIZE + 4, TETRIS_ROWS * TETRIS_CELL_SIZE + 4), 1)

        # Draw Locked Blocks
        for r, row in enumerate(self.grid):
            for c, color in enumerate(row):
                if color:
                    self._draw_block(c, r, color)

        # Draw Ghost Piece
        ghost_y = self._get_ghost_position()
        for r, row in enumerate(self.current_piece['shape']):
            for c, val in enumerate(row):
                if val:
                    self._draw_block(self.current_piece['x'] + c, ghost_y + r, (50, 50, 50), outline=True)

        # Draw Current Piece
        for r, row in enumerate(self.current_piece['shape']):
            for c, val in enumerate(row):
                if val:
                    self._draw_block(self.current_piece['x'] + c, self.current_piece['y'] + r, self.current_piece['color'])

        # Draw UI (Score, Next Piece)
        self._draw_ui()

        if self.game_over:
            self._draw_game_over()

    def _draw_block(self, x, y, color, outline=False):
        rect = pygame.Rect(TETRIS_OFFSET_X + x * TETRIS_CELL_SIZE, 
                           TETRIS_OFFSET_Y + y * TETRIS_CELL_SIZE, 
                           TETRIS_CELL_SIZE, TETRIS_CELL_SIZE)
        if outline:
            pygame.draw.rect(self.screen, color, rect, 1)
        else:
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, COLORS["BACKGROUND"], rect, 1)

    def _draw_ui(self):
        # Score
        score_surf = self.font.render(f"Score: {self.score}", True, COLORS["TEXT"])
        self.screen.blit(score_surf, (TETRIS_OFFSET_X + TETRIS_COLS * TETRIS_CELL_SIZE + 20, TETRIS_OFFSET_Y))

        # Next Piece Label
        next_surf = self.font.render("Next:", True, COLORS["TEXT"])
        self.screen.blit(next_surf, (TETRIS_OFFSET_X + TETRIS_COLS * TETRIS_CELL_SIZE + 20, TETRIS_OFFSET_Y + 50))

        # Next Piece Preview
        preview_x = TETRIS_OFFSET_X + TETRIS_COLS * TETRIS_CELL_SIZE + 20
        preview_y = TETRIS_OFFSET_Y + 80
        for r, row in enumerate(self.next_piece['shape']):
            for c, val in enumerate(row):
                if val:
                    rect = pygame.Rect(preview_x + c * TETRIS_CELL_SIZE, 
                                       preview_y + r * TETRIS_CELL_SIZE, 
                                       TETRIS_CELL_SIZE, TETRIS_CELL_SIZE)
                    pygame.draw.rect(self.screen, self.next_piece['color'], rect)
                    pygame.draw.rect(self.screen, COLORS["BACKGROUND"], rect, 1)

    def _draw_game_over(self):
        # ...reuse similar game over logic or make a shared UI component...
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(COLORS["BLACK"])
        self.screen.blit(overlay, (0, 0))
        
        font_big = pygame.font.SysFont(FONT_NAME, 64)
        text = font_big.render("GAME OVER", True, COLORS["DANGER"])
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)
        
        font_small = pygame.font.SysFont(FONT_NAME, 24)
        msg = font_small.render("Press SPACE to Restart or ESC for Menu", True, COLORS["TEXT"])
        msg_rect = msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(msg, msg_rect)
