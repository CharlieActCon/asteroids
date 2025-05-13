import pygame
import sys
from constants import *
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot

class Game:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.game_over = False
        self.game_over_text = "Game Over!"
        self.text_progress = 0
        self.text_timer = 0
        self.text_speed = 0.1  # seconds per letter
        
        # Initialize fonts with Press Start 2P
        try:
            self.font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 36)  # Main title font
            self.small_font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 16)  # Controls and descriptions
            self.score_font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 24)  # Score and level
        except:
            # Fallback to default font if Press Start 2P is not available
            print("Warning: Press Start 2P font not found, using default font")
            self.font = pygame.font.Font(None, 74)
            self.small_font = pygame.font.Font(None, 36)
            self.score_font = pygame.font.Font(None, 48)
        
        self.level_up = False
        self.upgrade_options = []
        self.rapid_fire_taken = False
        self.super_rapid_fire_taken = False
        self.ultra_rapid_fire_taken = False
        self.dual_shot_taken = False
        self.side_shot_taken = False
        self.tracking_shots_taken = False
        self.mega_rapid_fire_taken = False
        self.forcefield_taken = False
        self.intro_screen = True
        self.intro_updatable = pygame.sprite.Group()
        self.intro_drawable = pygame.sprite.Group()
        self.intro_asteroids = pygame.sprite.Group()
        self.intro_asteroid_field = None
        self.updatable = pygame.sprite.Group()
        self.drawable = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.shots = pygame.sprite.Group()
        self.reset_game()

    def reset_game(self):
        # Clear existing sprites
        for sprite in self.updatable:
            sprite.kill()
        for sprite in self.drawable:
            sprite.kill()
        for sprite in self.intro_updatable:
            sprite.kill()
        for sprite in self.intro_drawable:
            sprite.kill()
        
        # Set up player
        Player.containers = (self.updatable, self.drawable)
        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.updatable.add(self.player)
        self.drawable.add(self.player)

        # Set up asteroids
        Asteroid.containers = (self.asteroids, self.updatable, self.drawable)
        
        # Set up shots
        Shot.containers = (self.shots, self.updatable, self.drawable)
        
        # Create a fresh asteroid field
        AsteroidField.containers = (self.updatable,)
        self.asteroid_field = AsteroidField()

        # Set up intro screen asteroids
        if self.intro_screen:
            Asteroid.containers = (self.intro_asteroids, self.intro_updatable, self.intro_drawable)
            AsteroidField.containers = (self.intro_updatable,)
            self.intro_asteroid_field = AsteroidField()
        
        # Reset game state
        self.game_over = False
        self.text_progress = 0
        self.text_timer = 0
        self.score = 0
        self.level = 1
        self.asteroids_for_next_level = 50
        self.level_up = False
        self.upgrade_options = []
        self.rapid_fire_taken = False
        self.super_rapid_fire_taken = False
        self.ultra_rapid_fire_taken = False
        self.dual_shot_taken = False
        self.side_shot_taken = False
        self.tracking_shots_taken = False
        self.mega_rapid_fire_taken = False
        self.forcefield_taken = False

    def draw_score(self):
        # Draw score in top right
        score_text = f"SCORE: {self.score}"
        score_surface = self.score_font.render(score_text, True, "white")
        score_rect = score_surface.get_rect(topright=(SCREEN_WIDTH - 20, 20))
        self.screen.blit(score_surface, score_rect)

        # Draw level in top left
        level_text = f"LEVEL: {self.level}"
        level_surface = self.score_font.render(level_text, True, "white")
        level_rect = level_surface.get_rect(topleft=(20, 20))
        self.screen.blit(level_surface, level_rect)

    def check_level_up(self):
        if self.score >= self.asteroids_for_next_level:
            self.level += 1
            self.asteroids_for_next_level += 50
            self.level_up = True
            self.set_upgrade_options()
            # Reset forcefield if it's active
            if self.player.forcefield:
                self.player.reset_forcefield()

    def set_upgrade_options(self):
        if self.level == 2:
            # Level 2 always offers Dual Shot and Rapid Fire
            self.upgrade_options = [
                {
                    "name": "Rapid Fire",
                    "description": "Double your fire rate",
                    "key": "1",
                    "action": self.upgrade_rapid_fire
                },
                {
                    "name": "Dual Shot",
                    "description": "Shoot forward and backward",
                    "key": "2",
                    "action": self.upgrade_dual_shot
                }
            ]
        elif self.level == 3:
            self.upgrade_options = []
            if self.dual_shot_taken:
                # If Dual Shot was taken at level 2, offer Side Shots and Rapid Fire
                self.upgrade_options = [
                    {
                        "name": "Rapid Fire",
                        "description": "Double your fire rate",
                        "key": "1",
                        "action": self.upgrade_rapid_fire
                    },
                    {
                        "name": "Side Shots",
                        "description": "Shoot from both sides",
                        "key": "2",
                        "action": self.upgrade_side_shot
                    }
                ]
            else:
                # If Rapid Fire was taken at level 2, offer Dual Shot and Super Rapid Fire
                self.upgrade_options = [
                    {
                        "name": "Dual Shot",
                        "description": "Shoot forward and backward",
                        "key": "1",
                        "action": self.upgrade_dual_shot
                    },
                    {
                        "name": "Super Rapid Fire",
                        "description": "Double your fire rate again (4x total)",
                        "key": "2",
                        "action": self.upgrade_super_rapid_fire
                    }
                ]
        elif self.level == 4:
            self.upgrade_options = []
            if self.dual_shot_taken and self.side_shot_taken:
                # If both Dual Shot and Side Shots are taken, offer Rapid Fire and Tracking Shots
                self.upgrade_options = [
                    {
                        "name": "Rapid Fire",
                        "description": "Double your fire rate",
                        "key": "1",
                        "action": self.upgrade_rapid_fire
                    },
                    {
                        "name": "Tracking Shots",
                        "description": "Shots automatically target nearest asteroid",
                        "key": "2",
                        "action": self.upgrade_tracking_shots
                    }
                ]
            elif self.dual_shot_taken and not self.side_shot_taken:
                # If only Dual Shot is taken, offer Side Shots and Super Rapid Fire
                self.upgrade_options = [
                    {
                        "name": "Side Shots",
                        "description": "Shoot from both sides",
                        "key": "1",
                        "action": self.upgrade_side_shot
                    },
                    {
                        "name": "Super Rapid Fire",
                        "description": "Double your fire rate again (4x total)",
                        "key": "2",
                        "action": self.upgrade_super_rapid_fire
                    }
                ]
            elif not self.dual_shot_taken and self.rapid_fire_taken:
                # If only Rapid Fire is taken, offer Dual Shot and Ultra Rapid Fire
                self.upgrade_options = [
                    {
                        "name": "Dual Shot",
                        "description": "Shoot forward and backward",
                        "key": "1",
                        "action": self.upgrade_dual_shot
                    },
                    {
                        "name": "Ultra Rapid Fire",
                        "description": "Double your fire rate again (8x total)",
                        "key": "2",
                        "action": self.upgrade_ultra_rapid_fire
                    }
                ]
        elif self.level == 5:
            self.upgrade_options = []
            if self.dual_shot_taken and self.side_shot_taken and self.tracking_shots_taken:
                # If all directional upgrades are taken, offer Rapid Fire and Forcefield
                self.upgrade_options = [
                    {
                        "name": "Rapid Fire",
                        "description": "Double your fire rate",
                        "key": "1",
                        "action": self.upgrade_rapid_fire
                    },
                    {
                        "name": "Forcefield",
                        "description": "Create a ring of protective shots around your ship",
                        "key": "2",
                        "action": self.upgrade_forcefield
                    }
                ]
            elif self.dual_shot_taken and self.side_shot_taken and not self.tracking_shots_taken:
                # If Dual Shot and Side Shots are taken, offer Tracking Shots and Mega Rapid Fire
                self.upgrade_options = [
                    {
                        "name": "Tracking Shots",
                        "description": "Shots automatically target nearest asteroid",
                        "key": "1",
                        "action": self.upgrade_tracking_shots
                    },
                    {
                        "name": "Mega Rapid Fire",
                        "description": "Double your fire rate again (16x total)",
                        "key": "2",
                        "action": self.upgrade_mega_rapid_fire
                    }
                ]
            elif not self.dual_shot_taken and self.rapid_fire_taken and self.super_rapid_fire_taken:
                # If both Rapid Fire upgrades are taken, offer Dual Shot and Forcefield
                self.upgrade_options = [
                    {
                        "name": "Dual Shot",
                        "description": "Shoot forward and backward",
                        "key": "1",
                        "action": self.upgrade_dual_shot
                    },
                    {
                        "name": "Forcefield",
                        "description": "Create a ring of protective shots around your ship",
                        "key": "2",
                        "action": self.upgrade_forcefield
                    }
                ]
            elif not self.dual_shot_taken and self.rapid_fire_taken and not self.super_rapid_fire_taken:
                # If only Rapid Fire is taken, offer Super Rapid Fire and Forcefield
                self.upgrade_options = [
                    {
                        "name": "Super Rapid Fire",
                        "description": "Double your fire rate again (4x total)",
                        "key": "1",
                        "action": self.upgrade_super_rapid_fire
                    },
                    {
                        "name": "Forcefield",
                        "description": "Create a ring of protective shots around your ship",
                        "key": "2",
                        "action": self.upgrade_forcefield
                    }
                ]

    def upgrade_rapid_fire(self):
        self.player.fire_rate_multiplier = 2.0
        self.rapid_fire_taken = True
        self.level_up = False
        self.clear_asteroids()

    def upgrade_dual_shot(self):
        self.player.dual_shot = True
        self.dual_shot_taken = True
        self.level_up = False
        self.clear_asteroids()

    def upgrade_super_rapid_fire(self):
        self.player.fire_rate_multiplier *= 2.0
        self.super_rapid_fire_taken = True
        self.level_up = False
        self.clear_asteroids()

    def upgrade_side_shot(self):
        self.player.side_shot = True
        self.side_shot_taken = True
        self.level_up = False
        self.clear_asteroids()

    def upgrade_ultra_rapid_fire(self):
        self.player.fire_rate_multiplier *= 2.0
        self.ultra_rapid_fire_taken = True
        self.level_up = False
        self.clear_asteroids()

    def upgrade_tracking_shots(self):
        self.player.tracking_shots = True
        self.tracking_shots_taken = True
        self.level_up = False
        self.clear_asteroids()

    def upgrade_mega_rapid_fire(self):
        self.player.fire_rate_multiplier *= 2.0
        self.mega_rapid_fire_taken = True
        self.level_up = False
        self.clear_asteroids()

    def upgrade_forcefield(self):
        self.player.forcefield = True
        self.forcefield_taken = True
        self.level_up = False
        self.clear_asteroids()

    def clear_asteroids(self):
        """Clear all asteroids and reset player position when starting a new level"""
        # Clear all asteroids
        for asteroid in self.asteroids:
            asteroid.kill()
        
        # Reset player position and velocity
        self.player.position = pygame.math.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.player.velocity = pygame.math.Vector2(0, 0)
        self.player.rect.center = self.player.position

    def handle_level_up(self):
        # Draw level up text
        level_text = f"LEVEL {self.level} COMPLETE!"
        level_surface = self.font.render(level_text, True, "white")
        level_rect = level_surface.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 100))
        self.screen.blit(level_surface, level_rect)

        # Draw upgrade options with adjusted spacing
        for i, option in enumerate(self.upgrade_options):
            y_pos = SCREEN_HEIGHT/2 + i * 70  # Increased spacing for readability
            # Draw option name
            name_surface = self.score_font.render(f"{option['key']}: {option['name']}", True, "white")
            name_rect = name_surface.get_rect(center=(SCREEN_WIDTH/2, y_pos))
            self.screen.blit(name_surface, name_rect)
            
            # Draw description
            desc_surface = self.small_font.render(option['description'], True, "white")
            desc_rect = desc_surface.get_rect(center=(SCREEN_WIDTH/2, y_pos + 40))
            self.screen.blit(desc_surface, desc_rect)

    def handle_game_over(self, dt):
        self.text_timer += dt
        if self.text_timer >= self.text_speed and self.text_progress < len(self.game_over_text):
            self.text_progress += 1
            self.text_timer = 0

        # Draw game over text
        text = self.game_over_text[:self.text_progress]
        text_surface = self.font.render(text, True, "white")
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50))
        self.screen.blit(text_surface, text_rect)

        # Draw final score and level
        final_score_text = f"FINAL SCORE: {self.score}"
        final_level_text = f"LEVEL REACHED: {self.level}"
        final_score_surface = self.score_font.render(final_score_text, True, "white")
        final_level_surface = self.score_font.render(final_level_text, True, "white")
        final_score_rect = final_score_surface.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        final_level_rect = final_level_surface.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 40))
        self.screen.blit(final_score_surface, final_score_rect)
        self.screen.blit(final_level_surface, final_level_rect)

        # Draw menu options
        menu_text = self.small_font.render("PRESS R FOR MAIN MENU", True, "white")
        exit_text = self.small_font.render("PRESS Q TO QUIT", True, "white")
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 100))
        exit_rect = exit_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 150))
        self.screen.blit(menu_text, menu_rect)
        self.screen.blit(exit_text, exit_rect)

    def handle_intro_screen(self, dt):
        # Update intro asteroids
        if self.intro_asteroid_field:
            self.intro_asteroid_field.update(dt, 1)  # Use level 1 for consistent speed
        
        # Update all intro sprites
        for sprite in self.intro_updatable:
            if isinstance(sprite, Asteroid):
                sprite.update(dt)
        
        # Draw intro asteroids
        for sprite in self.intro_drawable:
            sprite.draw(self.screen)

        # Draw title
        title_text = "ASTEROIDS"
        title_surface = self.font.render(title_text, True, "white")
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/4))
        self.screen.blit(title_surface, title_rect)

        # Draw controls with adjusted spacing for the new font
        controls = [
            "CONTROLS:",
            "W - MOVE FORWARD",
            "S - MOVE BACKWARD",
            "A - ROTATE LEFT",
            "D - ROTATE RIGHT",
            "SPACE - SHOOT",
            "",
            "PRESS SPACE TO START"
        ]

        for i, text in enumerate(controls):
            y_pos = SCREEN_HEIGHT/2 + i * 35  # Reduced spacing for the pixel font
            text_surface = self.small_font.render(text, True, "white")
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH/2, y_pos))
            self.screen.blit(text_surface, text_rect)

    def start_game(self):
        # Clear intro asteroids
        if self.intro_asteroid_field:
            self.intro_asteroid_field.kill()
            self.intro_asteroid_field = None
        for asteroid in self.intro_asteroids:
            asteroid.kill()
        self.intro_asteroids.empty()
        
        # Reset asteroid containers for actual game
        Asteroid.containers = (self.asteroids, self.updatable, self.drawable)
        AsteroidField.containers = (self.updatable,)
        self.intro_screen = False

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0  # Convert to seconds

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if self.intro_screen:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.start_game()
                elif self.game_over:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.intro_screen = True
                            self.reset_game()
                        elif event.key == pygame.K_q:
                            running = False
                elif self.level_up:
                    if event.type == pygame.KEYDOWN:
                        for option in self.upgrade_options:
                            if event.unicode == option['key']:
                                option['action']()
                                break

            # Render
            self.screen.fill("black")
            if self.intro_screen:
                self.handle_intro_screen(dt)
            elif self.game_over:
                self.handle_game_over(dt)
            elif self.level_up:
                self.handle_level_up()
            else:
                if not self.game_over and not self.level_up:
                    # Handle shooting
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_SPACE]:
                        new_shots = self.player.shoot()
                        if new_shots:
                            for shot in new_shots:
                                self.shots.add(shot)
                                self.updatable.add(shot)
                                self.drawable.add(shot)
                    
                    # Handle collisions
                    for sprite in self.asteroids:
                        for hit in self.shots:
                            if sprite.collision(hit):
                                sprite.split()
                                hit.kill()
                                self.score += 1
                                self.check_level_up()
                        if sprite.collision(self.player):
                            # Check if forcefield can absorb the hit
                            if self.player.forcefield:  # First check if forcefield is active
                                # Calculate bounce direction
                                collision_vector = sprite.position - self.player.position
                                if collision_vector.length() > 0:  # Prevent division by zero
                                    collision_vector = collision_vector.normalize()
                                    # Move asteroid away from player to prevent sticking
                                    sprite.position = self.player.position + collision_vector * (self.player.radius + sprite.radius + 5)
                                    # Reverse and increase velocity
                                    sprite.velocity = -collision_vector * sprite.velocity.length() * 1.5
                                # Handle forcefield hit and check if it's depleted
                                if not self.player.handle_forcefield_collision():
                                    self.game_over = True
                            else:
                                self.game_over = True

                    # Update game
                    for sprite in self.updatable:
                        if isinstance(sprite, AsteroidField):
                            sprite.update(dt, self.level)
                        elif isinstance(sprite, Shot):
                            sprite.update(dt, self.asteroids)
                        else:
                            sprite.update(dt)

                for sprite in self.drawable:
                    sprite.draw(self.screen)
                self.draw_score()
            
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()