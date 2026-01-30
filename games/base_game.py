import pygame
from abc import ABC, abstractmethod
from settings import *

class BaseGame(ABC):
    def __init__(self, screen, create_game_callback=None, game_over_callback=None, highscore_manager=None, game_name="Unknown"):
        self.screen = screen
        # Callback to return to menu or switch states
        self.create_game_callback = create_game_callback 
        self.game_over_callback = game_over_callback
        self.highscore_manager = highscore_manager
        self.game_name = game_name
        self.active = False
        self.font_overlay_big = pygame.font.SysFont(FONT_NAME, 64)
        self.font_overlay_small = pygame.font.SysFont(FONT_NAME, 32)

    @abstractmethod
    def handle_events(self, event):
        """Process input events."""
        pass

    @abstractmethod
    def update(self):
        """Update game logic."""
        pass

    @abstractmethod
    def draw(self):
        """Render the game to the screen."""
        pass

    def reset(self):
        """Reset the game state to start over."""
        pass

    def draw_text_centered(self, text, font, color, center_x, center_y):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(center_x, center_y))
        self.screen.blit(surf, rect)

    def draw_game_over_overlay(self, message="GAME OVER"):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150) # Slightly darker for better contrast
        overlay.fill(COLORS["BACKGROUND"])
        self.screen.blit(overlay, (0, 0))

        self.draw_text_centered(message, self.font_overlay_big, COLORS["DANGER"], SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)
        
        # Show High Score
        if self.highscore_manager:
            high_score = self.highscore_manager.get_score(self.game_name)
            self.draw_text_centered(f"High Score: {high_score}", self.font_overlay_small, COLORS["HIGHLIGHT"], SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        self.draw_text_centered("Press SPACE to Restart", self.font_overlay_small, COLORS["TEXT"], SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
        self.draw_text_centered("Press ESC for Menu", self.font_overlay_small, COLORS["GRID"], SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90)

    def check_and_save_highscore(self, current_score):
        if self.highscore_manager:
            return self.highscore_manager.save_score(self.game_name, current_score)
        return False
