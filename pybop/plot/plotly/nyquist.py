from pybop.parameters.parameter import Inputs
from pybop.plot.nyquist import _nyquist


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
    default_layout_options = dict(
        title="Nyquist Plot",
        font=dict(family="Arial", size=14),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(
            title=dict(text="Z<sub>re</sub> / Ω", font=dict(size=16), standoff=15),
            showline=True,
            linewidth=2,
            linecolor="black",
            mirror=True,
            ticks="outside",
            tickwidth=2,
            tickcolor="black",
            ticklen=5,
        ),
        yaxis=dict(
            title=dict(text="-Z<sub>im</sub> / Ω", font=dict(size=16), standoff=15),
            showline=True,
            linewidth=2,
            linecolor="black",
            mirror=True,
            ticks="outside",
            tickwidth=2,
            tickcolor="black",
            ticklen=5,
            scaleanchor="x",
            scaleratio=1,
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        width=600,
        height=600,
    )

    # Overwrite with user-kwargs
    default_layout_options.update(layout_kwargs)

    trace_options_model = dict(
        mode="lines+markers",
        line=dict(color="#00CC96", width=2),
        marker=dict(size=8, color="#00CC96", symbol="circle"),
    )

    trace_options_reference = dict(
        name="Reference",
        mode="markers",
        marker=dict(size=8, color="#636EFA", symbol="circle-open"),
        showlegend=True,
    )

    figure_list = _nyquist(
        problem, trace_options_model, trace_options_reference, inputs=inputs
    )

    for fig in figure_list:
        fig.update_layout(**default_layout_options)
        if show:
            fig.show()

    return figure_list
