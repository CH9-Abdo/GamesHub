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

        # Draw Menu Options with High Scores
        start_y = 200
        for i, name in enumerate(self.game_names):
            if i == self.selected_index:
                color = COLORS["HIGHLIGHT"]
                # Add indicator
                indicator = "> "
            else:
                color = COLORS["TEXT"]
                indicator = "  "
            
            # Game Name
            text_surf = self.font_menu.render(indicator + name, True, color)
            rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * 60))
            self.screen.blit(text_surf, rect)
            
            # High Score (if applicable)
            if name != "Quit":
                game_instance = self.games[name]
                if game_instance.highscore_manager:
                    high_score = game_instance.highscore_manager.get_score(name)
                    if high_score > 0:
                        score_surf = self.font_small.render(f"High: {high_score}", True, COLORS["GRID"])
                        score_rect = score_surf.get_rect(midtop=(SCREEN_WIDTH // 2, rect.bottom - 5))
                        self.screen.blit(score_surf, score_rect)

        # Draw Instructions
        inst_surf = self.font_menu.render("ARROWS to Select, ENTER to Play", True, COLORS["GRID"])
        inst_rect = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(inst_surf, inst_rect)
    
    def reset(self):
        pass