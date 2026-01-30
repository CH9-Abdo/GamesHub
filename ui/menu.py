import pygame
import random
from settings import *

class MainMenu:
    def __init__(self, screen, game_manager, games_dict):
        self.screen = screen
        self.game_manager = game_manager
        self.games = games_dict # Dictionary of {"Name": GameInstance}
        self.game_names = list(self.games.keys()) + ["Quit"]
        self.selected_index = 0
        self.font_title = pygame.font.SysFont(FONT_NAME, FONT_SIZE_TITLE)
        self.font_menu = pygame.font.SysFont(FONT_NAME, FONT_SIZE_MENU)
        self.font_small = pygame.font.SysFont(FONT_NAME, 20)
        
        # Background Particles
        self.particles = []
        for _ in range(50):
            self.particles.append(self._create_particle())

    def _create_particle(self):
        return {
            'x': random.randint(0, SCREEN_WIDTH),
            'y': random.randint(0, SCREEN_HEIGHT),
            'speed': random.randint(1, 3),
            'size': random.randint(1, 3),
            'color': random.choice([COLORS["ACCENT"], COLORS["HIGHLIGHT"], COLORS["GRID"]])
        }

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.game_names)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.game_names)
            elif event.key == pygame.K_RETURN:
                selected_option = self.game_names[self.selected_index]
                if selected_option == "Quit":
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                else:
                    self.game_manager.set_state(self.games[selected_option])

    def update(self):
        # Update particles
        for p in self.particles:
            p['y'] += p['speed']
            if p['y'] > SCREEN_HEIGHT:
                p['y'] = 0
                p['x'] = random.randint(0, SCREEN_WIDTH)

    def draw(self):
        self.screen.fill(COLORS["BACKGROUND"])
        
        # Draw Particles
        for p in self.particles:
            pygame.draw.rect(self.screen, p['color'], (p['x'], p['y'], p['size'], p['size']))

        # Draw Title
        title_surf = self.font_title.render(TITLE, True, COLORS["ACCENT"])
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 80))
        
        # Simple Shadow for Title
        shadow_surf = self.font_title.render(TITLE, True, COLORS["HIGHLIGHT"])
        shadow_rect = shadow_surf.get_rect(center=(SCREEN_WIDTH // 2 + 3, 80 + 3))
        self.screen.blit(shadow_surf, shadow_rect)
        self.screen.blit(title_surf, title_rect)

        # Draw Menu Panel
        panel_width = 500
        panel_height = 400
        panel_rect = pygame.Rect((SCREEN_WIDTH - panel_width) // 2, 150, panel_width, panel_height)
        
        # Semi-transparent background for panel
        s = pygame.Surface((panel_width, panel_height))
        s.set_alpha(50)
        s.fill(COLORS["GRID"])
        self.screen.blit(s, panel_rect.topleft)
        pygame.draw.rect(self.screen, COLORS["ACCENT"], panel_rect, 2)

        # Draw Menu Options with High Scores aligned
        start_y = 180
        line_height = 50
        
        for i, name in enumerate(self.game_names):
            y_pos = start_y + i * line_height
            
            # Selection Highlight
            if i == self.selected_index:
                highlight_rect = pygame.Rect(panel_rect.left + 10, y_pos - 10, panel_width - 20, line_height)
                pygame.draw.rect(self.screen, (30, 30, 50), highlight_rect)
                pygame.draw.rect(self.screen, COLORS["HIGHLIGHT"], highlight_rect, 1)
                color = COLORS["HIGHLIGHT"]
                indicator = ">"
            else:
                color = COLORS["TEXT"]
                indicator = ""
            
            # Game Name (Left Aligned)
            name_surf = self.font_menu.render(f"{indicator} {name}", True, color)
            self.screen.blit(name_surf, (panel_rect.left + 30, y_pos))
            
            # High Score (Right Aligned)
            if name != "Quit":
                game_instance = self.games[name]
                if game_instance.highscore_manager:
                    high_score = game_instance.highscore_manager.get_score(name)
                    score_text = f"{high_score}" if high_score > 0 else "-"
                    score_surf = self.font_small.render(score_text, True, COLORS["ACCENT"])
                    score_rect = score_surf.get_rect(right=panel_rect.right - 30, centery=y_pos + 15)
                    self.screen.blit(score_surf, score_rect)
                    
                    # Label "Best"
                    label_surf = self.font_small.render("Best:", True, COLORS["GRID"])
                    label_rect = label_surf.get_rect(right=score_rect.left - 10, centery=y_pos + 15)
                    self.screen.blit(label_surf, label_rect)

        # Draw Instructions
        inst_surf = self.font_menu.render("ARROWS to Select, ENTER to Play", True, COLORS["GRID"])
        inst_rect = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(inst_surf, inst_rect)
    
    def reset(self):
        pass
