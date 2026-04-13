from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from pybop._result import Result

from pybop.plot.util import call_plotting_function
from pybop.problems.problem import Problem


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
