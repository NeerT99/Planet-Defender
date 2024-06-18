import pygame
import math
import time
import random
import os

pygame.init()

# CONSTANTS
FPS = 60
WIDTH, HEIGHT = 800, 800

# COLOURS
BACKGROUND_COLOR = (205, 192, 180)
PLANET_COLOR = (70, 130, 180) 
BULLET_COLOR = (255, 255, 0)  
FONT_COLOR = (211, 211, 211) 
SHIP_COLOR = (255, 50, 255)
BOMB_THREAT_COLOR = (255, 0, 0)
BOMB_COLOR = (255, 255, 0)
BOSS_BOMB_COLOR = (255, 0, 0)
MOVING_BOMB_COLOR = (0, 191, 255)
GAME_OVER_COLOR = (255, 0, 0)

# GAME VARIABLES
BULLETS_PER_SECOND = 10  
TIME_BETWEEN_SHOTS = 1 / BULLETS_PER_SECOND
ROTATION_SPEED = 0.01 # planet rotation speed

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Planet Defender")

# LOAD IMAGES
BACKGROUND_IMAGE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "space_img_bg.png")), (WIDTH, HEIGHT))
SHIP_IMAGE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "ufo_ship.png")), ((100, 60)))
SHIP_IMAGE = pygame.transform.rotate(SHIP_IMAGE, -90) 

class Bullet:
    VELOCITY = 10

    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.target_x = target_x
        self.target_y = target_y
        self.angle = math.atan2(target_y - y, target_x - x)
        self.collided = False

    def update(self):
        if not self.collided:
            self.x += self.VELOCITY * math.cos(self.angle)
            self.y += self.VELOCITY * math.sin(self.angle)

    def draw(self, window):
        if not self.collided:
            pygame.draw.circle(window, BULLET_COLOR, (int(self.x), int(self.y)), 5)

    # Check if the bullet is colliding with an object (using distance), in this case, the planet. If it is, remove it from the list
    def check_collision(self, obj):
        distance = math.sqrt((self.x - obj.x)**2 + (self.y - obj.y)**2)
        if distance <= obj.radius:
            self.collided = True
            return True
        return False

    def check_planet_collision(self, planet):
        distance_from_start = math.sqrt((self.start_x - planet.x)**2 + (self.start_y - planet.y)**2)
        current_distance = math.sqrt((self.x - planet.x)**2 + (self.y - planet.y)**2)
        if current_distance < distance_from_start and current_distance <= planet.radius:
            self.collided = True
            return True
        return False

class Ship:
    ROTATION_VELOCITY = 4 # sensitivity of the ship to keyboard inputs

    def __init__(self, x, y, radius, angle, distance, health=50):
        self.x = x
        self.y = y
        self.radius = radius
        self.angle = angle
        self.distance = distance
        self.bullets = []
        self.last_shot_time = time.time()
        self.health = health
        self.max_health = health
        self.image = SHIP_IMAGE

    def draw(self, window):
        # Position image to line up with bullets
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        new_rect = rotated_image.get_rect(center=(self.x, self.y))
        window.blit(rotated_image, new_rect.topleft)

        # draw the health bar for the ship
        self.draw_healthbar(window)

        # draw the bullets
        for bullet in self.bullets:
            bullet.draw(window)

    def draw_healthbar(self, window):
        bar_height = self.radius * 2
        bar_width = 5
        pygame.draw.rect(window, (255, 0, 0), (self.x + self.radius + 15, self.y - self.radius, bar_width, bar_height - 20))
        pygame.draw.rect(window, (0, 255, 0), (self.x + self.radius + 15, self.y - self.radius + bar_height * (1 - self.health / self.max_health), bar_width, bar_height * (self.health / self.max_health) - 20))

    def rotate(self, planet, direction):
        if direction == "left":
            self.angle += self.ROTATION_VELOCITY
        elif direction == "right":
            self.angle -= self.ROTATION_VELOCITY
        
        # Calculate new position based on angle
        self.x = planet.x + self.distance * math.cos(math.radians(self.angle))
        self.y = planet.y + self.distance * math.sin(math.radians(self.angle))

    def shoot(self, planet):
        current_time = time.time()
        if current_time - self.last_shot_time >= TIME_BETWEEN_SHOTS:
            # Create a new bullet aimed at the planet's center
            bullet = Bullet(self.x, self.y, planet.x, planet.y)
            self.bullets.append(bullet)
            self.last_shot_time = current_time

    # Check if bullets collide with any of the bombs
    def update_bullets(self, bombs, boss_bomb, moving_bomb, planet):
        for bullet in self.bullets:
            bullet.update()
            for bomb in bombs:
                if bullet.check_collision(bomb):
                    bomb.hit()
            if boss_bomb and bullet.check_collision(boss_bomb):
                boss_bomb.hit()
            if moving_bomb and bullet.check_collision(moving_bomb):
                moving_bomb.hit()
            if bullet.check_planet_collision(planet):
                bullet.collided = True
        # Remove bullets that have collided with any bomb or the planet
        self.bullets = [bullet for bullet in self.bullets if not bullet.collided]


class Planet:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.rotation_angle = 0

    def draw(self, window):
        pygame.draw.circle(window, PLANET_COLOR, (self.x, self.y), self.radius)

    # Rotate the planet and all bombs around it
    def rotate(self, bombs, boss_bomb, moving_bomb):
        self.rotation_angle += ROTATION_SPEED  # Adjust the speed of rotation here
        # Rotate the bombs at the same speed as the planet using ROTATION_SPEED
        for bomb in bombs:
            angle = math.atan2(bomb.y - self.y, bomb.x - self.x)
            distance = math.sqrt((bomb.x - self.x)**2 + (bomb.y - self.y)**2)
            angle += ROTATION_SPEED 
            bomb.x = self.x + distance * math.cos(angle)
            bomb.y = self.y + distance * math.sin(angle)
            bomb.angle = angle  # Update the bomb's angle for text positioning

        if boss_bomb:
            angle = math.atan2(boss_bomb.y - self.y, boss_bomb.x - self.x)
            distance = math.sqrt((boss_bomb.x - self.x)**2 + (boss_bomb.y - self.y)**2)
            angle += ROTATION_SPEED 
            boss_bomb.x = self.x + distance * math.cos(angle)
            boss_bomb.y = self.y + distance * math.sin(angle)
            boss_bomb.angle = angle

        if moving_bomb:
            angle = math.atan2(moving_bomb.y - self.y, moving_bomb.x - self.x)
            distance = math.sqrt((moving_bomb.x - self.y)**2 + (moving_bomb.y - self.y)**2)
            angle -= ROTATION_SPEED  # Move the bomb in the opposite direction of the planet
            moving_bomb.x = self.x + distance * math.cos(angle)
            moving_bomb.y = self.y + distance * math.sin(angle)
            moving_bomb.angle = angle

class Bomb:
    def __init__(self, planet, health):
        angle = random.uniform(0, 360)
        self.angle = angle
        self.x = planet.x + planet.radius * math.cos(math.radians(angle))
        self.y = planet.y + planet.radius * math.sin(math.radians(angle))
        self.radius = 20  # bomb size
        self.health = health # bomb health
        self.timer = 15  # bomb timer
        self.font = pygame.font.SysFont(None, 24)  # Font for displaying the timer

    # Draw the bomb
    def draw(self, window):
        pygame.draw.circle(window, BOMB_COLOR, (int(self.x), int(self.y)), self.radius)
        self.draw_timer(window)

    def draw_timer(self, window):
        # Calculate the text position based on updated angle
        text_x = self.x + (self.radius + 15) * math.cos(self.angle)
        text_y = self.y + (self.radius + 15) * math.sin(self.angle)
        # Color the bombs in red if they go below 5
        timer_color = FONT_COLOR if self.timer >= 6 else BOMB_THREAT_COLOR
        timer_text = self.font.render(str(int(self.timer)), True, timer_color)
        window.blit(timer_text, (text_x - timer_text.get_width() // 2, text_y - timer_text.get_height() // 2))

    def update_timer(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.timer = 0  # Stop at 0 to avoid negative values

    # Each bullet removes 1hp off
    def hit(self):
        self.health -= 1

class BossBomb(Bomb):
    def __init__(self, planet):
        super().__init__(planet, health=10)
        self.timer = 30 # increasing bomb timer for boss
        self.radius = 30  # Boss bomb size
        self.font = pygame.font.SysFont(None, 24)

    def draw(self, window):
        pygame.draw.circle(window, BOSS_BOMB_COLOR, (int(self.x), int(self.y)), self.radius)
        self.draw_timer(window)

class MovingBomb(Bomb):
    def __init__(self, planet):
        super().__init__(planet, health=5)
        self.angle = random.uniform(0, 360)
        self.x = planet.x + planet.radius * math.cos(math.radians(self.angle))
        self.y = planet.y + planet.radius * math.sin(math.radians(self.angle))
        self.timer = 21
        self.radius = 15  # Moving bomb size
        self.font = pygame.font.SysFont(None, 24)

    def draw(self, window):
        pygame.draw.circle(window, MOVING_BOMB_COLOR, (int(self.x), int(self.y)), self.radius)
        self.draw_timer(window)

class Meteor:
    VELOCITY = 5

    def __init__(self, x, y, target_x, target_y, direction):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.direction = direction
        self.radius = 15
        self.color = (169, 169, 169)  # Greyish color for meteors
        self.angle = math.atan2(target_y - y, target_x - x)

    # Meteors will fly in 1 of 3 directions - horizontally, vertically or diagonally
    def update(self):
        if self.direction == 'horizontal':
            self.x += self.VELOCITY if self.target_x > self.x else -self.VELOCITY
        elif self.direction == 'vertical':
            self.y += self.VELOCITY if self.target_y > self.y else -self.VELOCITY
        elif self.direction == 'diagonal':
            self.x += self.VELOCITY * math.cos(self.angle)
            self.y += self.VELOCITY * math.sin(self.angle)

    def draw(self, window):
        pygame.draw.circle(window, self.color, (int(self.x), int(self.y)), self.radius)

    def check_collision(self, obj):
        distance = math.sqrt((self.x - obj.x)**2 + (self.y - obj.y)**2)
        return distance <= self.radius + obj.radius

    # Will use this function in the game loop remove the meteors when they go off the screen
    def off_screen(self, width, height):
        return self.x < 0 or self.x > width or self.y < 0 or self.y > height

def draw(window, ship, planet, bombs, boss_bomb, moving_bomb, meteors, bomb_counter):
    window.blit(BACKGROUND_IMAGE, (0, 0))
    for bomb in bombs:
        bomb.draw(window)
    if boss_bomb:
        boss_bomb.draw(window)
    if moving_bomb:
        moving_bomb.draw(window)
    planet.draw(window)
    ship.draw(window)
    for meteor in meteors:
        meteor.draw(window)
    display_bomb_counter(window, bomb_counter, planet)
    pygame.display.update()

# Counter to show how many bombs have been destroyed
def display_bomb_counter(window, bomb_counter, planet):
    font = pygame.font.SysFont(None, 300)
    counter_text = font.render(str(bomb_counter), True, FONT_COLOR)
    window.blit(counter_text, (planet.x - counter_text.get_width() // 2, planet.y - counter_text.get_height() // 2))

def display_game_over(window):
    font = pygame.font.SysFont(None, 72)
    game_over_text = font.render("GAME OVER!", True, GAME_OVER_COLOR)
    window.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
    pygame.display.update()
    pygame.time.delay(3000)

def spawn_bombs(planet, num_bombs):
    bombs = []
    for _ in range(num_bombs):
        bombs.append(Bomb(planet, health=3))
    return bombs

# Main game loop
def main(window):
    clock = pygame.time.Clock()
    run = True
    bomb_counter = 0
    boss_bomb = None
    moving_bomb = None
    moving_bomb_spawned = False  # Flag to track if a moving bomb was spawned

    planet = Planet(WIDTH // 2, HEIGHT // 2, 200)
    ship = Ship(WIDTH // 2 + planet.radius + 100, HEIGHT // 2, 30, 0, planet.radius + 100)  # Larger ship with radius 30
    bombs = spawn_bombs(planet, 3)  # Spawn 3 bombs initially
    meteors = []  # List to store meteors

    start_time = time.time()
    meteor_spawn_time = 2  # Spawn a meteor every 2 seconds

    while run:
        dt = clock.tick(FPS) / 1000  # Time in seconds since last tick
        elapsed_time = time.time() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            ship.rotate(planet, "left")
        if keys[pygame.K_RIGHT]:
            ship.rotate(planet, "right")
        if keys[pygame.K_SPACE]:
            ship.shoot(planet)

        # Rotate the planet and bombs
        planet.rotate(bombs, boss_bomb, moving_bomb)

        # Update timers for bombs
        for bomb in bombs:
            bomb.update_timer(dt)
        if boss_bomb:
            boss_bomb.update_timer(dt)
        if moving_bomb:
            moving_bomb.update_timer(dt)

        # Update bullets and check collisions
        ship.update_bullets(bombs, boss_bomb, moving_bomb, planet)
        
        # Remove bombs with health <= 0 or timer <= 0
        bombs_to_remove = [bomb for bomb in bombs if bomb.health <= 0 or bomb.timer <= 0]
        bombs = [bomb for bomb in bombs if bomb.health > 0 and bomb.timer > 0]
        
        # Increment the bomb counter for removed bombs
        bomb_counter += len(bombs_to_remove)

        # Check for game over condition
        if any(bomb.timer <= 0 for bomb in bombs_to_remove) or (boss_bomb and boss_bomb.timer <= 0):
            display_game_over(window)
            run = False
            break

        # Spawn bombs if there are fewer than 3
        if len(bombs) < 3:
            bombs += spawn_bombs(planet, 3 - len(bombs))

        # Spawn a boss bomb if the counter is 25 or a multiple of 25 and no boss bomb exists
        if bomb_counter > 0 and bomb_counter % 25 == 0 and not boss_bomb:
            boss_bomb = BossBomb(planet)

        # Check if boss bomb is defeated and reset boss_bomb to None
        if boss_bomb and boss_bomb.health <= 0:
            boss_bomb = None

        # Spawn a moving bomb if the counter is 55 or a multiple of 55 and no moving bomb exists
        if bomb_counter > 0 and bomb_counter % 35 == 0 and not moving_bomb and not moving_bomb_spawned:
            moving_bomb = MovingBomb(planet)
            moving_bomb_spawned = True  # Set the flag to true when a moving bomb is spawned

        # Reset the flag after the moving bomb is destroyed
        if moving_bomb and moving_bomb.health <= 0:
            moving_bomb = None
            moving_bomb_spawned = False  # Reset the flag when the moving bomb is destroyed

        # Spawn meteors with 1 of the 3 directions randomly
        if elapsed_time % meteor_spawn_time < dt:
            direction = random.choice(['horizontal', 'vertical', 'diagonal'])
            if direction == 'horizontal':
                x = random.choice([-10, WIDTH])
                y = random.randint(-10, HEIGHT)
                target_x = WIDTH + 100 if x == 0 else -100
                target_y = y
            elif direction == 'vertical':
                x = random.randint(-10, WIDTH)
                y = random.choice([-10, HEIGHT])
                target_x = x
                target_y = HEIGHT + 100 if y == 0 else -100
            elif direction == 'diagonal':
                x = random.randint(-10, WIDTH)
                y = random.randint(-10, HEIGHT)
                target_x = WIDTH + 100 if x < WIDTH / 2 else -100
                target_y = HEIGHT + 100 if y < HEIGHT / 2 else -100
            meteor = Meteor(x, y, target_x, target_y, direction)
            meteors.append(meteor)

        # Update meteors for collision and when they go off screen
        for meteor in meteors[:]:
            meteor.update()
            if meteor.check_collision(ship):
                ship.health -= 10
                meteors.remove(meteor)
            elif meteor.off_screen(WIDTH, HEIGHT):
                meteors.remove(meteor)

        draw(window, ship, planet, bombs, boss_bomb, moving_bomb, meteors, bomb_counter)
        
    pygame.quit()

if __name__ == '__main__':
    main(WINDOW)
