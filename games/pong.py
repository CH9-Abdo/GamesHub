import pygame
import random
from settings import *
from games.base_game import BaseGame

class PongGame(BaseGame):
    def __init__(self, screen, return_to_menu_callback, highscore_manager=None, sound_manager=None, game_name="Pong"):
        super().__init__(screen, create_game_callback=None, game_over_callback=None, highscore_manager=highscore_manager, sound_manager=sound_manager, game_name=game_name)
        self.return_to_menu = return_to_menu_callback
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE_HUD)
        self.reset()

    def reset(self):
        self.paddle_left = pygame.Rect(20, SCREEN_HEIGHT // 2 - PONG_PADDLE_HEIGHT // 2, PONG_PADDLE_WIDTH, PONG_PADDLE_HEIGHT)
        self.paddle_right = pygame.Rect(SCREEN_WIDTH - 20 - PONG_PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PONG_PADDLE_HEIGHT // 2, PONG_PADDLE_WIDTH, PONG_PADDLE_HEIGHT)
        self.ball = pygame.Rect(SCREEN_WIDTH // 2 - PONG_BALL_RADIUS, SCREEN_HEIGHT // 2 - PONG_BALL_RADIUS, PONG_BALL_RADIUS * 2, PONG_BALL_RADIUS * 2)
        
        self.ball_speed_x = PONG_BALL_SPEED_X * random.choice((1, -1))
        self.ball_speed_y = PONG_BALL_SPEED_Y * random.choice((1, -1))
        
        self.score_left = 0
        self.score_right = 0
        self.game_over = False
        self.winner = None

    def handle_events(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.reset()
                elif event.key == pygame.K_ESCAPE:
                    self.return_to_menu()
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.return_to_menu()

    def update(self):
        if self.game_over:
            return

        # Player Movement (Left Paddle)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.paddle_left.y -= PONG_PADDLE_SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.paddle_left.y += PONG_PADDLE_SPEED
        
        # Clamp Left Paddle
        self.paddle_left.clamp_ip(self.screen.get_rect())

        # AI Movement (Right Paddle)
        # Simple AI: move towards ball center, but with some speed limit
        if self.ball.centery < self.paddle_right.centery:
            self.paddle_right.y -= PONG_PADDLE_SPEED - 1 # Slightly slower to make it beatable
        elif self.ball.centery > self.paddle_right.centery:
            self.paddle_right.y += PONG_PADDLE_SPEED - 1
        
        # Clamp Right Paddle
        self.paddle_right.clamp_ip(self.screen.get_rect())

        # Ball Movement
        self.ball.x += self.ball_speed_x
        self.ball.y += self.ball_speed_y

        # Ball Collisions with Walls
        if self.ball.top <= 0 or self.ball.bottom >= SCREEN_HEIGHT:
            self.ball_speed_y *= -1

        # Ball Collisions with Paddles
        if self.ball.colliderect(self.paddle_left) and self.ball_speed_x < 0:
            self.ball_speed_x *= -1.05 # Increase speed slightly
            self.play_sound("select")
        
        if self.ball.colliderect(self.paddle_right) and self.ball_speed_x > 0:
            self.ball_speed_x *= -1.05
            self.play_sound("select")

        # Scoring
        if self.ball.left <= 0:
            self.score_right += 1
            self.play_sound("score")
            self._reset_ball()
        elif self.ball.right >= SCREEN_WIDTH:
            self.score_left += 1
            self.play_sound("score")
            self._reset_ball()

        # Win Condition
        if self.score_left >= 10:
            self.game_over = True
            self.play_sound("gameover")
            self.winner = "PLAYER"
            # In Pong, score isn't usually the highscore metric (usually it's win streak or just winning), 
            # but let's save the winning score difference or just the player score.
            self.check_and_save_highscore(self.score_left) 
        elif self.score_right >= 10:
            self.game_over = True
            self.play_sound("gameover")
            self.winner = "COMPUTER"
            self.check_and_save_highscore(self.score_left) # Save player score even if lost

    def _reset_ball(self):
        self.ball.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.ball_speed_x = PONG_BALL_SPEED_X * random.choice((1, -1))
        self.ball_speed_y = PONG_BALL_SPEED_Y * random.choice((1, -1))

    def draw(self):
        self.screen.fill(COLORS["BACKGROUND"])

        # Draw Net
        pygame.draw.line(self.screen, COLORS["GRID"], (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 2)

        # Draw Paddles
        pygame.draw.rect(self.screen, COLORS["PADDLE"], self.paddle_left)
        pygame.draw.rect(self.screen, COLORS["ENEMY"], self.paddle_right)

        # Draw Ball
        pygame.draw.ellipse(self.screen, COLORS["BALL"], self.ball)

        # Draw Scores
        score_text = self.font.render(f"{self.score_left}   {self.score_right}", True, COLORS["TEXT"])
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        self.screen.blit(score_text, score_rect)

        if self.game_over:
            msg = "YOU WIN!" if self.winner == "PLAYER" else "YOU LOSE!"
            self.draw_game_over_overlay(msg)