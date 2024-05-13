import streamlit as st
from streamlit_navigation_bar import st_navbar
from views import Home, Domain, DataMart, KPIs
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

with open('App/assets/config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)
authenticator.login()
if st.session_state["authentication_status"]:
    pages = ["Home","Domain", "Data Marta", "Data Marta Reverse", "GitHub"]
    urls = {"GitHub": "https://github.com/gabrieltempass/streamlit-navigation-bar"}
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
        "Data Marta": DataMart.load_view,
        "Data Marta Reverse": KPIs.load_view,
    }
    go_to = functions.get(page)
    if go_to:
        go_to()

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')


