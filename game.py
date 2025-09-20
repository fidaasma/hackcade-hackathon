import pygame, sys
import os
import random
from settings import *
from player import Player
from seeker import Seeker

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Hide & Seek Game")
        self.clock = pygame.time.Clock()
        # Background
        bg_path = os.path.join('assets', 'bg.jpeg')
        self.bg = pygame.image.load(bg_path).convert()
        self.bg = pygame.transform.scale(self.bg, (WIDTH, HEIGHT))
        self.bg_zoom = 1.0  
        # Cave
        cave_path = os.path.join('assets', 'cave.jpeg')
        cave_img_raw = pygame.image.load(cave_path).convert_alpha()
        cave_img_raw = pygame.transform.scale(cave_img_raw, (120, 120))
        # Remove all nearly-white/light-gray pixels from cave (make them fully transparent)
        w, h = cave_img_raw.get_size()
        cave_img = pygame.Surface((w, h), pygame.SRCALPHA)
        for x in range(w):
            for y in range(h):
                color = cave_img_raw.get_at((x, y))
                if color.r > 200 and color.g > 200 and color.b > 200:
                    cave_img.set_at((x, y), (255, 255, 255, 0))
                else:
                    cave_img.set_at((x, y), color)
        self.cave_img = cave_img
        self.cave_rect = self.cave_img.get_rect(center=(WIDTH//2, HEIGHT-120))
        # Sprites
        self.player = Player((100, 300))
        self.seeker = Seeker((50, HEIGHT - 100))
        # Timer
        self.hiding_time = 5  # Player can hide for 5 seconds
        self.timer = self.hiding_time
        self.hide_allowed = True
        self.seeker_active = False  # Seeker starts inactive
        self.player_hidden = False
        # Game state
        self.game_over = False

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000
            self.handle_events()
            if not self.game_over:
                self.update(dt)
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if self.game_over and event.key == pygame.K_r:
                    self.restart()

    def update(self, dt):
        keys = pygame.key.get_pressed()
        # Simple player movement (allow movement even when hidden)
        if keys[pygame.K_LEFT]:
            self.player.rect.x -= self.player.speed
        if keys[pygame.K_RIGHT]:
            self.player.rect.x += self.player.speed
        if keys[pygame.K_UP]:
            self.player.rect.y -= self.player.speed
        if keys[pygame.K_DOWN]:
            self.player.rect.y += self.player.speed
        # Hide behind cave if enter is pressed during hiding time and near cave
        if self.hide_allowed and keys[pygame.K_RETURN]:
            if self.player.rect.colliderect(self.cave_rect):
                self.player_hidden = True
                self.player.rect.center = self.cave_rect.center
        # Unhide if player is hidden and presses Enter again while in cave
        if self.player_hidden and keys[pygame.K_RETURN]:
            if self.player.rect.colliderect(self.cave_rect):
                self.player_hidden = False
        # Countdown timer for hiding
        if self.timer > 0:
            self.timer -= dt
            self.hide_allowed = True
            self.seeker_active = False
        else:
            self.hide_allowed = False
            self.seeker_active = True
        # Seeker logic
        if self.seeker_active:
            if self.player_hidden:
                # Seeker moves randomly while searching
                if not hasattr(self, 'seeker_rand_timer'):
                    self.seeker_rand_timer = 0
                self.seeker_rand_timer += dt
                if self.seeker_rand_timer > 0.5:
                    self.seeker_rand_timer = 0
                    self.seeker_rand_dx = random.choice([-2, 0, 2])
                    self.seeker_rand_dy = random.choice([-2, 0, 2])
                self.seeker.rect.x += getattr(self, 'seeker_rand_dx', 0)
                self.seeker.rect.y += getattr(self, 'seeker_rand_dy', 0)
                # Keep seeker within screen bounds
                self.seeker.rect.x = max(0, min(WIDTH - self.seeker.rect.width, self.seeker.rect.x))
                self.seeker.rect.y = max(0, min(HEIGHT - self.seeker.rect.height, self.seeker.rect.y))
            else:
                # Seeker chases player
                if self.player.rect.x > self.seeker.rect.x:
                    self.seeker.rect.x += 2
                if self.player.rect.x < self.seeker.rect.x:
                    self.seeker.rect.x -= 2
                if self.player.rect.y > self.seeker.rect.y:
                    self.seeker.rect.y += 2
                if self.player.rect.y < self.seeker.rect.y:
                    self.seeker.rect.y -= 2
        # Collision (never when player is hidden)
        if not self.player_hidden and self.seeker.rect.colliderect(self.player.rect):
            self.game_over = True
        # Zoom background when moving
        if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]:
            self.bg_zoom = min(1.1, self.bg_zoom + 0.01)
        else:
            self.bg_zoom = max(1.0, self.bg_zoom - 0.01)

    def restart(self):
        self.player.rect.topleft = (100,300)
        self.seeker.rect.topleft = (50, HEIGHT - 100)
        self.timer = self.hiding_time
        self.hide_allowed = True
        self.seeker_active = False
        self.game_over = False

    def draw(self):
        # Background zoom
        zoomed_bg = pygame.transform.scale(self.bg, (int(WIDTH*self.bg_zoom), int(HEIGHT*self.bg_zoom)))
        rect = zoomed_bg.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.screen.blit(zoomed_bg, rect)
        # Dim the background
        dim_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim_surface.fill((0, 0, 0, 120))  # 120/255 alpha for dimming
        self.screen.blit(dim_surface, (0, 0))
        # Draw sprites (player first)
        self.screen.blit(self.player.image, self.player.rect)
        self.screen.blit(self.seeker.image, self.seeker.rect)
        # Draw cave after player so it covers the player if hiding
        self.screen.blit(self.cave_img, self.cave_rect)
        # Draw timer or game over
        font = pygame.font.SysFont(None, 36)
        if self.game_over:
            over_text = font.render("Game Over! Press R to Restart", True, (255, 0, 0))
            self.screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2 - over_text.get_height()//2))
        else:
            if self.timer > 0:
                text = font.render(f"Hiding Time: {int(self.timer)+1}", True, (255,255,0))
                self.screen.blit(text, (10,10))
                msg = font.render("Run and hide! You have 5 seconds!", True, (0,255,255))
                self.screen.blit(msg, (WIDTH//2 - msg.get_width()//2, 50))
            else:
                text = font.render(f"Seeker Active!", True, (255,255,255))
                self.screen.blit(text, (10,10))
        pygame.display.flip()
