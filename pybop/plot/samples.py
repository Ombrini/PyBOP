from typing import TYPE_CHECKING

import numpy as np

from pybop.plot.util import get_backend_from_figure

if TYPE_CHECKING:
    from pybop.samplers.base_pints_sampler import SamplingResult


def chains(result: "SamplingResult", show=True, backend=None, figures=None, axes=None):
    """
    Plot posterior distributions for each chain.
    """
    # Import backend
    backend = get_backend_from_figure(backend, figures)
    figures, axes, create_figure, _ = backend.parse_input_axes(
        figures, axes, num_plots=1
    )
    fig = backend.create_figure() if create_figure else figures[0]
    ax = axes[0]

    backend.update_axes_titles(fig, ax, "Value", "Density")
    backend.update_plot_titles(fig, ax, "Posterior Distribution")

    for i, chain in enumerate(result.chains):
        for j in range(chain.shape[1]):
            backend.plot_trace(
                backend.histogram_plot(
                    x=chain[:, j],
                    name=f"Chain {i} - Parameter {j}",
                    style=dict(alpha=0.75),
                ),
                fig,
                ax=ax,
            )

            backend.vline(
                fig,
                result.mean[j],
                style=dict(linewidth=1, linestyle="dashed", color="black"),
                ax=ax,
            )

    backend.legend(fig)

    if show:
        backend.show_figure(fig)
    else:
        return fig


def trace(result: "SamplingResult", show=True, backend=None, figures=None, axes=None):
    """
    Plot trace plots for the posterior samples.
    """
    # Import plotting backend
    backend = get_backend_from_figure(backend, figures)

    # Process input
    figures, axes, create_figure, single_axis = backend.parse_input_axes(
        figures, axes, num_plots=result.n_parameters
    )

    for i in range(result.n_parameters):
        ax = axes[i % len(axes)]
        title = "Parameter Trace Plot" if single_axis else f"Parameter {i} Trace Plot"
        if create_figure:
            fig = backend.create_figure()
            figures = np.append(figures, fig)

        fig = figures[i % len(figures)]
        backend.update_axes_titles(fig, ax, "Sample Index", "Value")
        if i == 0 or not single_axis:
            backend.update_plot_titles(fig, ax, title)

        for j, chain in enumerate(result.chains):
            label = f"Parameter {i} Chain {j}" if single_axis else f"Chain {j}"
            backend.plot_trace(backend.line(y=chain[:, i], label=label), fig, ax=ax)
        backend.legend(fig)

    if show:
        backend.show_figure(figures)
    else:
        return figures


def posterior(
    result: "SamplingResult", backend=None, show=True, figures=None, axes=None
):
    """
    Plot the summed posterior distribution across chains.
    """
    # Import backend
    backend = get_backend_from_figure(backend, figures)

    # Parse input
    figures, axes, create_figure, _ = backend.parse_input_axes(
        figures, axes, num_plots=1
    )
    fig = backend.create_figure() if create_figure else figures[0]
    ax = axes[0]

    backend.update_axes_titles(fig, ax, "Value", "Density")
    backend.update_plot_titles(fig, ax, "Posterior Distribution")

    for j in range(result.all_samples.shape[1]):
        backend.plot_trace(
            backend.histogram_plot(
                x=result.all_samples[:, j],
                name=f"Parameter {j}",
                style=dict(alpha=0.75),
            ),
            fig,
            ax=ax,
        )
        backend.vline(
            fig,
            result.mean[j],
            style=dict(linewidth=1, linestyle="dashed", color="black"),
            ax=ax,
        )

    backend.legend(fig)

    if show:
        backend.show_figure(fig)
    else:
        return fig


def summary_table(
    result: "SamplingResult", backend=None, figures=None, axes=None, show=True
):
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

    backend = get_backend_from_figure(backend, figures)
    figures, axes, create_figure, _ = backend.parse_input_axes(
        figures, axes, num_plots=1
    )
    fig = None if create_figure else figures[0]
    ax = axes[0]
    fig = backend.show_table(
        header=header,
        values=values,
        title="Summary Statistics",
        fig=fig,
        ax=ax,
    )
    if show:
        backend.show_figure(fig)
    else:
        return fig
