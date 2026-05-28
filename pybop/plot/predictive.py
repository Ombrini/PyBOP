from typing import TYPE_CHECKING

import numpy as np

from pybop.plot.util import import_backend, remove_brackets
from pybop.problems.meta_problem import MetaProblem
from pybop.simulators.failed_solution import FailedSolution

if TYPE_CHECKING:
    from pybop.optimisers.ep_bolfi_optimiser import BayesianOptimisationResult
    from pybop.samplers.base_sampler import SamplingResult


def predictive(
    result: "BayesianOptimisationResult | SamplingResult",
    number_of_traces: int = 8,
    data_legend_entry=None,
    rvs_legend_entry=None,
    pdf_plot=None,
    pdf_label: str = "PDF",
    colour_scale="viridis",
    show: bool = True,
    backend: str | None = None,
):
    """
    Plot the predictive posterior of a Bayesian optimisation result.
    """

    posterior_samples = result.posterior.sample_from_distribution(
        n_samples=number_of_traces
    )
    posterior_samples_pdf = np.asarray(
        [result.posterior.distribution.pdf(s) for s in posterior_samples]
    )
    pdf_range = np.asarray([posterior_samples_pdf.min(), posterior_samples_pdf.max()])

    # Create a plot for each problem
    problems = (
        result.problem.problems
        if isinstance(result.problem, MetaProblem)
        else [result.problem]
    )
    figure_list = []
    backend_module = import_backend(backend)

    for problem in problems:
        fig = backend_module.create_figure(
            xaxis_title=remove_brackets(problem.domain),
            yaxis_title=remove_brackets(problem.target[0]),
            style={
                "bg_color" : "white",
                "width" : 600,
                "height" : 600
            }
        )

        backend_module.plot_trace(
            backend_module.line_plot(
                x=problem.domain_data,
                y=problem.target_data[problem.target[0]],
                label=data_legend_entry

            ),
            fig
        )

        # Simulate the samples and add to plot
        inputs = [problem.parameters.to_dict(s) for s in posterior_samples]
        simulations = problem.simulate_batch(inputs=inputs)
        for pdf, sim in zip(posterior_samples_pdf, simulations, strict=False):
            if not isinstance(sim, FailedSolution):
                colors = backend_module.sample_color_scale(pdf, d_min = pdf_range[0], d_max=pdf_range[1] )
                backend_module.plot_trace(
                    backend_module.line_plot(
                        x=problem.domain_data,
                        y=sim[problem.target[0]].data,
                        style=dict(
                            color=colors[0],
                            linestyle="dotted"
                        )
                    ),
                    fig
                )

        # Add the colourbar
        backend_module.colorbar(fig, pdf_range, colorscale=colour_scale, label="Posterior PDF")

        if pdf_plot is not None:
            backend_module.plot_trace(
                backend_module.line_plot(
                    x=pdf_plot[0],
                    y=pdf_plot[1],
                    trace_names=pdf_label,
                )
            )
        if show:
            backend_module.show_figure(fig)

        figure_list.append(fig)

    return figure_list
