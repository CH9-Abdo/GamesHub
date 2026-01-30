import pygame
import math
import random
from settings import *
from games.base_game import BaseGame

class AsteroidsGame(BaseGame):
    """Classic Asteroids: destroy rocks, avoid collisions. Arrow keys + Space."""
    def __init__(self, screen, return_to_menu_callback, highscore_manager=None, sound_manager=None, game_name="Asteroids"):
        super().__init__(screen, create_game_callback=None, game_over_callback=None, highscore_manager=highscore_manager, sound_manager=sound_manager, game_name=game_name)
        self.return_to_menu = return_to_menu_callback
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE_HUD)
        self.reset()

    def reset(self):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        self.ship_x = cx
        self.ship_y = cy
        self.ship_vx = 0
        self.ship_vy = 0
        self.ship_angle = -math.pi / 2  # up
        self.bullets = []
        self.asteroids = []
        for _ in range(ASTEROIDS_ASTEROID_COUNT):
            self._spawn_asteroid(size=3)
        self.score = 0
        self.game_over = False
        self.lives = 3
        self.invincible_until = pygame.time.get_ticks() + 2000

    def _spawn_asteroid(self, size=3, x=None, y=None):
        if x is None:
            x = random.randint(0, SCREEN_WIDTH - 1)
        if y is None:
            y = random.randint(0, SCREEN_HEIGHT - 1)
        angle = random.random() * 2 * math.pi
        speed = ASTEROIDS_ASTEROID_SPEED * (0.5 + random.random())
        self.asteroids.append({
            'x': x, 'y': y, 'vx': math.cos(angle) * speed, 'vy': math.sin(angle) * speed,
            'size': size, 'points': 8, 'angles': [random.random() * 2 * math.pi for _ in range(8)]
        })

    def _ship_rect(self):
        s = ASTEROIDS_SHIP_SIZE
        return pygame.Rect(self.ship_x - s, self.ship_y - s, s * 2, s * 2)

    def _wrap(self, x, y):
        return x % SCREEN_WIDTH, y % SCREEN_HEIGHT

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
            if event.key == pygame.K_SPACE:
                bx = self.ship_x + math.cos(self.ship_angle) * (ASTEROIDS_SHIP_SIZE + 5)
                by = self.ship_y + math.sin(self.ship_angle) * (ASTEROIDS_SHIP_SIZE + 5)
                self.bullets.append({
                    'x': bx, 'y': by, 'vx': math.cos(self.ship_angle) * ASTEROIDS_BULLET_SPEED,
                    'vy': math.sin(self.ship_angle) * ASTEROIDS_BULLET_SPEED, 'life': ASTEROIDS_BULLET_LIFETIME
                })
                self.play_sound("shoot")

    def update(self):
        if self.game_over:
            return
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.ship_angle -= math.radians(ASTEROIDS_ROTATION_SPEED)
        if keys[pygame.K_RIGHT]:
            self.ship_angle += math.radians(ASTEROIDS_ROTATION_SPEED)
        if keys[pygame.K_UP]:
            self.ship_vx += math.cos(self.ship_angle) * ASTEROIDS_SPEED * 0.15
            self.ship_vy += math.sin(self.ship_angle) * ASTEROIDS_SPEED * 0.15
        self.ship_vx *= ASTEROIDS_FRICTION
        self.ship_vy *= ASTEROIDS_FRICTION
        self.ship_x += self.ship_vx
        self.ship_y += self.ship_vy
        self.ship_x, self.ship_y = self._wrap(self.ship_x, self.ship_y)

        for b in self.bullets[:]:
            b['x'] += b['vx']
            b['y'] += b['vy']
            b['x'], b['y'] = self._wrap(b['x'], b['y'])
            b['life'] -= 1
            if b['life'] <= 0:
                self.bullets.remove(b)

        for a in self.asteroids[:]:
            a['x'] += a['vx']
            a['y'] += a['vy']
            a['x'], a['y'] = self._wrap(a['x'], a['y'])

        # Bullet vs asteroid
        for b in self.bullets[:]:
            for a in self.asteroids[:]:
                dx = b['x'] - a['x']
                dy = b['y'] - a['y']
                if dx * dx + dy * dy < (20 + a['size'] * 15) ** 2:
                    self.score += ASTEROIDS_ASTEROID_POINTS * a['size']
                    self.play_sound("explosion")
                    if b in self.bullets:
                        self.bullets.remove(b)
                    self.asteroids.remove(a)
                    if a['size'] > 1:
                        for _ in range(2):
                            self._spawn_asteroid(size=a['size'] - 1, x=a['x'], y=a['y'])
                    break

        if not self.asteroids:
            for _ in range(ASTEROIDS_ASTEROID_COUNT):
                self._spawn_asteroid(size=3)

        now = pygame.time.get_ticks()
        if now >= self.invincible_until:
            ship_r = self._ship_rect()
            for a in self.asteroids:
                dx = self.ship_x - a['x']
                dy = self.ship_y - a['y']
                if abs(dx) > SCREEN_WIDTH // 2:
                    dx = dx - SCREEN_WIDTH if dx > 0 else dx + SCREEN_WIDTH
                if abs(dy) > SCREEN_HEIGHT // 2:
                    dy = dy - SCREEN_HEIGHT if dy > 0 else dy + SCREEN_HEIGHT
                if dx * dx + dy * dy < (ASTEROIDS_SHIP_SIZE + 10 + a['size'] * 12) ** 2:
                    self.lives -= 1
                    self.invincible_until = now + 2000
                    self.ship_x, self.ship_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
                    self.ship_vx = self.ship_vy = 0
                    if self.lives <= 0:
                        self.game_over = True
                        self.check_and_save_highscore(self.score)
                        self.play_sound("gameover")
                    break

    def draw(self):
        self.screen.fill(COLORS["BACKGROUND"])
        for b in self.bullets:
            pygame.draw.circle(self.screen, COLORS["BALL"], (int(b['x']), int(b['y'])), 3)
        for a in self.asteroids:
            pts = []
            for i in range(a['points']):
                r = 8 + a['size'] * 8
                ang = a['angles'][i] + pygame.time.get_ticks() * 0.001
                pts.append((a['x'] + math.cos(ang) * r, a['y'] + math.sin(ang) * r))
            if len(pts) >= 3:
                pygame.draw.polygon(self.screen, COLORS["GRID"], pts, 2)
        cx, cy = self.ship_x, self.ship_y
        angle = self.ship_angle
        tip = (cx + math.cos(angle) * ASTEROIDS_SHIP_SIZE, cy + math.sin(angle) * ASTEROIDS_SHIP_SIZE)
        left = (cx + math.cos(angle + 2.5) * ASTEROIDS_SHIP_SIZE, cy + math.sin(angle + 2.5) * ASTEROIDS_SHIP_SIZE)
        right = (cx + math.cos(angle - 2.5) * ASTEROIDS_SHIP_SIZE, cy + math.sin(angle - 2.5) * ASTEROIDS_SHIP_SIZE)
        pygame.draw.polygon(self.screen, COLORS["PADDLE"], [tip, left, right])
        inv = pygame.time.get_ticks() < self.invincible_until
        if inv and (pygame.time.get_ticks() // 100) % 2 == 0:
            pygame.draw.polygon(self.screen, COLORS["WARNING"], [tip, left, right], 2)
        score_surf = self.font.render(f"Score: {self.score}  Lives: {self.lives}", True, COLORS["TEXT"])
        self.screen.blit(score_surf, (10, 10))
        if self.game_over:
            self.draw_game_over_overlay(f"Score: {self.score}")
