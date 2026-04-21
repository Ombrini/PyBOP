import importlib.util
from copy import deepcopy
from dataclasses import dataclass

import pybop.plot


@dataclass
class _AxisData:
    row: int = 1
    col: int = 1
    row_span: int = 1
    col_span: int = 1
    xlabel: str | None = None
    ylabel: str | None = None

    def set_xlabel(self, xlabel: str):
        self.xlabel = xlabel

    def set_ylabel(self, ylabel: str):
        self.ylabel = ylabel


def create_axis(row, col, row_span=1, col_span=1):
    return _AxisData(row, col, row_span, col_span)


def set_backend(backend):
    err_msg = (
        f"Plotting backend {backend} is not available. The default backend has not been updated. \n"
        f"The default backend is set to {pybop.plot.backend}"
    )
    try:
        importlib.import_module("pybop.plot." + backend)
        pybop.plot.backend = backend

    except ModuleNotFoundError as error:
        # Raise an ModuleNotFoundError if the module or attribute is not available
        raise ModuleNotFoundError(err_msg) from error


def call_plotting_function(function_name, backend, **kwargs):
    if backend is None:
        backend = pybop.plot.backend
    err_msg = f"Plotting backend {backend} is not available."
    try:
        module = importlib.import_module("pybop.plot." + backend)
        if hasattr(module, function_name):
            plotting_function = getattr(module, function_name)
            # Return the imported attribute
            return plotting_function(**kwargs)
        else:
            err_msg = f"Plotting backend {backend} has no attribute {function_name}."
            raise ModuleNotFoundError(err_msg)

    except ModuleNotFoundError as error:
        # Raise an ModuleNotFoundError if the module or attribute is not available
        raise ModuleNotFoundError(err_msg) from error


def import_backend(backend):
    if backend is None:
        backend = pybop.plot.backend
    err_msg = f"Plotting backend {backend} is not available."
    try:
        module = importlib.import_module("pybop.plot." + backend)
    except ModuleNotFoundError as error:
        # Raise an ModuleNotFoundError if the module or attribute is not available
        raise ModuleNotFoundError(err_msg) from error

    return module


def update_and_show(fig, backend=None, **kwargs):
    return call_plotting_function("update_and_show", backend, fig=fig, **kwargs)


def get_default_options(plot_type, backend):
    if backend is None:
        backend = pybop.plot.backend

    if backend == "plotly":
        opts = pybop.plot.plotly.DEFAULT_PLOT_OPTIONS
    elif backend == "matplotlib":
        opts = pybop.plot.matplotlib.DEFAULT_PLOT_OPTIONS
    else:
        opts = {}

    if plot_type in opts.keys():
        return deepcopy(opts[plot_type])
    else:
        return {}
