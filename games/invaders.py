import pygame
import random
from settings import *
from games.base_game import BaseGame

class InvadersGame(BaseGame):
    def __init__(self, screen, return_to_menu_callback, highscore_manager=None, sound_manager=None, game_name="Invaders"):
        super().__init__(screen, create_game_callback=None, game_over_callback=None, highscore_manager=highscore_manager, sound_manager=sound_manager, game_name=game_name)
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
        self.powerups = [] # List of {'rect': Rect, 'type': str}
        
        self.level = 1
        self.score = 0
        self.lives = 3
        
        # Player attributes (can be modified by powerups)
        self.shoot_cooldown = 400
        self.bullet_count = 1 # Single shot
        self.shield_active = False
        self.shield_timer = 0
        
        self._start_level()
        
        self.game_over = False
        self.won = False
        self.last_shot = 0
        self.last_enemy_shot = 0

    def _start_level(self):
        self.enemies = self._create_enemies()
        self.enemy_direction = 1
        self.enemy_move_down = False
        self.enemy_speed = INVADERS_ENEMY_SPEED + (self.level - 1) * 0.5
        self.enemy_shoot_interval = max(300, 1000 - (self.level - 1) * 100)
        self.bullets = []
        self.enemy_bullets = []
        self.powerups = []

    def _create_enemies(self):
        enemies = []
        rows = 4 + (self.level // 3) # Add rows every 3 levels
        if rows > 6: rows = 6
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
            elif event.key == pygame.K_SPACE:
                self._shoot()

    def update(self):
        if self.game_over:
            return

        current_time = pygame.time.get_ticks()

        # Check if Level Cleared
        if not self.enemies:
            self.level += 1
            self.play_sound("score") # Level up sound
            self._start_level()
            # Brief pause or overlay could be added here
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
            e.x += self.enemy_speed * self.enemy_direction
            if e.right >= SCREEN_WIDTH or e.left <= 0:
                move_down = True
        
        if move_down:
            self.enemy_direction *= -1
            for e in self.enemies:
                e.y += INVADERS_DROP_SPEED
                if e.bottom >= self.player_rect.top:
                    self.game_over = True # Enemies reached player level
                    self.check_and_save_highscore(self.score)

        # Bullet Collisions (Player hitting Enemies)
        for b in self.bullets[:]:
            hit = False
            for e in self.enemies[:]:
                if b.colliderect(e):
                    self.enemies.remove(e)
                    self.bullets.remove(b)
                    self.score += 100
                    self.play_sound("explosion")
                    
                    # Chance to drop powerup
                    if random.random() < 0.1: # 10% chance
                        self._spawn_powerup(e.centerx, e.centery)
                        
                    hit = True
                    break
            if hit: continue

        # Enemy Shooting
        if current_time - self.last_enemy_shot > self.enemy_shoot_interval and self.enemies:
            # Scale firing rate with number of enemies (fewer enemies = faster shooting to keep pressure)
            # Or simpler: just random enemies shoot
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
                if not self.shield_active:
                    self.lives -= 1
                    self.play_sound("explosion")
                    if self.lives <= 0:
                        self.game_over = True
                        self.play_sound("gameover")
                        self.check_and_save_highscore(self.score)
                self.enemy_bullets.remove(b)

        # Update Powerups
        for p in self.powerups[:]:
            p['rect'].y += 3
            if p['rect'].top > SCREEN_HEIGHT:
                self.powerups.remove(p)
            elif p['rect'].colliderect(self.player_rect):
                self._apply_powerup(p['type'])
                self.powerups.remove(p)
                self.play_sound("select")

        # Update Shield
        if self.shield_active and current_time - self.shield_timer > 5000: # 5 seconds
            self.shield_active = False

    def _spawn_powerup(self, x, y):
        p_type = random.choice(['SHIELD', 'TRIPLE', 'LIFE'])
        rect = pygame.Rect(x - 10, y - 10, 20, 20)
        self.powerups.append({'rect': rect, 'type': p_type})

    def _apply_powerup(self, p_type):
        if p_type == 'SHIELD':
            self.shield_active = True
            self.shield_timer = pygame.time.get_ticks()
        elif p_type == 'TRIPLE':
            self.bullet_count = 3
            # Effect lasts until game over or reset? Let's make it permanent for the life?
            # Or maybe temporary. Let's make it last 10 seconds.
            # Simplified: Permanent until death or just accumulates?
            # Let's say temporary handling adds complexity, so let's keep it simple:
            # Triple shot is a permanent upgrade for this life.
            pass
        elif p_type == 'LIFE':
            self.lives += 1

    def _shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_cooldown:
            if self.bullet_count == 1:
                bullet = pygame.Rect(self.player_rect.centerx - 2, self.player_rect.top, 4, 10)
                self.bullets.append(bullet)
            else: # Triple shot
                for offset in [-15, 0, 15]:
                    bullet = pygame.Rect(self.player_rect.centerx - 2 + offset, self.player_rect.top, 4, 10)
                    self.bullets.append(bullet)
            
            self.play_sound("shoot")
            self.last_shot = current_time

    def draw(self):
        self.screen.fill(COLORS["BACKGROUND"])

        # Draw Player
        color = COLORS["PLAYER"]
        if self.shield_active:
            color = COLORS["HIGHLIGHT"] # Shield color
        
        pygame.draw.polygon(self.screen, color, [
            (self.player_rect.centerx, self.player_rect.top),
            (self.player_rect.left, self.player_rect.bottom),
            (self.player_rect.right, self.player_rect.bottom)
        ])
        
        if self.shield_active:
            pygame.draw.circle(self.screen, (0, 100, 255), self.player_rect.center, 30, 2)

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

        # Draw Powerups
        for p in self.powerups:
            color = COLORS["WHITE"]
            txt = "?"
            if p['type'] == 'SHIELD': 
                color = COLORS["HIGHLIGHT"]
                txt = "S"
            elif p['type'] == 'TRIPLE': 
                color = COLORS["WARNING"]
                txt = "3"
            elif p['type'] == 'LIFE': 
                color = COLORS["SUCCESS"]
                txt = "+"
            
            pygame.draw.rect(self.screen, color, p['rect'])
            # Simple text char
            txt_surf = self.font.render(txt, True, COLORS["BLACK"])
            self.screen.blit(txt_surf, (p['rect'].x + 5, p['rect'].y))

        # Draw HUD
        score_surf = self.font.render(f"Score: {self.score}  Lives: {self.lives}  Level: {self.level}", True, COLORS["TEXT"])
        self.screen.blit(score_surf, (10, 10))

        if self.game_over:
            self.draw_game_over_overlay(f"GAME OVER - Lvl {self.level}")
