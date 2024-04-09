import pygame
import random
import cv2
import numpy as np
from constraint import is_constraint_zone

WIDTH = 1200
HEIGHT = WIDTH
FPS = 60
N_PARTICLES = 2000
F_START = 1.0
F_END = 0.02
F_DURATION = 5.0 

WHITE = (255, 255, 255)
OUTSIDE_COLOR= [(100,100,100),(130,130,130),(30,30,30),(90,90,90)]
INSIDE_COLOR=(200,200,200)
BLACK = (1, 11, 22)
DARK_BLUE = (0, 0, 128)
DARK_PURPLE = (64, 0, 64)
DARK_GREEN = (0, 64, 0)
COLORS = [DARK_BLUE, DARK_PURPLE, DARK_GREEN]

class Particle:
    def __init__(self, x, y, speed, color):
        self.x = x
        self.y = y
        self.original_speed = speed
        self.speed = speed
        self.color = color

    def update(self, F):
        if is_constraint_zone(self.x, self.y, WIDTH):
            self.speed = self.original_speed * F
            color = (INSIDE_COLOR)
        else:
            self.speed = self.original_speed

        dx = random.uniform(-4, 4) * self.speed
        dy = random.uniform(-4, 4) * self.speed

        self.x += dx
        self.y += dy

        self.x = max(0, min(self.x, WIDTH))
        self.y = max(0, min(self.y, HEIGHT))

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 1)

def generate_random_particle():
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)
    speed = random.uniform(10, 16)
    color = random.choice(OUTSIDE_COLOR)
    return Particle(x, y, speed, color)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

particles = [generate_random_particle() for _ in range(N_PARTICLES)]

video_writer = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), FPS, (WIDTH, HEIGHT))

elapsed_time = 0.0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    t = min(elapsed_time / F_DURATION, 1.0)
    F = F_START + (F_END - F_START) * t

    for particle in particles:
        particle.update(F)
        particle.draw(screen)

    frame = np.array(pygame.surfarray.pixels3d(screen)).swapaxes(0, 1)

    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    video_writer.write(frame)

    pygame.display.flip()
    elapsed_time += clock.tick(FPS) / 1000.0

video_writer.release()
pygame.quit()