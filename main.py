import pygame
import sys
from constants import *
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot

updatable = pygame.sprite.Group()
drawable = pygame.sprite.Group()
Player.containers = (updatable, drawable)

asteroids = pygame.sprite.Group()
Asteroid.containers = (asteroids, updatable, drawable)
AsteroidField.containers = (updatable,)

shots = pygame.sprite.Group()
Shot.containers = (shots, updatable, drawable)

def main():
    pygame.init()
    clock = pygame.time.Clock()
    dt = 0
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    asteroid_field = AsteroidField()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    running = True
    while running:
        time_passed = clock.tick(60)
        dt = time_passed / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # shoot
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            new_shot = player.shoot()
        
        for sprite in asteroids:
            for hit in shots:
                if sprite.collision(hit):
                    sprite.split()
                    hit.kill()

        # update game
        updatable.update(dt)
        for sprite in asteroids:
            if sprite.collision(player):
                print("Game Over!")
                sys.exit()

        # render
        screen.fill("black")
        for sprite in drawable:
            sprite.draw(screen)
        pygame.display.flip()
        

    pygame.quit()


if __name__ == "__main__":
    main()