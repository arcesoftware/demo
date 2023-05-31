# -*- coding: utf-8 -*-
"""
Created on Tue May 30 17:16:45 2023

@author: jarc5624
"""
import numpy as np

def fib_sum(n):
    a, b = 0, 1
    fib_sum = 0  # Initialize sum variable
    while a <= n:
        fib_sum += a  # Add current Fibonacci number to the sum
        a, b = b, a+b
    return fib_sum

# Example usage
n = 1000
total_sum = fib_sum(n)

def multiply_by_constant(matrix, constant):
    # Check if the constant is not zero
    if constant != 0:
        # Apply the operation to the matrix
        result = constant * matrix
        return result
    else:
        print("Error: Division by zero.")
        return None

# Example usage
matrix = np.array([[2, -1, 0, 0, 0],
                    [-1, 2, -1, 0, 0],
                    [0, -1, 2, -1, 0],
                    [0, 0, -1, 2, -1],
                    [0, 0, 0, -1, 2]])

constant = total_sum
result = multiply_by_constant(matrix, constant)
print(result)
