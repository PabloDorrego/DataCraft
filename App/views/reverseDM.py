# Importar bibliotecas necesarias
from openai import AzureOpenAI, OpenAI
from snowflake.snowpark import Session
import json
import streamlit as st

def snowpark_auth(account, user, password) -> Session:
    connection_parameters = {
        "ACCOUNT": account,
        "USER": user,
        "PASSWORD": password
    }
    return Session.builder.configs(connection_parameters).create()
def execute_query_and_fetch_dataframe(session, db):
    # Configurar el rol y almacén de Snowflake
    session.sql("use role accountadmin").collect()
    session.sql("use warehouse compute_wh").collect()

    # Consulta para obtener metadatos de tablas y columnas
    query = """
    SELECT DISTINCT
        TABLES.TABLE_NAME,
        TABLES.COMMENT AS TABLE_DESC,
        COLUMNS.COLUMN_NAME,
        COLUMNS.COMMENT AS COLUMN_DESC,
        COLUMNS.DATA_TYPE
    FROM 
        {}.INFORMATION_SCHEMA.COLUMNS AS COLUMNS
    JOIN
        {}.INFORMATION_SCHEMA.TABLES AS TABLES
    ON
        COLUMNS.TABLE_NAME = TABLES.TABLE_NAME
        AND TABLES.TABLE_SCHEMA = 'DATA_MARTS'
    ORDER BY
        TABLES.TABLE_NAME, COLUMNS.COLUMN_NAME;
    """
    query = query.format(db, db)
    result = session.sql(query).collect()

    # Procesar y organizar los resultados en un formato específico
    result_json = {}
    for row in result:
        table_name = row['TABLE_NAME']
        table_comment = row['TABLE_DESC']
        column_name = row['COLUMN_NAME']
        column_comment = row['COLUMN_DESC']
        column_type = row["DATA_TYPE"]

        # Agregar información de tabla y columna al resultado
        if table_name not in result_json:
            result_json[table_name] = {
                'table': table_name,
                'comment': table_comment,
                'columns': []
            }

        result_json[table_name]['columns'].append({
            'column': column_name,
            'type': column_type,
            'comment': column_comment
        })

    return list(result_json.values())
def get_metadata(account, user, password, db):
    # Autenticación en Snowflake
    conn = snowpark_auth(account, user, password)

    # Generar prompt con metadatos de tablas y columnas
    GEN_SQL = """
Vas a actuar como un experto data architect de Snowflake llamado data marta reverse.
Tu especialidad es la de buscar los data marts presentes en los metadatos, que mejor se adapten a los kpis que quieras extraer.
Te enviaré un kpi que quiero utilizar y deberás sugerirme en base a mis metadatos que data mart utilizar.
Instrucciones:
1. Dar la bienvenida explicando que haces
2. Preguntar que deseo analizar
3. Analizar la respuesta y los metadatos y proporcionar el data mart que mejor se adapte para sacar esos insights
4. Dar detalles de porque elegiste el data mart y pasos para obtener el kpi

Importante, no inventes columnas ni tablas ni datamarts. 
Si no encuentras una respuesta coherente con los metadatos no hagas nada.
"""
    Metadata_prompt = ""
    Metadatat = execute_query_and_fetch_dataframe(conn,db)
    
    for i in Metadatat:
        table_value = i.get('table', '')
        comment_value = i.get('comment', '')
        
        Metadata_prompt += f"Table: {table_value}\nDescription: {comment_value}\nColumns:\n"
        
        for j in i.get('columns', []):
            column_value = j.get('column', '')
            comment_column_value = j.get('comment', '')
            
            Metadata_prompt += f"Column: {column_value}\nDescription: {comment_column_value}\n"
    
    prompt = GEN_SQL + Metadata_prompt
    return prompt
# Función para cargar la vista de Data Marta en la aplicación
def load_view():
    st.write("")
    st.write("")
    st.write("")
    # Título de la página
    st.title(":red[KPI identification]")

    # Estilos y configuraciones adicionales
    st.markdown("""
        <style>
       
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

    # Barra lateral con configuraciones de Azure OpenAI y Snowflake
    # st.sidebar.image("App/views/utils/cuadrado-inetum.png")
    # st.sidebar.header("Configuracion Azure OpenAI")

    # # Entradas para configuración de Azure OpenAI
    # ao_key = st.sidebar.text_input("Azure api token: ", type="password")
    # ao_version = st.sidebar.text_input("Azure api version:", "2023-10-01-preview")
    # ao_endpoint = st.sidebar.text_input("Azure endopoint:",type="password")
    # dep_name = st.sidebar.text_input("Azure deployment name:")

    # Crear instancia de AzureOpenAI con las configuraciones
    client = AzureOpenAI(
        api_key=st.session_state.ao_key,  
        api_version=st.session_state.ao_version,
        azure_endpoint=st.session_state.ao_endpoint
    )
    #model = dep_name
    model=st.session_state.dep_name


    # st.sidebar.header("Configuracion Snowflake")

    # # Entradas para configuración de Snowflake
    # acc_input = st.sidebar.text_input("Identificador cuenta de Snowflake",type='password')
    # user_input = st.sidebar.text_input("Nombre de usuario")
    # pass_input = st.sidebar.text_input("Contraseña",type='password')
    # input3 = st.sidebar.text_input("Base de datos:", "")



    # Botón para generar el metadata prompt
    if st.button("Comenzar"):
        #prompt_metadata = get_metadata(st.session_state.acc_input,st.session_state.user_input,st.session_state.pass_input,st.session_state.input3)
        prompt_metadata = get_metadata(st.session_state.acc_input,st.session_state.user_input,st.session_state.pass_input,st.session_state.input3)

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
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
    except:
        st.write("Por favor, haga click en el botón de comenzar.")
        st.stop()