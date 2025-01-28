import math
# Define the logarithmically averaged function f(a) Terence Tao, Joni Teräväinen
#1. The function f takes 5 parameters: a, g, h, x, m
#2. The parameter a is the constant that changes the function f
#3. The parameter g is a list of functions that are applied to the sum
#4. The parameter h is a list of constants that are applied to the functions in g
#5. The parameter x is the upper limit of the sum
#6. The parameter m is the lower limit of the sum
def f(a, g, h, x, m):
    sum = 0
    for n in range(x // m, x + 1):
        prod = 1
        for k in range(len(g)):
            prod *= g[k](n + a * h[k])
        sum += prod
    return (1 / math.log(m)) * sum

#7. The function f returns the logarithmically averaged function f(a)
# Define the values for the function inputs
a = 2
g = [
    lambda n: math.sin(n),
    lambda n: math.cos(n),
    lambda n: math.tan(n)
]
h = [1, 2, 3]
x = 111
m = 81

# Call the function and output the result
result = f(a, g, h, x, m)
print("f(a) = " + str(result))


