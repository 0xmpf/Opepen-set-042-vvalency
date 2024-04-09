import pygame
import random
import cv2
import numpy as np
from constraint import is_constraint_zone

WIDTH = 1200
HEIGHT = WIDTH
OUTSIDE_COLOR = [(100, 100, 100), (130, 130, 130), (30, 30, 30), (90, 90, 90)]
INSIDE_COLOR = (200, 200, 200)
FPS = 450
N_PARTICLES = 30000
F_START = 400
F_END = 400
F_DURATION = 1  

WHITE = (255, 255, 255)
BLACK = (1, 11, 22)
DARK_BLUE = (0, 0, 128)
DARK_PURPLE = (64, 0, 64)
DARK_GREEN = (0, 64, 0)
COLORS = [DARK_BLUE, DARK_PURPLE, DARK_GREEN]

GRAVITY_SOURCES = [
    (3 * WIDTH // 8, 3 * WIDTH // 8),
    (5 * WIDTH // 8, 3 * WIDTH // 8),
    (4 * WIDTH // 8, 6 * WIDTH // 8)
]

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = 0
        self.vy = 0

    def update(self, F, particles):
        fx = 0
        fy = 0
        for source in GRAVITY_SOURCES:
            dx = source[0] - self.x
            dy = source[1] - self.y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance > 0:
                force = F / (distance ** 2)
                fx += force * dx / distance
                fy += force * dy / distance
        self.vx += fx
        self.vy += fy
        self.x += self.vx
        self.y += self.vy

        margin = WIDTH * 0.05
        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT :
            particles.remove(self)
            return

        if is_constraint_zone(self.x, self.y, WIDTH):
            self.color = INSIDE_COLOR
        else:
            self.color = random.choice(OUTSIDE_COLOR)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 1)

def generate_random_particle():
    margin = WIDTH * 0.05
    x = random.uniform(margin, WIDTH - margin)
    y = random.uniform(margin, WIDTH - margin)
    color = random.choice(OUTSIDE_COLOR)
    return Particle(x, y, color)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

particles = []

video_writer = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), FPS, (WIDTH, HEIGHT))

elapsed_time = 0.0

if len(particles) < N_PARTICLES:
    for i in range(N_PARTICLES):
        particles.append(generate_random_particle())

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    t = min(elapsed_time / F_DURATION, 1.0)
    F = F_START + (F_END - F_START) * t

    for particle in particles[:]:
        particle.update(F, particles)
        particle.draw(screen)

    frame = np.array(pygame.surfarray.pixels3d(screen)).swapaxes(0, 1)

    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    video_writer.write(frame)

    pygame.display.flip()
    elapsed_time += clock.tick(FPS) / 1000.0

video_writer.release()
pygame.quit()