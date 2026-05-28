# Plotting backend default
DEFAULT_BACKEND = 'matplotlib'
backend=DEFAULT_BACKEND

from .util import set_backend, import_backend, _AxisData, remove_brackets, wrap_text, parse_data

#
# Import plots
#
from .standard_plots import trajectories, Subplots
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
