DEFAULT_PLOT_OPTIONS = {
    "standard_plot": {
        "default_layout_options": dict(
            title=None,
            title_x=0.5,
            xaxis=dict(
                title=dict(font={"size": 14}),
                showexponent="last",
                exponentformat="e",
                tickfont=dict(size=12),
            ),
            yaxis=dict(
                title=dict(font={"size": 14}),
                showexponent="last",
                exponentformat="e",
                tickfont=dict(size=12),
            ),
            legend=dict(x=1, y=1, xanchor="right", yanchor="top", font_size=12),
            showlegend=True,
            autosize=False,
            width=600,
            height=600,
            margin=dict(l=10, r=10, b=10, t=75, pad=4),
            plot_bgcolor="white",
        ),
        "default_trace_options": dict(line=dict(width=4), mode="lines"),
    },
    "contour": {
        "plot_options": dict(
            title="Cost Landscape",
            title_x=0.5,
            title_y=0.905,
            width=600,
            height=600,
            xaxis=dict(showexponent="last", exponentformat="e"),
            yaxis=dict(showexponent="last", exponentformat="e"),
            legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1),
            autosize=None,
            showlegend=None,
            margin=None,
        ),
        "trace_options_contour": dict(colorscale="Viridis", connectgaps=True),
        "trace_options_initial": dict(
            mode="markers",
            marker_symbol="x",
            marker=dict(
                color="white",
                line_color="black",
                line_width=1,
                size=14,
                showscale=False,
            ),
            name="Initial values",
        ),
        "trace_options_optim": dict(
            mode="markers",
            marker_symbol="cross",
            marker=dict(
                color="black",
                line_color="white",
                line_width=1,
                size=14,
                showscale=False,
            ),
            name="Final values",
        ),
    },
    "nyquist": {
        "plot_options": dict(
            font=dict(family="Arial", size=14),
            plot_bgcolor="white",
            paper_bgcolor="white",
            width=600,
            height=600,
            xaxis=dict(
                title=dict(font=dict(size=16), standoff=15),
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
                title=dict(font=dict(size=16), standoff=15),
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
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        ),
        "trace_options_model": dict(
            mode="lines+markers",
            line=dict(color="#00CC96", width=2),
            marker=dict(size=8, color="#00CC96", symbol="circle"),
        ),
        "trace_options_reference": dict(
            mode="markers",
            marker=dict(size=8, color="#636EFA", symbol="circle-open"),
            showlegend=True,
        ),
    },
    "parameters": dict(
        layout_options=dict(
            title="Parameter Convergence",
            width=1024,
            height=576,
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        ),
        subplot_options=dict(
            horizontal_spacing=0.1,
            vertical_spacing=0.15,
        ),
    ),
    "posterior": {
        "plot_options": dict(barmode="overlay",),
        "trace_options": dict(opacity=0.75),
        "trace_options_vline": dict(line_width=3, line_dash="dash", line_color="black"),
    },
    "predictive" : {
        "trace_options_pdf": dict(line={"dash": "dot"})
    },
    "problem": {
        "default_trace_options": dict(name="Model", mode="lines", showlegend=True),
        "design_cost_options": dict(name="Optimised"),
        "meta_problem_options": dict(mode="lines"),
        "reference_options": dict(name="Reference", mode="markers", showlegend=True),
        "fill_options": dict(fillcolor="rgba(255,229,204,0.8)"),
    },
    "voronoi": {
        "layout_options": dict(
            title_x=0.5,
            title_y=0.905,
            width=600,
            height=600,
            xaxis=dict(showexponent="last", exponentformat="e"),
            yaxis=dict(showexponent="last", exponentformat="e"),
            legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1),
        ),
        "outline_opts": dict(
            mode="lines",
            line=dict(color="white", width=0.5),
            showlegend=False,
        ),
        "optimised_opts": dict(
            mode="markers",
            marker_symbol="cross",
            marker=dict(
                color="black",
                line_color="white",
                line_width=1,
                size=14,
                showscale=False,
            ),
            name="Final values",
        ),
        "initial_opts": dict(
            mode="markers",
            marker_symbol="x",
            marker=dict(
                color="white",
                line_color="black",
                line_width=1,
                size=14,
                showscale=False,
            ),
            name="Initial values",
        ),
    },
}
