from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import us
import json
import glob

# --- Load and preprocess your data ---
data = pd.read_csv("pen_combined.csv")

# Ensure state abbreviations
data["State"] = data["State"].apply(lambda x: us.states.lookup(x).abbr if us.states.lookup(x) else x)

# --- Get available years for selection ---
years = sorted(data["Year-Range"].dropna().unique())

year_options = ["All Years"] + years

top_books = data["Title"].value_counts().head(10)

# Get all matching JSON files
json_files = glob.glob('books_info_final_*.json')

# Load and combine data from all matching files
data_json = []
for file in json_files:
    with open(file, 'r') as f:
        file_data = json.load(f)
        if isinstance(file_data, list):
            data_json.extend(file_data)

all_titles = []
all_categories = []

if isinstance(data_json, list):
    for item in data_json:
        volume_info = item.get("volumeInfo", {})
        title = volume_info.get("title", [])
        categories = volume_info.get("categories", [])

        unique_categories = []
        seen_categories = set()
        for category in categories:
            sections = category.split(' / ')
            for section in sections:
                if section not in seen_categories:
                    unique_categories.append(section)
                    seen_categories.add(section)

        all_titles.append(title)
        all_categories.append(unique_categories)

cat_df = pd.DataFrame({
    'Title': all_titles,
    'Categories': all_categories
})

data_gender = pd.read_csv('pen_with_genders.csv')

# with open("school_district_boundaries.geojson", "r") as fboundary:
#     geojson_sd_file = json.load(fboundary)

# --- Dash app setup ---
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Banned Books: A Hidden Narrative", style={'textAlign':'center'}),

    # choropleth char year filter
    html.H3("Number of Book Bans by State"),
    html.P("Select a school year:"),
    dcc.Dropdown(
        id='year-select-map',
        options=[{"label": year, "value": year} for year in year_options],
        value="All Years",  # Default to first year
        style={'width': '50%'}
    ),
    dcc.Graph(id="choropleth-map"),

    # Bar chart for top 10 banned books
    html.H3("Top 10 Most Banned Books"),

    # Bar chart year filter
    html.P("Select a school year:"),
    dcc.Dropdown(
        id='year-select-bar',
        options=[{"label": year, "value": year} for year in year_options],
        value="All Years",  # Default value is "All Years"
        style={'width': '50%'}
    ),
    dcc.Graph(id="top-books-bar-chart"),

    # Dumbbell chart year filter
   html.H3("Change in Number of Banned Books By State"),
    html.Div([
        html.Div([
            html.Label("Select Start Year:"),
            dcc.Dropdown(
                id="start-year",
                options=[{"label": y, "value": y} for y in years],
                value=years[0],
                clearable=False,
                style={"width": "100%"}
            ),
        ], style={"width": "45%", "display": "inline-block"}),
        html.Div([
            html.Label("Select End Year:"),
            dcc.Dropdown(
                id="end-year",
                options=[{"label": y, "value": y} for y in years],
                value=years[-1],
                clearable=False,
                style={"width": "100%"}
            ),
        ], style={"width": "45%", "display": "inline-block", "marginLeft": "5%"})
    ]),
    dcc.Graph(id="dumbbell-chart"),

    # Top school districts bar chart
    html.H3("School Districts with Most Banned Books"),

    # School district chart year filter
    html.P("Select a school year for the bar chart (or view all years):"),
    dcc.Dropdown(
        id='year-select-sd',
        options=[{"label": year, "value": year} for year in year_options],
        value="All Years",  # Default value is "All Years"
        style={'width': '50%'}
    ),
    dcc.Graph(id="top-sd-bar-chart"),

    # Book category bar chart
    html.H3("Top Categories of Banned Books"),

    html.P("Select a school year for the bar chart (or view all years):"),
    dcc.Dropdown(
        id='year-select-categories',
        options=[{"label": year, "value": year} for year in year_options],
        value="All Years",  # Default value is "All Years"
        style={'width': '50%'}
    ),
    dcc.Graph(id="top-cat-bar-chart"),

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

    # Genders of Authors
    html.H3("Most Banned Genders of Authors"),

    html.P("Select a school year for the bar chart (or view all years):"),
    dcc.Dropdown(
        id='year-select-genders',
        options=[{"label": year, "value": year} for year in year_options],
        value="All Years",  # Default value is "All Years"
        style={'width': '50%'}
    ),
    dcc.Graph(id="top-gender-bar-chart"),

    # # School district map
    # html.H3("Bans By District"),

    # html.P("Select a school year for the bar chart (or view all years):"),
    # dcc.Dropdown(
    #     id='year-select-sd-map',
    #     options=[{"label": year, "value": year} for year in year_options],
    #     value="All Years",  # Default value is "All Years"
    #     style={'width': '50%'}
    # ),
    # dcc.Graph(id="sd-map"),
])


# --- Callback for interactive choropleth ---
@app.callback(
    [Output("choropleth-map", "figure"),
     Output("top-books-bar-chart", "figure"),
     Output("dumbbell-chart", "figure"),
     Output("top-sd-bar-chart", "figure"),
     Output("top-cat-bar-chart", "figure"),
     Output("top-author-bar-chart", "figure"),
     Output("top-gender-bar-chart", "figure"),
     ],
    [Input("year-select-map", "value"),
     Input("year-select-bar", "value"),
     Input("start-year", "value"),
     Input("end-year", "value"),
     Input("year-select-sd", "value"),
     Input("year-select-categories", "value"),
     Input("year-select-authors", "value"),
     Input("year-select-genders", "value")
     ],
)

# Input("year-select-sd-map", "value")
# Output("sd-map", "figure")

def update_map(selected_year_map, selected_year_bar, start_year, end_year, selected_year_sd, selected_year_cat, selected_year_author, selected_year_gender,):
    # selected_year_sd_map

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
        color_continuous_scale="Reds",
        scope="usa",
    )

    choropleth_fig.update_layout(
        geo=dict(bgcolor='rgba(0,0,0,0)'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin={"r":0, "t":30, "l":0, "b":0}
    )

     # Handle bar chart data
    if selected_year_bar == "All Years":
        filtered_bar = data.copy()  # Aggregate all years for the bar chart
    else:
        filtered_bar = data[data["Year-Range"] == selected_year_bar]  # Filter by selected year

    # Count the number of bans per book
    top_books = filtered_bar["Title"].value_counts().head(10)

    # Create bar chart for top 10 banned books
    bar_chart_fig_top_books = go.Figure(data=[
        go.Bar(
            x=top_books.values,
            y=top_books.index,
            orientation="h"
        )
    ])

    bar_chart_fig_top_books.update_layout(
        xaxis_title="Number of Bans",
        yaxis_title="Book Title",
        yaxis=dict(autorange='reversed')
    )

    # Dumbbell Chart with Custom Start/End Year
    state_year_bans = data[data["Year-Range"].isin([start_year, end_year])]
    state_year_bans = state_year_bans.groupby(["State", "Year-Range"])["Title"].count().reset_index()
    state_year_bans.columns = ["State", "Year", "Ban Count"]

    top_states = state_year_bans.groupby("State")["Ban Count"].sum().nlargest(10).index.tolist()
    top_state_bans = state_year_bans[state_year_bans["State"].isin(top_states)]

    start_df = top_state_bans[top_state_bans["Year"] == start_year]
    end_df = top_state_bans[top_state_bans["Year"] == end_year]
    dumbbell_data = pd.merge(start_df, end_df, on="State", suffixes=("_start", "_end"))

    dumbbell_fig = go.Figure()

    dumbbell_fig.add_trace(go.Scatter(
        x=dumbbell_data["Ban Count_start"], y=dumbbell_data["State"],
        mode="markers", name=start_year,
        marker=dict(color="red", size=12)
    ))

    dumbbell_fig.add_trace(go.Scatter(
        x=dumbbell_data["Ban Count_end"], y=dumbbell_data["State"],
        mode="markers", name=end_year,
        marker=dict(color="blue", size=12)
    ))

    for i in range(len(dumbbell_data)):
        dumbbell_fig.add_trace(go.Scatter(
            x=[dumbbell_data["Ban Count_start"].iloc[i], dumbbell_data["Ban Count_end"].iloc[i]],
            y=[dumbbell_data["State"].iloc[i], dumbbell_data["State"].iloc[i]],
            mode="lines",
            line=dict(color="gray", width=2),
            showlegend=False
        ))

    dumbbell_fig.update_layout(
        title=f"{start_year} vs. {end_year}",
        xaxis_title="Number of Bans",
        yaxis_title="State"
    )

     # Handle sd bar chart data
    if selected_year_sd == "All Years":
        filtered_bar_sd = data.copy()  # Aggregate all years for the bar chart
    else:
        filtered_bar_sd = data[data["Year-Range"] == selected_year_sd]  # Filter by selected year

    # Count number of times each book was banned
    top_books_sd = filtered_bar_sd["District"].value_counts().head(10)

    # Create bar chart for top 10 banned books
    bar_chart_fig_top_sd = go.Figure(data=[
        go.Bar(
            x=top_books_sd.values,
            y=top_books_sd.index,
            orientation="h"
        )
    ])

    bar_chart_fig_top_sd .update_layout(
        xaxis_title="Number of Bans",
        yaxis_title="District",
        yaxis=dict(autorange='reversed')
    )

    # Top Book Categories
    if selected_year_cat == "All Years":
        filtered_bar_cat= data.copy()  # Aggregate all years for the bar chart
    else:
        filtered_bar_cat = data[data["Year-Range"] == selected_year_cat]  # Filter by selected year

    ## Get the titles for the selected year
    filtered_titles = filtered_bar_cat["Title"].unique()

    # Filter cat_df to include only books in those titles
    filtered_cat_df = cat_df[cat_df["Title"].isin(filtered_titles)]

    # Flatten the list of categories for those titles
    filtered_categories = [cat for sublist in filtered_cat_df["Categories"] for cat in sublist]

    # Count and get top 10 categories
    category_series = pd.Series(filtered_categories)
    top_10_categories = category_series.value_counts().head(10)

    bar_chart_fig_top_cat = go.Figure(data=[
        go.Bar(
            x=top_10_categories.values,
            y=top_10_categories.index,
            orientation="h"
        )
    ])

    bar_chart_fig_top_cat.update_layout(
        xaxis_title="Category",
        yaxis_title="Frequency",
        xaxis_tickangle=-45,
        yaxis=dict(autorange='reversed')
    )

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
            orientation="h"
        )
    ])

    bar_chart_fig_top_authors.update_layout(
        xaxis_title="Number of Bans",
        yaxis_title="Book Title",
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
            x=top_genders.index,
            y=top_genders.values
        )
    ])

    bar_chart_fig_top_genders.update_layout(
        xaxis_title="Sex or Gender",
        yaxis_title="Number of Authors"
    )

    # # Filter data
    # if selected_year_sd_map == "All Years":
    #     filtered_sd_map = data.copy()
    # else:
    #     filtered_sd_map = data[data["Year-Range"] == selected_year_sd_map]

    # # Aggregate book bans per state
    # state_bans_sd = filtered_sd_map.groupby("District")["Title"].count().reset_index()
    # state_bans_sd.columns = ["District", "Ban Count"]

    # # Create choropleth
    # choropleth_sd_map = px.choropleth(
    #     state_bans_sd,
    #     geojson=geojson_sd_file,
    #     locations="District",
    #     color="Ban Count",
    #     color_continuous_scale="Reds",
    #     scope="usa",
    # )

    # choropleth_sd_map.update_layout(
    #     geo=dict(bgcolor='rgba(0,0,0,0)'),
    #     plot_bgcolor='white',
    #     paper_bgcolor='white',
    #     margin={"r":0, "t":30, "l":0, "b":0}
    # )

    return choropleth_fig, bar_chart_fig_top_books, dumbbell_fig, bar_chart_fig_top_sd, bar_chart_fig_top_cat, bar_chart_fig_top_authors, bar_chart_fig_top_genders, 
# choropleth_sd_map


if __name__ == "__main__":
    app.run(debug=True)