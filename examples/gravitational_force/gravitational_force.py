from operator import mul, truediv

from numpy import power


def gravitational_force():
    var_0 = 2.0
    var_1 = 384000.0
    var_2 = power(var_1, var_0)
    var_3 = 7.34e+22
    var_4 = 5.2
    var_5 = mul(var_4, var_3)
    var_6 = 6.67e-11
    var_7 = mul(var_6, var_5)
    var_8 = truediv(var_7, var_2)
    return [var_8]


if __name__ == '__main__':
    gravitational_force()
