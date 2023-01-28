import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.signal import dlsim

# transfer function coefficients
num = [1, 0.1, 0.1, 0.1]
den = [1, -0.5, 0.2, 0.1, 0.1]

# create LTI system
sys = signal.dlti(num, den, dt=0.1)

# input signal
t = np.linspace(0, 10, num=100)
u = np.ones_like(t)

# compute system output
state = None
sys = sys._as_ss()
print(f"sys: {sys}")
y1 = []
for i in range(0, len(t)):
    if state is None:
        tt, y, state = dlsim(sys, [1, 1e6], t=None)
    else:
        tt, y, state = dlsim(sys, [1, 1e6], t=None, x0=state)
    print(f"state: {state}")
    state = state[1]
    print(f"tt: {tt}")
    print(f"state: {state}")

    print(f"y: {y}")
    y1.append(y[0][0])

y2 = sys.output(u, t)

print("y", y)

# plot output
plt.plot(t, y2[1][:-1:])
plt.plot(t, y1)
plt.xlabel("Time")
plt.ylabel("Output")
plt.legend(["scipy", "nodedge"])
plt.show()
