import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/', name="Home", order=0)

layout = dbc.Container([
    html.H1("Banned Books: A Hidden Narrative", className="text-center my-4"),
    html.P("Explore the patterns and trends in book banning across the US", className="lead text-center"),
    
    dbc.Row([
        dbc.Col(dbc.Card(
            [
                dbc.CardHeader("State-Level Analysis"),
                dbc.CardBody([
                    html.P("View bans by state and changes over time"),
                    dcc.Link("Explore State Data", href="/state-analysis", className="btn btn-primary")
                ])
            ], className="h-100"
        ), md=4),
        
        dbc.Col(dbc.Card(
            [
                dbc.CardHeader("Book Analysis"),
                dbc.CardBody([
                    html.P("Explore banned books by genre and topics"),
                    dcc.Link("Explore Book Data", href="/book-analysis", className="btn btn-primary")
                ])
            ], className="h-100"
        ), md=4),
        
        dbc.Col(dbc.Card(
            [
                dbc.CardHeader("Author Analysis"),
                dbc.CardBody([
                    html.P("See which authors are most frequently banned"),
                    dcc.Link("Explore Author Data", href="/author-analysis", className="btn btn-primary")
                ])
            ], className="h-100"
        ), md=4),
    ], className="mb-4"),
    
    dbc.Row(
        dbc.Col(dbc.Card(
            [
                dbc.CardHeader("District-Level Analysis"),
                dbc.CardBody([
                    html.P("See which school districts ban the most books"),
                    dcc.Link("Explore District Data", href="/district-analysis", className="btn btn-primary")
                ])
            ], className="h-100"
        ), md=4),
    )
])