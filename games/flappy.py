import pygame
import random
from settings import *
from games.base_game import BaseGame

class FlappyGame(BaseGame):
    def __init__(self, screen, return_to_menu_callback):
        super().__init__(screen)
        self.return_to_menu = return_to_menu_callback
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE_HUD)
        self.reset()

    def reset(self):
        self.bird_rect = pygame.Rect(100, SCREEN_HEIGHT // 2, 30, 30)
        self.bird_velocity = 0
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.last_pipe_time = pygame.time.get_ticks()

    def handle_events(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.reset()
                elif event.key == pygame.K_ESCAPE:
                    self.return_to_menu()
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.bird_velocity = FLAPPY_JUMP_STRENGTH
            elif event.key == pygame.K_ESCAPE:
                self.return_to_menu()

    def update(self):
        if self.game_over:
            return

        # Bird Physics
        self.bird_velocity += FLAPPY_GRAVITY
        self.bird_rect.y += int(self.bird_velocity)

        # Pipe Generation
        current_time = pygame.time.get_ticks()
        if current_time - self.last_pipe_time > FLAPPY_PIPE_FREQUENCY:
            self.last_pipe_time = current_time
            self._create_pipe()

        # Pipe Movement & Collision
        for pipe in self.pipes[:]:
            pipe['top'].x -= FLAPPY_PIPE_SPEED
            pipe['bottom'].x -= FLAPPY_PIPE_SPEED
            
            if not pipe['passed'] and pipe['top'].right < self.bird_rect.left:
                self.score += 1
                pipe['passed'] = True
            
            if pipe['top'].right < 0:
                self.pipes.remove(pipe)

            # Collision Check
            if self.bird_rect.colliderect(pipe['top']) or self.bird_rect.colliderect(pipe['bottom']):
                self.game_over = True

        # Ground/Ceiling Collision
        if self.bird_rect.top < 0 or self.bird_rect.bottom > SCREEN_HEIGHT:
            self.game_over = True

    def _create_pipe(self):
        gap_y = random.randint(100, SCREEN_HEIGHT - 100 - FLAPPY_PIPE_GAP)
        pipe_width = 60
        
        top_rect = pygame.Rect(SCREEN_WIDTH, 0, pipe_width, gap_y)
        bottom_rect = pygame.Rect(SCREEN_WIDTH, gap_y + FLAPPY_PIPE_GAP, pipe_width, SCREEN_HEIGHT - (gap_y + FLAPPY_PIPE_GAP))
        
        self.pipes.append({
            'top': top_rect,
            'bottom': bottom_rect,
            'passed': False
        })

    def draw(self):
        self.screen.fill(COLORS["BACKGROUND"])

        # Draw Pipes
        for pipe in self.pipes:
            pygame.draw.rect(self.screen, COLORS["SUCCESS"], pipe['top'])
            pygame.draw.rect(self.screen, COLORS["SUCCESS"], pipe['bottom'])
            # Borders
            pygame.draw.rect(self.screen, COLORS["GRID"], pipe['top'], 2)
            pygame.draw.rect(self.screen, COLORS["GRID"], pipe['bottom'], 2)

        # Draw Bird
        pygame.draw.rect(self.screen, COLORS["WARNING"], self.bird_rect)
        pygame.draw.rect(self.screen, COLORS["TEXT"], self.bird_rect, 1)

        # Draw Score
        score_surf = self.font.render(f"Score: {self.score}", True, COLORS["TEXT"])
        self.screen.blit(score_surf, (10, 10))

        if self.game_over:
            self.draw_game_over_overlay()
