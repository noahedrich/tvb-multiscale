# -*- coding: utf-8 -*-

import numpy as np

from tvb_multiscale.core.tvb.cosimulator.models.wilson_cowan_constraint import WilsonCowan
from tvb_multiscale.tvb_nest.interfaces.models.wilson_cowan import WilsonCowanTVBNESTInterfaceBuilder
from tvb_multiscale.tvb_nest.interfaces.models.wilson_cowan import WilsonCowanMultisynapseTVBNESTInterfaceBuilder
from tvb_multiscale.tvb_nest.nest_models.models.wilson_cowan import \
    WilsonCowanBuilder, WilsonCowanMultisynapseBuilder

from examples.tvb_nest.example import main_example


def wilson_cowan_example(**kwargs):

    # -----------------------------------Wilson Cowan oscillatory regime------------------------------------------------

    model_params = {
        "r_e": np.array([0.0]),
        "r_i": np.array([0.0]),
        "k_e": np.array([1.0]),
        "k_i": np.array([1.0]),
        "tau_e": np.array([10.0]),
        "tau_i": np.array([10.0]),
        "c_ee": np.array([10.0]),
        "c_ei": np.array([6.0]),
        "c_ie": np.array([10.0]),
        "c_ii": np.array([1.0]),
        "alpha_e": np.array([1.2]),
        "alpha_i": np.array([2.0]),
        "a_e": np.array([1.0]),
        "a_i": np.array([1.0]),
        "b_e": np.array([0.0]),
        "b_i": np.array([0.0]),
        "c_e": np.array([1.0]),
        "c_i": np.array([1.0]),
        "theta_e": np.array([2.0]),
        "theta_i": np.array([3.5]),
        "P": np.array([0.5]),
        "Q": np.array([0.0])
    }

    model_params.update(kwargs.pop("model_params", {}))

    populations_order = kwargs.pop("populations_order", 100)

    model = kwargs.pop("model", "RATE").upper()

    if kwargs.pop("multisynapse", True):
        nest_model_builder = WilsonCowanMultisynapseBuilder
        tvb_nest_model_builder = WilsonCowanMultisynapseTVBNESTInterfaceBuilder()
    else:
        nest_model_builder = WilsonCowanBuilder
        tvb_nest_model_builder = WilsonCowanTVBNESTInterfaceBuilder()
    tvb_nest_model_builder.model = model
    tvb_nest_model_builder.input_flag = kwargs.pop("input_flag", True)
    tvb_nest_model_builder.output_flag = kwargs.pop("output_flag", True)
    tvb_nest_model_builder.N_E = populations_order
    tvb_nest_model_builder.N_I = populations_order
    tvb_to_spikeNet_interfaces = []
    spikeNet_to_tvb_interfaces = []

    # An example of a configuration:
    # if model == "SPIKES":
    #     transformer_params = {"scale_factor": np.array([100.0]),
    #                           "number_of_neurons": np.array([tvb_nest_model_builder.N_E]).astype("i"),
    #                           "interaction": "multiple",
    #                           "correlation_factor": np.array([0.1])
    #                           }
    #     proxy_params = {"number_of_neurons": tvb_nest_model_builder.N_E}
    # else:
    #     transformer_params = {"scale_factor": tvb_nest_model_builder.N_E*np.array([100.0])}
    #     proxy_params = {"number_of_neurons": 1}
    # if spikeNet_model_builder == WilsonCowanMultisynapseBuilder:
    #     proxy_params["receptor_type"] = \
    #         lambda source_node, target_node: receptor_by_source_region(source_node, target_node, start=3)
    # tvb_to_spikeNet_interfaces = [{"model": model, "voi": "E", "populations": "E",
    #                                "transformer_params": transformer_params,
    #                                "proxy_params": proxy_params}]
    #
    # tvb_to_spikeNet_transformer = kwargs.pop("tvb_to_spikeNet_transformer",
    #                                          kwargs.pop("tvb_to_spikeNet_transformer_model", None))
    # if tvb_to_spikeNet_transformer:
    #     tvb_to_spikeNet_interfaces[0]["transformer_model"] = tvb_to_spikeNet_transformer
    # tvb_to_spikeNet_interfaces[0]["transformer_params"].update(kwargs.pop("tvb_to_spikeNet_transformer_params", {}))
    # tvb_to_spikeNet_proxy = kwargs.pop("tvb_to_spikeNet_proxy", kwargs.pop("tvb_to_spikeNet_proxy_model", None))
    # if tvb_to_spikeNet_proxy:
    #     tvb_to_spikeNet_interfaces[0]["proxy_model"] = tvb_to_spikeNet_proxy
    # tvb_to_spikeNet_interfaces[0]["proxy_params"].update(kwargs.pop("tvb_to_spikeNet_proxy_params", {}))
    #
    # spikeNet_to_tvb_interfaces = [{"voi": "E", "populations": "E",
    #                                "transformer_params":
    #                                    {"scale_factor":
    #                                         np.array([1e-4])/tvb_nest_model_builder.N_E}},  # (dt(ms) * 1000)Hz*n_neurons)
    #                               {"voi": "I", "populations": "I",
    #                                "transformer_params":
    #                                    {"scale_factor":
    #                                         np.array([1e-4])/tvb_nest_model_builder.N_I}}]  # (dt(ms) * 1000)Hz*n_neurons
    #
    # spikeNet_to_tvb_transformer = kwargs.pop("spikeNet_to_tvb_transformer",
    #                                          kwargs.pop("spikeNet_to_tvb_transformer_model", None))
    # if spikeNet_to_tvb_transformer:
    #     spikeNet_to_tvb_interfaces[0]["transformer_model"] = spikeNet_to_tvb_transformer
    # spikeNet_to_tvb_interfaces[0]["transformer_params"].update(kwargs.pop("spikeNet_to_tvb_transformer_params", {}))
    #

    main_example(WilsonCowan, model_params,
                 nest_model_builder, kwargs.pop("spiking_proxy_inds", [0, 1]), populations_order,
                 tvb_nest_model_builder, tvb_to_spikeNet_interfaces, spikeNet_to_tvb_interfaces, **kwargs)


if __name__ == "__main__":
    import sys
    if sys.argv[-1] == "1":
        wilson_cowan_example(model="RATE", multisynapse=True)
    else:
        wilson_cowan_example(model="RATE", multisynapse=False)
