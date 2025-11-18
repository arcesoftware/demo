import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import random
import colorsys

# =======================
# CONFIG
# =======================
WIDTH, HEIGHT = 1200, 800
points_per_frame = 5       # Growth speed per loop
loop_growth_z = 0.5        # Z increment per step
split_probability = 0.002  # Probability of loop splitting
merge_distance = 10.0      # Distance threshold for merging loops
twist_amplitude = 20.0     # Max X/Y/Z perturbation
max_loops = 20             # Max number of simultaneous loops

# Spirograph parameters
R = 200      # Outer circle
k = 0.3      # r/R
l = 0.8      # relative pen position

# Camera settings
camera_distance = 1000
camera_lerp = 0.05
zoom_speed = 20.0
last_mouse_pos = None
rotation_x, rotation_y = 0, 0
pan_x, pan_y = 0, 0

# Color palette
colors = [colorsys.hsv_to_rgb(h/360, 1, 1) for h in range(0, 360, 2)]

# =======================
# LOOP STATE
# =======================
class Loop:
    def __init__(self, phase=0.0):
        self.points = []
        self.phase = phase    # initial t offset
        self.step = 0
        self.cycle = 0
        self.active = True

loops = [Loop()]

camera_z = 0

# =======================
# FUNCTIONS
# =======================
def add_new_points():
    """Extend all loops and possibly split/merge dynamically"""
    new_loops = []
    for loop in loops:
        if not loop.active:
            continue
        for _ in range(points_per_frame):
            t = loop.step * 0.05 + loop.phase
            # Base spirograph equations
            x_c = (R*(1 - k)) * math.cos(t)
            y_c = (R*(1 - k)) * math.sin(t)
            t_prime = ((1 - k)/k) * t
            x = x_c + (l*k*R) * math.cos(t_prime)
            y = y_c - (l*k*R) * math.sin(t_prime)
            z = loop.step*loop_growth_z + loop.cycle*10.0
            # Add twist perturbation for dynamic evolution
            x += math.sin(loop.step*0.1 + random.random())*twist_amplitude
            y += math.cos(loop.step*0.1 + random.random())*twist_amplitude
            z += math.sin(loop.step*0.05 + random.random())*twist_amplitude*0.5
            loop.points.append((x,y,z))
            loop.step += 1
            # New cycle for Z lift
            if loop.step >= 600:
                loop.step = 0
                loop.cycle += 1

        # Randomly split loops
        if len(loops) + len(new_loops) < max_loops and random.random() < split_probability:
            new_loop = Loop(phase=loop.phase + random.uniform(0, 2*math.pi))
            new_loops.append(new_loop)
    loops.extend(new_loops)

    # Optional: merge loops that are close
    for i, loop1 in enumerate(loops):
        for j, loop2 in enumerate(loops):
            if i >= j or not loop1.active or not loop2.active:
                continue
            if len(loop1.points)==0 or len(loop2.points)==0:
                continue
            p1 = loop1.points[-1]
            p2 = loop2.points[-1]
            dist = math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)
            if dist < merge_distance:
                # Merge: deactivate one loop
                loop2.active = False

def draw_loops():
    """Draw all active loops with depth-based color"""
    glBegin(GL_LINE_STRIP)
    for loop in loops:
        for idx, (x, y, z) in enumerate(loop.points):
            z_color_factor = (z % 500)/500
            c = colors[idx % len(colors)]
            glColor3f(c[0]*z_color_factor, c[1]*z_color_factor, c[2]*z_color_factor)
            glVertex3f(x, y, z)
    glEnd()

# =======================
# MAIN LOOP
# =======================
def main():
    global camera_z, rotation_x, rotation_y, pan_x, pan_y, last_mouse_pos, camera_distance

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF|OPENGL)
    pygame.display.set_caption("Perelman-inspired Evolving 3D Spirograph")

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
            # Zoom
            if event.type == pygame.MOUSEWHEEL:
                camera_distance += -event.y*zoom_speed
            # Mouse grab
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in [1,2,3]:
                    last_mouse_pos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONUP:
                last_mouse_pos = None
            if event.type == pygame.MOUSEMOTION and last_mouse_pos:
                dx, dy = event.pos[0]-last_mouse_pos[0], event.pos[1]-last_mouse_pos[1]
                buttons = pygame.mouse.get_pressed()
                if buttons[0]:  # rotate
                    rotation_y += dx*0.3
                    rotation_x += dy*0.3
                if buttons[1]:  # pan
                    pan_x += dx*0.5
                    pan_y -= dy*0.5
                last_mouse_pos = event.pos

        # Update loops
        add_new_points()

        # Camera follows the tallest Z
        tip_z = max([loop.points[-1][2] for loop in loops if loop.points], default=0)
        target_camera_z = tip_z + camera_distance
        global camera_z
        camera_z += (target_camera_z - camera_z) * camera_lerp

        # Reset view
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(-pan_x, -pan_y, -camera_z)
        glRotatef(rotation_x, 1,0,0)
        glRotatef(rotation_y, 0,1,0)

        # Draw scene
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        draw_loops()
        pygame.display.flip()

    pygame.quit()

if __name__=="__main__":
    main()
