# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 08:52:11 2019

@author: Michael Silva
"""

import os

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]


def get_tree_list():
    soql_url = (
        "https://data.cityofnewyork.us/resource/nwxe-4ae8.json?"
        + "$select=spc_common,count(tree_id)"
        + "&$group=spc_common"
    ).replace(" ", "%20")
    temp = pd.read_json(soql_url).dropna()
    return temp.spc_common.tolist()

def get_steward_graph_data(boroname = "Bronx", tree="American beech"):
    soql_url = (
        "https://data.cityofnewyork.us/resource/nwxe-4ae8.json?"
        + "$select=steward,health,count(tree_id)"
        + "&$where=boroname='"
        + boroname
        + " AND spc_common='"
        + tree
        + "'"
        + "&$group=steward,health"
    ).replace(" ", "%20")
    df = pd.read_json(soql_url).dropna().rename(columns={"count_tree_id": "n"})


def get_tree_health_graph_data(tree="American beech"):
    soql_url = (
        "https://data.cityofnewyork.us/resource/nwxe-4ae8.json?"
        + "$select=boroname,health,count(tree_id)"
        + "&$where=spc_common='"
        + tree
        + "'"
        + "&$group=boroname,health"
    ).replace(" ", "%20")
    df = pd.read_json(soql_url).dropna().rename(columns={"count_tree_id": "n"})
    temp = (
        df.groupby("boroname")["n"].sum().reset_index().rename(columns={"n": "total"})
    )
    df = pd.merge(df, temp)
    df["share"] = df.n / df.total * 100

    shares = {
        "Bronx": {"Poor": 0.0, "Fair": 0.0, "Good": 0.0},
        "Brooklyn": {"Poor": 0.0, "Fair": 0.0, "Good": 0.0},
        "Manhattan": {"Poor": 0.0, "Fair": 0.0, "Good": 0.0},
        "Queens": {"Poor": 0.0, "Fair": 0.0, "Good": 0.0},
        "Staten Island": {"Poor": 0.0, "Fair": 0.0, "Good": 0.0},
    }

    for index, row in df.iterrows():
        shares[row["boroname"]][row["health"]] = row["share"]

    poor = {
        "name": "Poor",
        "text": "",
        "type": "bar",
        "x": ["Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island"],
        "y": [
            round(shares["Bronx"]["Poor"], 0),
            round(shares["Brooklyn"]["Poor"], 0),
            round(shares["Manhattan"]["Poor"], 0),
            round(shares["Queens"]["Poor"], 0),
            round(shares["Staten Island"]["Poor"], 0),
        ],
        "marker": {
            "line": {"color": "#444", "width": 0},
            "color": "rgb(215, 48, 39)",
            "opacity": 1,
        },
        "error_x": {
            "type": "percent",
            "color": "#444",
            "value": 10,
            "width": 4,
            "visible": False,
            "symmetric": True,
            "thickness": 2,
        },
    }
    fair = {
        "name": "Fair",
        "type": "bar",
        "x": ["Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island"],
        "y": [
            round(shares["Bronx"]["Fair"], 0),
            round(shares["Brooklyn"]["Fair"], 0),
            round(shares["Manhattan"]["Fair"], 0),
            round(shares["Queens"]["Fair"], 0),
            round(shares["Staten Island"]["Fair"], 0),
        ],
        "marker": {"color": "rgb(254, 224, 144)"},
        "error_x": {
            "type": "percent",
            "color": "#444",
            "value": 10,
            "width": 4,
            "visible": False,
            "symmetric": True,
            "thickness": 2,
        },
    }
    good = {
        "name": "Good",
        "type": "bar",
        "x": ["Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island"],
        "y": [
            round(shares["Bronx"]["Good"], 0),
            round(shares["Brooklyn"]["Good"], 0),
            round(shares["Manhattan"]["Good"], 0),
            round(shares["Queens"]["Good"], 0),
            round(shares["Staten Island"]["Good"], 0),
        ],
        "marker": {"color": "rgb(69, 117, 180)"},
        "error_x": {
            "type": "percent",
            "color": "#444",
            "value": 10,
            "width": 4,
            "visible": False,
            "symmetric": True,
            "thickness": 2,
        },
    }
    return [poor, fair, good]


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server


app.layout = html.Div(
    [
        html.H2("NYC Trees"),
        html.Div(
            [
                dcc.Dropdown(
                    id="tree-dropdown",
                    options=[{"label": i.title(), "value": i} for i in get_tree_list()],
                    value="American beech",
                ),
                dcc.Graph(
                    figure=go.Figure(
                        data=get_tree_health_graph_data(),
                        layout=go.Layout(
                            title="WHAT PERCENT OF AMERICAN BEECH TREES ARE IN POOR, FAIR OR GOOD HEALTH?"
                        ),
                    ),
                    id="tree-health-graph",
                ),
            ],
            style={"width": "48%", "float": "left"},
        ),
        html.Div(
            [
                dcc.Dropdown(
                    id="borough-dropdown",
                    options=[
                        {"label": i, "value": i}
                        for i in [
                            "Bronx",
                            "Brooklyn",
                            "Manhattan",
                            "Queens",
                            "Staten Island",
                        ]
                    ],
                    value="Bronx",
                ),
                dcc.Graph(
                    figure=go.Figure(
                        data=get_tree_health_graph_data(),
                        layout=go.Layout(
                            title="ARE STEWARDS IN THE BRONX MAKING A DIFFERENCE?"
                        ),
                    ),
                    id="steward-graph",
                ),
            ],
            style={"width": "48%", "float": "right"},
        ),
    ]
)

@app.callback(
    Output(component_id="tree-health-graph", component_property="figure"),
    [Input(component_id="tree-dropdown", component_property="value")],
)
def update_tree_health_graph(spc_common):
    fig = go.Figure(
        data=get_tree_health_graph_data(spc_common),
        layout=go.Layout(
            title="WHAT PERCENT OF "
            + spc_common.upper()
            + " TREES ARE IN POOR, FAIR OR GOOD HEALTH?"
        ),
    )
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
