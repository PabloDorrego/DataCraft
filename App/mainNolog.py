import streamlit as st
from streamlit_navigation_bar import st_navbar
from views import home, DMapp, connection, reverseDM
import streamlit as st
import streamlit_authenticator as stauth
import os
st.set_page_config(layout="wide")
pages = ["Home","Domain", "Data Marta", "Data Marta Reverse", "GitHub"]
urls = {"GitHub": "https://github.com/gabrieltempass/streamlit-navigation-bar"}
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
    "Home": home.load_view,
    "Domain": connection.load_view,
    "Data Marta": DMapp.load_view,
    "Data Marta Reverse": reverseDM.load_view,
}
go_to = functions.get(page)
if go_to:
    go_to()


