import turtle
import numpy as np
from math import atan2
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# Constants for the Lorenz-like system
RHO = 43.5
SIGMA = 10.0
BETA = 8.0 / 3.0
D0 = 19.0 / 3.0

# Dynamic range and scale adjustments
INITIAL_SCALE = 400
OFFSET_X, OFFSET_Y = 0, 0

# Define the system of equations
def lorenz_system(state, t):
    x, y, z, y1, z1 = state
    return (
        SIGMA * (y - x),
        x * (RHO - z) - y,
        x * y - x * y1 - BETA * z,
        x * z - 2 * x * z1 - D0 * y1,
        2 * x * y1 - 4 * BETA * z1
    )

# Initial conditions and time range
initial_state = [1.0, 1.0, 1.0, 1.0, 1.0]
time_points = np.arange(0.0, 200.0, 0.01)

# Solve the differential equations
states = odeint(lorenz_system, initial_state, time_points)

# Extract bounds for scaling and offsets
x_vals, z_vals = states[:, 0], states[:, 2]
OFFSET_X, OFFSET_Y = np.mean(x_vals), np.mean(z_vals)
max_range = max(np.max(np.abs(x_vals)), np.max(np.abs(z_vals)))
scale_factor = INITIAL_SCALE / max_range

# Initialize Turtle
turtle.screensize(canvwidth=7680, canvheight=4800, bg="black")
plotter = turtle.Turtle()
plotter.speed("fastest")
plotter.pensize(0.3)
plotter.radians()
plotter.pendown()

# Color gradient
colors = plt.cm.plasma(np.linspace(0, 1, len(states)))

# Drawing function with dynamic recomputation
def draw_lorenz():
    global states

    for i, (x, y, z, y1, z1) in enumerate(states):
        plotter.setpos((x - OFFSET_X) * scale_factor, (z - OFFSET_Y) * scale_factor)
        plotter.setheading(atan2(z1, y1))
        plotter.pencolor(colors[i][0], colors[i][1], colors[i][2])

    # Compute additional states dynamically
    final_state = states[-1]
    t_next = np.arange(time_points[-1] + 0.01, time_points[-1] + 200.0, 0.01)
    new_states = odeint(lorenz_system, final_state, t_next)
    states = np.vstack((states, new_states))

# Function to exit gracefully when clicking the window
def stop_drawing(x, y):
    turtle.bye()

plotter.onclick(stop_drawing)

try:
    draw_lorenz()
except turtle.Terminator:
    print("Drawing stopped.")

# Keep the window open until closed
turtle.done()