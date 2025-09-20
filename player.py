import pygame
import os
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        # Load animation frames from assets
        frame_files = [f'g{i}.jpeg' for i in range(1, 6)]
        self.frames = []
        for fname in frame_files:
            path = os.path.join('assets', fname)
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (130, 130))
            img.set_colorkey((255, 255, 255))
            self.frames.append(img)
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=pos)
        self.speed = 5  # Increased speed for faster movement
        self.animation_index = 0
        self.animation_timer = 0
        self.hiding = False
        self.hidden_spot = None

    def handle_input(self, dt, keys, hide_spots=None, hide_allowed=True):
        if self.hiding:
            return
        dx = dy = 0
        moving = False
        if keys[pygame.K_LEFT]:
            dx -= self.speed * dt
            moving = True
        if keys[pygame.K_RIGHT]:
            dx += self.speed * dt
            moving = True
        if keys[pygame.K_UP]:
            dy -= self.speed * dt
            moving = True
        if keys[pygame.K_DOWN]:
            dy += self.speed * dt
            moving = True
        self.rect.x += dx
        self.rect.y += dy
        # Hide when near spot + enter key
        if hide_allowed and keys[pygame.K_RETURN] and hide_spots:
            for spot in hide_spots:
                if self.rect.colliderect(spot.rect):
                    self.hiding = True
                    self.hidden_spot = spot
                    self.rect.center = spot.rect.center
                    break
        self.update_animation(dt, moving)

    def unhide(self):
        self.hiding = False
        self.hidden_spot = None

    def update_animation(self, dt, moving):
        if not moving:
            self.animation_index = 0
            self.image = self.frames[0]
            return
        self.animation_timer += dt
        if self.animation_timer > 0.12:
            self.animation_timer = 0
            self.animation_index = (self.animation_index + 1) % len(self.frames)
            self.image = self.frames[self.animation_index]

    def draw(self, surface):
        if not self.hiding:
            surface.blit(self.image, self.rect)
