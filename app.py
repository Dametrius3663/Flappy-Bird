'''Reference for PyGame Flappy Bird tutorial:
https://www.youtube.com/watch?v=UZg49z76cLw&t=1s&ab_channel=TechWithTim'''

'''This is the game that I used to learn python during my internship last summer.
I have since added some folder searching fiunctionality for the assets and the use of the images.'''
import pygame
from pygame.locals import *
import random
import os

#Initialization-
pygame.init()

clock = pygame.time.Clock()
fps = 60

# Screen dimensions and main surface
screen_width = 864
screen_height = 936
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

#Resource loading (images, fonts)
# Use paths relative to the script so assets can be bundled in the folder
base_dir = os.path.join(os.path.dirname(__file__), 'assets')
bg = pygame.image.load(os.path.join(base_dir, 'bg.png'))
ground_img = pygame.image.load(os.path.join(base_dir, 'ground.png'))
button_img = pygame.image.load(os.path.join(base_dir, 'restart.png'))

# Font used for displaying the score
font = pygame.font.SysFont('Bauhaus 93', 60)

#Colors
white = (255, 255, 255)

#Game state variables
# Variables controlling scrolling, game state, pipe timing and score
ground_scroll = 0
scroll_speed = 4
flying = False       # True once the player has started (bird falls/flies)
game_over = False    # True when player loses
pipe_gap = 150
pipe_frequency = 1500  # milliseconds between pipe spawns
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False    # helper to track when a pipe has been passed for scoring


#Helper functions
def draw_text(text, font, text_col, x, y):
    """Render `text` to the screen at (x, y) using `font` and color."""
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def reset_game():
    """Reset dynamic objects (pipes, bird position) and the score."""
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    return score


#Sprite classes
class Bird(pygame.sprite.Sprite):
    """Player-controlled bird. Handles animation, gravity and jumping."""
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        # load animation frames
        for num in range(1, 4):
            img = pygame.image.load(os.path.join(base_dir, f'bird{num}.png'))
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):
        # Gravity and vertical movement when the game is in 'flying' state
        if flying:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        # Only allow jumping and animation if game isn't over
        if not game_over:
            # Jump on mouse click (simple click-state handling)
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            # Handle flap animation cycling
            self.counter += 1
            flap_cooldown = 5
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            # Rotate sprite based on velocity for visual feedback
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            # If game over, point the bird straight down
            self.image = pygame.transform.rotate(self.images[self.index], -90)


class Pipe(pygame.sprite.Sprite):
    """Pipe obstacle (top or bottom). Moves left and removes itself off-screen."""
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join(base_dir, 'pipe.png'))
        self.rect = self.image.get_rect()
        # position == 1 => top pipe (flipped), -1 => bottom pipe
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        # Move pipe left and kill it when it leaves the screen
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()


class Button():
    """Clickable button used to restart the game when it's over."""
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        # Return True if the button was clicked this frame
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action


#Sprite groups and initial instances
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

# Create the player bird and add it to the group
flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)

# Restart button centered on screen
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)


 #Main game loop
run = True
while run:
    clock.tick(fps)

    # Draw background and sprites each frame
    screen.blit(bg, (0, 0))
    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)

    # Draw the scrolling ground
    screen.blit(ground_img, (ground_scroll, 768))

    #Scoring: detect when the bird passes a pipe
    if len(pipe_group) > 0:
        if (
            bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left
            and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right
            and pass_pipe == False
        ):
            pass_pipe = True
        if pass_pipe:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False

    # Draw the score to the screen
    draw_text(str(score), font, white, int(screen_width / 2), 20)

    # Collision and ground check: set game_over accordingly
    if flappy.rect.bottom >= 768:
        game_over = True
        flying = False

    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True

    # Gameplay updates (spawn pipes, scroll ground, update pipes)
    if not game_over and flying:
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        # Scroll the ground image and reset its offset periodically
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

        pipe_group.update()

    # Game over handling: draw restart button and reset if clicked
    if game_over:
        if button.draw() == True:
            game_over = False
            score = reset_game()

    # Event handling: quit and starting the game on first click
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not flying and not game_over:
            flying = True

    pygame.display.update()

pygame.quit()


