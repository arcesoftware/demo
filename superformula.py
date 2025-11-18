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
points_per_frame = 5
z_growth_per_cycle = 1.0
cycle_steps = 600

# Superformula parameters
a, b = 1, 1
m, n1, n2, n3 = 6, 0.3, 1.7, 1.7  # You can experiment with these
scale = 200

# Camera
camera_distance = 1000
camera_lerp = 0.05
zoom_speed = 20.0

# Mouse control
last_mouse_pos = None
rotation_x, rotation_y = 0, 0
pan_x, pan_y = 0, 0

# Colors
colors = [colorsys.hsv_to_rgb(h/360, 1, 1) for h in range(0, 360, 2)]

# =======================
# STATE
# =======================
points = []
current_step = 0
current_cycle = 0
camera_z = 0

# =======================
# FUNCTIONS
# =======================
def superformula(theta):
    """Compute the radius r for a given angle theta using the superformula."""
    part1 = abs(math.cos(m * theta / 4) / a) ** n2
    part2 = abs(math.sin(m * theta / 4) / b) ** n3
    r = (part1 + part2) ** (-1 / n1)
    return r

def add_new_points():
    global current_step, current_cycle, points

    for _ in range(points_per_frame):
        t = current_step * (2*math.pi/cycle_steps)  # step in one cycle

        # Superformula radius
        r = superformula(t)
        # Map to 3D spiral along Z
        x = scale * r * math.cos(t * 5)  # twisting factor
        y = scale * r * math.sin(t * 5)
        z = current_cycle * z_growth_per_cycle + 5 * math.sin(3*t)  # small vertical oscillation

        points.append((x, y, z))

        current_step += 1
        if current_step >= cycle_steps:
            current_step = 0
            current_cycle += 1  # Move up in Z for new cycle

def draw_points():
    glBegin(GL_LINE_STRIP)
    for idx, (x, y, z) in enumerate(points):
        z_color_factor = (z % (z_growth_per_cycle*10)) / (z_growth_per_cycle*10)
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
    pygame.display.set_caption("3D Superformula Line")

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
            if event.type == pygame.MOUSEWHEEL:
                camera_distance += -event.y * zoom_speed
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in [1,2,3]:
                    last_mouse_pos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONUP:
                last_mouse_pos = None
            if event.type == pygame.MOUSEMOTION and last_mouse_pos:
                dx, dy = event.pos[0]-last_mouse_pos[0], event.pos[1]-last_mouse_pos[1]
                buttons = pygame.mouse.get_pressed()
                if buttons[0]:
                    rotation_y += dx * 0.3
                    rotation_x += dy * 0.3
                if buttons[1]:
                    pan_x += dx * 0.5
                    pan_y -= dy * 0.5
                last_mouse_pos = event.pos

        add_new_points()

        tip_z = points[-1][2] if points else 0
        target_camera_z = tip_z + camera_distance
        camera_z += (target_camera_z - camera_z) * camera_lerp

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(-pan_x, -pan_y, -camera_z)
        glRotatef(rotation_x, 1,0,0)
        glRotatef(rotation_y, 0,1,0)

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        draw_points()
        pygame.display.flip()

    pygame.quit()

if __name__=="__main__":
    main()
