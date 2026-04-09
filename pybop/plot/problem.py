import numpy as np

from pybop.costs.design_cost import DesignCost
from pybop.costs.error_measures import ErrorMeasure
from pybop.parameters.parameter import Inputs
from pybop.plot.matplotlib.standard_plots import StandardPlot
from pybop.plot.util import get_default_options, update_and_show
from pybop.problems.meta_problem import MetaProblem
from pybop.problems.problem import Problem
from pybop.simulators.solution import Solution


def problem(
    problem: Problem,
    inputs: Inputs = None,
    show: bool = True,
    title="Scatter Plot",
    backend = None,
):
    """
    Produce a quick plot of the target dataset against optimised model output.

    Generates an interactive plot comparing the simulated model output with
    an optional target dataset and visualises uncertainty.

    Parameters
    ----------
    problem : pybop.Problem
        Problem object with dataset and targets attributes.
    inputs : Inputs
        Optimised (or example) parameter values.
    show : bool, optional
        If True, the figure is shown upon creation (default: True).

    Returns
    -------
    plotly.graph_objs.Figure
        The Plotly figure object for the scatter plot.
    """
    if inputs is None:
        inputs = problem.parameters.to_dict()
    elif not isinstance(inputs, dict):
        raise TypeError(f"Expecting a dictionary, received {type(inputs)}")

    domain = problem.domain
    if problem.domain_data is None:
        # Simulate the model for the both the initial and the given inputs
        target = problem.target
        problem.set_target(target + [domain])
        initial_inputs = problem.simulator.parameters.to_dict("initial")
        target_output = problem.simulate(initial_inputs)
        target_domain = target_output[domain].data
        model_output = problem.simulate(inputs)
        model_domain = model_output[domain].data
        problem.set_target(target)
    else:
        # Extract the time data and simulate the model for the given inputs
        target_output = Solution()
        for target in problem.target:
            target_output.set_solution_variable(
                target, data=problem.target_data[target]
            )
        target_domain = problem.domain_data
        model_output = problem.simulate(inputs)
        model_domain = target_domain[: len(model_output[target].data)]

    # Retrieve default layout options
    plot_options = get_default_options('problem', backend)
    trace_options = plot_options.get('default_trace_options') or {}
    design_cost_options = plot_options.get('design_cost_options') or {}
    meta_problem_options = plot_options.get('meta_problem_options') or {}
    reference_options = plot_options.get('reference_options') or {}
    fill_options = plot_options.get('fill_options') or {}

    # Create a plot for each output
    figure_list = []
    for var in problem.target:
        options = trace_options.copy()
        if isinstance(problem, MetaProblem):
            options.update(meta_problem_options)
        if isinstance(problem.cost, DesignCost):
            options.update(design_cost_options)

        print(isinstance(problem, MetaProblem), isinstance(problem.cost, DesignCost), options)

        # Create a plot dictionary
        plot_dict = StandardPlot(backend=backend)

        model_trace = plot_dict.create_trace(
            x=model_domain,
            y=model_output[var].data,
            **options
        )
        plot_dict.traces.append(model_trace)

        target_trace =plot_dict.create_trace(
            x=target_domain,
            y=target_output[var].data,
            **reference_options
        )
        plot_dict.traces.append(target_trace)

        if isinstance(problem.cost, ErrorMeasure) and len(
            model_output[var].data
        ) == len(target_output[var].data):
            # Compute the standard deviation as proxy for uncertainty
            plot_dict.sigma = np.std(model_output[var].data - target_output[var].data)

            # Convert x and upper and lower limits into lists to create a filled trace
            x = target_domain.tolist()
            y_upper = (model_output[var].data + plot_dict.sigma).tolist()
            y_lower = (model_output[var].data - plot_dict.sigma).tolist()

            fill_trace = plot_dict.create_fill_trace(x, y_upper, y_lower, **fill_options)
        plot_dict.traces = plot_dict.traces[::-1]
        # Generate the figure and update the layout
        fig = plot_dict(show=False)
        # plt.xlabel("Time / s")
        # plt.ylabel(StandardPlot.remove_brackets(var))
        # plt.title(title)
        # plt.legend()
        # plt.tight_layout()
        fig = update_and_show(fig, backend=backend)

        figure_list.append(fig)

    return figure_list
