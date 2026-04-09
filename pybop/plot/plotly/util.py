import warnings

def update_and_show(fig, show=True, **layout_kwargs):
    fig.update_layout(**layout_kwargs)
    if show:
        fig.show()
    return fig


DEFAULT_PLOT_OPTIONS = {
    'parameters' : dict(layout_options = dict(
        title="Parameter Convergence",
        width=1024,
        height=576,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )),
    'problem' : { 
        'default_trace_options' : dict (name="Model", mode="lines", showlegend=True),
        'design_cost_options' : dict(name = "Optimised"),
        'meta_problem_options' : dict(mode = "lines"),
        'reference_options' : dict(name="Reference", mode="markers", showlegend=True), 
        'fill_options' : dict(fillcolor ="rgba(255,229,204,0.8)" )  
    }
}