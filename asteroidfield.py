import pygame
import random
from asteroid import Asteroid
from constants import *


class AsteroidField(pygame.sprite.Sprite):
    edges = [
        [
            pygame.Vector2(1, 0),
            lambda y: pygame.Vector2(-ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT),
        ],
        [
            pygame.Vector2(-1, 0),
            lambda y: pygame.Vector2(
                SCREEN_WIDTH + ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT
            ),
        ],
        [
            pygame.Vector2(0, 1),
            lambda x: pygame.Vector2(x * SCREEN_WIDTH, -ASTEROID_MAX_RADIUS),
        ],
        [
            pygame.Vector2(0, -1),
            lambda x: pygame.Vector2(
                x * SCREEN_WIDTH, SCREEN_HEIGHT + ASTEROID_MAX_RADIUS
            ),
        ],
    ]

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.spawn_timer = 0.0
        self.base_speed = 40  # Minimum speed
        self.max_speed = 100  # Maximum speed

    def spawn(self, radius, position, velocity, speed_multiplier=1.0):
        asteroid = Asteroid(position.x, position.y, radius)
        asteroid.velocity = velocity * speed_multiplier

    def update(self, dt, level):
        # Calculate spawn rate based on level (decreases by 10% per level, minimum 0.2 seconds)
        current_spawn_rate = max(ASTEROID_SPAWN_RATE * (0.9 ** (level - 1)), 0.2)
        
        self.spawn_timer += dt
        if self.spawn_timer > current_spawn_rate:
            self.spawn_timer = 0

            # spawn a new asteroid at a random edge
            edge = random.choice(self.edges)
            
            # Adjust base speed range based on level (more gradual increase)
            level_speed_multiplier = 1.1 ** (level - 1)  # 10% increase per level instead of 20%
            adjusted_base_speed = self.base_speed * level_speed_multiplier
            adjusted_max_speed = self.max_speed * level_speed_multiplier
            
            # Cap the maximum speed to prevent asteroids from becoming too fast
            adjusted_max_speed = min(adjusted_max_speed, 200)  # Cap at 200 units per second
            
            speed = random.randint(int(adjusted_base_speed), int(adjusted_max_speed))
            velocity = edge[0] * speed
            velocity = velocity.rotate(random.randint(-30, 30))
            position = edge[1](random.uniform(0, 1))
            kind = random.randint(1, ASTEROID_KINDS)
            self.spawn(ASTEROID_MIN_RADIUS * kind, position, velocity, 1.0)  # Remove the second speed multiplier