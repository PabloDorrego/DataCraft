import streamlit as st
from streamlit_navigation_bar import st_navbar
from views import Home, Domain, DataMart, KPIs

st.set_page_config(layout="wide")
pages = ["Home","Domain", "Data Marts", "KPI", "GitHub"]
urls = {"GitHub": "https://github.com/PabloDorrego/DataCraft"}#https://github.com/gabrieltempass/streamlit-navigation-bar
# parent_dir = os.path.dirname(os.path.abspath(__file__))
# logo_path = os.path.join(parent_dir, "logo-uem.jpg")

styles = {
    "nav": {
        "background-color": "#FE0000",
        "justify-content": "left",
        
    },
    "img": {
        "margin-left": "3rem",

        "padding-right": "40%",
    },
    
    "span": {
        "color": "white",
        "padding": "15px",
    },
    "active": {
        "color": "var(--text-color)",
        "background-color": "white",
        "font-weight": "normal",
        "padding": "15px",
    }
}

page = st_navbar(
    pages,
    logo_path="App/assets/images/logo-uem.svg",    
    urls=urls,
    styles=styles,
    options=False,
)

functions = {
    "Home": Home.load_view,
    "Domain": Domain.load_view,
    "Data Marts": DataMart.load_view,
    "KPI": KPIs.load_view,
}
go_to = functions.get(page)
if go_to:
    go_to()


