from math import *

from pylab import *
from scipy.integrate import quad


# the function to be integrated:
def my_func(x):
    return cos(x)


x = arange(-pi, pi + 0.1, 0.1)
y_sin = [sin(el) for el in x]
y_cos_integrated = [quad(my_func, -pi, el)[0] - sin(pi) for el in x]

plot(x, y_sin, ".-")
plot(x, y_cos_integrated)
legend(["Sin", "Cos integrated"])
show()
