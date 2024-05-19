import streamlit as st
from streamlit_navigation_bar import st_navbar
#https://github.com/gabrieltempass/streamlit-navigation-bar
from views import home, Domain, DataMart, KPIs

st.set_page_config(layout="wide", page_title="DataCraft")
pages = ["Home","Domain", "Data Marts", "KPI", "GitHub"]
urls = {"GitHub": "https://github.com/PabloDorrego/DataCraft"}
#Diseño de la barra de navegación
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
options = {
    "show_menu": False,
    "show_sidebar": False,
    "use_padding": True,
}
#Barra de navegación
page = st_navbar(
    pages,
    logo_path="App/assets/images/logo-uem.svg",    
    urls=urls,
    styles=styles,
    options=options,
)
#Funiones para navegar entre las vistas
functions = {
    "Home": home.load_view,
    "Domain": Domain.load_view,
    "Data Marts": DataMart.load_view,
    "KPI": KPIs.load_view,
}
go_to = functions.get(page)
if go_to:
    go_to()


