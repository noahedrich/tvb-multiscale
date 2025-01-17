# -*- coding: utf-8 -*-

from copy import deepcopy

from tvb_multiscale.tvb_annarchy.config import CONFIGURED, initialize_logger
from tvb_multiscale.tvb_annarchy.annarchy_models.population import ANNarchyPopulation
from tvb_multiscale.tvb_annarchy.annarchy_models.region_node import ANNarchyRegionNode
from tvb_multiscale.tvb_annarchy.annarchy_models.brain import ANNarchyBrain
from tvb_multiscale.tvb_annarchy.annarchy_models.network import ANNarchyNetwork
from tvb_multiscale.tvb_annarchy.annarchy_models.builders.annarchy_factory import \
    load_annarchy, assert_model, create_population, connect_two_populations, create_device, connect_device
from tvb_multiscale.core.spiking_models.builders.factory import build_and_connect_devices
from tvb_multiscale.core.spiking_models.builders.base import SpikingModelBuilder


LOG = initialize_logger(__name__)


class ANNarchyModelBuilder(SpikingModelBuilder):

    """This is the base class of a ANNarchyModelBuilder,
       which builds a ANNarchyNetwork from user configuration inputs.
       The builder is half way opionionated.
    """

    config = CONFIGURED
    annarchy_instance = None
    modules_to_install = []
    _spiking_brain = ANNarchyBrain()
    _models_import_path = CONFIGURED.MYMODELS_IMPORT_PATH

    def __init__(self, tvb_simulator, nest_nodes_ids, annarchy_instance=None, config=CONFIGURED, logger=LOG):
        # Setting or loading an annarchy instance:
        self.annarchy_instance = annarchy_instance
        super(ANNarchyModelBuilder, self).__init__(tvb_simulator, nest_nodes_ids, config, logger)
        self._spiking_brain = ANNarchyBrain()

    def _configure_annarchy(self, **kwargs):
        if self.annarchy_instance is None:
            self.annarchy_instance = load_annarchy(self.config, self.logger)
        self.annarchy_instance.clear()  # This will restart ANNarchy!
        self._update_spiking_dt()
        self._update_default_min_delay()
        kwargs["dt"] = self.spiking_dt
        kwargs["seed"] = kwargs.pop("seed", self.config.ANNARCHY_SEED)
        kwargs["verbose"] = kwargs.pop("verbose", self.config.VERBOSE)
        self.annarchy_instance.setup(**kwargs)

    def configure(self, **kwargs):
        self._configure_annarchy()
        super(ANNarchyModelBuilder, self).configure()

    @property
    def min_delay(self):
        if self.annarchy_instance:
            return self.annarchy_instance.dt()
        else:
            return self.config.MIN_SPIKING_DT

    def set_synapse(self, syn_model, weights, delays, target, params={}):
        """Method to set the synaptic model, the weight, the delay,
           the synaptic target, and other possible synapse parameters
           to a synapse_params dictionary.
           Arguments:
            - syn_model: the name (string) of the synapse model
            - weight: the weight of the synapse
            - delay: the delay of the connection,
            - receptor_type: the receptor type
            - params: a dict of possible synapse parameters
           Returns:
            a dictionary of the whole synapse configuration
        """
        return {'synapse_model': syn_model, 'weights': weights,
                'delays': delays, 'target': target, 'params': params}

    def _assert_model(self, model):
        return assert_model(model, self.annarchy_instance, self._models_import_path)

    def build_spiking_population(self, label, model, size, params):
        """This methods builds an  ANNarchyPopulation instance,
           which represents a population of spiking neurons of the same neural model,
           and residing at a particular brain region node.
           Arguments:
            label: name (string) of the population
            model: name (string) of the neural model
            size: number (integer) of the neurons of this population
            params: dictionary of parameters of the neural model to be set upon creation
           Returns:
            a ANNarchyPopulation class instance
        """
        params["name"] = label
        annarchy_population = create_population(model, self.annarchy_instance, size=size,
                                                params=params, import_path=self._models_import_path)
        return ANNarchyPopulation(annarchy_population, label,
                                  annarchy_population.neuron_type.name, self.annarchy_instance)

    def connect_two_populations(self, pop_src, src_inds_fun, pop_trg, trg_inds_fun, conn_spec, syn_spec):
        """Method to connect two ANNarchyPopulation instances in the SpikingNetwork.
           Arguments:
            source: the source ANNarchyPopulation of the connection
            src_inds_fun: a function that selects a subset of the souce population neurons
            target: the target ANNarchyPopulation of the connection
            trg_inds_fun: a function that selects a subset of the target population neurons
            conn_spec: a dict of parameters of the connectivity pattern among the neurons of the two populations,
                       excluding weight and delay ones
            syn_spec: a dict of parameters of the synapses among the neurons of the two populations,
                      including weight, delay and synaptic target ones
        """
        # Prepare the synaptic model:
        syn_spec["synapse_model"] = self._assert_model(syn_spec["synapse_model"])
        # Get connection arguments by copying conn_spec. Make sure to pop out the "method" entry:
        conn_args = deepcopy(conn_spec)
        proj = connect_two_populations(pop_src, pop_trg, syn_spec["weights"], syn_spec["delays"],
                                       syn_spec["target"], params=syn_spec["params"],
                                       source_view_fun=src_inds_fun, target_view_fun=trg_inds_fun,
                                       synapse=syn_spec["synapse_model"], method=conn_args.pop("method"),
                                       name="%s -> %s" % (pop_src.label, pop_trg.label),
                                       annarchy_instance=self.annarchy_instance, **conn_args)
        # Add this projection to the source and target population inventories:
        pop_src.projections_pre.append(proj)
        pop_trg.projections_post.append(proj)

    def build_spiking_region_node(self, label="", input_node=None, *args, **kwargs):
        """This methods builds a ANNarchyRegionNode instance,
           which consists of a pandas.Series of all ANNarchyPopulation instances,
           residing at a particular brain region node.
           Arguments:
            label: name (string) of the region node. Default = ""
            input_node: an already created SpikingRegionNode() class. Default = None.
            *args, **kwargs: other optional positional or keyword arguments
           Returns:
            a ANNarchyRegionNode class instance
        """
        return ANNarchyRegionNode(label, input_node, self.annarchy_instance)

    def build_and_connect_devices(self, devices):
        """Method to build and connect input or output devices, organized by
           - the variable they measure or stimulate (pandas.Series), and the
           - population(s) (pandas.Series), and
           - brain region nodes (pandas.Series) they target.
           See tvb_multiscale.core.spiking_models.builders.factory,
           and tvb_multiscale.tvb_annarchy.annarchy_models.builders.annarchy_factory.
        """
        return build_and_connect_devices(devices, create_device, connect_device,
                                         self._spiking_brain, self.config, annarchy_instance=self.annarchy_instance,
                                         import_path=self._models_import_path)

    def build(self):
        """A method to build the final ANNarchyNetwork class based on the already created constituents."""
        return ANNarchyNetwork(self.annarchy_instance, self._spiking_brain,
                               self._output_devices, self._input_devices, config=self.config)
