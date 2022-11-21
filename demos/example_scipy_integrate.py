from math import *
from pylab import *
from scipy.integrate import quad


# A function to be integrated
def my_func(x):
    return cos(x)


if __name__ == "__main__":
    dx = 0.1
    x = arange(-pi, pi + dx, dx)
    y_sin = [sin(el) for el in x]
    y_cos_integrated = [quad(my_func, -pi, el)[0] - sin(pi) for el in x]

    plot(x, y_sin, ".-")
    plot(x, y_cos_integrated)
    legend(["Sin", "Integrated cos"])
    show()
