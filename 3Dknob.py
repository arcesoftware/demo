import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import colorsys

# =======================
# CONFIG
# =======================
WIDTH, HEIGHT = 1200, 800
points_per_frame = 5     # How many new points are added per frame
z_growth_per_cycle = 1.0 # How much Z increases after a full cycle
cycle_steps = 600        # Steps per full harmonic cycle

# Harmonic orbit parameters (3D Lissajous)
A, B, C = 200, 200, 200
a, b, c = 5, 4, 3        # Frequencies
delta_x, delta_y, delta_z = 0, math.pi/2, math.pi/4  # Phase offsets

# Camera settings
camera_distance = 1000
camera_lerp = 0.05
zoom_speed = 20.0

# Mouse control state
last_mouse_pos = None
rotation_x, rotation_y = 0, 0
pan_x, pan_y = 0, 0

# Colors: rainbow for depth
colors = [colorsys.hsv_to_rgb(h/360, 1, 1) for h in range(0, 360, 2)]

# =======================
# SPIRAL STATE
# =======================
points = []
current_step = 0
current_cycle = 0
camera_z = 0

# =======================
# FUNCTIONS
# =======================
def add_new_points():
    """Add points for harmonic orbit and lift Z after each full cycle."""
    global current_step, current_cycle, points
    
    for _ in range(points_per_frame):
        t = current_step * (2*math.pi/cycle_steps)
        
        x = A * math.sin(a*t + delta_x)
        y = B * math.sin(b*t + delta_y)
        z = C * math.sin(c*t + delta_z) + current_cycle * z_growth_per_cycle
        
        points.append((x, y, z))
        
        current_step += 1
        if current_step >= cycle_steps:
            current_step = 0
            current_cycle += 1  # Lift Z for new cycle

def draw_points():
    """Draw the persistent harmonic orbit with depth-based color."""
    glBegin(GL_LINE_STRIP)
    for idx, (x, y, z) in enumerate(points):
        # Depth-based color shift: fade with Z
        z_color_factor = (z % (z_growth_per_cycle*10)) / (z_growth_per_cycle*10)
        c = colors[idx % len(colors)]
        glColor3f(c[0]*z_color_factor, c[1]*z_color_factor, c[2]*z_color_factor)
        glVertex3f(x, y, z)
    glEnd()

# =======================
# MAIN LOOP
# =======================

global camera_distance

def main():
    global camera_z, rotation_x, rotation_y, pan_x, pan_y, last_mouse_pos, camera_distance

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF|OPENGL)
    pygame.display.set_caption("3D Harmonic Orbit")

    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (WIDTH/HEIGHT), 0.1, 5000.0)
    glEnable(GL_DEPTH_TEST)
    glLineWidth(2)

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Zoom with mouse wheel
            if event.type == pygame.MOUSEWHEEL:
                camera_distance += -event.y * zoom_speed
            # Mouse grab rotation
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in [1, 2, 3]:  # left/middle/right
                    last_mouse_pos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONUP:
                last_mouse_pos = None
            if event.type == pygame.MOUSEMOTION and last_mouse_pos:
                dx, dy = event.pos[0]-last_mouse_pos[0], event.pos[1]-last_mouse_pos[1]
                buttons = pygame.mouse.get_pressed()
                if buttons[0]:  # Left drag: rotate
                    rotation_y += dx * 0.3
                    rotation_x += dy * 0.3
                if buttons[1]:  # Middle drag: pan
                    pan_x += dx * 0.5
                    pan_y -= dy * 0.5
                last_mouse_pos = event.pos

        # Add points
        add_new_points()

        # Smooth camera following Z (optional: could track the tip)
        tip_z = points[-1][2] if points else 0
        target_camera_z = tip_z + camera_distance
        camera_z += (target_camera_z - camera_z) * camera_lerp

        # Reset view
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Apply camera transforms
        glTranslatef(-pan_x, -pan_y, -camera_z)
        glRotatef(rotation_x, 1,0,0)
        glRotatef(rotation_y, 0,1,0)

        # Draw scene
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        draw_points()
        pygame.display.flip()

    pygame.quit()

if __name__=="__main__":
    main()
