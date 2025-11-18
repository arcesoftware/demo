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

# Lorenz parameters (classic chaotic regime)
SIGMA = 10.0
RHO = 28.0
BETA = 8.0 / 3.0

DT = 0.008              # integration timestep per small RK4 substep
SUBSTEPS = 1            # how many RK4 substeps per appended point (increase for smoother integration)
POINTS_PER_FRAME = 6    # how many points to append each frame (controls drawing speed)
SCALE = 6.0             # scales the attractor to screen size

# Camera initial values
zoom = -60.0 * SCALE    # camera Z (negative away from origin)
pan_x = 0.0
pan_y = 0.0
yaw = 0.0    # rotate around Z axis (horizontal)
pitch = 0.0  # rotate around X axis (vertical)

# Interaction state
dragging = False
panning_mouse = False
last_mouse = (0, 0)

# Persistent drawing
points = []         # list of (x,y,z) tuples
MAX_POINTS = None   # set to e.g. 200_000 to cap memory, or None for unlimited

# Color palette (HSV -> RGB)
def depth_color(z):
    """Map Z to a hue and brightness for depth effect."""
    # Normalize z roughly to a range for hue mapping — tweak divisor for look
    hue = (0.5 + 0.02 * z) % 1.0
    # brightness depends on z distance (closer = brighter)
    value = 0.6 + 0.4 * (1.0 - (abs(z) / 40.0))
    value = max(0.18, min(1.0, value))
    r, g, b = colorsys.hsv_to_rgb(hue, 0.95, value)
    return r, g, b

# =======================
# Lorenz RK4 integration
# =======================
def lorenz_deriv(x, y, z):
    dx = SIGMA * (y - x)
    dy = x * (RHO - z) - y
    dz = x * y - BETA * z
    return dx, dy, dz

def rk4_step(x, y, z, dt):
    k1x, k1y, k1z = lorenz_deriv(x, y, z)
    k1x *= dt; k1y *= dt; k1z *= dt

    k2x, k2y, k2z = lorenz_deriv(x + 0.5 * k1x, y + 0.5 * k1y, z + 0.5 * k1z)
    k2x *= dt; k2y *= dt; k2z *= dt

    k3x, k3y, k3z = lorenz_deriv(x + 0.5 * k2x, y + 0.5 * k2y, z + 0.5 * k2z)
    k3x *= dt; k3y *= dt; k3z *= dt

    k4x, k4y, k4z = lorenz_deriv(x + k3x, y + k3y, z + k3z)
    k4x *= dt; k4y *= dt; k4z *= dt

    xn = x + (k1x + 2*k2x + 2*k3x + k4x) / 6.0
    yn = y + (k1y + 2*k2y + 2*k3y + k4y) / 6.0
    zn = z + (k1z + 2*k2z + 2*k3z + k4z) / 6.0
    return xn, yn, zn

# Initialize Lorenz seed
x = 0.1
y = 0.0
z = 0.0

# Start with a few points so something is visible immediately
for _ in range(80):
    x, y, z = rk4_step(x, y, z, DT)
    points.append((x * SCALE, y * SCALE, z * SCALE))

# =======================
# OpenGL helpers
# =======================
def draw_line_strip(pt_list):
    glBegin(GL_LINE_STRIP)
    for (i, (xx, yy, zz)) in enumerate(pt_list):
        c = depth_color(zz / SCALE)  # pass z in original units
        glColor3f(*c)
        glVertex3f(xx, yy, zz)
    glEnd()

# =======================
# Main loop
# =======================
def main():
    global x, y, z
    global zoom, pan_x, pan_y, yaw, pitch
    global dragging, panning_mouse, last_mouse, points

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Lorenz Attractor — Continuous 3D Drawing")

    # Projection
    glMatrixMode(GL_PROJECTION)
    gluPerspective(60.0, WIDTH / HEIGHT, 0.1, 10000.0)
    glEnable(GL_DEPTH_TEST)
    glLineWidth(2.0)

    clock = pygame.time.Clock()
    running = True

    while running:
        dt_frame = clock.tick(60) / 1000.0

        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            elif event.type == pygame.MOUSEWHEEL:
                # zoom in/out (mouse wheel y positive = up)
                zoom += -event.y * 10.0

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # left
                    dragging = True
                if event.button == 2:  # middle
                    panning_mouse = True
                last_mouse = event.pos

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
                if event.button == 2:
                    panning_mouse = False

            elif event.type == MOUSEMOTION:
                if last_mouse is None:
                    last_mouse = event.pos
                mx, my = event.pos
                dx = mx - last_mouse[0]
                dy = my - last_mouse[1]
                last_mouse = (mx, my)

                if dragging:
                    # orbit: vertical motion tilts (pitch), horizontal rotates (yaw)
                    pitch += dy * 0.25
                    yaw += dx * 0.25
                if panning_mouse:
                    pan_x += dx * 0.08
                    pan_y -= dy * 0.08

        # Integrate and append new points
        for _ in range(POINTS_PER_FRAME):
            # make SUBSTEPS if you want very fine integration per appended point
            for _ in range(SUBSTEPS):
                x, y, z = rk4_step(x, y, z, DT)
            if MAX_POINTS is None or len(points) < MAX_POINTS:
                points.append((x * SCALE, y * SCALE, z * SCALE))
            else:
                # if capped, pop oldest to keep continuous trail
                points.pop(0)
                points.append((x * SCALE, y * SCALE, z * SCALE))

        # --- draw ---
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # apply camera transforms: pan, zoom (translate Z), then orbit rotations
        glTranslatef(pan_x, pan_y, zoom)
        glRotatef(pitch, 1.0, 0.0, 0.0)
        glRotatef(yaw, 0.0, 1.0, 0.0)

        # draw attractor polyline
        draw_line_strip(points)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
