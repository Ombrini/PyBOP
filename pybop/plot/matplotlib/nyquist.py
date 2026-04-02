from matplotlib import pyplot as plt

from pybop.parameters.parameter import Inputs
from pybop.plot.matplotlib.standard_plots import StandardPlot


def nyquist(problem, inputs: Inputs = None, show=True, **layout_kwargs):
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
    if not isinstance(inputs, dict):
        inputs = problem.parameters.to_dict(inputs)

    model_output = problem.simulate(inputs)
    domain_data = model_output["Impedance"].data.real
    target_output = problem.target_data

    figure_list = []
    for var in problem.target:
        plot_dict = StandardPlot(
            x=domain_data,
            y=-model_output[var].data.imag,
            trace_names="Model",
        )

        fig = plot_dict(show=False)
        plot_dict.traces[0].set_color("#00CC96")
        plot_dict.traces[0].set_linewidth(2)
        plot_dict.traces[0].set_marker(".")
        plot_dict.traces[0].set_markersize(8)

        target_trace = plot_dict.create_trace(
            x=target_output[var].real,
            y=-target_output[var].imag,
            label="Reference",
        )
        target_trace.set_linestyle("None")
        target_trace.set_marker("o")
        target_trace.set_fillstyle("none")
        target_trace.set_markersize(8)
        target_trace.set_markeredgecolor("#636EFA")

        # Layout
        plt.title("Nyquist Plot", fontsize=14, x=0.2)
        plt.xlabel(r"$Z_{re} / \Omega$", fontsize=16)
        plt.ylabel(r"$-Z_{im} / \Omega$", fontsize=16)
        plt.legend(loc="upper right", bbox_to_anchor=(1, 1.08), ncols=2)

        if show:
            plt.show()

        figure_list.append(fig)

    return figure_list
