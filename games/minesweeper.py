import pygame
import random
from settings import *
from games.base_game import BaseGame

class MinesweeperGame(BaseGame):
    def __init__(self, screen, return_to_menu_callback, highscore_manager=None, sound_manager=None, game_name="Minesweeper"):
        super().__init__(screen, create_game_callback=None, game_over_callback=None, highscore_manager=highscore_manager, sound_manager=sound_manager, game_name=game_name)
        self.return_to_menu = return_to_menu_callback
        self.font = pygame.font.SysFont(FONT_NAME, 24)
        self.reset()

    def reset(self):
        self.rows = MINESWEEPER_ROWS
        self.cols = MINESWEEPER_COLS
        self.num_mines = MINESWEEPER_MINES
        self.cell_size = MINESWEEPER_CELL_SIZE
        self.offset_x = MINESWEEPER_OFFSET_X
        self.offset_y = MINESWEEPER_OFFSET_Y
        
        self.grid = [[{'mine': False, 'revealed': False, 'flagged': False, 'neighbors': 0} 
                      for _ in range(self.cols)] for _ in range(self.rows)]
        
        self._place_mines()
        self._calculate_neighbors()
        
        self.game_over = False
        self.won = False
        self.start_time = pygame.time.get_ticks()
        self.time_elapsed = 0
        self.first_click = True

    def _place_mines(self):
        mines_placed = 0
        while mines_placed < self.num_mines:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            if not self.grid[r][c]['mine']:
                self.grid[r][c]['mine'] = True
                mines_placed += 1

    def _calculate_neighbors(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c]['mine']:
                    continue
                count = 0
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if i == 0 and j == 0: continue
                        nr, nc = r + i, c + j
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            if self.grid[nr][nc]['mine']:
                                count += 1
                self.grid[r][c]['neighbors'] = count

    def handle_events(self, event):
        if self.game_over or self.won:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.reset()
                elif event.key == pygame.K_ESCAPE:
                    self.return_to_menu()
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.return_to_menu()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            # Convert mouse pos to grid coords
            c = (mx - self.offset_x) // self.cell_size
            r = (my - self.offset_y) // self.cell_size
            
            if 0 <= r < self.rows and 0 <= c < self.cols:
                if event.button == 1: # Left Click (Reveal)
                    self._reveal(r, c)
                elif event.button == 3: # Right Click (Flag)
                    self._toggle_flag(r, c)

    def _reveal(self, r, c):
        cell = self.grid[r][c]
        if cell['revealed'] or cell['flagged']:
            return
        
        # Ensure first click is safe
        if self.first_click:
            self.first_click = False
            if cell['mine']:
                # Move mine
                cell['mine'] = False
                while True:
                    nr = random.randint(0, self.rows - 1)
                    nc = random.randint(0, self.cols - 1)
                    if not self.grid[nr][nc]['mine'] and (nr != r or nc != c):
                        self.grid[nr][nc]['mine'] = True
                        break
                self._calculate_neighbors()
        
        cell['revealed'] = True
        
        if cell['mine']:
            self.game_over = True
            self.play_sound("explosion")
            self._reveal_all_mines()
        else:
            self.play_sound("select")
            if cell['neighbors'] == 0:
                self._reveal_neighbors(r, c)
            self._check_win()

    def _reveal_neighbors(self, r, c):
        stack = [(r, c)]
        while stack:
            cr, cc = stack.pop()
            for i in range(-1, 2):
                for j in range(-1, 2):
                    nr, nc = cr + i, cc + j
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        neighbor = self.grid[nr][nc]
                        if not neighbor['revealed'] and not neighbor['flagged']:
                            neighbor['revealed'] = True
                            if neighbor['neighbors'] == 0:
                                stack.append((nr, nc))

    def _toggle_flag(self, r, c):
        cell = self.grid[r][c]
        if not cell['revealed']:
            cell['flagged'] = not cell['flagged']

    def _reveal_all_mines(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c]['mine']:
                    self.grid[r][c]['revealed'] = True

    def _check_win(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if not self.grid[r][c]['mine'] and not self.grid[r][c]['revealed']:
                    return
        self.won = True
        self.play_sound("score")
        # Highscore is based on time (lower is better), but current highscore manager assumes higher is better.
        # We can store negative time or inverted score. Let's store inverted time (e.g., 10000 - time_seconds)
        score = max(0, 1000 - int(self.time_elapsed)) 
        self.check_and_save_highscore(score)

    def update(self):
        if not self.game_over and not self.won:
            self.time_elapsed = (pygame.time.get_ticks() - self.start_time) / 1000

    def draw(self):
        self.screen.fill(COLORS["BACKGROUND"])

        # Draw Grid
        for r in range(self.rows):
            for c in range(self.cols):
                rect = pygame.Rect(
                    self.offset_x + c * self.cell_size,
                    self.offset_y + r * self.cell_size,
                    self.cell_size, self.cell_size
                )
                
                cell = self.grid[r][c]
                
                if cell['revealed']:
                    if cell['mine']:
                        pygame.draw.rect(self.screen, COLORS["DANGER"], rect)
                        pygame.draw.circle(self.screen, COLORS["BLACK"], rect.center, self.cell_size // 4)
                    else:
                        pygame.draw.rect(self.screen, (200, 200, 200), rect)
                        if cell['neighbors'] > 0:
                            # Colors for numbers
                            colors = [
                                (0, 0, 255), (0, 128, 0), (255, 0, 0), (0, 0, 128),
                                (128, 0, 0), (0, 128, 128), (0, 0, 0), (128, 128, 128)
                            ]
                            color = colors[cell['neighbors'] - 1]
                            text = self.font.render(str(cell['neighbors']), True, color)
                            text_rect = text.get_rect(center=rect.center)
                            self.screen.blit(text, text_rect)
                else:
                    # Unrevealed
                    pygame.draw.rect(self.screen, (100, 100, 100), rect)
                    # Bevel effect
                    pygame.draw.line(self.screen, (150, 150, 150), rect.topleft, rect.topright)
                    pygame.draw.line(self.screen, (150, 150, 150), rect.topleft, rect.bottomleft)
                    pygame.draw.line(self.screen, (50, 50, 50), rect.bottomleft, rect.bottomright)
                    pygame.draw.line(self.screen, (50, 50, 50), rect.topright, rect.bottomright)
                    
                    if cell['flagged']:
                        # Draw flag
                        start_pos = (rect.centerx - 5, rect.centery + 5)
                        pygame.draw.line(self.screen, COLORS["BLACK"], start_pos, (start_pos[0], start_pos[1] - 15), 2)
                        pygame.draw.polygon(self.screen, COLORS["DANGER"], [
                            (start_pos[0], start_pos[1] - 15),
                            (start_pos[0] + 10, start_pos[1] - 10),
                            (start_pos[0], start_pos[1] - 5)
                        ])

                pygame.draw.rect(self.screen, COLORS["GRID"], rect, 1)

        # Draw HUD
        time_text = self.font.render(f"Time: {int(self.time_elapsed)}", True, COLORS["TEXT"])
        self.screen.blit(time_text, (self.offset_x, self.offset_y - 30))
        
        mines_left = self.num_mines - sum(1 for r in range(self.rows) for c in range(self.cols) if self.grid[r][c]['flagged'])
        mines_text = self.font.render(f"Mines: {mines_left}", True, COLORS["TEXT"])
        mines_rect = mines_text.get_rect(topright=(self.offset_x + self.cols * self.cell_size, self.offset_y - 30))
        self.screen.blit(mines_text, mines_rect)

        if self.game_over:
            self.draw_game_over_overlay("GAME OVER")
        elif self.won:
            self.draw_game_over_overlay("YOU WIN!")
