import pygame
import random
import cv2
import numpy as np
from constraint import is_constraint_zone

WIDTH = 1200
HEIGHT = WIDTH
FPS = 60
N_WORDS_PER_DEPTH_SMALL = 150 
N_WORDS_PER_DEPTH_BIG = 30  
MIN_SPEED = 2
MAX_SPEED = 8
MIN_HEIGHT = 0
MAX_HEIGHT = 1000
LETTER_SPACING = 15
CONSTRAINT_ZONE_COLOR = (255, 255, 255, 128) 

DARKEST_DARK_GREY = (5, 5, 5)
LIGHTEST_DARK_GREY = (80, 80, 80)
LIGHT_GREY = (192, 192, 192)
WEIRD_CHARS = "!@#$%^&*()_+{}[]|\\:<>?/"

with open("bip32_words.txt", "r") as file:
    BIP32_WORDS = file.read().splitlines()

class Word:
    def __init__(self, x, y, text, speed, height, depth, is_big):
        self.x = x
        self.y = y
        self.original_text = text
        self.text = text
        self.speed = speed
        self.height = height
        self.is_big = is_big
        if is_big:
            self.size = int(2 ** (2/3 * self.speed))  
        else:
            self.size = int(2 ** (1/4 * self.speed))  
        self.depth = depth

    def update(self):
        self.y += self.speed

        for i in range(len(self.text)):
            if is_constraint_zone(self.x + i * LETTER_SPACING, self.y, WIDTH):
                weird_char = random.choice(WEIRD_CHARS)
                if self.text[i] != weird_char:
                    self.text = self.text[:i] + weird_char + self.text[i+1:]
            else:
                if self.text[i] != self.original_text[i]:
                    self.text = self.text[:i] + self.original_text[i] + self.text[i+1:]

    def draw(self, screen, font):
        scaling_factor = font.get_height() / 36
        letter_spacing = int(LETTER_SPACING * scaling_factor)

        for i in range(len(self.text)):
            if is_constraint_zone(self.x + i * letter_spacing, self.y, WIDTH):
                color = LIGHT_GREY
            else:
                speed_ratio = (self.speed - MIN_SPEED) / (MAX_SPEED - MIN_SPEED)
                color = tuple(int(c * (1 - speed_ratio) + d * speed_ratio) for c, d in zip(DARKEST_DARK_GREY, LIGHTEST_DARK_GREY))
            char_surface = font.render(self.text[i], True, color)
            screen.blit(char_surface, (self.x + i * letter_spacing, self.y))

def generate_words_at_depth(depth):
    words = []
    for _ in range(N_WORDS_PER_DEPTH_SMALL):
        x = random.uniform(0, WIDTH)
        y = -random.randint(MIN_HEIGHT, MAX_HEIGHT)
        text = random.choice(BIP32_WORDS)
        speed = MIN_SPEED + depth * ((MAX_SPEED - MIN_SPEED) / (MAX_SPEED - 1))
        height_factor = 30
        height = height_factor ** speed
        word = Word(x, y, text, speed, height, depth, is_big=False)
        words.append(word)

    for _ in range(N_WORDS_PER_DEPTH_BIG):
        x = random.uniform(0, WIDTH)
        y = -random.randint(MIN_HEIGHT, MAX_HEIGHT)
        text = random.choice(BIP32_WORDS)
        speed = MIN_SPEED + depth * ((MAX_SPEED - MIN_SPEED) / (MAX_SPEED - 1))
        height_factor = 30
        height = height_factor ** speed
        word = Word(x, y, text, speed, height, depth, is_big=True)
        words.append(word)

    return words

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

words = []
for depth in range(MAX_SPEED):
    words.extend(generate_words_at_depth(depth))

video_writer = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), FPS, (WIDTH, HEIGHT))

font_path = "font.ttf"

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    for word in words:
        word.update()
        font_size = word.size
        if not word.is_big and font_size <= 8:  
            font_size = 8
        font = pygame.font.Font(font_path, font_size)
        word.draw(screen, font)

        if word.y > HEIGHT:
            words.remove(word)
            if word.is_big:
                words.append(generate_words_at_depth(word.depth)[-1])  
            else:
                words.append(generate_words_at_depth(word.depth)[0])  

    words.sort(key=lambda word: word.depth, reverse=True)

    frame = np.array(pygame.surfarray.pixels3d(screen)).swapaxes(0, 1)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    video_writer.write(frame)

    pygame.display.flip()
    clock.tick(FPS)

video_writer.release()
pygame.quit()