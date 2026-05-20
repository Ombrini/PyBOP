from typing import TYPE_CHECKING

from pybop.plot import StandardPlot
from pybop.plot.util import get_default_options, import_backend
from pybop.plot.plotly import PlotlyManager

if TYPE_CHECKING:
    from pybop.samplers.base_pints_sampler import SamplingResult


def chains(result: "SamplingResult", show=True, backend=None):
    """
    Plot posterior distributions for each chain.
    """
    options = get_default_options("posterior", backend)
    plot_options = options.get("plot_options") or {}
    trace_options = options.get("trace_options") or {}
    trace_options_vline = options.get("trace_options_vline") or {}

    # Import backend
    backend = import_backend(backend)
    

    fig = backend.create_figure(
        title="Posterior Distribution",
        xaxis_title="Value",
        yaxis_title="Density",
        **plot_options
    )

    for i, chain in enumerate(result.chains):
        for j in range(chain.shape[1]):
            backend.plot_trace(
                backend.histogram_plot(
                    x=chain[:, j],
                    name=f"Chain {i} - Parameter {j}",
                    **trace_options
                ),
                fig
            )

            backend.add_vline(
                fig, 
                result.mean[j],
                **trace_options_vline
            )

    backend.legend(fig)
            
    if show:
        backend.show_figure(fig)

def trace(result: "SamplingResult", show=True, backend=None):
    """
    Plot trace plots for the posterior samples.
    """
    # Import plotting backend
    backend = import_backend(backend)


    figlist = []
    for i in range(result.n_parameters):
        fig = backend.create_figure(
            title=f"Parameter {i} Trace Plot",
            xaxis_title="Sample Index",
            yaxis_title="Value",
        )
        for j, chain in enumerate(result.chains):
            backend.plot_trace(
                backend.line_plot(y=chain[:, i], label=f"Chain {j}"),
                fig
            )
        backend.legend(fig)
        figlist.append(fig)

    if show:
        backend.show_figure(figlist)

    return figlist



def posterior(result: "SamplingResult", backend=None, show=True):
    """
    Plot the summed posterior distribution across chains.
    """
    options = get_default_options("posterior", backend)
    plot_options = options.get("plot_options") or {}
    trace_options = options.get("trace_options") or {}
    trace_options_vline = options.get("trace_options_vline") or {}
    # Import backend
    backend = import_backend(backend)
    fig = backend.create_figure(
        title="Posterior Distribution",
        xaxis_title="Value",
        yaxis_title="Density",
        **plot_options,
    )

    for j in range(result.all_samples.shape[1]):
        backend.plot_trace(
            backend.histogram_plot(
                x=result.all_samples[:, j], name=f"Parameter {j}", **trace_options
            ),
            fig
        )
        backend.add_vline(fig, result.mean[j], **trace_options_vline)

    backend.legend(fig)

    if show:
        backend.show_figure(fig)


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

    backend = import_backend(backend)
    backend.show_table(
        header=header,
        values=values,
        title="Summary Statistics",
    )

