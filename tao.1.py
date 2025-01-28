import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Define the logarithmically averaged function f(a)
def f(a, g, h, x, m):
    sum = 0
    for n in range(int(x // m), int(x) + 1):
        prod = 1
        for k in range(len(g)):
            prod *= g[k](n + a * h[k])
        sum += prod
    return (1 / np.log(m)) * sum


# Define the values for the function inputs
g = [
    lambda n: np.sin(n),
    lambda n: np.cos(n),
    lambda n: np.tan(n)
]
h = [1, 2, 3]
x = 16180
m = 1618033

# Create a 3D plot of the function
fig = plt.figure()
ax = fig.add_subplot(projection='3d')

a_vals = np.linspace(0, 10, 100)
X, Y = np.meshgrid(a_vals, np.linspace(0, 100, 100))
Z = np.array([[f(a, g, h, x, m) for a in a_vals] for x in np.linspace(0, 100, 100)])
surf = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none')

result = f(a, g, h, x, m)
print("f(a) = " + str(result))

# Define the animation function
def animate(frame):
    ax.view_init(elev=30, azim=frame)
    return surf,

# Create the animation
anim = FuncAnimation(fig, animate, frames=np.linspace(0, 360, 100), interval=50)

# Display the animation
plt.show()
