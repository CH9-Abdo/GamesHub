import pygame
import random
from settings import *
from games.base_game import BaseGame

class BreakoutGame(BaseGame):
    def __init__(self, screen, return_to_menu_callback, highscore_manager=None, sound_manager=None, game_name="Breakout"):
        super().__init__(screen, create_game_callback=None, game_over_callback=None, highscore_manager=highscore_manager, sound_manager=sound_manager, game_name=game_name)
        self.return_to_menu = return_to_menu_callback
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE_HUD)
        self.reset()

    def reset(self):
        self.paddle_rect = pygame.Rect(
            (SCREEN_WIDTH - BREAKOUT_PADDLE_WIDTH) // 2,
            SCREEN_HEIGHT - 40,
            BREAKOUT_PADDLE_WIDTH,
            BREAKOUT_PADDLE_HEIGHT
        )
        self.ball_rect = pygame.Rect(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            BREAKOUT_BALL_RADIUS * 2,
            BREAKOUT_BALL_RADIUS * 2
        )
        self.ball_speed = [5, -5]
        self.bricks = self._create_bricks()
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.won = False

    def _create_bricks(self):
        bricks = []
        rows = 6
        cols = 10
        padding = 5
        width = (SCREEN_WIDTH - (cols + 1) * padding) // cols
        height = 25
        
        colors = [COLORS["DANGER"], COLORS["WARNING"], COLORS["SUCCESS"], COLORS["ACCENT"], COLORS["HIGHLIGHT"], COLORS["TEXT"]]

        for r in range(rows):
            for c in range(cols):
                rect = pygame.Rect(
                    padding + c * (width + padding),
                    padding + 50 + r * (height + padding),
                    width,
                    height
                )
                bricks.append({'rect': rect, 'color': colors[r % len(colors)]})
        return bricks

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
        
        # Continuous input handling in update for smoother movement

    def update(self):
        if self.game_over or self.won:
            return

        # Paddle Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.paddle_rect.x -= 8
        if keys[pygame.K_RIGHT]:
            self.paddle_rect.x += 8
        
        # Clamp paddle
        if self.paddle_rect.left < 0: self.paddle_rect.left = 0
        if self.paddle_rect.right > SCREEN_WIDTH: self.paddle_rect.right = SCREEN_WIDTH

        # Ball Movement
        self.ball_rect.x += self.ball_speed[0]
        self.ball_rect.y += self.ball_speed[1]

        # Wall Collisions
        if self.ball_rect.left <= 0 or self.ball_rect.right >= SCREEN_WIDTH:
            self.ball_speed[0] = -self.ball_speed[0]
        if self.ball_rect.top <= 0:
            self.ball_speed[1] = -self.ball_speed[1]
        
        if self.ball_rect.bottom >= SCREEN_HEIGHT:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
                self.play_sound("gameover")
                self.check_and_save_highscore(self.score)
            else:
                self.play_sound("explosion")
                # Reset ball
                self.ball_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                self.ball_speed = [5 * random.choice([-1, 1]), -5]

        # Paddle Collision
        if self.ball_rect.colliderect(self.paddle_rect):
            self.play_sound("select")
            self.ball_speed[1] = -abs(self.ball_speed[1]) # Bounce up
            # Adjust angle based on hit position
            offset = (self.ball_rect.centerx - self.paddle_rect.centerx) / (BREAKOUT_PADDLE_WIDTH / 2)
            self.ball_speed[0] += offset * 2
            self.ball_speed[0] = max(-8, min(8, self.ball_speed[0])) # Clamp horizontal speed

        # Brick Collision
        hit_index = self.ball_rect.collidelist([b['rect'] for b in self.bricks])
        if hit_index != -1:
            brick = self.bricks.pop(hit_index)
            self.ball_speed[1] = -self.ball_speed[1]
            self.score += 10
            self.play_sound("score")
            if not self.bricks:
                self.won = True
                self.check_and_save_highscore(self.score)

    def draw(self):
        self.screen.fill(COLORS["BACKGROUND"])

        # Draw Paddle
        pygame.draw.rect(self.screen, COLORS["ACCENT"], self.paddle_rect)

        # Draw Ball
        pygame.draw.ellipse(self.screen, COLORS["WHITE"], self.ball_rect)

        # Draw Bricks
        for brick in self.bricks:
            pygame.draw.rect(self.screen, brick['color'], brick['rect'])

        # Draw HUD
        score_surf = self.font.render(f"Score: {self.score}  Lives: {self.lives}", True, COLORS["TEXT"])
        self.screen.blit(score_surf, (10, 10))

        if self.game_over:
            self.draw_game_over_overlay("GAME OVER")
        elif self.won:
            self.draw_game_over_overlay("YOU WIN!")
