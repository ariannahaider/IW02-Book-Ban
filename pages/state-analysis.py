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

layout = html.Div(
    style={"maxWidth": "1200px", "margin": "0 auto", "padding": "20px"},
    children=[
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

    html.H3("Number of Book Bans by State - Colored with Political Leanings"),
    # State chart year filter
    html.P("Select a school year:"),
    dcc.Dropdown(
        id='year-select-ten-state',
        options=[{"label": year, "value": year} for year in year_options],
        value="All Years",  # Default value is "All Years"
        className="mb-4"
    ),
    dcc.Graph(id="top-ten-state-bar-chart"),

    html.H3("Number of Book Bans by School District"),
    # School district chart year filter
    html.P("Select a school year:"),
    dcc.Dropdown(
        id='year-select-sd',
        options=[{"label": year, "value": year} for year in year_options],
        value="All Years",  # Default value is "All Years"
        className="mb-4"
    ),
    dcc.Graph(id="top-sd-bar-chart"),

    html.H3("Distribution Across Districts within a State"),
    # School district by state filter
    html.P("Select a state:"),
    dcc.Dropdown(
        id='state-select-sd',
        options=[{"label": state, "value": state} for state in states],
        value="AK",  # Default value is "All Years"
        className="mb-4"
    ),
    dcc.Graph(id="top-state-sd-bar-chart"),
])

@dash.callback(
    [Output("choropleth-map", "figure"),
     Output("change-year-chart", "figure"),
     Output("top-ten-state-bar-chart", "figure"),
     Output("top-sd-bar-chart", "figure"),
     Output("top-state-sd-bar-chart", "figure")],
    [Input("year-select-map", "value"),
     Input("change-chart", "value"),
     Input("year-select-ten-state","value"),
     Input("year-select-sd", "value"),
     Input("state-select-sd", "value")]
)
def update_state_visualizations(selected_year_map, selected_state_change, selected_year_top_10, selected_year_sd, selected_state_sd):
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

    # Handle top ten state chart data
    if selected_year_top_10 == "All Years":
        filtered_bar_ten_state = data.copy()  # Aggregate all years for the bar chart
    else:
        filtered_bar_ten_state = data[data["Year-Range"] == selected_year_top_10]  # Filter by selected year

    # Count number of times each book was banned
    top_books_state = filtered_bar_ten_state["State"].value_counts().head(10)

    state_political_leanings = {
        'AL': 'Republican',
        'AK': 'Republican',
        'AZ': 'Swing',
        'AR': 'Republican',
        'CA': 'Democrat',
        'CO': 'Democrat',
        'CT': 'Democrat',
        'DE': 'Democrat',
        'FL': 'Republican',
        'GA': 'Swing',
        'HI': 'Democrat',
        'ID': 'Republican',
        'IL': 'Democrat',
        'IN': 'Republican',
        'IA': 'Republican',
        'KS': 'Republican',
        'KY': 'Republican',
        'LA': 'Republican',
        'ME': 'Democrat',
        'MD': 'Democrat',
        'MA': 'Democrat',
        'MI': 'Swing',
        'MN': 'Democrat',
        'MS': 'Republican',
        'MO': 'Republican',
        'MT': 'Republican',
        'NE': 'Republican',
        'NV': 'Swing',
        'NH': 'Democrat',
        'NJ': 'Democrat',
        'NM': 'Democrat',
        'NY': 'Democrat',
        'NC': 'Republican',
        'ND': 'Republican',
        'OH': 'Republican',
        'OK': 'Republican',
        'OR': 'Democrat',
        'PA': 'Swing',
        'RI': 'Democrat',
        'SC': 'Republican',
        'SD': 'Republican',
        'TN': 'Republican',
        'TX': 'Republican',
        'UT': 'Republican',
        'VT': 'Democrat',
        'VA': 'Democrat',
        'WA': 'Democrat',
        'WV': 'Republican',
        'WI': 'Swing',
        'WY': 'Republican'
    }

    marker_colors = [
        'red' if state_political_leanings.get(state, 'Unknown') == 'Republican' else 'blue' if state_political_leanings.get(state, 'Unknown') == 'Democrat' else 'gray'
        for state in top_books_state.index
    ]

    # Create bar chart for top 10 banned books
    bar_chart_fig_10_state = go.Figure(data=[
        go.Bar(
            x=top_books_state.values,
            y=top_books_state.index,
            orientation="h",
            marker_color=marker_colors,
            showlegend=False
        )
    ])

    # Add dummy traces for the legend (red and blue colors for political leanings)
    bar_chart_fig_10_state.add_trace(go.Scatter(
        x=[None], y=[None], mode='markers',
        marker=dict(color='red', size=10),
        name='Republican'
    ))

    bar_chart_fig_10_state.add_trace(go.Scatter(
        x=[None], y=[None], mode='markers',
        marker=dict(color='blue', size=10),
        name='Democrat'
    ))

    bar_chart_fig_10_state.add_trace(go.Scatter(
        x=[None], y=[None], mode='markers',
        marker=dict(color='gray', size=10),
        name='Swing'
    ))

    bar_chart_fig_10_state.update_layout(
        xaxis_title="Number of Bans",
        yaxis_title="State",
        yaxis=dict(autorange='reversed'),
        legend_title="Political Leaning"
    )

    # Handle sd bar chart data
    if selected_year_sd == "All Years":
        filtered_bar_sd = data.copy()  # Aggregate all years for the bar chart
    else:
        filtered_bar_sd = data[data["Year-Range"] == selected_year_sd]  # Filter by selected year

    filtered_bar_sd["District + State"] = filtered_bar_sd["District"] + ", " + filtered_bar_sd["State"]

    # Count number of times each book was banned
    top_books_sd = filtered_bar_sd["District + State"].value_counts().head(10)

    # Create bar chart for top 10 banned books
    bar_chart_fig_top_sd = go.Figure(data=[
        go.Bar(
            x=top_books_sd.values,
            y=top_books_sd.index,
            orientation="h",
            marker_color='#d6a5c0'
        )
    ])

    bar_chart_fig_top_sd.update_layout(
        xaxis_title="Number of Bans",
        yaxis_title="District",
        yaxis=dict(autorange='reversed')
    )

    # Filter data
    filtered_state = data[data["State"] == selected_state_sd]

    num_bans = filtered_state.groupby("District")["Title"].count().reset_index()
    num_bans.columns = ["District", "Ban Count"]
    num_bans_sorted = num_bans.sort_values(by="Ban Count", ascending=False)

     # Create bar chart for top 10 sds by state
    bar_chart_fig_top_sd_state = px.bar(
        num_bans_sorted.head(10),
        x="Ban Count",
        y="District",
        orientation="h",
    )

    bar_chart_fig_top_sd_state.update_layout(
        xaxis_title="Number of Bans",
        yaxis_title="District",
        yaxis=dict(autorange='reversed')
    )

    return choropleth_fig, change_fig, bar_chart_fig_10_state, bar_chart_fig_top_sd, bar_chart_fig_top_sd_state