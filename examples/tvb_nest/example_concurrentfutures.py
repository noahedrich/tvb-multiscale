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
input_param = np.array([np.array(params) for params in input_param])
input_param = input_param.T
print('PARAMETERS:')
print(input_param)


# dummy simulation function
def sim_run(w1, w2, w3):
    out = w1 + w2 + w3
    print('%.1f + %.1f + %.1f = %.1f' % (w1, w2, w3, out))
    return out


print('\nRESULTS:')
# run locally, not parallel
# results = map(sim_run, *input_param)
# print(list(results))

# run parallel
with ProcessPoolExecutor(max_workers=10) as executor:
    results = executor.map(sim_run, *input_param)
    print(list(results))
