import pygame
from circleshape import CircleShape
from shot import Shot
from constants import PLAYER_RADIUS
from constants import PLAYER_TURN_SPEED
from constants import PLAYER_SPEED
from constants import PLAYER_SHOOT_SPEED
from constants import PLAYER_SHOOT_COOLDOWN
import time
from constants import SCREEN_WIDTH, SCREEN_HEIGHT


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.original_image = self.image
        self.rect = self.image.get_rect(center=(x, y))
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)
        self.angle = 0
        self.rotation_speed = PLAYER_TURN_SPEED
        self.max_speed = PLAYER_SPEED * 2  # Double the base speed
        self.acceleration_magnitude = PLAYER_SPEED * 3  # Triple the base speed for quick acceleration
        self.drag = 0.98  # Reduced drag for better momentum
        self.fire_rate = 0.5  # seconds between shots
        self.last_shot_time = 0
        self.fire_rate_multiplier = 1.0
        self.dual_shot = False
        self.side_shot = False
        self.tracking_shots = False
        self.forcefield = False
        self.forcefield_shots = []
        self.forcefield_radius = 50
        self.forcefield_shot_count = 8
        self.forcefield_angle = 0
        self.forcefield_rotation_speed = 90  # degrees per second
        self.radius = 15  # Half of the triangle's height
        self.shot_counter = 0  # Counter for tracking shots
        self.forcefield_hits = 0  # Track number of hits the forcefield can take
        self.max_forcefield_hits = 2  # Maximum number of hits the forcefield can take
        self.forcefield_hit_cooldown = 0  # Cooldown timer for forcefield hits

    def collision(self, other):
        # Use the radius for collision detection
        return self.position.distance_to(other.position) <= self.radius + other.radius

    def update(self, dt):
        # Handle rotation
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.angle += self.rotation_speed * dt
        if keys[pygame.K_d]:
            self.angle -= self.rotation_speed * dt

        # Handle acceleration
        if keys[pygame.K_w]:
            self.acceleration = pygame.math.Vector2(0, -self.acceleration_magnitude)
            self.acceleration.rotate_ip(-self.angle)
        elif keys[pygame.K_s]:
            self.acceleration = pygame.math.Vector2(0, self.acceleration_magnitude)
            self.acceleration.rotate_ip(-self.angle)
        else:
            self.acceleration = pygame.math.Vector2(0, 0)

        # Update velocity and position
        self.velocity += self.acceleration * dt
        self.velocity *= self.drag
        if self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)
        self.position += self.velocity * dt

        # Update rect position
        self.rect.center = self.position

        # Wrap around screen edges
        if self.rect.left > SCREEN_WIDTH:
            self.rect.right = 0
            self.position.x = self.rect.centerx
        elif self.rect.right < 0:
            self.rect.left = SCREEN_WIDTH
            self.position.x = self.rect.centerx
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.bottom = 0
            self.position.y = self.rect.centery
        elif self.rect.bottom < 0:
            self.rect.top = SCREEN_HEIGHT
            self.position.y = self.rect.centery

        # Update forcefield if active
        if self.forcefield:
            self.forcefield_angle += self.forcefield_rotation_speed * dt
            if self.forcefield_angle >= 360:
                self.forcefield_angle -= 360

            # Create new forcefield shots if needed
            while len(self.forcefield_shots) < self.forcefield_shot_count:
                angle = self.forcefield_angle + (360 / self.forcefield_shot_count) * len(self.forcefield_shots)
                shot = Shot(self.position.x, self.position.y, angle, is_forcefield=True)
                self.forcefield_shots.append(shot)

            # Update forcefield shots
            for shot in self.forcefield_shots[:]:
                if shot.active:
                    shot.update_position(self.position, self.forcefield_radius, self.forcefield_angle)
                else:
                    self.forcefield_shots.remove(shot)

        # Update forcefield hit cooldown
        if self.forcefield_hit_cooldown > 0:
            self.forcefield_hit_cooldown -= dt

    def shoot(self):
        current_time = time.time()
        if current_time - self.last_shot_time < self.fire_rate / self.fire_rate_multiplier:
            return []

        self.last_shot_time = current_time
        shots = []

        # Determine if this shot should be tracking
        is_tracking = False
        if self.tracking_shots:
            self.shot_counter = (self.shot_counter + 1) % 5
            is_tracking = (self.shot_counter == 0)  # Every 5th shot is tracking

        # Forward shot
        shots.append(Shot(self.position.x, self.position.y, self.angle, is_tracking=is_tracking))

        # Backward shot if dual shot is active
        if self.dual_shot:
            shots.append(Shot(self.position.x, self.position.y, self.angle + 180, is_tracking=is_tracking))

        # Side shots if side shot is active
        if self.side_shot:
            shots.append(Shot(self.position.x, self.position.y, self.angle + 90, is_tracking=is_tracking))
            shots.append(Shot(self.position.x, self.position.y, self.angle - 90, is_tracking=is_tracking))

        return shots

    def draw(self, screen):
        # Draw the player triangle
        forward = pygame.math.Vector2(0, -1).rotate(-self.angle)
        right = pygame.math.Vector2(1, 0).rotate(-self.angle)
        
        # Calculate triangle points
        tip = self.position + forward * self.radius
        left = self.position - forward * self.radius - right * self.radius
        right_point = self.position - forward * self.radius + right * self.radius
        
        # Draw the triangle
        pygame.draw.polygon(screen, "white", [tip, left, right_point], 2)

        # Draw forcefield shots if active
        if self.forcefield:
            for shot in self.forcefield_shots:
                if shot.active:
                    shot.draw(screen)

    def upgrade_forcefield(self):
        self.forcefield = True
        self.forcefield_hits = 0
        self.forcefield_shots = []
        # Create initial forcefield shots
        for i in range(self.forcefield_shot_count):
            angle = (360 / self.forcefield_shot_count) * i
            shot = Shot(self.position.x, self.position.y, angle, is_forcefield=True)
            self.forcefield_shots.append(shot)

    def handle_forcefield_collision(self):
        if self.forcefield and self.forcefield_hit_cooldown <= 0:
            self.forcefield_hits += 1
            print(f"Forcefield hit! Hits taken: {self.forcefield_hits}")  # Debug print
            self.forcefield_hit_cooldown = 0.5  # Set cooldown to 0.5 seconds
            
            if self.forcefield_hits >= self.max_forcefield_hits:
                # Forcefield is depleted
                print("Forcefield depleted!")  # Debug print
                self.forcefield = False
                self.forcefield_shots = []
                return False
            elif self.forcefield_hits == 1:
                # After first hit, reduce to half the shots
                print("Forcefield weakened!")  # Debug print
                remaining_shots = []
                for i in range(0, len(self.forcefield_shots), 2):
                    if i < len(self.forcefield_shots):
                        remaining_shots.append(self.forcefield_shots[i])
                self.forcefield_shots = remaining_shots
            return True  # Return True if forcefield is still active
        return self.forcefield  # Return True if forcefield is active but on cooldown

    def reset_forcefield(self):
        """Reset the forcefield to full strength"""
        if self.forcefield:  # Only reset if forcefield is active
            self.forcefield_hits = 0
            self.forcefield_shots = []
            # Create new forcefield shots
            for i in range(self.forcefield_shot_count):
                angle = (360 / self.forcefield_shot_count) * i
                shot = Shot(self.position.x, self.position.y, angle, is_forcefield=True)
                self.forcefield_shots.append(shot)
