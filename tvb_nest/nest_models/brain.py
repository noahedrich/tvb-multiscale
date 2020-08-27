# -*- coding: utf-8 -*-
from pandas import Series

from tvb_multiscale.spiking_models.brain import SpikingBrain


class NESTBrain(SpikingBrain):

    nest_instance = None
    _weight_attr = "weight"
    _delay_attr = "delay"
    _receptor_attr = "receptor"

    def __init__(self, input_brain=None, nest_instance=None, **kwargs):
        self.nest_instance = nest_instance
        super(NESTBrain, self).__init__(input_brain, **kwargs)

    @property
    def spiking_simulator_module(self):
        if self.nest_instance is None:
            for i_pop, pop_lbl, pop in self._loop_generator():
                self.nest_instance = pop.nest_instance
                if self.nest_instance is not None:
                    break
        return self.nest_instance