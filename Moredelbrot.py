import turtle
import colorsys
import numpy as np

# Set the screen's background color
turtle.bgcolor("black")
# Set the turtle's pen size to 1 pixel
turtle.pensize(1)
# Set the turtle's speed to the maximum
turtle.speed(0)
# Set the screen size
turtle.screensize(canvwidth=7680, canvheight=4800, bg='black')

# Define the escape time function
def escape_time(c, max_iterations):
    z = 0
    for i in range(max_iterations):
        z = z*z + c
        if abs(z) > 2:
            return i
    return max_iterations

# Define the proximity function using NumPy
def proximity(x, y):
    # Convert pixel coordinates to NumPy arrays
    x_arr = np.array(x)
    y_arr = np.array(y)
    
    # Calculate the distance from the origin using the Euclidean norm
    distance = np.linalg.norm(np.array([x_arr, y_arr]), axis=0)
    
    return distance

# Define the maximum proximity (distance) for color mapping
max_proximity = (400 ** 2 + 400 ** 2) ** 0.5

# Define the gradient color function
def gradient_color(distance):
    # Map the distance to a value between 0 and 1
    normalized_distance = distance / max_proximity
    # Convert the distance to a color gradient using HSV color space
    hue = normalized_distance  # Use the distance directly as hue for simplicity
    saturation = 1.0
    value = 1.0
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    return r, g, b

# Set the maximum number of iterations
max_iterations = 256

# Iterate over the complex plane
for x in range(-400, 400):
    for y in range(-400, 400):
        # Convert pixel coordinates to complex number
        c = complex(x/200, y/200)
        # Calculate the escape time for the current point
        i = escape_time(c, max_iterations)
        if i == max_iterations:
            # Get the proximity (distance) to the origin
            dist = proximity(x, y)
            # Get the gradient color based on proximity
            r, g, b = gradient_color(dist)
            # Set the pen color
            turtle.pencolor(r, g, b)
            # Move the turtle to the current point and draw a dot
            turtle.penup()
            turtle.goto(x, y)
            turtle.dot()

# Hide the turtle and keep the screen open
turtle.hideturtle()
turtle.exitonclick()
