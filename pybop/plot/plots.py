from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybop._result import Result

from pybop.plot.util import import_backend


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
    backend = import_backend(backend)
    return backend.surface(
        result=result,
        bounds=bounds,
        normalise=normalise,
        resolution=resolution,
        show=show,
        **layout_kwargs,
    )
