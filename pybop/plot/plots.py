from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from pybop._result import Result
    from pybop.samplers.base_pints_sampler import SamplingResult

from pybop.parameters.parameter import Inputs
from pybop.plot.util import call_plotting_function
from pybop.problems.problem import Problem


def chains(result: "SamplingResult", show=True, backend=None, **kwargs):
    """
    Plot posterior distributions for each chain.
    """
    return call_plotting_function("chains", backend, result=result, **kwargs)


def contour(
    call_object: "Problem | Result",
    gradient: bool = False,
    bounds: np.ndarray | None = None,
    transformed: bool = False,
    steps: int = 10,
    show: bool = True,
    backend=None,
    **layout_kwargs,
):
    """
    Plot a 2D visualisation of a cost landscape using Plotly.

    This function generates a contour plot representing the cost landscape for a provided
    callable cost function over a grid of parameter values within the specified bounds.

    Parameters
    ----------
    call_object : pybop.Problem | pybop.Result
        Either:
        - the cost function to be evaluated. Must accept a list of parameter values and return a cost value.
        - an optimiser result which provides a specific optimisation trace overlaid on the cost landscape.
    gradient : bool, optional
        If True, the gradient is shown (default: False).
    bounds : numpy.ndarray | list[list[float]], optional
        A 2x2 array specifying the [min, max] bounds for each parameter. If None, uses
        `parameters.get_bounds_for_plotly`.
    transformed : bool, optional
        Uses the transformed parameter values (as seen by the optimiser) for plotting.
    steps : int, optional
        The number of grid points to divide the parameter space into along each dimension (default: 10).
    show : bool, optional
        If True, the figure is shown upon creation (default: True).
    **layout_kwargs : optional
        Valid Plotly layout keys and their values,
        e.g. `xaxis_title="Time [s]"` or
        `xaxis={"title": "Time [s]", font={"size":14}}`

    Returns
    -------
    plotly.graph_objs.Figure
        The Plotly figure object containing the cost landscape plot.

    Raises
    ------
    ValueError
        If the cost function does not return a valid cost when called with a parameter list.
    """
    return call_plotting_function(
        "contour",
        backend,
        call_object=call_object,
        gradient=gradient,
        bounds=bounds,
        transformed=transformed,
        steps=steps,
        show=show,
        **layout_kwargs,
    )


def convergence(result: "Result", show=True, backend=None, **layout_kwargs):
    """
    Plot the convergence of the optimisation algorithm.

    Parameters
    -----------
    result : pybop.Result
        Optimisation result containing the history of parameter values and associated cost.
    show : bool, optional
        If True, the figure is shown upon creation (default: True).
    **layout_kwargs : optional
        Valid Plotly layout keys and their values,
        e.g. `xaxis_title="Time [s]"` or
        `xaxis={"title": "Time [s]", font={"size":14}}`

    Returns
    ---------
    fig : plotly.graph_objs.Figure
        The Plotly figure object for the convergence plot.
    """
    return call_plotting_function(
        "convergence", backend, result=result, show=show, **layout_kwargs
    )


def dataset(
    dataset, signal=None, trace_names=None, show=True, backend=None, **layout_kwargs
):
    """
    Quickly plot a PyBOP Dataset using Plotly.

    Parameters
    ----------
    dataset : object
        A PyBOP dataset.
    signal : list or str, optional
        The name of the time series to plot (default: "Voltage [V]").
    trace_names : list or str, optional
        Name(s) for the trace(s) (default: "Data").
    show : bool, optional
        If True, the figure is shown upon creation (default: True).
    **layout_kwargs : optional
        Valid Plotly layout keys and their values,
        e.g. `xaxis_title="Time / s"` or
        `xaxis={"title": "Time [s]", font={"size":14}}`

    Returns
    -------
    plotly.graph_objs.Figure
        The Plotly figure object for the scatter plot.
    """
    call_plotting_function(
        "dataset",
        backend,
        dataset=dataset,
        signal=signal,
        trace_names=trace_names,
        show=show,
        **layout_kwargs,
    )


def nyquist(problem, inputs: Inputs = None, show=True, backend=None, **layout_kwargs):
    """
    Generates Nyquist plots for the given problem by evaluating the model's output and target values.

    Parameters
    ----------
    problem : pybop.Problem
        An instance of a problem class that contains the parameters and methods
        for evaluation and target retrieval.
    inputs : Inputs, optional
        Input parameters for the problem. If not provided, the default parameters from the problem
        instance will be used. These parameters are verified before use (default is None).
    show : bool, optional
        If True, the plots will be displayed.
    **layout_kwargs : dict, optional
        Additional keyword arguments for customising the plot layout. These arguments are passed to
        `fig.update_layout()`.

    Returns
    -------
    list
        A list of plotly `Figure` objects, each representing a Nyquist plot for the model's output and target values.

    Notes
    -----
    - The function extracts the real part of the impedance from the model's output and the real and imaginary parts
      of the impedance from the target output.
    - For each signal in the problem, a Nyquist plot is created with the model's impedance plotted as a scatter plot.
    - An additional trace for the reference (target output) is added to the plot.
    - The plot layout can be customised using `layout_kwargs`.

    Example
    -------
    >>> problem = pybop.EISProblem()
    >>> nyquist_figures = nyquist(problem, show=True, title="Nyquist Plot", xaxis_title="Real(Z)", yaxis_title="Imag(Z)")
    >>> # The plots will be displayed and nyquist_figures will contain the list of figure objects.
    """
    return call_plotting_function(
        "nyquist", backend, problem=problem, inputs=inputs, show=show, **layout_kwargs
    )


def parameters(result: "Result", show=True, backend=None, **layout_kwargs):
    """
    Plot the evolution of parameters during the optimisation process using Plotly.

    Parameters
    ----------
    result : pybop.Result
        Optimisation result containing the history of parameter values and associated cost.
    show : bool, optional
        If True, the figure is shown upon creation (default: True).
    **layout_kwargs : optional
        Valid Plotly layout keys and their values,
        e.g. `xaxis_title="Time [s]"` or
        `xaxis={"title": "Time [s]", font={"size":14}}`

    Returns
    -------
    plotly.graph_objs.Figure
        A Plotly figure object showing the parameter evolution over iterations.
    """
    return call_plotting_function(
        "parameters", backend, result=result, show=show, **layout_kwargs
    )


def posterior(result: "SamplingResult", show=True, backend=None, **kwargs):
    """
    Plot the summed posterior distribution across chains.
    """
    return call_plotting_function("posterior", backend, result=result, **kwargs)


def problem(
    problem: Problem,
    inputs: Inputs = None,
    show: bool = True,
    backend=None,
    **layout_kwargs,
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
    **layout_kwargs : optional
            Valid Plotly layout keys and their values,
            e.g. `xaxis_title="Time / s"` or
            `xaxis={"title": "Time [s]", font={"size":14}}`

    Returns
    -------
    plotly.graph_objs.Figure
        The Plotly figure object for the scatter plot.
    """
    return call_plotting_function(
        "problem", backend, problem=problem, inputs=inputs, show=show, **layout_kwargs
    )


def summary_table(result: "SamplingResult", backend=None):
    """
    Display summary statistics in a table.
    """

    return call_plotting_function("summary_table", backend, result=result)


def surface(
    result: "Result",
    bounds=None,
    normalise=True,
    resolution=250,
    show=True,
    backend=None,
    **layout_kwargs,
):
    """
    Plot a 2D representation of the Voronoi diagram with color-coded regions.

    Parameters:
    -----------
    result : pybop.Result
        Optimisation result containing the history of parameter values and associated cost.
    bounds : numpy.ndarray, optional
        A 2x2 array specifying the [min, max] bounds for each parameter. If None, uses
        `cost.parameters.get_bounds_for_plotly`.
    normalise : bool, optional
        If True, the voronoi regions are computed using the Euclidean distance between
        points normalised with respect to the bounds (default: True).
    resolution : int, optional
        Resolution of the plot. Default is 500.
    show : bool, optional
        If True, the figure is shown upon creation (default: True).
    **layout_kwargs : optional
        Valid Plotly layout keys and their values,
        e.g. `xaxis_title="Time [s]"` or
        `xaxis={"title": "Time [s]", font={"size":14}}`
    """
    return call_plotting_function(
        "surface",
        backend,
        result=result,
        bounds=bounds,
        normalise=normalise,
        resolution=resolution,
        show=show,
        **layout_kwargs,
    )


def trace(result: "SamplingResult", backend=None, **kwargs):
    """
    Plot trace plots for the posterior samples.
    """
    return call_plotting_function("trace", backend, result=result, **kwargs)


def trajectories(x, y, trace_names=None, show=True, backend=None, **layout_kwargs):
    """
    Quickly plot one or more trajectories using Plotly.

    Parameters
    ----------
    x : list or np.ndarray
        X-axis data points.
    y : list or np.ndarray
        Y-axis data points for each trajectory.
    trace_names : list or str, optional
        Name(s) for the trace(s) (default: None).
    **layout_kwargs : optional
            Valid Plotly layout keys and their values,
            e.g. `xaxis_title="Time / s"` or
            `xaxis={"title": "Time [s]", font={"size":14}}`

    Returns
    -------
    plotly.graph_objs.Figure
        The Plotly figure object for the scatter plot.
    """

    return call_plotting_function(
        "trajectories",
        backend,
        x=x,
        y=y,
        trace_names=trace_names,
        show=show,
        **layout_kwargs,
    )
