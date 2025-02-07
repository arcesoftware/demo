import turtle
import colorsys
import numpy as np

# Setup turtle graphics
screen = turtle.Screen()
screen.bgcolor("black")
turtle.speed(0)
turtle.hideturtle()
turtle.tracer(0)  # Disable auto-update for faster rendering
turtle.pensize(0)

# Constants
WIDTH, HEIGHT = 800, 800
MAX_ITERATIONS = 300
X_RANGE = (-2, 1)
Y_RANGE = (-1.5, 1.5)
DOT_SIZE = 1  # Dot size for drawing

# Setup screen bounds
screen.setup(width=WIDTH, height=HEIGHT)

# Color mapping function
def gradient_color(iteration, max_iter):
    hue = iteration / max_iter
    saturation, value = 1.0, 1.0
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    return r, g, b

# Compute pixel to complex-plane mapping
x_pixels = np.linspace(X_RANGE[0], X_RANGE[1], WIDTH)
y_pixels = np.linspace(Y_RANGE[0], Y_RANGE[1], HEIGHT)

# Mandelbrot escape time function
def escape_time(c, max_iterations):
    z = 0
    for n in range(max_iterations):
        z = z * z + c
        if abs(z) > 2:
            return n + 1 - np.log(np.log2(abs(z)))  # Smooth escape
    return max_iterations

# Render Mandelbrot Set
for ix, x in enumerate(x_pixels):
    for iy, y in enumerate(y_pixels):
        c = complex(x, y)
        iter_count = escape_time(c, MAX_ITERATIONS)

        # Avoid coloring points inside the Mandelbrot set
        if iter_count < MAX_ITERATIONS:
            r, g, b = gradient_color(iter_count, MAX_ITERATIONS)
            turtle.pencolor(r, g, b)
            turtle.penup()
            turtle.goto(ix - WIDTH // 2, HEIGHT // 2 - iy)
            turtle.dot(DOT_SIZE)

    # Update periodically for faster rendering
    if ix % 10 == 0:
        screen.update()

# Final update
screen.update()
turtle.done()
