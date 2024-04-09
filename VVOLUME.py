import pygame
import numpy as np
import math
import cv2
from constraint import is_constraint_zone

WIDTH, HEIGHT = 1200, 1200
RADIUS = 3 * WIDTH / 4  
FPS = 60
N_LINES= 3
BACKGROUND_COLOR = (0, 0, 0)
PARTICLE_COLOR = (255, 255, 255)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

fourcc = cv2.VideoWriter_fourcc(*'mp4v')  
video_writer = cv2.VideoWriter('output.mp4', fourcc, FPS, (WIDTH, HEIGHT))


def create_sphere_particles(lat_lines, long_lines, radius):
    particles = []
    for i in range(lat_lines):
        lat = math.pi * i / lat_lines - math.pi / 2
        for j in range(int(long_lines * math.cos(lat))):  
            long = 2 * math.pi * j / (long_lines * math.cos(lat) if math.cos(lat) > 0 else 1)
            x = radius * math.cos(lat) * math.cos(long)
            y = radius * math.cos(lat) * math.sin(long)
            z = radius * math.sin(lat)
            particles.append([x, y, z])
    return np.array(particles)

def rotate_y(particles, angle):
    rotation_matrix = np.array([[math.cos(angle), 0, math.sin(angle)],
                                [0, 1, 0],
                                [-math.sin(angle), 0, math.cos(angle)]])
    return np.dot(particles, rotation_matrix)

def project(particles):
    fov = WIDTH  
    distance = WIDTH 
    for i in range(len(particles)):
        particles[i][0] = (fov * particles[i][0]) / (distance + particles[i][2]) + WIDTH / 2
        particles[i][1] = (fov * particles[i][1]) / (distance + particles[i][2]) + HEIGHT / 2
    return particles

def draw_particles(particles):
    for particle in particles:
        in_constraint_zone = is_constraint_zone(particle[0], particle[1], WIDTH)
        depth = (particle[2] + RADIUS) / (2 * RADIUS)  

        if depth > 0.5:  
            depth_color = 190
            size = 1  
        else:
            depth_color = max(0, 255 - (255 * depth))  
            size = 1 

        if in_constraint_zone:
            depth_color = 255
            size = 3 

        color = (depth_color, depth_color, depth_color)  
        pygame.draw.circle(screen, color, (int(particle[0]), int(particle[1])), size)

particles = create_sphere_particles(N_LINES*16, N_LINES*32, RADIUS / 2)  

angle = 0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill(BACKGROUND_COLOR)
    
    rotated_particles = rotate_y(particles, angle)
    projected_particles = project(rotated_particles.copy())
    draw_particles(projected_particles)
    
    frame = np.array(pygame.surfarray.array3d(pygame.display.get_surface()))
    frame = cv2.transpose(frame)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    video_writer.write(frame)

    pygame.display.flip()
    clock.tick(FPS)
    
    angle += math.pi / 180  

pygame.quit()
