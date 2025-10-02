# cuda_julia.py
import math
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from numba import cuda, int32

# ===== CONFIG =====
WIDTH, HEIGHT = 1280, 720
GRID_SIZE = 128        # safe default; increase with caution (memory/time)
MAX_ITER = 20
BOUNDS = (-1.618033, 1.618033)
C = (-0.4, 0.6)
MIN_ITER = 12          # filter to remove "dust"
ZOOM_SENSITIVITY = 0.1
ROTATE_SENSITIVITY = 0.5
PAN_SENSITIVITY = 0.02

# ===== CAMERA STATE =====
cam_dist = 6.0
rot_x = rot_y = rot_z = 0.0
pan_x = pan_y = 0.0

# ===== CUDA KERNEL =====
# writes iteration count (0..max_iter) to `iters_flat[idx]`
@cuda.jit
def julia_iters_kernel(iters_flat, grid_size, bounds_min, bounds_max, c0, c1, iter_limit):
    i, j, k = cuda.grid(3)
    if i >= grid_size or j >= grid_size or k >= grid_size:
        return

    # compute linear index
    idx = i + j * grid_size + k * grid_size * grid_size

    # map grid index -> coordinate in bounds
    sx = (bounds_max - bounds_min) / grid_size
    x = bounds_min + i * sx
    y = bounds_min + j * sx
    z = bounds_min + k * sx

    zx = x
    zy = y
    zz = z

    iteration = 0
    # standard escape loop
    while iteration < iter_limit:
        r2 = zx * zx + zy * zy + zz * zz
        if r2 >= 4.0:
            break

        r = math.sqrt(r2)
        # avoid domain error in acos when r == 0
        if r == 0.0:
            theta = 0.0
        else:
            # clamp zz / r to [-1,1] to be safe
            v = zz / r
            if v > 1.0:
                v = 1.0
            elif v < -1.0:
                v = -1.0
            theta = math.acos(v)

        phi = math.atan2(zy, zx)
        # power; use n=8-like transform originally used in your code
        n = 8
        rn = r ** n
        theta_n = theta * n
        phi_n = phi * n

        sin_t = math.sin(theta_n)

        zx = rn * sin_t * math.cos(phi_n) + c0
        zy = rn * sin_t * math.sin(phi_n) + c1
        zz = rn * math.cos(theta_n) + 0.0  # favorite z-offset was 0 in your Julia version

        iteration += 1

    # store iteration count (0..iter_limit)
    iters_flat[idx] = iteration


# ===== Host-side function to call kernel and collect points safely =====
def generate_julia_3d_cuda(grid_size, iter_limit, c, bounds, min_iter=MIN_ITER):
    # Check CUDA availability
    if not cuda.is_available():
        raise RuntimeError("CUDA is not available on this machine. Install drivers/ensure GPU presence.")

    # Flattened device array of int32, one per voxel
    total = grid_size * grid_size * grid_size
    iters_host = np.empty(total, dtype=np.int32)
    iters_dev = cuda.device_array(total, dtype=np.int32)

    # kernel launch configuration: keep block dim modest (8,8,8)
    threads_per_block = (8, 8, 8)
    blocks_per_grid = (
        (grid_size + threads_per_block[0] - 1) // threads_per_block[0],
        (grid_size + threads_per_block[1] - 1) // threads_per_block[1],
        (grid_size + threads_per_block[2] - 1) // threads_per_block[2],
    )

    # launch kernel
    julia_iters_kernel[blocks_per_grid, threads_per_block](
        iters_dev,
        grid_size,
        bounds[0],
        bounds[1],
        c[0],
        c[1],
        iter_limit
    )

    # copy results back
    iters_dev.copy_to_host(iters_host)

    # build point list on host (safe)
    points = []
    step = (bounds[1] - bounds[0]) / grid_size
    idx = 0
    for i in range(grid_size):
        x = bounds[0] + i * step
        for j in range(grid_size):
            y = bounds[0] + j * step
            for k in range(grid_size):
                it = int(iters_host[idx])
                if (it > min_iter) and (it < iter_limit):
                    z = bounds[0] + k * step
                    points.append((x, y, z, it))
                idx += 1

    return points


# ===== OpenGL helpers (unchanged) =====
def init_opengl(width, height):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    glEnable(GL_PROGRAM_POINT_SIZE)
    glEnable(GL_POINT_SMOOTH)
    glPointSize(2)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)


def render_points(points, max_iter):
    glBegin(GL_POINTS)
    for x, y, z, it in points:
        norm = it / max_iter
        glColor4f(norm, 0.4, 1.0 - norm, 0.05 + norm * 0.5)
        glVertex3f(x, y, z)
    glEnd()


# ===== Integration example: animate iteration growth using CUDA generator =====
def main():
    global cam_dist, rot_x, rot_y, rot_z, pan_x, pan_y

    # small GRID for interactive demo — increase only if your GPU & time allow
    grid_size = GRID_SIZE
    max_iter = MAX_ITER

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("3D Julia Set (CUDA accelerated)")

    init_opengl(WIDTH, HEIGHT)
    clock = pygame.time.Clock()

    dragging = False
    last_mouse_pos = None

    frame = 0
    current_iter = 2
    anim_done = False
    points = []

    # pre-warm CUDA context once to avoid surprises
    if cuda.is_available():
        _ = cuda.current_context()  # will create context early (safer)

    running = True
    while running:
        dt = clock.tick(30)
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragging = True
                    last_mouse_pos = pygame.mouse.get_pos()
                elif event.button == 4:
                    cam_dist -= ZOOM_SENSITIVITY
                elif event.button == 5:
                    cam_dist += ZOOM_SENSITIVITY
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
            elif event.type == MOUSEMOTION and dragging:
                x, y = pygame.mouse.get_pos()
                dx = x - last_mouse_pos[0]
                dy = y - last_mouse_pos[1]
                rot_y += dx * ROTATE_SENSITIVITY
                rot_x += dy * ROTATE_SENSITIVITY
                last_mouse_pos = (x, y)

        keys = pygame.key.get_pressed()
        if keys[K_w]:
            pan_y += PAN_SENSITIVITY
        if keys[K_s]:
            pan_y -= PAN_SENSITIVITY
        if keys[K_a]:
            pan_x -= PAN_SENSITIVITY
        if keys[K_d]:
            pan_x += PAN_SENSITIVITY
        if keys[K_q]:
            rot_z += ROTATE_SENSITIVITY
        if keys[K_e]:
            rot_z -= ROTATE_SENSITIVITY
        if keys[K_r]:
            cam_dist = 6.0
            rot_x = rot_y = rot_z = 0
            pan_x = pan_y = 0
            current_iter = 2
            anim_done = False

        # ==== update points using CUDA every few frames to animate growth ====
        if (not anim_done) and (frame % 4 == 0):
            try:
                points = generate_julia_3d_cuda(grid_size, current_iter, C, BOUNDS, MIN_ITER)
            except Exception as e:
                print("CUDA generation failed:", e)
                print("Falling back to empty point set for this frame.")
                points = []
            current_iter += 1
            if current_iter > max_iter:
                current_iter = max_iter
                anim_done = True

        # ==== render ====
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(pan_x, pan_y, -cam_dist)
        glRotatef(rot_x, 1, 0, 0)
        glRotatef(rot_y, 0, 1, 0)
        glRotatef(rot_z, 0, 0, 1)

        render_points(points, max_iter)
        pygame.display.flip()
        frame += 1

    pygame.quit()


if __name__ == "__main__":
    main()
