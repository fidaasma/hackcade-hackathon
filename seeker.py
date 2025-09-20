import pygame
import os
from settings import *

class Seeker(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        # Load animation frames from assets and remove white bg
        frame_files = [f'd{i}.jpeg' for i in range(1, 5)]
        self.frames = []
        for fname in frame_files:
            path = os.path.join('assets', fname)
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (180, 180))
            # Remove all nearly-white/light-gray pixels (make them fully transparent)
            w, h = img.get_size()
            new_img = pygame.Surface((w, h), pygame.SRCALPHA)
            for x in range(w):
                for y in range(h):
                    color = img.get_at((x, y))
                    if color.r > 200 and color.g > 200 and color.b > 200:
                        new_img.set_at((x, y), (255, 255, 255, 0))
                    else:
                        new_img.set_at((x, y), color)
            self.frames.append(new_img)
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=pos)
        self.speed = SEEKER_SPEED
        self.animation_index = 0
        self.animation_timer = 0

    def chase(self, player, dt):
        if player.hiding:
            return
        moved = False
        # Move towards player
        if self.rect.x < player.rect.x:
            self.rect.x += self.speed * dt
            moved = True
        elif self.rect.x > player.rect.x:
            self.rect.x -= self.speed * dt
            moved = True
        if self.rect.y < player.rect.y:
            self.rect.y += self.speed * dt
            moved = True
        elif self.rect.y > player.rect.y:
            self.rect.y -= self.speed * dt
            moved = True
        self.update_animation(dt, moved)

    def update_animation(self, dt, moving=True):
        if not moving:
            self.animation_index = 0
            self.image = self.frames[0]
            return
        self.animation_timer += dt
        if self.animation_timer > 0.15:
            self.animation_timer = 0
            self.animation_index = (self.animation_index + 1) % len(self.frames)
            self.image = self.frames[self.animation_index]

    def draw(self, surface):
        surface.blit(self.image, self.rect)
