import pygame
import random
import cv2
import numpy as np
from constraint import is_constraint_zone

WIDTH = 1000
HEIGHT = WIDTH
FPS = 60
N_LINES = 50
OUTSIDE_COLOR = [(100, 100, 100,200), (130, 130, 130,180), (30, 30, 30,220), (90, 90, 90,200)]
INSIDE_COLOR = (200, 200, 200,180)
N_PARTICLES = 100
SIZE_PARTICLE_INSIDE = 2
SIZE_PARTICLE_OUTSIDE = 1

WHITE = (255, 255, 255)
BLACK = (1, 11, 22)
DARK_BLUE = (0, 0, 128)
DARK_PURPLE = (64, 0, 64)
DARK_GREEN = (0, 64, 0)
COLORS = [DARK_BLUE, DARK_PURPLE, DARK_GREEN]

class BarcodeLine:
    def __init__(self, x, speed):
        self.x = x
        self.speed = speed
        self.color_index = random.randint(0, len(COLORS) - 1)

    def update(self):
        self.x += self.speed

    def draw(self, screen):
        color = random.choice(OUTSIDE_COLOR)
        for i in range(N_PARTICLES):
            y = i * (HEIGHT // N_PARTICLES)
            if is_constraint_zone(self.x, y, WIDTH):
                distortion = random.randint(-2, 2)
                distortiony=random.randint(-1,1)
                pygame.draw.circle(screen, INSIDE_COLOR, (self.x + distortion, y+distortiony), SIZE_PARTICLE_INSIDE)
            else:
                pygame.draw.circle(screen, random.choice(OUTSIDE_COLOR), (self.x, y), SIZE_PARTICLE_OUTSIDE)

def generate_random_line(x):
    speed = random.uniform(1, 3)
    return BarcodeLine(x, speed)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

lines = []
x = 0
while x < WIDTH:
    line = generate_random_line(x)
    lines.append(line)
    x += random.randint(5, 20) 

video_writer = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), FPS, (WIDTH, HEIGHT))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    for line in lines:
        line.update()
        line.draw(screen)

    lines = [line for line in lines if line.x < WIDTH]

    if random.random() < 0.1:
        x = 0
        line = generate_random_line(x)
        lines.append(line)

    frame = np.array(pygame.surfarray.pixels3d(screen)).swapaxes(0, 1)

    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    video_writer.write(frame)

    pygame.display.flip()
    clock.tick(FPS)

video_writer.release()

pygame.quit()