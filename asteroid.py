import pygame
from circleshape import CircleShape
import random
from constants import ASTEROID_MIN_RADIUS



class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.radius = radius

    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.position, self.radius, 2)

    def update(self, dt):
        self.position += (self.velocity * dt)

    def split(self):
        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS:
            return
        random_angle = random.uniform(20, 50)
        new_direction1 = self.velocity.rotate(random_angle)
        new_direction2 = self.velocity.rotate(-random_angle)
        smaller_asteroids = self.radius - ASTEROID_MIN_RADIUS
        new_asteroid1 = Asteroid(self.position.x, self.position.y, smaller_asteroids)
        new_asteroid2 = Asteroid(self.position.x, self.position.y, smaller_asteroids)
        new_asteroid1.velocity = new_direction1 * 1.2
        new_asteroid2.velocity = new_direction2 * 1.2