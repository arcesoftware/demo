
import numpy as np
import plotly.graph_objects as go
import soundfile as sf

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
x = 100
m = 1000

# Create data for the plot
a = 2
a_vals = np.linspace(0, 10, 100)
x_vals = np.linspace(0, 100, 100)
X, Y = np.meshgrid(a_vals, x_vals)
Z = np.array([[f(a, g, h, x, m) for a in a_vals] for x in x_vals])

# Create a 3D surface plot with Plotly
fig = go.Figure(data=[go.Surface(x=X, y=Y, z=Z)])
fig.update_layout(
    title='Logarithmically Averaged Function',
    scene=dict(
        xaxis_title='a',
        yaxis_title='x',
        zaxis_title='f(a)'
    ),
    margin=dict(l=0, r=0, b=0, t=40),
    font=dict(family='Helvetica', size=14),
    width=800,
    height=800
)
fig.show()

# Generate an audio signal from the 2D array
duration = 10 # in seconds
samplerate = 44100 # in Hz
t = np.linspace(0, duration, duration * samplerate, False)
audio_signal = np.interp(Z, (Z.min(), Z.max()), (-1, 1))
audio_signal = np.resize(audio_signal, (duration * samplerate,))
    
# Export the audio file to c:\aws
sf.write('c:/aws/output.wav', audio_signal, samplerate)
