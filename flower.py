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

# Hypocycloid parameters
R_big = 200     # Radius of fixed circle
r_small = 60    # Rolling circle radius
d = 120         # Point distance from circle center

growth_speed = 0.03
points_per_frame = 4
z_growth = 0.2

# Camera
zoom = -800        # starting zoom
cam_x = 0
cam_y = 0
rot_x = 0
rot_y = 0

# Mouse
dragging = False
panning = False
last_mouse = (0, 0)

# Path
path = []
t_value = 0.0

def depth_color(z):
    """Depth-based hue cycling."""
    hue = (z * 0.004) % 1.0
    return colorsys.hsv_to_rgb(hue, 1, 1)

def add_points():
    """Grow the hypocycloid path over time."""
    global t_value

    for _ in range(points_per_frame):
        t = t_value

        # Hypocycloid parametric
        x = (R_big - r_small) * math.cos(t) + d * math.cos(((R_big - r_small) / r_small) * t)
        y = (R_big - r_small) * math.sin(t) - d * math.sin(((R_big - r_small) / r_small) * t)
        z = t * z_growth

        path.append((x, y, z))

        t_value += growth_speed


def draw_path():
    glBegin(GL_LINE_STRIP)
    for x, y, z in path:
        glColor3f(*depth_color(z))
        glVertex3f(x, y, z)
    glEnd()


def main():
    global zoom, cam_x, cam_y, dragging, panning, last_mouse, rot_x, rot_y

    pygame.init()
    pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Hypocycloid 3D Growing Path")

    # Setup projection
    glMatrixMode(GL_PROJECTION)
    gluPerspective(60, WIDTH / HEIGHT, 0.1, 10000.0)

    # OpenGL state
    glEnable(GL_DEPTH_TEST)
    glLineWidth(3)

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            # Mouse wheel zoom
            if event.type == pygame.MOUSEWHEEL:
                zoom += event.y * 30

            # Mouse button down
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: dragging = True
                if event.button == 2: panning = True
                last_mouse = pygame.mouse.get_pos()

            # Mouse button up
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: dragging = False
                if event.button == 2: panning = False

            # Mouse motion
            if event.type == pygame.MOUSEMOTION:
                mx, my = pygame.mouse.get_pos()
                dx = mx - last_mouse[0]
                dy = my - last_mouse[1]

                if dragging:
                    rot_x += dy * 0.3
                    rot_y += dx * 0.3

                if panning:
                    cam_x += dx * 0.5
                    cam_y -= dy * 0.5

                last_mouse = (mx, my)

        # Grow curve
        add_points()

        # Clear frame
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Reset camera
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Translate camera
        glTranslatef(cam_x, cam_y, zoom)

        # Rotate view
        glRotatef(rot_x, 1, 0, 0)
        glRotatef(rot_y, 0, 1, 0)

        # Draw the hypocycloid
        draw_path()

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
