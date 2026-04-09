import importlib.util

import pybop.plot


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


def update_and_show(fig, backend=None, **kwargs):
    return call_plotting_function("update_and_show", backend, fig=fig,  **kwargs)


def get_default_options(plot_type, backend):
    if backend is None:
        backend = pybop.plot.backend

    if backend == 'plotly':
        opts = pybop.plot.plotly.DEFAULT_PLOT_OPTIONS
    elif backend == 'matplotlib':
        opts = pybop.plot.matplotlib.DEFAULT_PLOT_OPTIONS
    else:
        opts = {}

    if plot_type in opts.keys():
        return opts[plot_type]
    else:
        return {}