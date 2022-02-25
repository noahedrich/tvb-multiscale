#... here all the imports
import itertools
from concurrent.futures import ProcessPoolExecutor
import numpy as np

# lists of all weights that want to check
w1 = np.arange(0,1,0.25)
w2 = np.arange(0,1,0.25)
w3 = np.arange(0,1,0.25)

# all possible combinations of weights
a = [w1, w2, w3]
input_param = list(itertools.product(*a))
input_param = [np.array(params) for params in input_param]
print(input_param)


# dummy simulation function
def sim_run(w1, w2, w3):
    return w1 + w2 + w3


with ProcessPoolExecutor(max_workers=10) as executor:
    for params in input_param:
        results = executor.map(sim_run, params)
        print('%.1f + %.1f + %.1f = %.1f' % (*params, results))
