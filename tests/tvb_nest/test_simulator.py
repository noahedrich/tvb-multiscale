# -*- coding: utf-8 -*-
import os
import shutil

from tvb.basic.profile import TvbProfile
TvbProfile.set_profile(TvbProfile.LIBRARY_PROFILE)

import matplotlib as mpl
mpl.use('Agg')

import numpy as np

from tvb_multiscale.tvb_nest.config import Config
from examples.tvb_nest.example import main_example
from tvb_multiscale.tvb_nest.nest_models.builders.models.wilson_cowan import WilsonCowanBuilder
from tvb_multiscale.tvb_nest.interfaces.builders.models.wilson_cowan import \
    WilsonCowanBuilder as InterfacWilsonCowanBuilder

from tvb.datatypes.connectivity import Connectivity
from tvb.simulator.models.wilson_cowan_constraint import WilsonCowan


def prepare_launch_default_simulation():
    config = Config(output_base="outputs/")
    config.figures.SAVE_FLAG = False
    config.figures.SHOW_FLAG = False
    config.figures.MATPLOTLIB_BACKEND = "Agg"

    connectivity = Connectivity.from_file(config.DEFAULT_CONNECTIVITY_ZIP)

    # Select the regions for the fine scale modeling with NEST spiking networks
    nest_nodes_ids = []  # the indices of fine scale regions modeled with NEST
    # In this example, we model parahippocampal cortices (left and right) with NEST
    for id in range(connectivity.region_labels.shape[0]):
        if connectivity.region_labels[id].find("hippo") > 0:
            nest_nodes_ids.append(id)

    results, simulator = \
        main_example(WilsonCowan, WilsonCowanBuilder, InterfacWilsonCowanBuilder,
                     nest_nodes_ids, nest_populations_order=20, connectivity=connectivity,
                     simulation_length=55.0, exclusive_nodes=True, config=config)

    return simulator.connectivity.weights, simulator.connectivity.tract_lengths, results[0][1]


def test_connectivity_weights_shape(weights=None):
    if weights is None:
        (weights, tract_lengths, results) = prepare_launch_default_simulation()
    assert weights.shape == (68, 68)


def test_connectivity_tract_lengths_shape(tract_lengths=None):
    if tract_lengths is None:
        (weights, tract_lengths, results) = prepare_launch_default_simulation()
    assert tract_lengths.shape == (68, 68)


def test_results_shape(results=None):
    if results is None:
        (weights, tract_lengths, results) = prepare_launch_default_simulation()
    assert not np.isinf(results.ravel()).all()
    assert not np.isnan(results.ravel()).all()
    assert results.shape == (550, 4, 68, 1)


def teardown_function():
    output_folder = Config().out._out_base
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)


if __name__ == "__main__":
    (weights, tract_lengths, results) = prepare_launch_default_simulation()
    test_connectivity_weights_shape(weights)
    test_connectivity_tract_lengths_shape(tract_lengths)
    test_results_shape(results)
