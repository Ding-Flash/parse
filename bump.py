from htrace import Parse
import seaborn as sns
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import math
sns.set()
sns.set_style("whitegrid")

x = np.array(range(1, 500))
y = list(map(lambda x: 1 - math.exp(-20000/x**2), x))
line = sns.lineplot(x=x,y=y)
line.set(xlabel='call times of function', ylabel='sampling rate')

plt.savefig('../bump.pdf')
plt.show()
