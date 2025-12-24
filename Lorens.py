import turtle
import numpy as np
from math import atan2
from scipy.integrate import odeint

turtle.screensize(canvwidth=7680, canvheight=4800, bg='black')
# Set the values of ρ, σ, and β
rho = 43.5
sigma = 10.0
beta = 8.0 / 3.0
d0 = 19.0 / 3.0
scale = 10


def f(state, t):
    x, y, z, y1, z1 = state  # Unpack the state vector
    return sigma * (y - x), x * (
                rho - z) - y, x * y - x * y1 - beta * z, x * z - 2 * x * z1 - d0 * y1, 2 * x * y1 - 4 * beta * z1  # Derivatives


state0 = [1.0, 1.0, 1.0, 1.0, 1.0]
t = np.arange(0.0, 40.0, 0.01)

states = odeint(f, state0, t)

# Create a turtle and set the pen size
t = turtle.Turtle()
t.speed('fastest')
t.pensize(1)
t.pencolor('red')
t.radians()
t.pendown()

i = 0
while i < len(states):
    x, y, z, y1, z1 = states[i]
    t.setpos(x * scale, z * scale)
    t.setheading(atan2(z1, y1))

    # Set the pen color to a random color
    t.pencolor(np.random.rand(3))

    i += 1

# Keep the window open until it is closed
turtle.mainloop()