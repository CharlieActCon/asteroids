import pygame
import math
from circleshape import CircleShape
from constants import SHOT_RADIUS, SCREEN_WIDTH, SCREEN_HEIGHT

class Shot(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, is_forcefield=False, is_tracking=False):
        super().__init__()
        self.image = pygame.Surface((8, 4), pygame.SRCALPHA)  # Changed size for rocket shape
        self.rect = self.image.get_rect(center=(x, y))
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, -1).rotate(-angle) * 500
        self.is_forcefield = is_forcefield
        self.is_tracking = is_tracking
        self.active = True
        self.forcefield_angle = angle
        self.forcefield_radius = 50
        self.radius = SHOT_RADIUS  # For collision detection
        self.turn_speed = 180  # degrees per second for tracking shots
        self.angle = angle  # Store angle for drawing

    def update(self, dt, asteroids=None):
        if not self.active:
            return

        if self.is_forcefield:
            # Forcefield shots are updated by the player
            return

        if self.is_tracking and asteroids:
            # Find nearest asteroid
            nearest_asteroid = None
            min_distance = float('inf')
            for asteroid in asteroids:
                distance = self.position.distance_to(asteroid.position)
                if distance < min_distance:
                    min_distance = distance
                    nearest_asteroid = asteroid

            if nearest_asteroid:
                # Calculate direction to nearest asteroid
                direction = nearest_asteroid.position - self.position
                target_angle = math.degrees(math.atan2(-direction.y, direction.x))
                
                # Calculate current angle
                current_angle = math.degrees(math.atan2(-self.velocity.y, self.velocity.x))
                
                # Calculate angle difference
                angle_diff = (target_angle - current_angle) % 360
                if angle_diff > 180:
                    angle_diff -= 360
                
                # Limit turn rate
                max_turn = self.turn_speed * dt
                if abs(angle_diff) > max_turn:
                    angle_diff = max_turn if angle_diff > 0 else -max_turn
                
                # Update velocity direction
                self.velocity = self.velocity.rotate(angle_diff)
                self.angle = current_angle + angle_diff  # Update angle for drawing

        # Update position
        self.position += self.velocity * dt
        self.rect.center = self.position

        # Remove if off screen
        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
            self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT):
            self.kill()

    def update_position(self, player_position, radius, base_angle):
        if not self.active:
            return

        # Calculate new position based on forcefield angle and radius
        angle_rad = math.radians(self.forcefield_angle + base_angle)
        self.position.x = player_position.x + math.cos(angle_rad) * radius
        self.position.y = player_position.y + math.sin(angle_rad) * radius
        self.rect.center = self.position

    def draw(self, screen):
        if self.active:
            if self.is_tracking:
                # Draw rocket shape
                forward = pygame.math.Vector2(0, -1).rotate(-self.angle)
                right = pygame.math.Vector2(1, 0).rotate(-self.angle)
                
                # Calculate rocket points
                tip = self.position + forward * 4
                left_wing = self.position - forward * 2 - right * 2
                right_wing = self.position - forward * 2 + right * 2
                back = self.position - forward * 4
                
                # Draw rocket body
                pygame.draw.polygon(screen, "white", [tip, left_wing, back, right_wing], 2)
                
                # Draw rocket trail
                trail_start = back
                trail_end = back - forward * 3
                pygame.draw.line(screen, "white", trail_start, trail_end, 1)
            else:
                # Draw regular shot as circle
                pygame.draw.circle(screen, "white", self.position, self.radius, 2)