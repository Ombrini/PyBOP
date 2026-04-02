# Plotting backend default
DEFAULT_BACKEND = 'matplotlib'
backend=DEFAULT_BACKEND

from .util import set_backend, call_plotting_function, get_class

#
# Import plots
#
from .plots import (
    chains,
    contour,
    convergence,
    dataset,
    nyquist,
    parameters,
    posterior,
    problem,
    summary_table,
    surface,
    trace,
    trajectories
    )

from .voronoi import voronoi_data, _voronoi_regions
from . import matplotlib
from . import plotly

StandardPlot = matplotlib.StandardPlot
StandardSubplot = matplotlib.StandardSubplot
