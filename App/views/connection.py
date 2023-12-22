# Importar bibliotecas necesarias
import streamlit as st
from streamlit_chat import message
import streamlit.components.v1 as components
import requests
import json
from openai import OpenAI, AzureOpenAI
from typing import List
from views.utils.functions import *
from views.utils import MetadataExtractor2 as me
from snowflake.snowpark import Session
import utils as utl

# Función principal para cargar la vista de dominios
def load_view():
    # Inicialización de variables de sesión
    if 'client' not in st.session_state:
        st.session_state['client'] = ""
    if "model" not in st.session_state:
        st.session_state['model'] = ""
    if 'display_result' not in st.session_state:
        st.session_state.display_result = True
    if 'reset' not in st.session_state:
        st.session_state.reset = False
    if 'area' not in st.session_state:
        st.session_state['area'] = ""
    if 'description' not in st.session_state:
        st.session_state['description'] = ""
    if 'prompt_metadata' not in st.session_state:
        st.session_state['prompt_metadata'] = ""
    if 'finish' not in st.session_state:
        st.session_state['finish'] = False

    # Estilos CSS personalizados
    st.markdown("""
        <style>
        section[data-testid="stSidebar"]{
            top: 5%; 
            height: 100% !important;
        }
        div[data-testid="collapsedControl"] {
            top: 100px !important;
        }
        </style>""", unsafe_allow_html=True)

    st.markdown(
    """
    <style>
        iframe[data-testid="stIFrame"] {
            height: 0 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
    )

    def callback():
        # Lógica para manejar la entrada del usuario y generar el prompt
        if des:
            st.session_state.client = client
            prompt_metadata = me.get_metadata(acc_input, user_input, pass_input, input3)
            prompt_metadata += f"\n\nEsta es la descripción de la empresa: {st.session_state.description}\nEstas son las áreas de negocio: {st.session_state.area}"
            st.session_state['area'] = area
            st.session_state['description'] = des
            st.session_state.display_result = False
            st.session_state.reset = False
            st.session_state.model = model
            st.session_state.prompt_metadata = prompt_metadata
        else:
            st.error("Por favor, rellene ambos campos")

    # Lógica para mostrar o generar el resultado
    if not st.session_state.display_result and not st.session_state.finish:
        metadata = st.session_state["prompt_metadata"]
        promt_json = open('/home/site/wwwroot/App/views/utils/promptjson.txt', 'r').read()

        if "messages" not in st.session_state:
            # Inicialización del chat
            st.session_state.messages = [{"role": "system", "content": metadata}]
            st.session_state.messages.append({"role": "system", "content": promt_json})
            cl = st.session_state.client.chat.completions.create(model=st.session_state["model"], messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages], stream=True)
            full_response = ""
            for response in cl:
                if response.choices:
                    full_response += (response.choices[0].delta.content or "")
            st.session_state.messages.append({"role": "system", "content": full_response})
            if "domains" not in st.session_state:
                st.session_state["domains"] = full_response

        with st.sidebar:
            # Crear la barra lateral
            st.image("/home/site/wwwroot/App/views/utils/cuadrado-inetum.png")
            st.markdown("""<h1 style="color:#018579; ">Domain GenAI chatbot</h1>""", unsafe_allow_html=True)

            # Aceptar la entrada del usuario
            prompt = get_text()

            # Mostrar el historial del chat
            for message in st.session_state.messages:
                if message["role"] != "system":
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

            if prompt:
                # Añadir el mensaje del usuario al historial
                st.session_state.messages.append({"role": "user", "content": prompt})

                # Mostrar el mensaje del usuario
                with st.chat_message("user"):
                    st.markdown(prompt)

                full_response = ""
                cl = st.session_state.client.chat.completions.create(model=st.session_state["model"], messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages], stream=True)
                for response in cl:
                    if response.choices:
                        full_response += (response.choices[0].delta.content or "")

                if validateJSON(full_response):
                    # Lógica para procesar la respuesta JSON del asistente
                    st.session_state.messages.append({"role": "system", "content": full_response})
                    st.session_state["domains"] = full_response
                    st.session_state.messages.append({"role": "system", "content": "Ahora dame el codigo sql"})
                    cl = st.session_state.client.chat.completions.create(model=st.session_state["model"], messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages], stream=True)
                    full_response = ""
                    for response in cl:
                        if response.choices:
                            full_response += (response.choices[0].delta.content or "")
                    st.session_state.messages.append({"role": "system", "content": full_response})
                    st.session_state.messages.append({"role": "assistant", "content": "¡Hecho! ¿Necesitas algo más?"})
                else:
                    # Mostrar la respuesta del asistente en caso de no ser un JSON válido
                    with st.chat_message("assistant"):
                        message_placeholder = st.empty()
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                        message_placeholder.markdown(full_response)

    if not st.session_state.display_result:
        # Mostrar resultados y generar SQL
        container = st.container()
        with container:
            dominios = get_JSON()
            if not st.session_state.finish:
                st.image("/home/site/wwwroot/App/views/utils/logo-inetum.svg")
                create_domains(dominios["dominios"], container)
                send = st.button("Generar SQL y finalizar", on_click=fin)
            if st.session_state.finish:
                generarSQL(container)
                create_domains(dominios["dominios"], container)

    if st.session_state.display_result:
        # Configuración de la interfaz para la generación de dominios
        st.title(":red[DOMAIN]")
        st.header("Configuracion Azure OpenAI")
        ao_key = st.text_input("Azure api token: ", "f1b219e7d6254e77a47efce20d22df34", type="password")
        ao_version = st.text_input("Azure api version:", "2023-10-01-preview")
        ao_endpoint = st.text_input("Azure endopoint:", "https://domain-datamart-gpt4.openai.azure.com/", type="password")
        dep_name = st.text_input("Azure deployment name:", "genai-llm")

        client = AzureOpenAI(
            api_key=ao_key,
            api_version=ao_version,
            azure_endpoint=ao_endpoint
        )
        model = dep_name

        st.header("Configuracion Snowflake")

        acc_input = st.text_input("Identificador cuenta de Snowflake", "TGKDGYU-UA22805")
        user_input = st.text_input("Nombre de usuario", "SNOWPARK")
        pass_input = st.text_input("Contraseña", "Snowpark1", type='password')

        input3 = st.text_input("Base de datos:", "DEMO")

        st.header("Información de la empresa")
        des = get_des() 
        area = get_area()   
        send = st.button("Generar", disabled=(area is ""), on_click=callback)
