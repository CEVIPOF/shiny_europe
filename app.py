import plotly.express as px
import pandas as pd
from shiny.express import input, render, ui
from shinywidgets import render_widget

ui.page_opts(title="Sidebar layout", fillable=True)

ui.page_opts()

with ui.layout_columns():
    with ui.card():
        "56% de personnes intéressées par l'élection"
    with ui.card():
        "45% de personnes certaines d'aller voter"

with ui.sidebar():
    ui.input_select("var", "Select variable", choices=["Y3CERT", "Y3INTEURST"])

@render_widget
def hist():
    df = pd.read_csv('data_interet.csv')
    fig = px.line(df, x="date", y=input.var(), text="date_glose")
    fig.update_traces(textposition="top right", line=dict(color='grey', width=2, dash='dash'), line_shape="spline")
    fig.update_traces(marker=dict(size=12, line=dict(width=2, color='dimgrey')))
    return fig
