"""Visualizations and confidence gauge charts for Decision Model outputs."""
from typing import Dict, Any, Optional
import plotly.graph_objects as go

def create_noul_gauge(probability: float, title: str = "Probability of True") -> go.Figure:
    """Create a sleek gauge meter for noul (yes/no) probability."""
    prob_pct = round(probability * 100, 1)

    # Color ranges based on probability
    bar_color = "#10b981" if probability >= 0.7 else ("#f59e0b" if probability >= 0.4 else "#ef4444")

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=prob_pct,
            number={"suffix": "%", "font": {"size": 28, "color": "#f8fafc"}},
            title={"text": title, "font": {"size": 16, "color": "#94a3b8"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#475569"},
                "bar": {"color": bar_color, "thickness": 0.4},
                "bgcolor": "#1e293b",
                "borderwidth": 1,
                "bordercolor": "#334155",
                "steps": [
                    {"range": [0, 40], "color": "rgba(239, 68, 68, 0.15)"},
                    {"range": [40, 70], "color": "rgba(245, 158, 11, 0.15)"},
                    {"range": [70, 100], "color": "rgba(16, 185, 129, 0.15)"},
                ],
                "threshold": {
                    "line": {"color": "#38bdf8", "width": 3},
                    "thickness": 0.75,
                    "value": prob_pct,
                },
            },
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=40, b=20),
        height=220,
    )
    return fig

def create_choice_barchart(
    probabilities: Dict[str, float],
    selected_choice: str,
    title: str = "Choice Probability Distribution"
) -> go.Figure:
    """Create horizontal probability bar chart for choice questions."""
    options = list(probabilities.keys())
    values = [round(probabilities[k] * 100, 2) for k in options]
    colors = [
        "#38bdf8" if k == selected_choice else "rgba(148, 163, 184, 0.35)"
        for k in options
    ]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=options,
            orientation="h",
            marker=dict(
                color=colors,
                line=dict(
                    color=["#0284c7" if k == selected_choice else "rgba(148, 163, 184, 0.5)" for k in options],
                    width=1.5
                ),
            ),
            text=[f"{v:.1f}% {'(Selected)' if k == selected_choice else ''}" for k, v in zip(options, values)],
            textposition="auto",
            textfont=dict(color="#f8fafc", size=13),
        )
    )

    fig.update_layout(
        title=dict(text=title, font=dict(color="#94a3b8", size=15)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            range=[0, max(100, max(values) + 10) if values else 100],
            showgrid=True,
            gridcolor="rgba(148, 163, 184, 0.1)",
            tickfont=dict(color="#94a3b8"),
            title=dict(text="Probability (%)", font=dict(color="#94a3b8")),
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(color="#f8fafc", size=14),
        ),
        margin=dict(l=20, r=20, t=40, b=20),
        height=max(180, len(options) * 55),
    )
    return fig

def create_score_distribution_chart(
    score: float,
    probabilities: Optional[Dict[str, float]] = None,
    legend: Optional[Dict[str, str]] = None,
    title: str = "Ordinal Score Distribution"
) -> go.Figure:
    """Create visualization for score questions with rubric points."""
    if not probabilities:
        # Simple score indicator
        fig = go.Figure(
            go.Indicator(
                mode="number+gauge",
                value=round(score, 2),
                title={"text": title, "font": {"size": 16, "color": "#94a3b8"}},
                gauge={
                    "axis": {"range": [0, max(3.0, score + 1.0)]},
                    "bar": {"color": "#a855f7"},
                },
            )
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            height=200,
            margin=dict(l=20, r=20, t=30, b=20),
        )
        return fig

    indices = list(probabilities.keys())
    values = [round(probabilities[k] * 100, 2) for k in indices]
    labels = []
    for k in indices:
        desc = legend.get(k, f"Tier {k}") if legend else f"Tier {k}"
        # truncate long descriptions for chart axis
        if len(desc) > 35:
            desc = desc[:32] + "..."
        labels.append(f"[{k}] {desc}")

    fig = go.Figure(
        go.Bar(
            x=labels,
            y=values,
            marker=dict(
                color="rgba(168, 85, 247, 0.7)",
                line=dict(color="#a855f7", width=1.5),
            ),
            text=[f"{v:.1f}%" for v in values],
            textposition="outside",
            textfont=dict(color="#f8fafc", size=12),
        )
    )

    fig.update_layout(
        title=dict(text=f"{title} (Weighted Score: {score:.2f})", font=dict(color="#94a3b8", size=15)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            tickfont=dict(color="#cbd5e1", size=12),
            showgrid=False,
        ),
        yaxis=dict(
            range=[0, 110],
            showgrid=True,
            gridcolor="rgba(148, 163, 184, 0.1)",
            tickfont=dict(color="#94a3b8"),
            title=dict(text="Probability (%)", font=dict(color="#94a3b8")),
        ),
        margin=dict(l=20, r=20, t=50, b=30),
        height=260,
    )
    return fig
