from pm4py.algo.conformance.tokenreplay import factory as tr_factory
from collections import Counter
from copy import copy


def give_color_to_direction_static(dir):
    """
    Assigns a color to the direction (static-defined colors)

    Parameters
    --------------
    dir
        Direction

    Returns
    --------------
    col
        Color
    """
    direction_colors = [[-0.5, "#4444FF"], [-0.1, "#AAAAFF"], [0.0, "#CCCCCC"], [0.5, "#FFAAAA"], [1.0, "#FF4444"]]
    for col in direction_colors:
        if col[0] >= dir:
            return col[1]


def compare_element_usage_two_logs(net, im, fm, log1, log2, parameters=None):
    """
    Returns some statistics (also visual) about the comparison of the usage
    of the elements in two logs given an accepting Petri net

    Parameters
    -------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    log1
        First log
    log2
        Second log
    parameters
        Parameters of the algorithm (to be passed to the token-based replay)

    Returns
    ----------------
    aggregated_statistics
        Statistics about the usage of places, transitions and arcs in the net
    """
    if parameters is None:
        parameters = {}

    tr_parameters = copy(parameters)
    tr_parameters["enable_place_fitness"] = True

    rep_traces1, pl_fit_trace1, tr_fit_trace1, ne_act_model1 = tr_factory.apply(log1, net, im, fm,
                                                                                parameters=tr_parameters)
    rep_traces2, pl_fit_trace2, tr_fit_trace2, ne_act_model2 = tr_factory.apply(log2, net, im, fm,
                                                                                parameters=tr_parameters)

    tr_occ1 = Counter([y for x in rep_traces1 for y in x["activated_transitions"]])
    tr_occ2 = Counter([y for x in rep_traces2 for y in x["activated_transitions"]])
    pl_occ1 = Counter({p: pl_fit_trace1[p]["c"] + pl_fit_trace1[p]["r"] for p in pl_fit_trace1})
    pl_occ2 = Counter({p: pl_fit_trace2[p]["c"] + pl_fit_trace2[p]["r"] for p in pl_fit_trace2})

    all_replayed_transitions = set(tr_occ1.keys()).union(set(tr_occ2.keys()))
    all_replayed_places = set(pl_occ1.keys()).union(set(pl_occ2.keys()))

    all_transitions = all_replayed_transitions.union(set(net.transitions))
    all_places = all_replayed_places.union(set(net.places))
    aggregated_statistics = {}
    for place in all_places:
        aggregated_statistics[place] = {"log1_occ": pl_occ1[place], "log2_occ": pl_occ2[place],
                                        "total_occ": pl_occ1[place] + pl_occ2[place]}
        aggregated_statistics[place]["label"] = "(%d/%d/%d)" % (
            pl_occ1[place], pl_occ2[place], pl_occ1[place] + pl_occ2[place])
        dir = (pl_occ2[place] - pl_occ1[place]) / (pl_occ1[place] + pl_occ2[place]) if (pl_occ1[place] + pl_occ2[
            place]) > 0 else 0
        aggregated_statistics[place]["direction"] = dir
        aggregated_statistics[place]["color"] = give_color_to_direction_static(dir)

    for trans in all_transitions:
        aggregated_statistics[trans] = {"log1_occ": tr_occ1[trans], "log2_occ": tr_occ2[trans],
                                        "total_occ": tr_occ1[trans] + tr_occ2[trans]}
        if trans.label is not None:
            aggregated_statistics[trans]["label"] = trans.label+" "
        else:
            aggregated_statistics[trans]["label"] = ""
        aggregated_statistics[trans]["label"] = aggregated_statistics[trans]["label"] + "(%d/%d/%d)" % (
            tr_occ1[trans], tr_occ2[trans], tr_occ1[trans] + tr_occ2[trans])
        dir = (tr_occ2[trans] - tr_occ1[trans]) / (tr_occ1[trans] + tr_occ2[trans]) if (tr_occ1[trans] + tr_occ2[
            trans]) > 0 else 0
        aggregated_statistics[trans]["direction"] = dir
        aggregated_statistics[trans]["color"] = give_color_to_direction_static(dir)
        for arc in trans.in_arcs:
            aggregated_statistics[arc] = aggregated_statistics[trans]
        for arc in trans.out_arcs:
            aggregated_statistics[arc] = aggregated_statistics[trans]

    return aggregated_statistics
