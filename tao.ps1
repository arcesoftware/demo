﻿# Define the logarithmically averaged function f(a)
function f($a, $g, $h, $x, $m) {
    $sum = 0
    for ($n = [int]($x / $m); $n -le $x; $n++) {
        $prod = 1
        for ($k = 0; $k -lt $g.Length; $k++) {
            $prod *= &$g[$k]($n + $a * $h[$k])
        }
        $sum += $prod
    }
    return (1 / [Math]::Log($m)) * $sum
}

# Define the values for the function inputs
$a = 2

$g = @(
    {param($n) [Math]::Sin($n)},
    {param($n) [Math]::Cos($n)},
    {param($n) [Math]::Tan($n)}
)
$h = @(1, 2, 3)
$x = 100
$m = 1000

# Call the function and output the result
$result = f $a $g $h $x $m
Write-Host "f(a) = $result"

# Calculate f(a) using the provided matrix
$matrix = @(
    @(2, -1, 0, 0, 0),
    @(-1, 2, -1, 0, 0),
    @(0, -1, 2, -1, 0),
    @(0, 0, -1, 2, -1),
    @(0, 0, 0, -1, 2)
)

$a = 3  # Set the value of a for the calculation
$result = f $a $g $h $matrix $m
Write-Host "f(a) using the matrix = $result"
