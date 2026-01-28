import pygame
from settings import *

class MainMenu:
    def __init__(self, screen, game_manager, games_dict):
        self.screen = screen
        self.game_manager = game_manager
        self.games = games_dict # Dictionary of {"Name": GameInstance}
        self.game_names = list(self.games.keys())
        self.selected_index = 0
        self.font_title = pygame.font.SysFont(FONT_NAME, FONT_SIZE_TITLE)
        self.font_menu = pygame.font.SysFont(FONT_NAME, FONT_SIZE_MENU)

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.game_names)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.game_names)
            elif event.key == pygame.K_RETURN:
                selected_game_name = self.game_names[self.selected_index]
                self.game_manager.set_state(self.games[selected_game_name])

    def update(self):
        pass

    def draw(self):
        self.screen.fill(COLORS["BACKGROUND"])
        
        # Draw Title
        title_surf = self.font_title.render(TITLE, True, COLORS["ACCENT"])
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_surf, title_rect)

        # Draw Menu Options
        for i, name in enumerate(self.game_names):
            color = COLORS["HIGHLIGHT"] if i == self.selected_index else COLORS["TEXT"]
            text_surf = self.font_menu.render(name, True, color)
            rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, 250 + i * 60))
            self.screen.blit(text_surf, rect)

        # Draw Instructions
        inst_surf = self.font_menu.render("Use ARROWS to Select, ENTER to Play", True, COLORS["GRID"])
        inst_rect = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(inst_surf, inst_rect)
    
    def reset(self):
        pass
