# Importamos las bibliotecas necesarias
import streamlit as st
from openai import AzureOpenAI
import utils as utl
from views import home, DMapp, connection, Orchestrator, reverseDM, app

import hmac
import streamlit as st

# Configuramos la página de la aplicación Streamlit
st.set_page_config(
    page_title="GenAI domains",
    page_icon="🤖",
    layout="wide"
)
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the passward is validated.
    if st.session_state.get("password_correct", False):
        return True
    col1,col2,col3=st.columns(3)
    with col2:
        st.image("App/views/utils/logo-inetum.svg")
        st.write(":red[Debes introducir la contraseña para usar el acelerador]")
        # Show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
    if "password_correct" in st.session_state:
        with col2:
            st.error("😕 Password incorrect")
    return False





# Deshabilitamos la advertencia de uso global de Pyplot
st.set_option('deprecation.showPyplotGlobalUse', False)

# Inyectamos hojas de estilo personalizadas y componentes de navegación
utl.inject_custom_css()
st.markdown('<div style="position: fixed; top: 0; left: 0; width: 100%;">', unsafe_allow_html=True)
utl.navbar_component()
st.markdown('</div>', unsafe_allow_html=True)

# Ocultamos el iframe predeterminado de Streamlit
st.markdown(
    """
    <style>
        iframe[data-testid="stIFrame"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Definimos la función de navegación para determinar la vista actual y cargarla
def navigation():
    route = utl.get_current_route()
    # Determinamos la vista actual y cargamos la función correspondiente
    if route == "home":
        home.load_view()
    elif route == "connection":
        #if not check_password():
        #    st.stop()  # Do not continue if check_password is not True.
        connection.load_view()
    elif route == "DMapp":
        #if not check_password():
        #    st.stop()  # Do not continue if check_password is not True.
        DMapp.load_view()
    elif route == "orchestrator":
        #if not check_password():
        #    st.stop()  # Do not continue if check_password is not True.
        Orchestrator.load_view()
    elif route == "reverseDM":
        #if not check_password():
        #    st.stop()  # Do not continue if check_password is not True.
        reverseDM.load_view()
    elif route == "app":
        #if not check_password():
        #    st.stop()  # Do not continue if check_password is not True.
        app.load_view()
   
    elif route is None:
        home.load_view()
    

# Llamamos a la función de navegación para iniciar la aplicación
        
navigation()
