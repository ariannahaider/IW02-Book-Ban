from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import dash

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = html.Div([
    dbc.NavbarSimple(
        children=[
            dbc.NavLink("Home", href="/"),
            dbc.NavLink("State Analysis", href="/state-analysis"),
            dbc.NavLink("Book Analysis", href="/book-analysis"),
            dbc.NavLink("Author Analysis", href="/author-analysis"),
            dbc.NavLink("District Analysis", href="/district-analysis"),
        ],
        brand="Banned Books Dashboard",
        color="primary",
        dark=True,
        sticky="top",
    ),
    
    dash.page_container
])

if __name__ == '__main__':
    app.run(debug=True)