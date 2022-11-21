from pylab import *
from scipy.integrate import odeint

"""
A spring-mass system with damping
"""


# Define the system of differential equation
def damped_oscillator(x, t):
    p, v = x
    # Return the derivative vector (dp/dt, dv/dt)
    return (v, -k * (p - L) / m - b * v)


if __name__ == "__main__":
    # Time vector
    t = arange(0, 20.1, 0.1)

    # Initial values of p, v
    x0 = array([1, 0])

    # Assume certain values of parameters b, k, L, m; these would be given in the problem
    b = 0.4
    k = 8.0
    L = 0.5
    m = 1.0

    x = odeint(damped_oscillator, x0, t)  # solve ODE

    # Plot p, v, phase, using matplotlib
    figure(1)
    plot(t, x[:, 0], t, x[:, 1])  # x[:,0] is p; u[:,1] is v
    xlabel("Time")
    title("Damped oscillator")

    figure(2)
    plot(x[:, 0], x[:, 1])
    title("Phase-space")
    xlabel("Position")
    ylabel("Velocity")

    show()
