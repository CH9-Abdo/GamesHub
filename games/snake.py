import pygame
import random
from settings import *
from games.base_game import BaseGame

class SnakeGame(BaseGame):
    def __init__(self, screen, return_to_menu_callback, highscore_manager=None, sound_manager=None, game_name="Snake"):
        super().__init__(screen, create_game_callback=None, game_over_callback=None, highscore_manager=highscore_manager, sound_manager=sound_manager, game_name=game_name)
        self.return_to_menu = return_to_menu_callback
        self.reset()
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE_HUD)

    def reset(self):
        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = self._get_random_position()
        self.powerup = None
        self.powerup_timer = 0
        self.score = 0
        self.game_over = False
        self.move_timer = 0
        self.move_interval = 150  # milliseconds
        self.active_powerups = [] # List of {'type': type, 'end_time': time}

    def _get_random_position(self):
        while True:
            pos = (random.randint(0, SNAKE_GRID_WIDTH - 1),
                   random.randint(0, SNAKE_GRID_HEIGHT - 1))
            if pos not in self.snake:
                return pos

    def handle_events(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.reset()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.return_to_menu()
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and self.direction != (0, 1):
                self.next_direction = (0, -1)
            elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                self.next_direction = (0, 1)
            elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                self.next_direction = (-1, 0)
            elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                self.next_direction = (1, 0)
            elif event.key == pygame.K_ESCAPE:
                self.return_to_menu()

    def update(self):
        if self.game_over:
            return

        current_time = pygame.time.get_ticks()
        
        # Powerup Spawning
        if self.powerup is None and random.random() < 0.005: # Chance per frame
             self.powerup = {
                 'pos': self._get_random_position(),
                 'type': random.choice(['SPEED', 'SLOW', 'BONUS', 'CUT']),
                 'spawn_time': current_time
             }
        
        # Remove old powerup
        if self.powerup and current_time - self.powerup['spawn_time'] > 8000: # 8 seconds
            self.powerup = None

        if current_time - self.move_timer > self.move_interval:
            self.move_timer = current_time
            self._move_snake()

    def _move_snake(self):
        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Check collisions (Walls or Self)
        if (new_head in self.snake or
            new_head[0] < 0 or new_head[0] >= SNAKE_GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= SNAKE_GRID_HEIGHT):
            self.game_over = True
            self.play_sound("gameover")
            self.check_and_save_highscore(self.score)
            return

        self.snake.insert(0, new_head)

        # Check Food
        if new_head == self.food:
            self.score += 10
            self.play_sound("score")
            self.food = self._get_random_position()
            # Default speed up logic (can be overridden by powerup)
            if self.move_interval > 50:
                 self.move_interval -= 2
        
        # Check Powerup
        elif self.powerup and new_head == self.powerup['pos']:
            self._apply_powerup(self.powerup['type'])
            self.powerup = None
            self.play_sound("select") # Use select sound for powerup
        else:
            self.snake.pop()

    def _apply_powerup(self, p_type):
        if p_type == 'SPEED':
            self.move_interval = max(50, self.move_interval - 50)
            self.score += 5
        elif p_type == 'SLOW':
            self.move_interval = min(300, self.move_interval + 50)
            self.score += 5
        elif p_type == 'BONUS':
            self.score += 50
        elif p_type == 'CUT':
            if len(self.snake) > 3:
                # Cut half the tail
                cut_len = len(self.snake) // 2
                self.snake = self.snake[:len(self.snake) - cut_len]
                self.score += 5

    def draw(self):
        self.screen.fill(COLORS["BACKGROUND"])

        # Draw Grid (Subtle)
        for x in range(0, SCREEN_WIDTH, SNAKE_CELL_SIZE):
            pygame.draw.line(self.screen, (20, 20, 30), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, SNAKE_CELL_SIZE):
            pygame.draw.line(self.screen, (20, 20, 30), (0, y), (SCREEN_WIDTH, y))

        # Draw Snake (Rounded Rects)
        for i, (x, y) in enumerate(self.snake):
            rect = pygame.Rect(x * SNAKE_CELL_SIZE + 1, y * SNAKE_CELL_SIZE + 1,
                             SNAKE_CELL_SIZE - 2, SNAKE_CELL_SIZE - 2)
            color = COLORS["SUCCESS"] if i == 0 else COLORS["ACCENT"] # Head is different
            
            # Rounded corners
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            
            # Eyes for Head
            if i == 0:
                eye_radius = 2
                offset = 5
                # Simple logic to position eyes based on direction
                dx, dy = self.direction
                eye1_pos = (rect.centerx - offset if dx == 0 else rect.centerx, rect.centery - offset if dy == 0 else rect.centery)
                eye2_pos = (rect.centerx + offset if dx == 0 else rect.centerx, rect.centery + offset if dy == 0 else rect.centery)
                if dx != 0: eye1_pos, eye2_pos = (rect.centerx + dx*3, rect.centery - offset), (rect.centerx + dx*3, rect.centery + offset)
                if dy != 0: eye1_pos, eye2_pos = (rect.centerx - offset, rect.centery + dy*3), (rect.centerx + offset, rect.centery + dy*3)
                
                pygame.draw.circle(self.screen, COLORS["BLACK"], eye1_pos, eye_radius)
                pygame.draw.circle(self.screen, COLORS["BLACK"], eye2_pos, eye_radius)


        # Draw Food (Circle)
        fx, fy = self.food
        food_center = (fx * SNAKE_CELL_SIZE + SNAKE_CELL_SIZE // 2, fy * SNAKE_CELL_SIZE + SNAKE_CELL_SIZE // 2)
        pygame.draw.circle(self.screen, COLORS["HIGHLIGHT"], food_center, SNAKE_CELL_SIZE // 2 - 2)

        # Draw Powerup
        if self.powerup:
            px, py = self.powerup['pos']
            p_rect = pygame.Rect(px * SNAKE_CELL_SIZE, py * SNAKE_CELL_SIZE,
                                 SNAKE_CELL_SIZE, SNAKE_CELL_SIZE)
            
            p_color = COLORS["WHITE"]
            if self.powerup['type'] == 'SPEED': p_color = COLORS["DANGER"]
            elif self.powerup['type'] == 'SLOW': p_color = COLORS["PADDLE"]
            elif self.powerup['type'] == 'BONUS': p_color = COLORS["WARNING"]
            elif self.powerup['type'] == 'CUT': p_color = (100, 100, 100)
            
            # Star shape or just a smaller circle with ring
            pygame.draw.circle(self.screen, p_color, p_rect.center, SNAKE_CELL_SIZE // 2 - 2)
            pygame.draw.circle(self.screen, COLORS["WHITE"], p_rect.center, SNAKE_CELL_SIZE // 2 - 2, 1)

        # Draw Score
        score_surf = self.font.render(f"Score: {self.score}", True, COLORS["TEXT"])
        self.screen.blit(score_surf, (10, 10))

        if self.game_over:
            self.draw_game_over_overlay(f"Score: {self.score}")

    def _draw_game_over(self):
        # Deprecated, using BaseGame.draw_game_over_overlay
        pass