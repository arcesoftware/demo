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
    step = (bounds
