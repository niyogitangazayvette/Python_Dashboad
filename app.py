import pandas as pd
from dash import Dash, Input, Output, dcc, html

# Load and prepare data
data = (
    pd.read_csv(r"C:\Users\user\Downloads\Dashboad\Python_Dashboad\assets\avocado.csv")
    .assign(Date=lambda df: pd.to_datetime(df["Date"], format="%Y-%m-%d"))
    .sort_values(by="Date")
)
data["Year"] = data["Date"].dt.year

regions = data["region"].sort_values().unique()
avocado_types = data["type"].sort_values().unique()

# External stylesheet
external_stylesheets = [
    {
        "href": (
            "https://fonts.googleapis.com/css2?"
            "family=Lato:wght@400;700&display=swap"
        ),
        "rel": "stylesheet",
    },
]

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Avocado Analytics: Understand Your Avocados!"

# Layout
app.layout = html.Div([
    html.Div([
        html.P("🥑", className="header-emoji"),
        html.H1("Avocado Analytics", className="header-title"),
        html.P(
            "Analyze the behavior of avocado prices and the number "
            "of avocados sold in the US between 2015 and 2018",
            className="header-description",
        ),
    ], className="header"),

    html.Div([
        html.Div([
            html.Div("Region", className="menu-title"),
            dcc.Dropdown(
                id="region-filter",
                options=[{"label": r, "value": r} for r in regions],
                value="Albany",
                clearable=False,
                className="dropdown",
            ),
        ]),
        html.Div([
            html.Div("Type", className="menu-title"),
            dcc.Dropdown(
                id="type-filter",
                options=[{"label": t.title(), "value": t} for t in avocado_types],
                value="organic",
                clearable=False,
                className="dropdown",
            ),
        ]),
        html.Div([
            html.Div("Date Range", className="menu-title"),
            dcc.DatePickerRange(
                id="date-range",
                min_date_allowed=data["Date"].min().date(),
                max_date_allowed=data["Date"].max().date(),
                start_date=data["Date"].min().date(),
                end_date=data["Date"].max().date(),
            ),
        ]),
    ], className="menu"),

    html.Div([
        html.Div(dcc.Graph(id="price-chart", config={"displayModeBar": False}), className="card"),
        html.Div(dcc.Graph(id="volume-chart", config={"displayModeBar": False}), className="card"),
        html.Div(dcc.Graph(id="top-region-chart", config={"displayModeBar": False}), className="card"),
        html.Div(dcc.Graph(id="price-by-type", config={"displayModeBar": False}), className="card"),
        html.Div(dcc.Graph(id="volume-by-year", config={"displayModeBar": False}), className="card"),
        html.Div(dcc.Graph(id="bags-vs-price", config={"displayModeBar": False}), className="card"),
    ], className="wrapper"),
])

# Callback
@app.callback(
    Output("price-chart", "figure"),
    Output("volume-chart", "figure"),
    Output("top-region-chart", "figure"),
    Output("price-by-type", "figure"),
    Output("volume-by-year", "figure"),
    Output("bags-vs-price", "figure"),
    Input("region-filter", "value"),
    Input("type-filter", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
)
def update_charts(region, avocado_type, start_date, end_date):
    filtered_data = data.query(
        "region == @region and type == @avocado_type and Date >= @start_date and Date <= @end_date"
    )

    # C Price
    price_chart_figure = {
        "data": [{
            "x": filtered_data["Date"],
            "y": filtered_data["AveragePrice"],
            "type": "lines",
            "hovertemplate": "$%{y:.2f}<extra></extra>",
        }],
        "layout": {
            "title": {"text": "Average Price of Avocados", "x": 0.05},
            "xaxis": {"fixedrange": True},
            "yaxis": {"tickprefix": "$", "fixedrange": True},
            "colorway": ["#407E60B8"],
        },
    }

    #  Volume
    volume_chart_figure = {
        "data": [{
            "x": filtered_data["Date"],
            "y": filtered_data["Total Volume"],
            "type": "lines",
        }],
        "layout": {
            "title": {"text": "Avocados Sold", "x": 0.05},
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#73CE99"],
        },
    }

    # Chart 3: Top 10 regions
    top_regions = (
        data.query("type == @avocado_type and Date >= @start_date and Date <= @end_date")
        .groupby("region", as_index=False)["Total Volume"]
        .sum()
        .sort_values("Total Volume", ascending=False)
        .head(10)
    )
    top_region_chart_figure = {
        "data": [{
            "type": "bar",
            "x": top_regions["Total Volume"],
            "y": top_regions["region"],
            "orientation": "h",
            "text": top_regions["Total Volume"].round(0),
            "textposition": "auto",
            "marker": {"color": "#80C09AD5"},
        }],
        "layout": {
            "title": {"text": "Top 10 Regions by Avocados Sold", "x": 0.05},
            "xaxis": {"title": "Total Volume"},
            "yaxis": {"title": "Region", "autorange": "reversed"},
            "height": 500,
            "margin": {"l": 100, "r": 20, "t": 50, "b": 50},
        },
    }

    # Chart 4: Average Price by Type
    avg_price_by_type = (
        data.query("region == @region and Date >= @start_date and Date <= @end_date")
        .groupby("type", as_index=False)["AveragePrice"]
        .mean()
    )
    price_by_type_figure = {
        "data": [{
            "type": "bar",
            "x": avg_price_by_type["type"],
            "y": avg_price_by_type["AveragePrice"],
            "marker": {"color": ["#AEEAC4EA", "#08843ED6"]},
        }],
        "layout": {
            "title": {"text": "Average Price by Avocado Type", "x": 0.05},
            "yaxis": {"tickprefix": "$"},
        },
    }

    #  Total Volume by Year
    volume_by_year = (
        data.query("region == @region and type == @avocado_type and Date >= @start_date and Date <= @end_date")
        .groupby("Year", as_index=False)["Total Volume"]
        .sum()
    )
    volume_by_year_figure = {
        "data": [{
            "type": "bar",
            "x": volume_by_year["Year"].astype(str),
            "y": volume_by_year["Total Volume"],
            "marker": {"color": "#2A87468A"},
        }],
        "layout": {
            "title": {"text": "Total Volume by Year", "x": 0.05},
            "xaxis": {"title": "Year"},
            "yaxis": {"title": "Volume"},
        },
    }

    # Total Bags vs Average Price
    scatter_figure = {
        "data": [{
            "x": filtered_data["Total Bags"],
            "y": filtered_data["AveragePrice"],
            "mode": "markers",
            "marker": {"color": "#27AE85E7", "size": 8, "opacity": 0.6},
        }],
        "layout": {
            "title": {"text": "Total Bags vs Average Price", "x": 0.05},
            "xaxis": {"title": "Total Bags"},
            "yaxis": {"title": "Average Price ($)"},
        },
    }

    return (
        price_chart_figure,
        volume_chart_figure,
        top_region_chart_figure,
        price_by_type_figure,
        volume_by_year_figure,
        scatter_figure,
    )

# Run app
if __name__ == "__main__":
    app.run(debug=True)
