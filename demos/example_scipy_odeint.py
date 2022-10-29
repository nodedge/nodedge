from pylab import *
from scipy.integrate import odeint

"""
A spring-mass system with damping
"""


def damped_osc(u, t):  # defines the system of diff. eq.
    x, v = u
    return (v, -k * (x - L) / m - b * v)  # the vector (dx/dt, dv/dt)


t = arange(0, 20.1, 0.1)
u0 = array([1, 0])  # initial values of x, v

# assume certain values of parameters b, k, L, m; these would be given in the problem
b = 0.4
k = 8.0
L = 0.5
m = 1.0

u = odeint(damped_osc, u0, t)  # solve ODE
# plot x, v, phase, using matplotlib

figure(1)
plot(t, u[:, 0], t, u[:, 1])  # u[:,0] is x; u[:,1] is v
xlabel("Time")
title("Damped Oscillator")

figure(2)
plot(u[:, 0], u[:, 1])
title("Phase-space")
xlabel("Position")
ylabel("Velocity")
show()
