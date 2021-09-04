import numpy as np
import matplotlib.pyplot as plt
import warnings

t = np.linspace(0, 5, 6)

warnings.simplefilter("ignore")

x = np.linspace(0, 10, 11)
y = x ** 2

print np.array([1, 2, 3]) * np.array([1, 2, 3])
print t.reshape((6, 1)) * x.reshape((1, 11))

plt.figure()
plt.ion()
plt.xlim(0, 10)
plt.ylim(0, 100)
plt.show()
for i in range(0, 10):
    plt.hold(True)
    xx = x[i:i+2]
    yy = y[i:i+2]
    plt.pause(0.05)
    plt.plot(xx, yy, color="red")

plt.show(block=True)