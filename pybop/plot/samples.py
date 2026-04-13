from typing import TYPE_CHECKING

from pybop.plot import StandardPlot
from pybop.plot.util import update_and_show, get_default_options, call_plotting_function

if TYPE_CHECKING:
    from pybop.samplers.base_pints_sampler import SamplingResult


def chains(result: "SamplingResult", show=True, backend=None):
    """
    Plot posterior distributions for each chain.
    """
    options = get_default_options('posterior', backend)
    plot_options = options.get("plot_options") or {}
    trace_options = options.get("trace_options") or {}
    trace_options_vline = options.get("trace_options_vline") or {}

    plot_dict = StandardPlot(
        backend=backend,
        title="Posterior Distribution",
        xaxis_title="Value",
        yaxis_title="Density",
        **plot_options
    )

    for i, chain in enumerate(result.chains):
        for j in range(chain.shape[1]):
            hist = plot_dict.create_histogram(
                x=chain[:, j],
                name=f"Chain {i} - Parameter {j}",
                **trace_options
            )
            plot_dict.traces.append(hist)

    fig = plot_dict(show=False)
    for j in range(chain.shape[1]):
        plot_dict.create_vline(fig, result.mean[j], **trace_options_vline)
    
    update_and_show(fig, backend=backend)

def trace(result: "SamplingResult", show = True, backend=None):
    """
    Plot trace plots for the posterior samples.
    """
    figlist = []
    options = get_default_options('trace', backend)
    plot_options = options.get("plot_options") or {}
    trace_options = options.get("trace_options") or {}
    for i in range(result.n_parameters):
        plots = StandardPlot(
            title=f"Parameter {i} Trace Plot",
            xaxis_title="Sample Index",
            yaxis_title="Value",
            backend=backend,
            **plot_options
        )

        for j, chain in enumerate(result.chains):
            plots.traces.append(plots.create_trace(y=chain[:, i], label=f"Chain {j}", **trace_options))
        fig = plots(show=False)
        figlist.append(fig)

    update_and_show(figlist, show=show, backend=backend)

    return figlist

def posterior(result: "SamplingResult", backend=None):
    """
    Plot the summed posterior distribution across chains.
    """
    options = get_default_options('posterior', backend)
    plot_options = options.get("plot_options") or {}
    trace_options = options.get("trace_options") or {}
    trace_options_vline = options.get("trace_options_vline") or {}
    # Import plotly only when needed
    plot_dict = StandardPlot(
        backend=backend,
        title="Posterior Distribution",
        xaxis_title="Value",
        yaxis_title="Density",
        **plot_options
    )

    for j in range(result.all_samples.shape[1]):
        hist = plot_dict.create_histogram(
            x=result.all_samples[:, j],
            name=f"Parameter {j}",
            **trace_options
        )

        plot_dict.traces.append(hist)

    
    fig = plot_dict(show=False)
    for j in range(result.all_samples.shape[1]):
        plot_dict.create_vline(fig, result.mean[j], **trace_options_vline)

    update_and_show(fig, backend=backend)

def summary_table(result: "SamplingResult", backend=None):
    """
    Display summary statistics in a table.
    """

    summary_stats = result.get_summary_statistics()

    header = ["Statistic", "Value"]
    values = [
        ["Mean", summary_stats["mean"]],
        ["Median", summary_stats["median"]],
        ["Standard Deviation", summary_stats["std"]],
        ["95% CI Lower", summary_stats["ci_lower"]],
        ["95% CI Upper", summary_stats["ci_upper"]],
    ]
    
    call_plotting_function('show_table', backend=backend, header=header, values=values, title="Summary Statistics")