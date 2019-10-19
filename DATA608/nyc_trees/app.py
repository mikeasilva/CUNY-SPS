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


def get_human_intervention(x):
    if x == "None":
        return "Nature Only"
    else:
        return "Steward Intervention"


def get_steward_graph_data(boroname="Bronx", tree="American beech"):
    soql_url = (
        "https://data.cityofnewyork.us/resource/nwxe-4ae8.json?"
        + "$select=steward,health,count(tree_id)"
        + "&$where=spc_common='"
        + tree
        + "' AND boroname='"
        + boroname
        + "'"
        + "&$group=steward,health"
    ).replace(" ", "%20")
    df = pd.read_json(soql_url).dropna().rename(columns={"count_tree_id": "n"})
    df["type"] = df.steward.apply(get_human_intervention)

    df = df.groupby(["type", "health"])["n"].sum().reset_index()

    temp = df.groupby("type")["n"].sum().reset_index().rename(columns={"n": "total"})
    df = pd.merge(df, temp)
    df["share"] = df.n / df.total * 100

    shares = {
        "Steward Intervention": {"Poor": 0.0, "Fair": 0.0, "Good": 0.0},
        "Nature Only": {"Poor": 0.0, "Fair": 0.0, "Good": 0.0},
    }

    for index, row in df.iterrows():
        shares[row["type"]][row["health"]] = row["share"]

    poor = {
        "name": "Poor",
        "type": "bar",
        "x": ["Steward Intervention", "Nature Only"],
        "y": [
            round(shares["Steward Intervention"]["Poor"], 0),
            round(shares["Nature Only"]["Poor"], 0),
        ],
        "marker": {"color": "rgb(215, 48, 39)"},
    }
    fair = {
        "name": "Fair",
        "type": "bar",
        "x": ["Steward Intervention", "Nature Only"],
        "y": [
            round(shares["Steward Intervention"]["Fair"], 0),
            round(shares["Nature Only"]["Fair"], 0),
        ],
        "marker": {"color": "rgb(254, 224, 144)"},
    }
    good = {
        "name": "Good",
        "type": "bar",
        "x": ["Steward Intervention", "Nature Only"],
        "y": [
            round(shares["Steward Intervention"]["Good"], 0),
            round(shares["Nature Only"]["Good"], 0),
        ],
        "marker": {"color": "rgb(69, 117, 180)"},
    }
    return [poor, fair, good]


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
        "type": "bar",
        "x": ["Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island"],
        "y": [
            round(shares["Bronx"]["Poor"], 0),
            round(shares["Brooklyn"]["Poor"], 0),
            round(shares["Manhattan"]["Poor"], 0),
            round(shares["Queens"]["Poor"], 0),
            round(shares["Staten Island"]["Poor"], 0),
        ],
        "marker": {"color": "rgb(215, 48, 39)"},
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
    }
    return [poor, fair, good]


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div(
    [
        html.H2("NYC Trees"),
        html.P(
            "How healthy are NYC's trees?  Are the activities of stewards helping the trees?  The following visualizations allow you to search a tree and view the results of the steward actions and answer these questions yourself.  Please keep in mind that correlation is not causation when looking at the steward intervention vs nature alone graph."
        ),
        html.Div(
            [
                dcc.Dropdown(
                    id="tree-dropdown",
                    options=[{"label": i.title(), "value": i} for i in get_tree_list()],
                    value="American beech",
                ),
                dcc.Graph(
                    config={"displayModeBar": False},
                    figure=go.Figure(
                        data=get_tree_health_graph_data(),
                        layout=go.Layout(
                            title="ARE AMERICAN BEECH TREES HEALTHY?",
                            yaxis=go.layout.YAxis(
                                title=go.layout.yaxis.Title(text="Percent"),
                                range=[0, 100],
                            ),
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
                    searchable=False,
                ),
                dcc.Graph(
                    config={"displayModeBar": False},
                    figure=go.Figure(
                        data=get_steward_graph_data(),
                        layout=go.Layout(
                            title="ARE BRONX STEWARDS MAKING A DIFFERENCE?",
                            yaxis=go.layout.YAxis(
                                title=go.layout.yaxis.Title(text="Percent"),
                                range=[0, 100],
                            ),
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
            title="ARE " + spc_common.upper() + " TREES HEALTHY?",
            yaxis=go.layout.YAxis(
                title=go.layout.yaxis.Title(text="Percent"), range=[0, 100]
            ),
        ),
    )

    return fig


@app.callback(
    Output(component_id="steward-graph", component_property="figure"),
    [
        Input(component_id="borough-dropdown", component_property="value"),
        Input(component_id="tree-dropdown", component_property="value"),
    ],
)
def update_tree_health_graph(borough, spc_common):
    fig = go.Figure(
        data=get_steward_graph_data(borough, spc_common),
        layout=go.Layout(
            title="ARE " + borough.upper() + " STEWARDS MAKING A DIFFERENCE?",
            yaxis=go.layout.YAxis(
                title=go.layout.yaxis.Title(text="Percent"), range=[0, 100]
            ),
        ),
    )

    return fig


if __name__ == "__main__":
    app.run_server()
