# Plotting backend default
DEFAULT_BACKEND = 'matplotlib'
current_backend=DEFAULT_BACKEND

from .util import (
    AxisData,
    use_backend,
    get_backend,
    parse_data,
    remove_brackets,
    wrap_text
)

#
# Import plots
#
from .standard_plots import StandardPlot, StandardSubplot
from .trajectories import trajectories
from .contour import contour
from .dataset import dataset
from .convergence import convergence
from .parameters import parameters
from .problem import problem
from .nyquist import nyquist
from .voronoi import surface
from .samples import trace, chains, posterior, summary_table
from .predictive import predictive
from .distribution import distribution

# Import backend specific plotting functions
from . import  backends
