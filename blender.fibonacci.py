import bpy

def fibonacci(n):
    fibo = []
    for i in range(n):
        if i == 0 or i == 1:
            fibo.append(i)
        else:
            f = fibo[i-1] + fibo[i-2]
            fibo.append(f)
    return fibo

# Get the Fibonacci sequence
fibo = fibonacci(10)

# Set the starting location of the first cube
x = 0
y = 0
z = 0

# Create the first cube at the starting location
bpy.ops.mesh.primitive_cube_add(location=(x, y, z))

# Get a reference to the first cube
cube1 = bpy.context.object

# Set the size of the first cube
cube1.scale = (fibo[0], fibo[0], fibo[0])

# Set the starting location for the second cube
x += fibo[0]
y += fibo[0]
z += fibo[0]

# Create the second cube at the starting location
bpy.ops.mesh.primitive_cube_add(location=(x, y, z))

# Get a reference to the second cube
cube2 = bpy.context.object

# Set the size of the second cube
cube2.scale = (fibo[1], fibo[1], fibo[1])

# Set the starting location for the third cube
x += fibo[1]
y += fibo[1]
z += fibo[1]

# Create the third cube at the starting location
bpy.ops.mesh.primitive_cube_add(location=(x, y, z))

# Get a reference to the third cube
cube3 = bpy.context.object

# Set the size of the third cube
cube3.scale = (fibo[2], fibo[2], fibo[2])

# Add the remaining cubes in the Fibonacci sequence using a loop
for i in range(3, len(fibo)):
    # Set the starting location for the next cube
    x += fibo[i-1]
    y += fibo[i-1]
    z += fibo[i-1]

    # Create the next cube at the starting location
    bpy.ops.mesh.primitive_cube_add(location=(x, y, z))

    # Get a reference to the next cube
    cube = bpy.context.object

    # Set the size of the next cube
    cube.scale = (fibo[i], fibo[i], fibo[i])
