import pygame
import random
import cv2
import numpy as np
from constraint import which_constraint_zone

WIDTH = 1200
HEIGHT = WIDTH
FPS = 60
N_PARTICLES = 700
MIN_FURTHEST_PARTICLES = 6
REPULSION_RADIUS = 20
LINK_DISTANCE_RANGE = (10, 200)
MAX_LINKS_PER_PARTICLE = 6
LINK_THICKNESS = 1
BEZIER_CURVE_POINTS = 18
MAX_VELOCITY = 2
LIGHTEST_DARK_GREY = (80, 80, 80,128)
DARKEST_GREY = (128, 128, 128,200)

OUTSIDE_COLOR = [(100, 100, 100), (130, 130, 130), (30, 30, 30), (90, 90, 90)]
INSIDE_COLOR = (200, 200, 200)
WHITE = (180, 180, 180)
BLACK = (1, 11, 22)
DARK_BLUE = (0, 0, 128)
DARK_PURPLE = (64, 0, 64)
DARK_GREEN = (0, 64, 0)
COLORS = [DARK_BLUE, DARK_PURPLE, DARK_GREEN]
LINK_COLOR = (128, 128, 128)

class Link:
    def __init__(self, particles):
        self.particles = particles
        self.thickness = LINK_THICKNESS

    def is_valid(self):
        zones = [particle.zone for particle in self.particles]
        return len(set(zones)) == 1 and None not in zones

    def draw(self, screen):
        if len(self.particles) == 2:
            particle1, particle2 = self.particles
            self.draw_bezier_curve(screen, particle1.x, particle1.y, particle2.x, particle2.y, self.thickness)

    def draw_bezier_curve(self, screen, x1, y1, x2, y2, thickness):
        control_points = [(x1, y1), ((x1 + x2) // 2, (y1 + y2) // 2), (x2, y2)]
        curve_points = self.bezier_curve(control_points, BEZIER_CURVE_POINTS)

        if thickness == 1:
            link_color = LIGHTEST_DARK_GREY
        elif thickness == 4:
            link_color = DARKEST_GREY
        else:
            t = (thickness - 1) / 3
            link_color = tuple(int(start + t * (end - start)) for start, end in zip(LIGHTEST_DARK_GREY, DARKEST_GREY))

        pygame.draw.lines(screen, link_color, False, curve_points, thickness)

    def bezier_curve(self, control_points, num_points):
        curve_points = []
        for t in np.linspace(0, 1, num_points):
            x, y = self.bezier_point(control_points, t)
            curve_points.append((int(x), int(y)))
        return curve_points

    def bezier_point(self, control_points, t):
        n = len(control_points) - 1
        x, y = 0, 0
        for i, (px, py) in enumerate(control_points):
            coefficient = self.binomial(n, i) * (1 - t) ** (n - i) * t ** i
            x += coefficient * px
            y += coefficient * py
        return x, y

    def binomial(self, n, k):
        return np.math.factorial(n) // (np.math.factorial(k) * np.math.factorial(n - k))

class Particle:
    def __init__(self, x, y, velocity, color):
        self.x = x
        self.y = y
        self.velocity = velocity
        self.color = color
        self.zone = None
        self.links = []

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]

        if self.x <= 0 or self.x >= WIDTH:
            self.velocity[0] = -self.velocity[0]
        if self.y <= 0 or self.y >= HEIGHT:
            self.velocity[1] = -self.velocity[1]

        speed = np.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)
        if speed > MAX_VELOCITY:
            self.velocity[0] *= MAX_VELOCITY / speed
            self.velocity[1] *= MAX_VELOCITY / speed

        self.zone = which_constraint_zone(self.x, self.y, WIDTH)
        if self.zone is not None : 
            self.color=WHITE
    def draw(self, screen):
        size = max(1, 0.7*len(self.links)) if len(self.links) > 0 else 1
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

def generate_random_particle():
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)
    velocity_factor = 0.2
    velocity = [random.uniform(-1, 1), random.uniform(-1, 1)]
    velocity = [v * velocity_factor for v in velocity]
    color = (200,200,200,50)
    return Particle(x, y, velocity, color)

def distance(particle1, particle2):
    return np.sqrt((particle1.x - particle2.x) ** 2 + (particle1.y - particle2.y) ** 2)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

particles = [generate_random_particle() for _ in range(N_PARTICLES)]

video_writer = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), FPS, (WIDTH, HEIGHT))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0,0,0))

    for particle in particles:
        particle.update()

    for i in range(len(particles)):
        for j in range(i + 1, len(particles)):
            particle1 = particles[i]
            particle2 = particles[j]
            if particle1.zone == particle2.zone and particle1.zone is not None:
                dist = distance(particle1, particle2)
                if dist < REPULSION_RADIUS:
                    dx = particle1.x - particle2.x
                    dy = particle1.y - particle2.y
                    force = (REPULSION_RADIUS - dist) / REPULSION_RADIUS
                    force_x = dx / dist * force
                    force_y = dy / dist * force
                    particle1.velocity[0] += force_x
                    particle1.velocity[1] += force_y
                    particle2.velocity[0] -= force_x
                    particle2.velocity[1] -= force_y

    zones = set(particle.zone for particle in particles if particle.zone is not None)
    for zone in zones:
        zone_particles = [particle for particle in particles if particle.zone == zone]
        if len(zone_particles) >= MIN_FURTHEST_PARTICLES + 1:
            center_x = sum(particle.x for particle in zone_particles) / len(zone_particles)
            center_y = sum(particle.y for particle in zone_particles) / len(zone_particles)
            center_particle = min(zone_particles, key=lambda p: (p.x - center_x) ** 2 + (p.y - center_y) ** 2)

            furthest_particles = sorted(zone_particles, key=lambda p: (p.x - center_particle.x) ** 2 + (p.y - center_particle.y) ** 2)[-MIN_FURTHEST_PARTICLES:]

            for particle in furthest_particles:
                if len(center_particle.links) < MAX_LINKS_PER_PARTICLE and len(particle.links) < MAX_LINKS_PER_PARTICLE:
                    link = Link([center_particle, particle])
                    center_particle.links.append(link)
                    particle.links.append(link)

            for i in range(len(zone_particles)):
                for j in range(i + 1, len(zone_particles)):
                    particle1 = zone_particles[i]
                    particle2 = zone_particles[j]
                    dist = distance(particle1, particle2)
                    if LINK_DISTANCE_RANGE[0] <= dist <= LINK_DISTANCE_RANGE[1] and len(particle1.links) < MAX_LINKS_PER_PARTICLE and len(particle2.links) < MAX_LINKS_PER_PARTICLE:
                        link = Link([particle1, particle2])
                        particle1.links.append(link)
                        particle2.links.append(link)

            for particle in zone_particles:
                if len(set(link.particles[0] if link.particles[0] != particle else link.particles[1] for link in particle.links)) < 2:
                    available_particles = [p for p in zone_particles if p != particle and p not in [link.particles[0] if link.particles[0] != particle else link.particles[1] for link in particle.links]]
                    if len(available_particles) >= 2:
                        for i in range(2 - len(particle.links)):
                            other_particle = random.choice(available_particles)
                            link = Link([particle, other_particle])
                            particle.links.append(link)
                            other_particle.links.append(link)
                            available_particles.remove(other_particle)

    for particle in particles:
        merged_links = {}
        for link in particle.links:
            if len(link.particles) == 2:
                other_particle = link.particles[0] if link.particles[0] != particle else link.particles[1]
                if other_particle in merged_links:
                    merged_links[other_particle].thickness = min(merged_links[other_particle].thickness + LINK_THICKNESS, 4)  # Limit the thickness to a maximum of 4
                else:
                    merged_links[other_particle] = link
        particle.links = list(merged_links.values())

    for particle in particles:
        particle.links = [link for link in particle.links if link.is_valid()]

    for particle in particles:
        for link in particle.links:
            link.draw(screen)
    for particle in particles:
        particle.draw(screen)

    frame = np.array(pygame.surfarray.pixels3d(screen)).swapaxes(0, 1)

    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    video_writer.write(frame)

    pygame.display.flip()
    clock.tick(FPS)

video_writer.release()
pygame.quit()