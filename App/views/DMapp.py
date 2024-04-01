# Importar bibliotecas necesarias
from openai import AzureOpenAI, OpenAI
import streamlit as st
from views.utils import DataMart as me

# Función para cargar la vista de Data Marta en la aplicación
def load_view():
    st.sidebar.image("App/views/utils/cuadrado-inetum.png")
    st.sidebar.header("Configuracion Azure OpenAI")

    # Entradas para configuración de Azure OpenAI
    ao_key = st.sidebar.text_input("Azure api token: ", type="password")
    ao_version = st.sidebar.text_input("Azure api version:", "2023-10-01-preview")
    ao_endpoint = st.sidebar.text_input("Azure endopoint:",type="password")
    dep_name = st.sidebar.text_input("Azure deployment name:")

    # Crear instancia de AzureOpenAI con las configuraciones
    client = AzureOpenAI(
        api_key=ao_key,  
        api_version=ao_version,
        azure_endpoint=ao_endpoint
    )
    st.session_state["client"]=client
    model = dep_name
    st.session_state["model"]=model

    st.sidebar.header("Configuracion Snowflake")

    # Entradas para configuración de Snowflake
    acc_input = st.sidebar.text_input("Identificador cuenta de Snowflake",type='password')
    user_input = st.sidebar.text_input("Nombre de usuario")
    pass_input = st.sidebar.text_input("Contraseña",type='password')
    input3 = st.sidebar.text_input("Base de datos:",)

    # Título de la página
    st.title(":red[Data Marta]")

    #Estilos y configuraciones adicionales
    st.markdown("""
        <style>
        section[data-testid="stSidebar"]{
            top: 6%; 
            height: 100% !important;
        }
        div[data-testid="collapsedControl"] {
            visibility: visible;
        }
        </style>""", unsafe_allow_html=True)
    
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

    # Configuración de la barra lateral con información adicional
    st.sidebar.header("Información")

    # Caja de texto para el primer input
    input1 = st.sidebar.text_area("Añade una descripcion de la empresa", "")

    # Caja de texto para el segundo input
    input2 = st.sidebar.text_area("Añade los dominios de la empresa", "")

    # Botón para generar el metadata prompt
    if st.sidebar.button("Comenzar"):
        prompt_metadata = me.get_metadata(acc_input, user_input, pass_input, input3)
        prompt_metadata += f"\n\nEstos son los dominios de la empresa: {input1}\n\nEstos son los dominios de datos: {input2}"

    try: 
        if "messages_datamart" not in st.session_state:
            st.session_state.messages_datamart = [{"role": "system", "content": prompt_metadata}]

        # Interfaz del chatbot y manejo de mensajes
        if prompt := st.chat_input():
            st.session_state.messages_datamart.append({"role": "user", "content": prompt})

        for message in st.session_state.messages_datamart:
            if message["role"] == "system":
                continue
            with st.chat_message(message["role"]):
                st.write(message["content"])
                if "results" in message:
                    st.dataframe(message["results"])

        if st.session_state.messages_datamart[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                response = ""
                resp_container = st.empty()
                for delta in client.chat.completions.create(
                        model=model,
                        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages_datamart],
                        stream=True,
                ):
                    if delta.choices:
                        response += (delta.choices[0].delta.content or "")
                    resp_container.markdown(response)

                message = {"role": "assistant", "content": response}
                st.session_state.messages_datamart.append(message)
    except:
        st.error("Por favor, rellene todos los campos de configuración")
        st.stop()
