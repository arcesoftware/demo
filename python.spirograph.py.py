#Juan Arce, Costa Rica.
#https://arcecostarica.wordpress.com/

import turtle

# taking input for the number of  sides of the polygon
n = int(input("Enter a Fibonacci number : "))

# taking input for the length of the sides of the polygon
l = int(input("Enter the next number in the Fibonacci sequence : "))


wn = turtle.Screen()
wn.bgcolor("black")
wn.title("Turtle")
skk = turtle.Turtle()
skk.speed(200)
angle = 180 - 180 * (n - 2) / 2
wn.setup(width=200, height=200, startx=0, starty=0)
# sets window to 200x200 pixels, in upper left of screen
wn.setup(width=.75, height=0.5, startx=None, starty=None)


# sets window to 75% of screen by 50% of screen and centers


def sqrfuncE(binet):
    for binet in range(binet):
        skk.color("red")
        skk.fd(binet)
        skk.left(angle)
        skk.speed()


def sqrfuncW(binet):
    for binet in range(binet):
        skk.color("green")
        skk.fd(binet)
        skk.left(angle)
        skk.speed()


count = 0
while count <= n:
    sqrfuncW(n - l), sqrfuncE(l + l + n + n)
    sqrfuncW(l - n - l - n), sqrfuncE(l + n)
    sqrfuncW(n + l + n + l), sqrfuncE(n - l - n - l)
    sqrfuncW(n + n + n), sqrfuncE(l - l - l)
    sqrfuncW(n - 2), sqrfuncE(n + 1 + n + 2)

skk.done()
