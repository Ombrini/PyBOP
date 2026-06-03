import textwrap
from dataclasses import dataclass

import numpy as np

import pybop.plot


def use_backend(backend):
    """
    Select a plotting backend to be used for all subsequent plots.

    Parameters
    ----------
    backend : str
        The plotting backend to be used.
    """
    err_msg = (
        f"Plotting backend {backend} is not available. The current backend has not been updated. \n"
        f"The current backend is set to {pybop.plot.current_backend}"
    )
    if backend.lower() in ["matplotlib", "plotly"]:
        pybop.plot.current_backend = backend

    else:
        raise ModuleNotFoundError(err_msg)


def get_backend(backend=None):
    """
    Get instance of PlotBackend class for a given plotting backend

    Parameters
    ----------
    backend : str, optional
        The plotting backend to be used (default: pybop.plot.current_backend)
    """
    if backend is None:
        backend = pybop.plot.current_backend
    err_msg = f"Plotting backend {backend} is not available."
    if backend.lower() == "matplotlib":
        return pybop.plot.backends.MatplotlibBackend()
    elif backend.lower() == "plotly":
        return pybop.plot.backends.PlotlyBackend()
    else:
        raise ModuleNotFoundError(err_msg)


@dataclass
class AxisData:
    """
    Simple dataclass to store info needed to construct
    subplots from specifying size and location of individual axes.
    """

    row: int = 1
    col: int = 1
    row_span: int = 1
    col_span: int = 1


def parse_data(x, y):
    """
    Check the type and dimensions of the data and convert if necessary to a list
    of 'things plotly can take', e.g. numpy arrays or lists of numbers.

    Parameters
    ----------
    x : list or np.ndarray, optional
        X-axis data points.
    y : list or np.ndarray, optional
        Primary Y-axis data points for simulated model output.
    """
    if isinstance(x, list):
        # If it's a list of numpy arrays, it's fine
        # If it's a list of lists, it's fine
        # If it's neither, it's a list of numbers that we need to wrap
        if not isinstance(x[0], np.ndarray) and not isinstance(x[0], list):
            x = [x]
    elif isinstance(x, np.ndarray):
        x = np.squeeze(x)
        if x.ndim == 1:
            x = [x]
        else:
            x = x.tolist()
    if isinstance(y, list):
        if not isinstance(y[0], np.ndarray) and not isinstance(y[0], list):
            y = [y]
    if isinstance(y, np.ndarray):
        y = np.squeeze(y)
        if y.ndim == 1:
            y = [y]
        else:
            y = y.tolist()
    if len(x) > 1 and len(x) != len(y):
        raise ValueError(
            "Input x should have either one data series or the same number as y."
        )
    return x, y


def remove_brackets(s):
    """
    Remove square brackets from a string and replace with forward slashes
    as per section 7.1 of the SI Handbook
    """
    # If s is an iterable (but not a string), apply the function recursively to each element
    if hasattr(s, "__iter__") and not isinstance(s, str):
        return type(s)(remove_brackets(i) for i in s)
    elif isinstance(s, str):
        start = s.find("[")
        end = s.find("]")
        if start != -1 and end != -1:
            char_in_brackets = s[start + 1 : end]
            return s[:start] + " / " + char_in_brackets + s[end + 1 :]
    return s


def wrap_text(text, width, backend="matplotlib"):
    """
    Wrap text to a specified width with HTML line breaks.

    Parameters
    ----------
    text : str
        The text to wrap.
    width : int
        The width to wrap the text to.

    Returns
    -------
    str
        The wrapped text.
    """
    wrapped_text = textwrap.fill(text, width=width, break_long_words=False)
    if backend == "plotly":
        return wrapped_text.replace("\n", "<br>")
    else:
        return wrapped_text
