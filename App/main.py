# Importamos las bibliotecas necesarias
import streamlit as st
from openai import AzureOpenAI
import utils as utl
from views import home, DMapp, connection, Orchestrator, reverseDM
import webbrowser

# Función para abrir una página web
def abrir_pagina_web(url):
    webbrowser.open(url)

# Configuramos la página de la aplicación Streamlit
st.set_page_config(
    page_title="GenAI domains",
    page_icon="🤖",
    layout="wide"
)

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
        connection.load_view()
    elif route == "DMapp":
        DMapp.load_view()
    elif route == "orchestrator":
        Orchestrator.load_view()
    elif route == "reverseDM":
        reverseDM.load_view()
    elif route == "assistant":
        abrir_pagina_web("https://sf-openai-bot.streamlit.app/")
    elif route is None:
        home.load_view()
    

# Llamamos a la función de navegación para iniciar la aplicación
navigation()
