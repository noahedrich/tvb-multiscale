# -*- coding: utf-8 -*-

from tvb_multiscale.tvb_nest.interfaces.models.wilson_cowan import WilsonCowanTVBNESTInterfaceBuilder
from tvb_multiscale.tvb_nest.interfaces.models.wilson_cowan import WilsonCowanMultisynapseTVBNESTInterfaceBuilder
from tvb_multiscale.tvb_nest.nest_models.models.wilson_cowan import \
    WilsonCowanBuilder, WilsonCowanMultisynapseBuilder

from examples.tvb_nest.example import main_example
from examples.models.wilson_cowan import wilson_cowan_example as wilson_cowan_example_base

# wrapper function to pass kwargs through map()
def wilson_cowan_wrapper(kwargs):
    return wilson_cowan_example(**kwargs)


def wilson_cowan_example(**kwargs):
    print("\n\n\n KEY WORD ARGUMENTS:")
    print(kwargs)

    if kwargs.pop("multisynapse", True):
        print("multisynapse = True")
        nest_model_builder = WilsonCowanMultisynapseBuilder()
        tvb_nest_model_builder = WilsonCowanMultisynapseTVBNESTInterfaceBuilder()
    else:
        print("multisynapse = False")
        nest_model_builder = WilsonCowanBuilder()
        tvb_nest_model_builder = WilsonCowanTVBNESTInterfaceBuilder()

    return main_example(wilson_cowan_example_base, nest_model_builder, tvb_nest_model_builder, **kwargs)


if __name__ == "__main__":
    import sys
    import numpy as np
    import itertools
    from concurrent.futures import ProcessPoolExecutor

    # arrays of all parameter values that want to check
    c_ee = np.array([1.0, 5.0])
    c_ei = np.array([1.0, 5.0])
    c_ie = np.array([1.0, 5.0])
    c_ii = np.array([1.0, 5.0])

    # all possible combinations of parameters
    a = [c_ee, c_ei, c_ie, c_ii]
    input_param = list(itertools.product(*a))
    input_param = np.array([np.array(params) for params in input_param])
    input_param = input_param.T
    print(input_param)

    # convert arrays of parameter values to dicts, so can use as kwargs
    input_param_names = ["c_ee", "c_ei", "c_ie", "c_ii"]
    input_param_dicts = []
    for params in input_param:
        # parameters that remain fixed
        d = {"model": "RATE",
             "multisynapse": True,
             "model_params": {}}
        # parameters that change value
        for key, val in zip(input_param_names, params):
            d["model_params"][key] = val
        input_param_dicts.append(d)

    # distribute simulation to different workers
    with ProcessPoolExecutor(max_workers=10) as executor:
        executor.map(wilson_cowan_wrapper, input_param_dicts)
