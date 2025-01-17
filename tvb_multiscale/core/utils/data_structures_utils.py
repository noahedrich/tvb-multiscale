# -*- coding: utf-8 -*-

from inspect import stack
from itertools import product
from collections import OrderedDict
from six import string_types

import numpy as np
from scipy.stats import describe
from pandas import unique
from xarray import DataArray


from tvb.contrib.scripts.utils.data_structures_utils import \
    ensure_list, flatten_list, is_integer, extract_integer_intervals


def get_caller_fun_name(caller_id=1):
    return str(stack()[caller_id][3])


def get_ordered_dimensions(dims, dims_order):
    out_dims = []
    for dim in dims_order:
        if dim in dims:
            out_dims.append(dim)
    return out_dims


def flatten_neurons_inds_in_DataArray(data_array, neurons_dim_label="Neuron"):
    dims = list(data_array.dims)
    try:
        dim_id = dims.index(neurons_dim_label)
    except:
        dim_id = -1
    neurons_dim_label = dims[dim_id]
    neuron_labels = np.arange(data_array.shape[dim_id])
    data_array.coords[neurons_dim_label] = neuron_labels
    return data_array


def filter_events(events, variables=None, times=None, exclude_times=[]):
    """This method will select/exclude part of the measured events, depending on user inputs
        Arguments:
            events: dictionary of events
            variables: sequence (list, tuple, array) of variables to be included in the output,
                       assumed to correspond to keys of the events dict.
                       Default=None, corresponds to all keys of events.
            times: sequence (list, tuple, array) of times the events of which should be included in the output.
                     Default = None, corresponds to all events' times.
            exclude_times: sequence (list, tuple, array) of times
                             the events of which should be excluded from the output. Default = [].
        Returns:
              the filtered dictionary (of arrays per attribute) of events
    """

    def in_fun(values):
        # Function to return a boolean about whether a value is
        # within a sequence or an interval (len(values) == 2) of values:
        if len(values) == 2:
            if values[0] is not None:
                if values[1] is not None:
                    return lambda x: x >= values[0] and x <= values[1]
                else:
                    return lambda x: x >= values[0]
            elif values[1] is not None:
                return lambda x: x <= values[0]
            else:
                return lambda x: x
        else:
            return lambda x: x in values

    # The variables to return:
    if variables is None:
        variables = events.keys()

    # The events:
    output_events = OrderedDict()

    events_times = np.array(events["times"])

    n_events = len(events["times"])
    if n_events > 0:
        # As long as there are events:
        # If we (un)select times...
        if times is not None and len(times) > 0:
            in_times = in_fun(flatten_list(times))
        else:
            in_times = lambda x: True
        if exclude_times is not None and len(exclude_times) > 0:
            not_in_exclude_times = lambda x: not in_fun(flatten_list(exclude_times))(x)
        else:
            not_in_exclude_times = lambda x: True
        inds = np.logical_and(np.ones((n_events,)),
                              [in_times(time) and not_in_exclude_times(time)
                               for time in events_times])
        for var in ensure_list(variables):
            output_events[var] = events[var][inds]
    else:
        for var in ensure_list(variables):
            output_events[var] = []
    return output_events


def summarize(results, digits=None):

    def unique_floats_fun(vals):
        scale = 10 ** np.floor(np.log10(np.percentile(np.abs(vals), 95)))
        return scale * unique(np.around(vals / scale, decimals=digits))

    def stats_fun(vals):
        d = describe(vals)
        summary = {}
        summary["n"] = d.nobs
        summary["mean"] = d.mean
        summary["minmax"] = d.minmax
        summary["var"] = d.variance
        return summary

    output = {}
    for attr, val in results.items():
        vals = ensure_list(val)
        try:
            val_type = str(np.array(vals).dtype)
            if isinstance(vals[0], string_types) or val_type[0] == "i" or val_type[0] == "b" or val_type[0] == "o":
                # String, integer or boolean values
                unique_vals = list(unique(vals).astype(val_type))
                n_unique_vals = len(unique_vals)
                if n_unique_vals < 2:
                    # If they are all of the same value, just set this value:
                    output[attr] = unique_vals[0]
                elif n_unique_vals <= 10:
                    # Otherwise, return a summary dictionary with the indices of each value:
                    output[attr] = OrderedDict()
                    vals = np.array(vals)
                    for unique_val in unique_vals:
                        output[attr][unique_val] = extract_integer_intervals(np.where(vals == unique_val)[0])
                else:
                    if val_type[0] == "i":
                        output[attr] = extract_integer_intervals(vals)
                    else:
                        output[attr] = unique_vals
            else:  # Assuming floats or arbitrary objects...
                unique_vals = unique(vals)
                if len(unique_vals) > 3:
                    # If there are more than three different values, try to summarize them...
                    try:
                        if is_integer(digits):
                            output[attr] = unique_floats_fun(unique_vals)
                        else:
                            output[attr] = stats_fun(np.array(vals))
                    except:
                        output[attr] = unique_vals
                else:
                    if len(unique_vals) == 1:
                        output[attr] = unique_vals[0]
                    output[attr] = unique_vals
        except:
            # Something went wrong, return the original propety
            output[attr] = list(vals)
    return output


def cross_dimensions_and_coordinates_MultiIndex(dims, pop_labels, all_regions_lbls):
    from pandas import MultiIndex
    stacked_dims = "-".join(dims)
    names = []
    new_dims = []
    for d in ["i", "j"]:
        names.append([dim + "_" + d for dim in dims])
        new_dims.append(stacked_dims + "_" + d)
    new_coords = {new_dims[0]: MultiIndex.from_product([pop_labels, all_regions_lbls], names=names[0]),
                  new_dims[1]: MultiIndex.from_product([pop_labels, all_regions_lbls], names=names[1])}
    return new_dims, new_coords


def combine_DataArray_dims(arr, dims_combinations, join_string=", ", return_array=True):
    new_dims = []
    new_coords = {}
    stacked_dims = {}
    for dim_combin in dims_combinations:
        new_dim = join_string.join(["%s" % arr.dims[i_dim] for i_dim in dim_combin])
        new_dims.append(new_dim)
        stacked_dims[new_dim] =[arr.dims[i_dim] for i_dim in dim_combin]
        new_coords[new_dim] = [join_string.join(coord_combin)
                               for coord_combin in product(*[arr.coords[arr.dims[i_dim]].data for i_dim in dim_combin])]
    if return_array:
        return DataArray(arr.stack(**stacked_dims).data, dims=new_dims, coords=new_coords, name=arr.name)
    else:
        return arr.stack(**stacked_dims).data, new_dims, new_coords

