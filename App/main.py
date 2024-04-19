import streamlit as st
from streamlit_navigation_bar import st_navbar
from views import home, DMapp, connection, reverseDM
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

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')


