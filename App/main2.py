import streamlit as st
from streamlit_navigation_bar import st_navbar
from views import home, DMapp, connection, Orchestrator, reverseDM, app

pages = ["Home","Domain", "Data Marta", "Data Marta Reverse", "GitHub"]
urls = {"GitHub": "https://github.com/gabrieltempass/streamlit-navigation-bar"}
styles = {
    "nav": {
        "background-color": "#7BD192",
    },
    "div": {
        "max-width": "32rem",
    },
    "span": {
        "border-radius": "0.5rem",
        "padding": "0.4375rem 0.625rem",
        "margin": "0 0.125rem",
    },
    "active": {
        "background-color": "rgba(255, 255, 255, 0.25)",
    },
    "hover": {
        "background-color": "rgba(255, 255, 255, 0.35)",
    },
}

page = st_navbar(
    pages,
    urls=urls,
    styles=styles,
    options=False,
)

functions = {
    "Home": home.load_view,
    "Domain": connection.load_view,
    "Data Marta": DMapp.load_view,
    "Data Marta Reverse": reverseDM.load_view,
}
go_to = functions.get(page)
if go_to:
    go_to()