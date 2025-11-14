import numpy as np
import matplotlib.pyplot as plt

# Julia set parameters
width, height = 800, 800
max_iter = 300
zoom = 1.5
c = complex(-0.7, 0.27015)  # Julia constant

# Create a grid of complex numbers
x = np.linspace(-zoom, zoom, width)
y = np.linspace(-zoom, zoom, height)
X, Y = np.meshgrid(x, y)
Z = X + 1j * Y

# Initialize escape time array
escape_times = np.zeros(Z.shape, dtype=int)

# Compute escape times
for i in range(max_iter):
    mask = np.abs(Z) <= 2
    Z[mask] = Z[mask] ** 2 + c
    escape_times[mask & (np.abs(Z) > 2)] = i

# Plot the Julia set
plt.figure(figsize=(8, 8))
plt.imshow(escape_times, cmap='inferno', extent=(-zoom, zoom, -zoom, zoom))
plt.title(f"Julia Set for c = {c}")
plt.colorbar(label="Escape Time")
plt.show()
