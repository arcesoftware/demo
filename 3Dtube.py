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
R = 150         # Major radius (torus)
r = 50          # Minor radius (tube)
points_per_frame = 5
turns_theta = 4
turns_phi = 6.85
z_growth_per_point = 0.3

# Camera state
zoom = -400.0
zoom_speed = 40
camera_x = 0
camera_y = 0
pan_x = 0
pan_y = 0
rot_x = 0
rot_y = 0

dragging_left = False
dragging_middle = False
last_mouse_x = 0
last_mouse_y = 0

# Generate rainbow colors
colors = [colorsys.hsv_to_rgb(h/360, 1, 1) for h in range(0, 360, 2)]

spiral1 = []
spiral2 = []
current_step = 0

# =======================
# Spiral Growth
# =======================
def add_new_points():
    global current_step
    for _ in range(points_per_frame):
        step = current_step / 100.0

        theta = 2 * math.pi * turns_theta * step
        phi = 2 * math.pi * turns_phi * step

        # Spiral 1
        x1 = (R + r * math.cos(phi)) * math.cos(theta)
        y1 = (R + r * math.cos(phi)) * math.sin(theta)
        z1 = r * math.sin(phi) + z_growth_per_point * current_step
        spiral1.append((x1, y1, z1))

        # Spiral 2 (opposite side)
        phi2 = phi + math.pi
        x2 = (R + r * math.cos(phi2)) * math.cos(theta)
        y2 = (R + r * math.cos(phi2)) * math.sin(theta)
        z2 = r * math.sin(phi2) + z_growth_per_point * current_step
        spiral2.append((x2, y2, z2))

        current_step += 1

# =======================
# Depth-based Color
# =======================
def depth_color(base_color, z, camera_z):
    # Distance → 0…1
    d = max(0.0, min(1.0, (z - camera_z + 200) / 800))

    # Closer = brighter + warmer
    hue_shift = 0.15 * (1 - d)  # small hue shift
    scale = 0.3 + 0.7 * (1 - d)  # brightness

    r, g, b = base_color
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    h = (h + hue_shift) % 1.0
    v *= scale

    return colorsys.hsv_to_rgb(h, s, v)

# =======================
# Drawing
# =======================
def draw_spiral(points, camera_z):
    glBegin(GL_LINE_STRIP)
    for idx, (x, y, z) in enumerate(points):
        base_c = colors[idx % len(colors)]
        c = depth_color(base_c, z, camera_z)
        glColor3f(*c)
        glVertex3f(x, y, z)
    glEnd()

# =======================
# MAIN
# =======================
def main():
    global zoom, rot_x, rot_y, pan_x, pan_y
    global dragging_left, dragging_middle
    global last_mouse_x, last_mouse_y

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Torus Spiral – Zoom, Pan, Orbit")

    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, WIDTH / HEIGHT, 0.1, 5000.0)
    glEnable(GL_DEPTH_TEST)
    glLineWidth(3)

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            # ====================
            # Mouse wheel → Zoom
            # ====================
            if event.type == pygame.MOUSEWHEEL:
                zoom += event.y * zoom_speed

            # ====================
            # Mouse pressing
            # ====================
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragging_left = True
                if event.button == 2:
                    dragging_middle = True
                last_mouse_x, last_mouse_y = event.pos

            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    dragging_left = False
                if event.button == 2:
                    dragging_middle = False

            # ====================
            # Mouse motion → Orbit + Pan
            # ====================
            if event.type == MOUSEMOTION:
                mx, my = event.pos
                dx = mx - last_mouse_x
                dy = my - last_mouse_y

                if dragging_left:
                    rot_x += dy * 0.3
                    rot_y += dx * 0.3

                if dragging_middle:
                    pan_x += dx * 0.5
                    pan_y -= dy * 0.5

                last_mouse_x, last_mouse_y = mx, my

        # Grow spirals
        add_new_points()

        # Background
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Camera Transform
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glTranslatef(pan_x, pan_y, zoom)
        glRotatef(rot_x, 1, 0, 0)
        glRotatef(rot_y, 0, 1, 0)

        # Draw spirals
        camera_z = -zoom
        draw_spiral(spiral1, camera_z)
        draw_spiral(spiral2, camera_z)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
