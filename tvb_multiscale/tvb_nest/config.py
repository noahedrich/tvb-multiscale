# -*- coding: utf-8 -*-

import sys
import os

from tvb_multiscale.core.config import Config as ConfigBase, log_path
from tvb_multiscale.core.utils.log_utils import initialize_logger as initialize_logger_base


TVB_NEST_DIR = os.path.abspath(__file__).split("tvb_nest")[0]
WORKING_DIR = os.environ.get("WORKING_DIR", os.getcwd())
MYMODULES_DIR = os.environ.get("MYMODULES_DIR",
                               os.path.join(TVB_NEST_DIR, "tvb_nest/nest/modules"))
MYMODULES_BLD_DIR = os.environ.get("MYMODULES_BLD_DIR",
                                   os.path.join(TVB_NEST_DIR, "tvb_nest/nest/modules_builds"))


class Config(ConfigBase):
    # WORKING DIRECTORY:
    TVB_NEST_DIR = TVB_NEST_DIR
    WORKING_DIR = WORKING_DIR
    RECORDINGS_DIR = os.path.join(WORKING_DIR, "nest_recordings")
    MYMODULES_DIR = MYMODULES_DIR
    MYMODULES_BLD_DIR = MYMODULES_BLD_DIR

    MASTER_SEED = 0

    # NEST properties:
    # M_ALL=0,  display all messages
    # M_DEBUG=5,  display debugging messages and above
    # M_STATUS=7,  display status messages and above
    # M_INFO=10, display information messages and above
    # M_DEPRECATED=18, display deprecation warnings and above
    # M_WARNING=20, display warning messages and above
    # M_ERROR=30, display error messages and above
    # M_FATAL=40, display failure messages and above
    # M_QUIET=100, suppress all messages
    NEST_VERBOCITY = 40

    DEFAULT_NEST_TOTAL_NUM_VIRTUAL_PROCS = 1

    DEFAULT_NEST_KERNEL_CONFIG = {"data_path": RECORDINGS_DIR, "overwrite_files": True, "print_time": True,
                                  'grng_seed': MASTER_SEED + DEFAULT_NEST_TOTAL_NUM_VIRTUAL_PROCS,
                                  'rng_seeds': range(MASTER_SEED + 1 + DEFAULT_NEST_TOTAL_NUM_VIRTUAL_PROCS,
                                                     MASTER_SEED + 1 + (2 * DEFAULT_NEST_TOTAL_NUM_VIRTUAL_PROCS))}
    DEFAULT_MODEL = "iaf_cond_alpha"

    # Delays should be at least equal to NEST time resolution
    DEFAULT_SYNAPSE = "static_synapse"
    DEFAULT_CONNECTION = {"synapse_model": DEFAULT_SYNAPSE, "weight": 1.0, "delay": 1.0, 'receptor_type': 0,
                          "source_inds": None, "target_inds": None, "params": {},
                          "syn_spec": {"synapse_model": DEFAULT_SYNAPSE, "params": {}},
                          "conn_spec": {"allow_autapses": True, 'allow_multapses': True, 'rule': "all_to_all",
                                        "indegree": None, "outdegree": None, "N": None, "p": 0.1}}

    DEFAULT_TVB_TO_NEST_INTERFACE = "inhomogeneous_poisson_generator"
    DEFAULT_NEST_TO_TVB_INTERFACE = "spike_recorder"

    # Available NEST output devices for the interface and their default properties
    NEST_OUTPUT_DEVICES_PARAMS_DEF = {"multimeter": {"record_from": ["V_m"], "record_to": "memory"},
                                      "voltmeter": {"record_to": "memory"},
                                      "spike_recorder": {"record_to": "memory"},
                                      "spike_multimeter": {'record_from': ["spike"], "record_to": "memory"}}

    NEST_INPUT_DEVICES_PARAMS_DEF = {"spike_generator": {"allow_offgrid_times": False},
                                     "poisson_generator": {},
                                     "mip_generator": {"p_copy": 0.5, "mother_seed": 0},
                                     "inhomogeneous_poisson_generator": {"allow_offgrid_times": False}}

    def __init__(self, output_base=None, separate_by_run=False, initialize_logger=True):
        super(Config, self).__init__(output_base, separate_by_run, initialize_logger)
        self.NEST_PATH = os.environ["NEST_INSTALL_DIR"]
        self.PYTHON = os.environ["NEST_PYTHON_PREFIX"]
        self.DATA_DIR = os.path.join(self.NEST_PATH, "share/nest")
        self.SLI_PATH = os.path.join(self.DATA_DIR, "sli")
        self.DOC_DIR = os.path.join(self.NEST_PATH, "share/doc/nest")
        self.MODULE_PATH = os.path.join(self.NEST_PATH, "lib/nest")
        self.TVB_NEST_DIR = TVB_NEST_DIR
        self.WORKING_DIR = WORKING_DIR
        self.RECORDINGS_DIR = os.path.join(self.out.FOLDER_RES, "nest_recordings")
        self.DEFAULT_NEST_KERNEL_CONFIG["data_path"] = self.RECORDINGS_DIR
        self.MYMODULES_DIR = MYMODULES_DIR
        self.MYMODULES_BLD_DIR = MYMODULES_BLD_DIR

    def configure_nest_path(self, logger=None):
        if logger is None:
            logger = initialize_logger_base(__name__, self.out.FOLDER_LOGS)
        logger.info("Loading a NEST instance...")
        nest_path = self.NEST_PATH
        os.environ['NEST_INSTALL_DIR'] = nest_path
        log_path('NEST_INSTALL_DIR', logger)
        os.environ['NEST_DATA_DIR'] = os.path.join(nest_path, "share/nest")
        log_path('NEST_DATA_DIR', logger)
        os.environ['NEST_DOC_DIR'] = os.path.join(nest_path, "share/doc/nest")
        log_path('NEST_DOC_DIR', logger)
        os.environ['NEST_MODULE_PATH'] = os.path.join(nest_path, "lib/nest")
        log_path('NEST_MODULE_PATH', logger)
        os.environ['PATH'] = os.path.join(nest_path, "bin") + ":" + os.environ['PATH']
        log_path('PATH', logger)
        LD_LIBRARY_PATH = os.environ.get('LD_LIBRARY_PATH', '')
        if len(LD_LIBRARY_PATH) > 0:
            LD_LIBRARY_PATH = ":" + LD_LIBRARY_PATH
        os.environ['LD_LIBRARY_PATH'] = os.environ['NEST_MODULE_PATH'] + LD_LIBRARY_PATH
        log_path('LD_LIBRARY_PATH', logger)
        os.environ['SLI_PATH'] = os.path.join(os.environ['NEST_DATA_DIR'], "sli")
        log_path('SLI_PATH', logger)
        os.environ['NEST_PYTHON_PREFIX'] = self.PYTHON
        log_path('NEST_PYTHON_PREFIX', logger)
        sys.path.insert(0, os.environ['NEST_PYTHON_PREFIX'])
        logger.info("%s: %s" % ("system path", sys.path))


CONFIGURED = Config(initialize_logger=False)
CONFIGURED.configure_nest_path()


def initialize_logger(name, target_folder=None):
    if target_folder is None:
        target_folder = Config().out.FOLDER_LOGS
    return initialize_logger_base(name, target_folder)
