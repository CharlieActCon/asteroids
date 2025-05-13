import pygame
from circleshape import CircleShape
import random
import math
from constants import ASTEROID_MIN_RADIUS

class Explosion(CircleShape):
    def __init__(self, position, radius):
        super().__init__(position.x, position.y, radius)
        self.lifetime = 0.3  # seconds
        self.time_alive = 0
        self.lines = self._generate_lines()
        
    def _generate_lines(self):
        lines = []
        num_lines = random.randint(8, 12)
        for _ in range(num_lines):
            angle = random.uniform(0, 2 * math.pi)
            length = random.uniform(self.radius * 0.5, self.radius * 1.5)
            end_point = pygame.Vector2(
                math.cos(angle) * length,
                math.sin(angle) * length
            )
            lines.append(end_point)
        return lines
    
    def draw(self, screen):
        alpha = int(255 * (1 - self.time_alive / self.lifetime))
        if alpha <= 0:
            self.kill()
            return
            
        for line in self.lines:
            end_pos = self.position + line
            pygame.draw.line(screen, (255, 255, 255, alpha), self.position, end_pos, 2)
    
    def update(self, dt):
        self.time_alive += dt
        if self.time_alive >= self.lifetime:
            self.kill()
            
    def collision(self, other):
        return False  # Explosions don't collide with anything

class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.radius = radius
        self.vertices = self._generate_vertices()
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-30, 30)  # degrees per second

    def _generate_vertices(self):
        num_vertices = random.randint(8, 12)  # Random number of vertices
        vertices = []
        for i in range(num_vertices):
            # Generate random radius variation
            radius_variation = random.uniform(0.7, 1.3)
            # Calculate angle for this vertex
            angle = (i / num_vertices) * 2 * math.pi
            # Calculate vertex position with random radius variation
            x = math.cos(angle) * self.radius * radius_variation
            y = math.sin(angle) * self.radius * radius_variation
            vertices.append(pygame.Vector2(x, y))
        return vertices

    def draw(self, screen):
        # Rotate and translate vertices
        rotated_vertices = []
        for vertex in self.vertices:
            # Rotate vertex
            rotated = vertex.rotate(self.rotation)
            # Translate to position
            rotated_vertices.append(self.position + rotated)
        
        # Draw the polygon
        pygame.draw.polygon(screen, "white", rotated_vertices, 2)

    def update(self, dt):
        self.position += (self.velocity * dt)
        self.rotation += self.rotation_speed * dt

    def split(self):
        # Create explosion effect
        explosion = Explosion(self.position, self.radius)
        if hasattr(self, 'containers'):
            for container in self.containers:
                container.add(explosion)
                
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