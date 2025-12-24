import pygame

import random

import math

import time

from noise import pnoise3

from PIL import Image, UnidentifiedImageError

import numpy as np

import os

 

# Pygame setup

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1600, 900

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption("Optimized Cosmic Particle Simulation")

clock = pygame.time.Clock()

 

# Constants

BACKGROUND_COLOR = (0, 0, 0)

PARTICLE_LIMIT = 5000

PROJECTION_SCALE = 600

ZOOM_LEVEL = 0.4

FALLBACK_IMAGE = False  # Used if image file not found

 

# Particle class

class Satellite:

    def __init__(self, x, y, z):

        self.x, self.y, self.z = x, y, z

        self.vx = random.uniform(-1, 1)

        self.vy = random.uniform(-1, 1)

        self.vz = random.uniform(-1, 1)

        self.radius = 2

        self.trail = []

 

    def apply_noise_wind(self):

        scale = 0.004

        t = time.time() * 0.2

        self.vx += pnoise3(self.x * scale, self.y * scale, t) * 0.2

        self.vy += pnoise3(self.y * scale, self.z * scale, t) * 0.2

        self.vz += pnoise3(self.z * scale, self.x * scale, t) * 0.2

 

    def apply_dancing_gravity(self):

        t = time.time()

        cx = 150 * math.sin(t * 0.3)

        cy = 150 * math.cos(t * 0.4)

        cz = 100 * math.sin(t * 0.25)

        dx, dy, dz = cx - self.x, cy - self.y, cz - self.z

        dist = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2) + 1.0  # Avoid division by zero

        force = 100 / (dist * dist)

        self.vx += dx * force

        self.vy += dy * force

        self.vz += dz * force

 

    def update(self):

        decay = 0.995

        self.vx *= decay

        self.vy *= decay

        self.vz *= decay

 

        self.x += self.vx

        self.y += self.vy

        self.z += self.vz

 

        self.trail.append((self.x, self.y, self.z))

        self.trail = self.trail[-10:]

 

    def dynamic_color(self):

        t = time.time()

        phase = self.x * 0.01 + self.z * 0.01 + t * 0.5

        R = int(127 + 128 * math.sin(phase)) % 256

        G = int(127 + 128 * math.sin(phase + 2)) % 256

        B = int(127 + 128 * math.sin(phase + 4)) % 256

        return (R, G, B)

 

    def project(self, x, y, z):

        if z > -PROJECTION_SCALE + 1:

            scale = PROJECTION_SCALE / (z + PROJECTION_SCALE)

        else:

            scale = 0.0001  # Prevent explosion in projection

        px = int(x * scale * ZOOM_LEVEL + SCREEN_WIDTH / 2)

        py = int(y * scale * ZOOM_LEVEL + SCREEN_HEIGHT / 2)

        return px, py

 

    def draw(self, surface):

        color = self.dynamic_color()

        px, py = self.project(self.x, self.y, self.z)

 

        if 0 <= px < SCREEN_WIDTH and 0 <= py < SCREEN_HEIGHT:

            pygame.draw.circle(surface, color, (px, py), self.radius)

 

        for i, (tx, ty, tz) in enumerate(self.trail):

            trail_x, trail_y = self.project(tx, ty, tz)

            if 0 <= trail_x < SCREEN_WIDTH and 0 <= trail_y < SCREEN_HEIGHT:

                alpha = max(0.1, 1.0 - i / len(self.trail))

                faded = (

                    int(color[0] * alpha),

                    int(color[1] * alpha),

                    int(color[2] * alpha)

                )

                pygame.draw.circle(surface, faded, (trail_x, trail_y), max(1, self.radius - 1))

 

# Image-based initialization

def image_to_particles(image_path, max_particles=PARTICLE_LIMIT):

    global FALLBACK_IMAGE

    particles = []

 

    try:

        img = Image.open(image_path).convert('L').resize((100, 100))

        data = img.load()

 

        for y in range(img.height):

            for x in range(img.width):

                if data[x, y] < 100:

                    sx = (x - 50) * 6

                    sy = (y - 50) * 6

                    sz = random.uniform(-10, 10)

                    p = Satellite(sx, sy, sz)

                    particles.append(p)

                    if len(particles) >= max_particles:

                        return particles

    except (FileNotFoundError, UnidentifiedImageError):

        FALLBACK_IMAGE = True

        print("Image not found — generating random cloud.")

        for _ in range(max_particles):

            particles.append(Satellite(

                random.uniform(-300, 300),

                random.uniform(-300, 300),

                random.uniform(-300, 300)))

    return particles

 

# Fourier spectrum

def compute_velocity_spectrum(satellites):

    v_mags = [math.sqrt(s.vx**2 + s.vy**2 + s.vz**2) for s in satellites]

    spectrum = np.fft.fft(v_mags)

    print("Fourier Spectrum (first 10 freqs):")

    for i in range(1, min(15, len(spectrum))):

        print(f"Freq {i:>2}: Amplitude {abs(spectrum[i]):.2f}")

 

# Keyboard controls

def handle_events():

    global ZOOM_LEVEL, running

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            return False

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_UP:

                ZOOM_LEVEL = min(ZOOM_LEVEL + 0.1, 3.0)

            elif event.key == pygame.K_DOWN:

                ZOOM_LEVEL = max(ZOOM_LEVEL - 0.1, 0.1)

            elif event.key == pygame.K_f:

                compute_velocity_spectrum(satellites)

            elif event.key == pygame.K_ESCAPE:

                return False

    return True

 

# Initialize particles

satellites = image_to_particles("your_image.png")

 

# Main loop

running = True

while running:

    running = handle_events()

    screen.fill(BACKGROUND_COLOR)

 

    for s in satellites:

        s.apply_noise_wind()

        s.apply_dancing_gravity()

        s.update()

        s.draw(screen)

 

    pygame.display.flip()

    clock.tick(30)

 

pygame.quit()