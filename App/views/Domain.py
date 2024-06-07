# Importar bibliotecas necesarias
import streamlit as st
from streamlit_chat import message
import streamlit.components.v1 as components
import requests
import json
from openai import OpenAI, AzureOpenAI
from typing import List
from views.utils.functions import *
from views.utils import MetadataExtractorDomain as me
from snowflake.snowpark import Session
import utils as utl
import time
import openai
from snowflake.connector.errors import DatabaseError

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
            top: 6rem;

        }
        div[data-testid="collapsedControl"] {
            visibility: visible;
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
            try: 
                prompt_metadata = me.get_metadata(st.session_state.acc_input, st.session_state.user_input, st.session_state.pass_input, st.session_state.input3)
                
                prompt_metadata += f"\n\nEsta es la descripción de la empresa: {st.session_state.description}\nEstas son las áreas de negocio: {st.session_state.area}"
            except DatabaseError as e:
                # Manejo de errores específicos de la base de datos
                if "too many failed attempts" in str(e).lower():
                    st.error("Tu cuenta de Snowflake ha sido bloqueada debido a demasiados intentos fallidos. Inténtalo de nuevo después de 15 minutos o contacta a tu administrador de cuenta para obtener ayuda.")
                elif "incorrect username or password" in str(e).lower():
                    st.error("Nombre de usuario o contraseña incorrectos. Por favor, revisa tus credenciales y vuelve a intentarlo.")
                else:
                    st.error("Error al acceder a la base de datos. Por favor, verifica tus credenciales y asegúrate de que la base de datos está disponible.")
                st.stop()
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
        promt_json = open('App/views/utils/promptjson.txt', 'r').read()

        if "messages" not in st.session_state:
            # Inicialización del chat
            st.session_state.messages = [{"role": "system", "content": metadata}]
            st.session_state.messages.append({"role": "system", "content": promt_json})
            try:
                cl = st.session_state.client.chat.completions.create(model=st.session_state["model"], messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages], stream=False)
            except openai.RateLimitError as e :
                # Manejo del error específico de límite de tasa de llamadas de OpenAI
                st.error(f"Error de límite de tasa de llamadas de OpenAI: \n{e}")
                st.stop()
            full_response = ""
            st.text("")
            st.text("")
            st.text("")
            print(type(cl))
            print(cl)

            with st.status("Generando dominios...", expanded=True) as status:
                st.write("Accediendo a la base de datos...")
                time.sleep(2)
                st.write("Metadatos extraídos.")
                time.sleep(2)
                st.write("Procesando consulta...")
                for choice in cl.choices:
                    if choice.message and choice.message.content:
                        full_response += choice.message.content
                status.update(label="Dominios generados!", state="complete", expanded=False)

            st.session_state.messages.append({"role": "system", "content": full_response})
            if "domains" not in st.session_state:
                st.session_state["domains"] = full_response

        with st.sidebar:
            # Crear la barra lateral
            #st.image("App/views/utils/cuadrado-inetum.png")
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
                try:
                    # Procesar la respuesta del asistente
                    cl = st.session_state.client.chat.completions.create(model=st.session_state["model"], messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages], stream=True)
                except openai.RateLimitError as e :
                    # Manejo del error específico de límite de tasa de llamadas de OpenAI
                    st.error(f"Error de límite de tasa de llamadas de OpenAI: \n{e}")
                    st.stop()
                with st.spinner('Procesando consulta...'):
                    for response in cl:
                        if response.choices:
                            full_response += (response.choices[0].delta.content or "")

                if validateJSON(full_response):
                    # Lógica para procesar la respuesta JSON del asistente
                    st.session_state.messages.append({"role": "system", "content": full_response})
                    st.session_state["domains"] = full_response
                    st.session_state.messages.append({"role": "system", "content": "Ahora dame el codigo sql"})
                    try:
                        # Procesar la respuesta del asistente
                        cl = st.session_state.client.chat.completions.create(model=st.session_state["model"], messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages], stream=True)
                    except openai.RateLimitError as e :
                        # Manejo del error específico de límite de tasa de llamadas de OpenAI
                        st.error(f"Error de límite de tasa de llamadas de OpenAI: \n{e}")
                        st.stop()
                    full_response = ""
                    # Elemento de carga mientras se procesa la respuesta
                    with st.spinner('Procesando consulta...'):
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
                send = st.sidebar.button("Generar SQL y finalizar", on_click=fin)

                create_domains(dominios["dominios"], container)
            if st.session_state.finish:
                generarSQL(container)
                create_domains(dominios["dominios"], container)

    if st.session_state.display_result:
       # Credenaciales de acceso a Azure OpenAI
        client = AzureOpenAI(
            api_key=st.session_state.ao_key,
            api_version=st.session_state.ao_version,
            azure_endpoint=st.session_state.ao_endpoint
        )
        model = st.session_state.dep_name

        st.title("")
        st.info("Antes de comenzar, asegurese de seleccionar la base de datos correcta.",icon="🚨")
        #Formulario para configurar la conexión a Snowflake
        with st.expander("Configuración "):
            with st.form(key="config"):
                acc_input = st.text_input("Identificador cuenta de Snowflake", value=st.session_state.acc_input)
                user_input = st.text_input("Nombre de usuario", value=st.session_state.user_input)
                pass_input = st.text_input("Contraseña", type='password',value=st.session_state.pass_input)
                input3 = st.text_input("Base de datos:", value=st.session_state.input3)
                submitted = st.form_submit_button("Guardar configuración")
                if submitted:
                    st.session_state.acc_input=acc_input
                    st.session_state.user_input=user_input
                    st.session_state.pass_input=pass_input
                    st.session_state.input3=input3
        st.header("Información de la empresa")
        des = get_des() 
        area = get_area()
        # Botón para generar los dominios
        st.button("Generar", disabled=(area is ""), on_click=callback)
    st.title("")
    st.title("")

