import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash import Dash
import us

# Load your data (same as original)
data = pd.read_csv("pen_combined.csv")

data["State"] = data["State"].apply(lambda x: us.states.lookup(x).abbr if us.states.lookup(x) else x)

years = sorted(data["Year-Range"].dropna().unique())

year_options = ["All Years"] + years

states = sorted(data["State"].dropna().unique())

dash.register_page(__name__, path='/state-analysis', name="State Analysis")

layout = html.Div([
    html.H1("State-Level Book Ban Analysis", className="text-center my-4"),
    
    # Choropleth Map
    html.H3("Number of Book Bans by State"),
    dcc.Dropdown(
        id='year-select-map',
        options=[{"label": year, "value": year} for year in year_options],
        value="All Years",
        className="mb-4"
    ),
    dcc.Graph(id="choropleth-map"),
    
    html.H3("Change in Book Bans by State"),
    dcc.Dropdown(
        id='change-chart',
        options=[{"label": state, "value": state} for state in states],
        value="AK",
        className="mb-4"
    ),
    dcc.Graph(id="change-year-chart"),
])

@dash.callback(
    [Output("choropleth-map", "figure"),
     Output("change-year-chart", "figure")],
    [Input("year-select-map", "value"),
     Input("change-chart", "value")]
)
def update_state_visualizations(selected_year_map, selected_state_change):
     # Filter data
    if selected_year_map == "All Years":
        filtered = data.copy()
    else:
        filtered = data[data["Year-Range"] == selected_year_map]

    # Aggregate book bans per state
    state_bans = filtered.groupby("State")["Title"].count().reset_index()
    state_bans.columns = ["State", "Ban Count"]

    # Create choropleth
    choropleth_fig = px.choropleth(
        state_bans,
        locations="State",
        locationmode="USA-states",
        color="Ban Count",
        color_continuous_scale="sunset",
        scope="usa",
    )

    choropleth_fig.update_layout(
        geo=dict(bgcolor='rgba(0,0,0,0)'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin={"r":0, "t":30, "l":0, "b":0}
    )

    # Filter data
    filtered = data[data["State"] == selected_state_change]

    num_bans = filtered.groupby("Year-Range")["Title"].count().reset_index()
    num_bans.columns = ["Year-Range", "Ban Count"]

    change_fig = px.line(
        num_bans,
        x='Year-Range',
        y='Ban Count',
        markers=True,
    )
    
    change_fig.update_layout(
        xaxis_title='School Year',
        yaxis_title='Number of Banned Books',
        hovermode='x unified'
    )


    return choropleth_fig, change_fig