import pygame
import random
from settings import *
from games.base_game import BaseGame

class MemoryGame(BaseGame):
    """Card matching (concentration) game. Click two cards to find pairs."""
    def __init__(self, screen, return_to_menu_callback, highscore_manager=None, sound_manager=None, game_name="Memory"):
        super().__init__(screen, create_game_callback=None, game_over_callback=None, highscore_manager=highscore_manager, sound_manager=sound_manager, game_name=game_name)
        self.return_to_menu = return_to_menu_callback
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE_HUD)
        self.reset()

    def reset(self):
        self.rows = MEMORY_ROWS
        self.cols = MEMORY_COLS
        self.cell_size = MEMORY_CELL_SIZE
        self.offset_x = MEMORY_OFFSET_X
        self.offset_y = MEMORY_OFFSET_Y
        n_pairs = (self.rows * self.cols) // 2
        values = list(range(n_pairs)) * 2
        random.shuffle(values)
        self.cards = []  # list of {'value': int, 'flipped': bool, 'matched': bool}
        for v in values:
            self.cards.append({'value': v, 'flipped': False, 'matched': False})
        self.first_index = None
        self.moves = 0
        self.matches = 0
        self.game_over = False
        self.lock_until = 0  # delay before hiding non-matching pair

    def _index_at_pos(self, mx, my):
        c = (mx - self.offset_x) // self.cell_size
        r = (my - self.offset_y) // self.cell_size
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return r * self.cols + c
        return None

    def handle_events(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.reset()
                elif event.key == pygame.K_ESCAPE:
                    self.return_to_menu()
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.return_to_menu()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if pygame.time.get_ticks() < self.lock_until:
                return
            idx = self._index_at_pos(*pygame.mouse.get_pos())
            if idx is None:
                return
            card = self.cards[idx]
            if card['matched'] or card['flipped']:
                return
            card['flipped'] = True
            if self.first_index is None:
                self.first_index = idx
                self.play_sound("select")
            else:
                self.moves += 1
                first_card = self.cards[self.first_index]
                if first_card['value'] == card['value']:
                    first_card['matched'] = True
                    card['matched'] = True
                    self.matches += 1
                    self.play_sound("score")
                    if self.matches == (self.rows * self.cols) // 2:
                        self.game_over = True
                        self.check_and_save_highscore(self.moves)
                        self.play_sound("gameover")
                else:
                    self.lock_until = pygame.time.get_ticks() + 800
                    def hide_pair():
                        first_card['flipped'] = False
                        card['flipped'] = False
                    # We'll hide in update() when lock_until expires
                    self._pending_hide = (self.first_index, idx)
                self.first_index = None

    def update(self):
        if self.game_over:
            return
        now = pygame.time.get_ticks()
        if hasattr(self, '_pending_hide') and now >= self.lock_until:
            i, j = self._pending_hide
            self.cards[i]['flipped'] = False
            self.cards[j]['flipped'] = False
            del self._pending_hide

    def draw(self):
        self.screen.fill(COLORS["BACKGROUND"])
        palette = [COLORS["ACCENT"], COLORS["HIGHLIGHT"], COLORS["SUCCESS"], COLORS["WARNING"],
                   COLORS["DANGER"], COLORS["PADDLE"], COLORS["ENEMY"], COLORS["TEXT"]]
        for idx, card in enumerate(self.cards):
            r, c = idx // self.cols, idx % self.cols
            x = self.offset_x + c * self.cell_size
            y = self.offset_y + r * self.cell_size
            rect = pygame.Rect(x + 2, y + 2, self.cell_size - 4, self.cell_size - 4)
            if card['matched']:
                pygame.draw.rect(self.screen, COLORS["SUCCESS"], rect, border_radius=6)
                pygame.draw.rect(self.screen, COLORS["GRID"], rect, 2, border_radius=6)
            elif card['flipped']:
                pygame.draw.rect(self.screen, palette[card['value'] % len(palette)], rect, border_radius=6)
                pygame.draw.rect(self.screen, COLORS["GRID"], rect, 2, border_radius=6)
                num = self.font.render(str(card['value'] + 1), True, COLORS["BLACK"])
                self.screen.blit(num, num.get_rect(center=rect.center))
            else:
                pygame.draw.rect(self.screen, COLORS["GRID"], rect, border_radius=6)
                pygame.draw.rect(self.screen, COLORS["ACCENT"], rect, 2, border_radius=6)
        score_surf = self.font.render(f"Moves: {self.moves}  Pairs: {self.matches}", True, COLORS["TEXT"])
        self.screen.blit(score_surf, (10, 10))
        if self.game_over:
            self.draw_game_over_overlay(f"Moves: {self.moves}")
