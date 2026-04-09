# Plotting backend default
DEFAULT_BACKEND = 'matplotlib'
backend=DEFAULT_BACKEND

from .util import set_backend, call_plotting_function, get_default_options

#
# Import plots
#
from .plots import (
    chains,
    contour,
    convergence,
    posterior,
    summary_table,
    surface,
    trace
    )

from .standard_plots import StandardPlot, StandardSubplot, trajectories
from .dataset import dataset
from .nyquist import nyquist
from .parameters import parameters
from .problem import problem
from .voronoi import voronoi_data, _voronoi_regions
from . import matplotlib
from . import plotly
