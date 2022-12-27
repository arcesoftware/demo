

import turtle
from math import atan2

screen = turtle.Screen()
screen.title('Lorenz Attractor')

t = turtle.Turtle()
t.speed('fastest')
t.pensize(1)
t.pencolor('red')
t.radians()
t.pendown()

dt = 0.01  # time step
sigma = 10.0
beta = 8/3
rho = 28.0
scale = 10  # set the scale factor for the plot

# Set the initial conditions
x, y, z = 1.0, 1.0, 1.0
dx, dy = 0.0, 0.0  # initialize the x velocity



while True:
    t.setpos(x*scale, y*scale)
    t.setheading(atan2(dy, dx))
    
    # Solve the differential equations
    dx = (sigma*(y - x)) * dt
    dy = (x*(rho - z) - y) * dt
    dz = (x*y - beta*z) * dt
    
    x += dx
    y += dy
    z += dz
    
# Keep the window open until it is closed
turtle.mainloop()
