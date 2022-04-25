import turtle
from turtle import *
from random import randint
# taking input for the number of  sides of the polygon
n = 25
# taking input for the length of the sides of the polygon
l = 25
angle = 180 - 180 * (n - 2) / 1.5
turtle.screensize(canvwidth=7680, canvheight=4800, bg="black")
wn = turtle.Screen()
wn.title("Armadillo")
skk = turtle.Turtle()
skk.speed(0)
colormode(255)
def sqrfuncE(binet):
    for binet in range(binet):
        skk.color(randint(0, 255),randint(0, 255),randint(0, 255))
        skk.fd(binet)
        skk.left(angle)
def sqrfuncW(binet):
    for binet in range(binet):
        skk.color(randint(0, 255),randint(0, 255),randint(0, 255))
        skk.fd(binet)
        skk.left(angle)
count = 0
while count <= n:
    sqrfuncW(n - l), sqrfuncE(l + l + n + n)
    sqrfuncW(l - n - l - n), sqrfuncE(l + n)
    sqrfuncW(n + l + n + l), sqrfuncE(n - l - n - l)
    sqrfuncW(n + n + n), sqrfuncE(l - l - l)
    sqrfuncW(n - 2), sqrfuncE(n + 1 + n + 2)
skk.done()