from pybop.parameters.parameter import Inputs
from pybop.plot.standard_plots import StandardPlot
from pybop.plot.util import get_default_options, import_backend


def nyquist(
    problem, inputs: Inputs = None, show=True, title="Nyquist Plot", backend=None
):
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

    options = get_default_options("nyquist", backend)
    plot_options = options.get("plot_options") or {}
    trace_options_model = options.get("trace_options_model") or {}
    trace_options_reference = options.get("trace_options_reference") or {}

    if not isinstance(inputs, dict):
        inputs = problem.parameters.to_dict(inputs)

    model_output = problem.simulate(inputs)
    domain_data = model_output["Impedance"].data.real
    target_output = problem.target_data
    figure_list = []
    backend = import_backend(backend)
    for var in problem.target:
        fig = backend.create_figure(
            xaxis_title=r"$Z_{re} / \Omega$", 
            yaxis_title=r"$-Z_{im} / \Omega$",
            title=title,
            **plot_options,
        )

        backend.plot_trace(
            backend.line_plot(
            x=domain_data,
            y=-model_output[var].data.imag,
            label="Model",
            **trace_options_model
            ),
            fig
        )

        backend.plot_trace(
            backend.line_plot(
                x=target_output[var].real,
                y=-target_output[var].imag,
                label="Reference",
                **trace_options_reference,
            ),
            fig
        )
        backend.legend(fig)
        figure_list.append(fig)

    
    if show:
        backend.show_figure(fig)

    return figure_list
