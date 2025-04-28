import dash
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import json
import glob
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

# Get all matching JSON files
json_files = glob.glob('/Users/ariannahaider/IW02-Book-Ban/books_info_finals/books_info_final_*.json')

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

# Explode the categories so that each category gets its own row
exploded_df = cat_df.explode('Categories').dropna(subset=['Categories'])
genres = [
    "adventure and adventurers",
    "biography",
    "comics (graphic works)",
    "drama",
    "dystopian",
    "fantasy",
    "fiction",
    "folklore",
    "graphic novels",
    "historical fiction",
    "horror",
    "humor",
    "literary fiction",
    "memoir",
    "mystery",
    "nonfiction",
    "novel",
    "picture books",
    "poetry",
    "realistic fiction",
    "romance",
    "science fiction",
    "short stories",
    "thriller",
    "young adult literature"
]

topics = [
    "abortion",
    "abuse",
    "accidents",
    "acting",
    "activism",
    "adolescence",
    "adoption",
    "adultery",
    "aeronautics",
    "african american authors",
    "aging",
    "alcohol",
    "aliens",
    "american history",
    "animal rights",
    "antisemitism",
    "art",
    "asian americans",
    "atheism",
    "autism",
    "beauty standards",
    "bullying",
    "cancer",
    "capitalism",
    "censorship",
    "child abuse",
    "climate change",
    "colonialism",
    "communism",
    "consent",
    "conservation",
    "crime",
    "death",
    "disability",
    "discrimination",
    "divorce",
    "drug abuse",
    "eating disorders",
    "environment",
    "evolution",
    "feminism",
    "gender identity",
    "genocide",
    "grief",
    "gun violence",
    "health",
    "homelessness",
    "immigration",
    "incarceration",
    "incest",
    "indigenous peoples",
    "islamophobia",
    "lgbtq",
    "mental health",
    "miscarriage",
    "murder",
    "nontraditional families",
    "police brutality",
    "pregnancy",
    "racism",
    "rape",
    "religion",
    "school shootings",
    "sex education",
    "sexual assault",
    "sexuality",
    "slavery",
    "suicide",
    "terrorism",
    "trauma",
    "violence",
    "war",
    "white supremacy",
    "witchcraft",
    "women's rights"
]

# Convert categories in the DataFrame to lowercase for comparison
exploded_df['Categories'] = exploded_df['Categories'].astype(str).str.lower()

# Convert genres and topics lists to lowercase for comparison
genres = [genre.lower() for genre in genres]
topics = [topic.lower() for topic in topics]

# Filter for genres and topics case-insensitively
genres_df = exploded_df[exploded_df['Categories'].isin(genres)]
topics_df = exploded_df[exploded_df['Categories'].isin(topics)]

dash.register_page(__name__, path='/book-analysis', name="Book Analysis")

layout = html.Div(
    style={"maxWidth": "1200px", "margin": "0 auto", "padding": "20px"},
    children=[
    html.H1("Book-Level Book Ban Analysis", className="text-center my-4"),

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

    # Book Genre bar chart
    html.H3("Top Genres of Banned Books"),

    html.P("Select a school year:"),
    dcc.Dropdown(
        id='year-select-genres',
        options=[{"label": year, "value": year} for year in year_options],
        value="All Years",  # Default value is "All Years"
        style={'width': '50%'}
    ),
    dcc.Graph(id="top-genre-bar-chart"),

     # Book Topic bar chart
    html.H3("Top Topics of Banned Books"),

    html.P("Select a school year:"),
    dcc.Dropdown(
        id='year-select-topics',
        options=[{"label": year, "value": year} for year in year_options],
        value="All Years",  # Default value is "All Years"
        style={'width': '50%'}
    ),
    dcc.Graph(id="top-topic-bar-chart"),
])

# --- Callback for interactive choropleth ---
@dash.callback(
     [Output("top-books-bar-chart", "figure"),
     Output("top-genre-bar-chart", "figure"),
     Output("top-topic-bar-chart", "figure"),
     ],
    [Input("year-select-bar", "value"),
     Input("year-select-genres", "value"),
     Input("year-select-topics", "value"),
     ],
)

def update_map(selected_year_bar, selected_year_genre, selected_year_topic,):

     # Handle bar chart data
    if selected_year_bar == "All Years":
        filtered_bar = data.copy()  # Aggregate all years for the bar chart
    else:
        filtered_bar = data[data["Year-Range"] == selected_year_bar]  # Filter by selected year

    book_counts = (
        filtered_bar.groupby(['Normalized Title', 'Author'])
        .size()
        .reset_index(name='Count')
        .sort_values(by='Count', ascending=False)
    )
    
    # Show top 10 most banned books
    top_10 = book_counts.head(10)

    # Create bar chart for top 10 banned books
    bar_chart_fig_top_books = px.bar(
        top_10,
        x="Count",
        y="Normalized Title",
        orientation="h"
    )

    bar_chart_fig_top_books.update_layout(
        xaxis_title="Number of Bans",
        yaxis_title="Book Title",
        yaxis=dict(autorange='reversed')
    )

    # Top Book Genres
    if selected_year_genre == "All Years":
        filtered_bar_genre= data.copy()  # Aggregate all years for the bar chart
    else:
        filtered_bar_genre = data[data["Year-Range"] == selected_year_genre]  # Filter by selected year

    ## Get the titles for the selected year
    filtered_titles_g = filtered_bar_genre["Title"].unique()

    # Filter cat_df to include only books in those titles
    filtered_cat_df_g = cat_df[cat_df["Title"].isin(filtered_titles_g)]
    
    filtered_categories = [cat for sublist in filtered_cat_df_g["Categories"] for cat in sublist]
    filtered_genres = [cat.lower() for cat in filtered_categories if cat.lower() in genres]

    # Count and get top 10 categories
    genre_series = pd.Series(filtered_genres)
    top_10_genres = genre_series.value_counts().head(10)

    bar_chart_fig_top_genre = go.Figure(data=[
        go.Bar(
            x=top_10_genres.values,
            y=top_10_genres.index,
            orientation="h",
            marker_color="#355c7d"
        )
    ])

    bar_chart_fig_top_genre.update_layout(
        xaxis_title="Genre",
        yaxis_title="Frequency",
        xaxis_tickangle=-45,
        yaxis=dict(autorange='reversed')
    )

    # Top Book Topics
    if selected_year_topic == "All Years":
        filtered_bar_topics= data.copy()  # Aggregate all years for the bar chart
    else:
        filtered_bar_topics = data[data["Year-Range"] == selected_year_topic]  # Filter by selected year

    ## Get the titles for the selected year
    filtered_titles_t = filtered_bar_topics["Title"].unique()

    # Filter cat_df to include only books in those titles
    filtered_cat_df_g = cat_df[cat_df["Title"].isin(filtered_titles_t)]
    
    filtered_categories = [cat for sublist in filtered_cat_df_g["Categories"] for cat in sublist]
    filtered_topics = [cat.lower() for cat in filtered_categories if cat.lower() in topics]

    # Count and get top 10 categories
    topic_series = pd.Series(filtered_topics)
    top_10_topics = topic_series.value_counts().head(10)

    bar_chart_fig_top_topic = go.Figure(data=[
        go.Bar(
            x=top_10_topics.values,
            y=top_10_topics.index,
            orientation="h",
            marker_color="#355c7d"
        )
    ])

    bar_chart_fig_top_topic.update_layout(
        xaxis_title="Topics",
        yaxis_title="Frequency",
        xaxis_tickangle=-45,
        yaxis=dict(autorange='reversed')
    )

    return bar_chart_fig_top_books, bar_chart_fig_top_genre, bar_chart_fig_top_topic,