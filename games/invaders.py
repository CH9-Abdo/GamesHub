import pygame
import random
from settings import *
from games.base_game import BaseGame

class InvadersGame(BaseGame):
    def __init__(self, screen, return_to_menu_callback, highscore_manager=None, game_name="Invaders"):
        super().__init__(screen, create_game_callback=None, game_over_callback=None, highscore_manager=highscore_manager, game_name=game_name)
        self.return_to_menu = return_to_menu_callback
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE_HUD)
        self.reset()

    def reset(self):
        self.player_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 20, 
            SCREEN_HEIGHT - 50, 
            40, 20
        )
        self.bullets = []
        self.enemy_bullets = []
        self.enemies = self._create_enemies()
        self.enemy_direction = 1
        self.enemy_move_down = False
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.won = False
        self.last_shot = 0
        self.last_enemy_shot = 0

    def _create_enemies(self):
        enemies = []
        rows = 4
        cols = 8
        width = 40
        height = 30
        padding = 15
        
        start_x = (SCREEN_WIDTH - (cols * (width + padding))) // 2
        start_y = 50

        for r in range(rows):
            for c in range(cols):
                rect = pygame.Rect(
                    start_x + c * (width + padding),
                    start_y + r * (height + padding),
                    width, height
                )
                enemies.append(rect)
        return enemies

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
            elif event.key == pygame.K_SPACE:
                self._shoot()

    def update(self):
        if self.game_over or self.won:
            return

        # Player Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player_rect.x -= INVADERS_PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.player_rect.x += INVADERS_PLAYER_SPEED
        
        self.player_rect.clamp_ip(self.screen.get_rect())

        # Update Bullets
        for b in self.bullets[:]:
            b.y -= INVADERS_BULLET_SPEED
            if b.bottom < 0:
                self.bullets.remove(b)

        # Update Enemies
        move_down = False
        for e in self.enemies:
            e.x += INVADERS_ENEMY_SPEED * self.enemy_direction
            if e.right >= SCREEN_WIDTH or e.left <= 0:
                move_down = True
        
        if move_down:
            self.enemy_direction *= -1
            for e in self.enemies:
                e.y += INVADERS_DROP_SPEED
                if e.bottom >= self.player_rect.top:
                    self.game_over = True # Enemies reached player level

        # Bullet Collisions
        for b in self.bullets[:]:
            hit = False
            for e in self.enemies[:]:
                if b.colliderect(e):
                    self.enemies.remove(e)
                    self.bullets.remove(b)
                    self.score += 100
                    hit = True
                    break
            if hit: continue

        # Enemy Shooting
        current_time = pygame.time.get_ticks()
        if current_time - self.last_enemy_shot > 1000 and self.enemies:
            shooter = random.choice(self.enemies)
            bullet = pygame.Rect(shooter.centerx - 2, shooter.bottom, 4, 10)
            self.enemy_bullets.append(bullet)
            self.last_enemy_shot = current_time

        # Update Enemy Bullets
        for b in self.enemy_bullets[:]:
            b.y += 5
            if b.top > SCREEN_HEIGHT:
                self.enemy_bullets.remove(b)
            elif b.colliderect(self.player_rect):
                self.lives -= 1
                self.enemy_bullets.remove(b)
                if self.lives <= 0:
                    self.game_over = True

        if not self.enemies:
            self.won = True

    def _shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > 400: # Cooldown
            bullet = pygame.Rect(self.player_rect.centerx - 2, self.player_rect.top, 4, 10)
            self.bullets.append(bullet)
            self.last_shot = current_time

    def draw(self):
        self.screen.fill(COLORS["BACKGROUND"])

        # Draw Player
        pygame.draw.polygon(self.screen, COLORS["PLAYER"], [
            (self.player_rect.centerx, self.player_rect.top),
            (self.player_rect.left, self.player_rect.bottom),
            (self.player_rect.right, self.player_rect.bottom)
        ])

        # Draw Enemies
        for e in self.enemies:
            pygame.draw.rect(self.screen, COLORS["ENEMY"], e)
            # Add some details (eyes)
            pygame.draw.rect(self.screen, COLORS["BACKGROUND"], (e.x + 8, e.y + 8, 5, 5))
            pygame.draw.rect(self.screen, COLORS["BACKGROUND"], (e.right - 13, e.y + 8, 5, 5))

        # Draw Bullets
        for b in self.bullets:
            pygame.draw.rect(self.screen, COLORS["ACCENT"], b)
        
        for b in self.enemy_bullets:
            pygame.draw.rect(self.screen, COLORS["DANGER"], b)

        # Draw HUD
        score_surf = self.font.render(f"Score: {self.score}  Lives: {self.lives}", True, COLORS["TEXT"])
        self.screen.blit(score_surf, (10, 10))

        if self.game_over:
            self.draw_game_over_overlay("GAME OVER")
        elif self.won:
            self.draw_game_over_overlay("YOU WIN!")
