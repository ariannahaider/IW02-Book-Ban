import dash
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import re


# --- Load and preprocess your data ---
data = pd.read_csv("pen_combined.csv")

# --- Get available years for selection ---
years = sorted(data["Year-Range"].dropna().unique())

year_options = ["All Years"] + years

top_books = data["Title"].value_counts().head(10)

# Define normalization function
def normalize_title(title):
    if pd.isnull(title):
        return ""
    title = title.lower()
    title = title.replace('&', 'and')  # convert ampersands to 'and'
    title = re.sub(r'\(.*?\)', '', title)  # remove anything in parentheses
    title = re.sub(r'\s+', ' ', title)  # collapse multiple spaces
    title = title.strip()
    return title

# Apply the function to create a new column
data['Normalized Title'] = data['Title'].apply(normalize_title)

data_gender = pd.read_csv('pen_with_genders.csv')

dash.register_page(__name__, path='/author-analysis', name="Book Analysis")

layout = html.Div(
    style={"maxWidth": "1200px", "margin": "0 auto", "padding": "20px"},
    children=[
    html.H1("Author-Level Book Ban Analysis", className="text-center my-4"),

    # Number of bans by author bar chart
    html.H3("Authors with Most Banned Books"),

    html.P("Select a school year for the bar chart (or view all years):"),
    dcc.Dropdown(
        id='year-select-authors',
        options=[{"label": year, "value": year} for year in year_options],
        value="All Years",  # Default value is "All Years"
        style={'width': '50%'}
    ),
    dcc.Graph(id="top-author-bar-chart"),

    # Number of unique books by author bar chart
    html.H3("Authors with Most Unique Banned Books"),

    html.P("Select a school year for the bar chart (or view all years):"),
    dcc.Dropdown(
        id='year-select-authors-unique',
        options=[{"label": year, "value": year} for year in year_options],
        value="All Years",  # Default value is "All Years"
        style={'width': '50%'}
    ),
    dcc.Graph(id="top-author-unique-bar-chart"),

    # Genders of Authors
    html.H3("Most Banned Genders of Authors"),

    html.P("Select a school year:"),
    dcc.Dropdown(
        id='year-select-genders',
        options=[{"label": year, "value": year} for year in year_options],
        value="All Years",  # Default value is "All Years"
        style={'width': '50%'}
    ),
    dcc.Graph(id="top-gender-bar-chart"),
])

# --- Callback for interactive choropleth ---
@dash.callback(
     [Output("top-author-bar-chart", "figure"),
      Output("top-author-unique-bar-chart", "figure"),
     Output("top-gender-bar-chart", "figure"),
     ],
    [Input("year-select-authors", "value"),
     Input("year-select-authors-unique", "value"),
     Input("year-select-genders", "value"),
    ],
)

def update_map(selected_year_author, selected_year_unique, selected_year_gender):

     # Handle bar chart data
    if selected_year_author == "All Years":
        filtered_bar_authors = data.copy()  # Aggregate all years for the bar chart
    else:
        filtered_bar_authors = data[data["Year-Range"] == selected_year_author]  # Filter by selected year

    # Count the number of bans per author
    top_authors = filtered_bar_authors["Author"].value_counts().head(10)

    # Create bar chart for top 10 banned books
    bar_chart_fig_top_authors = go.Figure(data=[
        go.Bar(
            x=top_authors.values,
            y=top_authors.index,
            orientation="h",
            marker_color="#99b898"
        )
    ])

    bar_chart_fig_top_authors.update_layout(
        xaxis_title="Number of Bans",
        yaxis_title="Book Title",
        yaxis=dict(autorange='reversed')
    )

    # Handle bar chart data
    if selected_year_unique == "All Years":
        filtered_bar_unique = data.copy()  # Aggregate all years for the bar chart
    else:
        filtered_bar_unique = data[data["Year-Range"] == selected_year_unique]  # Filter by selected year

    books_per_author = (
        filtered_bar_unique.groupby('Author')['Normalized Title']
        .nunique()
        .reset_index(name='Unique Book Count')
        .sort_values(by='Unique Book Count', ascending=False)
    )

    # Create bar chart for top 10 banned books
    bar_chart_fig_top_unique = px.bar(
        books_per_author.head(10),
        x="Unique Book Count",
        y="Author",
        orientation="h",
    )

    bar_chart_fig_top_unique.update_layout(
        xaxis_title="Number Unique of Bans",
        yaxis_title="Author",
        yaxis=dict(autorange='reversed')
    )

    # Handle bar chart data
    if selected_year_gender == "All Years":
        filtered_bar_gender = data_gender.copy()  # Aggregate all years for the bar chart
    else:
        filtered_bar_gender = data_gender[data_gender["Year-Range"] == selected_year_gender]  # Filter by selected year

    # Count the number of bans per author
    top_genders = filtered_bar_gender["sex or gender"].value_counts().head(10)

    # Create bar chart for top 10 banned books
    bar_chart_fig_top_genders = go.Figure(data=[
        go.Bar(
            x=top_genders.values,
            y=top_genders.index,
            orientation="h",
            marker_color="#fc766a"
        )
    ])

    bar_chart_fig_top_genders.update_layout(
        xaxis_title="Sex or Gender",
        yaxis_title="Number of Authors",
        yaxis=dict(autorange="reversed")
    )

    return bar_chart_fig_top_authors, bar_chart_fig_top_unique, bar_chart_fig_top_genders