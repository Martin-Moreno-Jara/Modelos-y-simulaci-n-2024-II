import numpy as np
generator=np.random.default_rng(30)
def expon(mean):
        return generator.exponential(mean)

for i in range(0,21):
        print(expon(4.6))