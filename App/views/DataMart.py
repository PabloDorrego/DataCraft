# Importar bibliotecas necesarias
from openai import AzureOpenAI, OpenAI
import openai
from snowflake.connector.errors import DatabaseError
import streamlit as st
from views.utils import MetadataExtractorDataMart as me

# Función para cargar la vista de Data Marta en la aplicación
def load_view():
    # Crear instancia de AzureOpenAI con las configuraciones de la sesión
    client = AzureOpenAI(
            api_key=st.session_state.ao_key,
            api_version=st.session_state.ao_version,
            azure_endpoint=st.session_state.ao_endpoint
        )
    model = st.session_state.dep_name

    # Título de la página
    st.title(":red[Data Marts]")

    # Estilos y configuraciones adicionales
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
                display: none;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    with st.sidebar:
        st.info("Antes de comenzar, asegurese de seleccionar la base de datos correcta.",icon="🚨")
        # Formulario para configurar la conexión a Snowflake
        with st.expander("Configuración "):
            with st.form(key="config"):
                acc_input = st.text_input("Identificador cuenta de Snowflake", value=st.session_state.acc_input)
                user_input = st.text_input("Nombre de usuario", value=st.session_state.user_input)
                pass_input = st.text_input("Contraseña", type='password',value=st.session_state.pass_input)
                input3 = st.text_input("Base de datos:", value=st.session_state.input3)
                # Every form must have a submit button.
                submitted = st.form_submit_button("Guardar configuración")
                if submitted:
                    st.session_state.acc_input=acc_input
                    st.session_state.user_input=user_input
                    st.session_state.pass_input=pass_input
                    st.session_state.input3=input3
    # Configuración de la barra lateral con información adicional
    st.sidebar.header("Información extra")

    # Caja de texto para el primer input
    input1 = st.sidebar.text_area("Añade una descripcion de la empresa", "")

    # Caja de texto para el segundo input
    input2 = st.sidebar.text_area("Añade los dominios de la empresa", "")

    # Botón para generar el metadata prompt
    if st.sidebar.button("Comenzar"):
        try:
            prompt_metadata = me.get_metadata(st.session_state.acc_input, st.session_state.user_input, st.session_state.pass_input, st.session_state.input3)
            prompt_metadata += f"\n\nEstos son los dominios de la empresa: {input1}\n\nEstos son los dominios de datos: {input2}"
        except DatabaseError as e:
            # Manejo de errores específicos de la base de datos
            if "too many failed attempts" in str(e).lower():
                st.error("Tu cuenta de Snowflake ha sido bloqueada debido a demasiados intentos fallidos. Inténtalo de nuevo después de 15 minutos o contacta a tu administrador de cuenta para obtener ayuda.")
            elif "incorrect username or password" in str(e).lower():
                st.error("Nombre de usuario o contraseña incorrectos. Por favor, revisa tus credenciales y vuelve a intentarlo.")
            else:
                st.error("Error al acceder a la base de datos. Por favor, verifica tus credenciales y asegúrate de que la base de datos está disponible.")
            st.stop()
    st.sidebar.title("")
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
                with st.spinner("Generando respuesta..."):
                    try:
                        for delta in client.chat.completions.create(
                                model=model,
                                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages_datamart],
                                stream=True,
                        ):
                            if delta.choices:
                                response += (delta.choices[0].delta.content or "")
                    except openai.RateLimitError as e :
                        # Manejo del error específico de límite de tasa de llamadas de OpenAI
                        st.error(f"Error de límite de tasa de llamadas de OpenAI: \n{e}")
                        st.stop()
                    resp_container.markdown(response)

                message = {"role": "assistant", "content": response}
                st.session_state.messages_datamart.append(message)
        st.title("")
        st.title("")
        st.title("")
    except:
        st.write("Por favor, completa los campos para comenzar.")
        st.stop()