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
R = 5.0       # big radius
r = 3.0       # small radius
d = 5.0       # distance from small circle

points_per_frame = 5
max_steps = 1000     # one flower's lifetime (1 full curve)
z_step_height = 30   # how much to move up before drawing next flower

# Camera
zoom = -200
yaw, pitch = 0, 0
last_mouse_pos = None
pan_x, pan_y = 0, 0

# Flowers stack
flowers = []      # list of list-of-points
current_flower = []
current_step = 0
current_z_offset = 0

# Colors
colors = [colorsys.hsv_to_rgb(h/360, 1, 1) for h in range(0, 360, 2)]


# =======================
# Generate single hypocycloid point
# =======================
def hypocycloid_3d(t, z_offset):
    x = (R - r) * math.cos(t) + d * math.cos((R - r) * t / r)
    y = (R - r) * math.sin(t) - d * math.sin((R - r) * t / r)

    # Add subtle vertical motion to make it 3D
    z = math.sin(t * 2) * 2 + z_offset
    return (x * 10, y * 10, z)


# =======================
# Add new points, manage new flowers
# =======================
def grow_flowers():
    global current_step, current_flower, current_z_offset

    for _ in range(points_per_frame):
        t = current_step * 0.02
        point = hypocycloid_3d(t, current_z_offset)
        current_flower.append(point)
        current_step += 1

        # When a flower finishes, lock it + start next
        if current_step >= max_steps:
            flowers.append(current_flower)
            current_flower = []
            current_step = 0
            current_z_offset += z_step_height  # go up!
            break


# =======================
# Draw a flower
# =======================
def draw_flower(points):
    glBegin(GL_LINE_STRIP)
    for i, (x, y, z) in enumerate(points):
        c = colors[i % len(colors)]
        glColor3f(*c)
        glVertex3f(x, y, z)
    glEnd()


# =======================
# MAIN RENDER LOOP
# =======================
def main():
    global zoom, yaw, pitch, last_mouse_pos, pan_x, pan_y

    pygame.init()
    pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("3D Hypocycloid Flower Generator with Z-Stepping")

    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, WIDTH / HEIGHT, 0.1, 5000.0)

    glEnable(GL_DEPTH_TEST)
    glLineWidth(3)

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            # Zoom
            elif event.type == pygame.MOUSEWHEEL:
                zoom += event.y * 10

            elif event.type == MOUSEBUTTONDOWN:
                last_mouse_pos = pygame.mouse.get_pos()

            elif event.type == MOUSEBUTTONUP:
                last_mouse_pos = None

            elif event.type == MOUSEMOTION and last_mouse_pos:
                x, y = pygame.mouse.get_pos()
                dx = x - last_mouse_pos[0]
                dy = y - last_mouse_pos[1]

                buttons = pygame.mouse.get_pressed()

                if buttons[0]:  # left = orbit
                    yaw += dx * 0.3
                    pitch += dy * 0.3
                elif buttons[1]:  # middle = pan
                    pan_x += dx * 0.3
                    pan_y -= dy * 0.3

                last_mouse_pos = (x, y)

        # Grow curves
        grow_flowers()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Camera transform
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(pan_x, pan_y, zoom)
        glRotatef(pitch, 1, 0, 0)
        glRotatef(yaw, 0, 0, 1)

        # Draw all previous flowers
        for flower in flowers:
            draw_flower(flower)

        # Draw current flower
        draw_flower(current_flower)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
