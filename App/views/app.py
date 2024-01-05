import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
from views.utils.analyze import AnalyzeGPT, SQL_Query, ChatGPT_Handler
from pathlib import Path
from dotenv import load_dotenv
import os
def load_view():
    # verifica si la aplicación se está ejecutando localmente o en Azure y carga 
    #las variables de entorno correspondientes desde un archivo "secrets.env" si es necesario.
    if os.getenv("WEBSITE_SITE_NAME") is None:
        env_path = Path(".") / "secrets.env"
        load_dotenv(dotenv_path=env_path)

    # carga una configuración de una variable de entorno o usa un valor predeterminado si no está definida.
    def load_setting(setting_name, session_name, default_value=""):
        """
        Function to load the setting information from session
        """
        if session_name not in st.session_state:
            if os.environ.get(setting_name) is not None:
                st.session_state[session_name] = os.environ.get(setting_name)
            else:
                st.session_state[session_name] = default_value


    #load_setting("AZURE_OPENAI_CHATGPT_DEPLOYMENT", "chatgpt", "gpt-35-turbo")
    load_setting("AZURE_OPENAI_GPT4_DEPLOYMENT", "gpt4", "gpt-35-turbo")
    load_setting(
        "AZURE_OPENAI_ENDPOINT", "endpoint", "https://resourcenamehere.openai.azure.com/"
    )
    load_setting("AZURE_OPENAI_API_KEY", "apikey")
    load_setting("SNOW_ACCOUNT", "snowaccount")
    load_setting("SNOW_USER", "snowuser")
    load_setting("SNOW_PASSWORD", "snowpassword")
    load_setting("SNOW_ROLE", "snowrole")
    load_setting("SNOW_DATABASE", "snowdatabase")
    load_setting("SNOW_SCHEMA", "snowschema")
    load_setting("SNOW_WAREHOUSE", "snowwarehouse")

    if "show_settings" not in st.session_state:
        st.session_state["show_settings"] = False

    # guarda las configuraciones de OpenAI y Snowflake en la sesión.
    def saveOpenAI():
        #st.session_state.chatgpt = st.session_state.txtChatGPT
        st.session_state.gpt4 = st.session_state.txtGPT4
        st.session_state.endpoint = st.session_state.txtEndpoint
        st.session_state.apikey = st.session_state.txtAPIKey
        st.session_state.snowaccount = st.session_state.txtSNOWAccount
        st.session_state.snowuser = st.session_state.txtSNOWUser
        st.session_state.snowpassword = st.session_state.txtSNOWPasswd
        st.session_state.snowrole = st.session_state.txtSNOWRole
        st.session_state.snowdatabase = st.session_state.txtSNOWDatabase
        st.session_state.snowschema = st.session_state.txtSNOWSchema
        st.session_state.snowwarehouse = st.session_state.txtSNOWWarehouse

        # We can close out the settings now
        st.session_state["show_settings"] = False

    # mostrar u ocultar las configuraciones en la interfaz de usuario.
    def toggleSettings():
        st.session_state["show_settings"] = not st.session_state["show_settings"]

    # Definición de variables de configuración para Azure OpenAI
    api_type = "azure"
    api_version = "2023-10-01-preview"
    api_key = st.session_state.apikey
    api_base = st.session_state.endpoint
    max_response_tokens = 1500
    token_limit = 6000
    temperature = 0.2

    
    st.title('Snowflake OpenAI Assistant')
    st.write('Este es un asistente experimental que requiere acceso a Azure OpenAI. La aplicación permite el uso de OpenAI para ayudar a obtener información de Snowflake con solo hacer preguntas. El asistente también puede generar código SQL y Python para las Preguntas.')
    # Estilos y configuraciones adicionales
    st.markdown("""
        <style>
        section[data-testid="stSidebar"]{
            top: 6%; 
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
                display: none;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


    col1, col2 = st.columns((3, 1))

    with st.sidebar:
        st.image("App/views/utils/logo-inetum.svg")
        #barra lateral con opciones para elegir entre dos aplicaciones: "SQL Assistant" y "Data Analysis Assistant".
        options = ("SQL Assistant", "Data Analysis Assistant")
        index = st.radio(
            "Choose the app", range(len(options)), format_func=lambda x: options[x]
        )
        #Si se elige la opción "SQL Assistant", se muestra un mensaje de sistema y se configura un extractor para analizar preguntas y consultas SQL.
        if index == 0:
            system_message = """
            You are an agent designed to interact with a Snowflake with schema detail in Snowflake.
            Given an input question, create a syntactically correct Snowflake query to run, then look at the results of the query and return the answer.
            You can order the results by a relevant column to return the most interesting data in the database.
            Never query for all the columns from a specific table, only ask for a the few relevant columns given the question.
            You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.
            DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
            Remember to format SQL query as in ```sql\n SQL QUERY HERE ``` in your response.

            """
            few_shot_examples = ""
            extract_patterns = [("sql", r"```sql\n(.*?)```")]
            extractor = ChatGPT_Handler(extract_patterns=extract_patterns)
        #Si se elige la opción "Data Analysis Assistant", se muestra un mensaje de sistema y se configura un extractor para analizar el flujo de pensamiento del asistente de análisis de datos.
        elif index == 1:
            system_message = """
            You are a smart AI assistant to help answer business questions based on analyzing data. 
            You can plan solving the question with one more multiple thought step. At each thought step, you can write python code to analyze data to assist you. Observe what you get at each step to plan for the next step.
            You are given following utilities to help you retrieve data and communicate your result to end user.
            1. execute_sql(sql_query: str): A Python function can query data from the Snowflake given a query which you need to create. The query has to be syntactically correct for Snowflake and only use tables and columns under <<data_sources>>. The execute_sql function returns a Python pandas dataframe contain the results of the query.  The columns retrieved are always lowercase
            2. Use plotly library for data visualization. 
            3. Use observe(label: str, data: any) utility function to observe data under the label for your evaluation. Use observe() function instead of print() as this is executed in streamlit environment. Due to system limitation, you will only see the first 10 rows of the dataset.
            4. To communicate with user, use show() function on data, text and plotly figure. show() is a utility function that can render different types of data to end user. Remember, you don't see data with show(), only user does. You see data with observe()
                - If you want to show  user a plotly visualization, then use ```show(fig)`` 
                - If you want to show user data which is a text or a pandas dataframe or a list, use ```show(data)```
                - Never use print(). User don't see anything with print()
            5. Lastly, don't forget to deal with data quality problem. You should apply data imputation technique to deal with missing data or NAN data.
            6. Always follow the flow of Thought: , Observation:, Action: and Answer: as in template below strictly. 
            7. Dont repeat thoughts. Follow your thoughts until you reach de answer. Thought 1, Thought 2, ... , Answer

            """

            few_shot_examples = """
            <<Template>>
            Question: User Question
            Thought 1: Your thought here.
            Action: 
            ```python
            #Import neccessary libraries here
            import numpy as np
            #Query some data 
            sql_query = "SOME SQL QUERY"
            step1_df = execute_sql(sql_query)
            # Replace 0 with NaN. Always have this step.
            step1_df['some_column'] = step1_df['some_column'].replace(0, np.nan)
            #observe query result
            observe("some_label", step1_df) #Always use observe() instead of print
            ```
            Observation: 
            step1_df is displayed here
            Thought 2: Your thought here
            Action:  
            ```python
            import plotly.express as px 
            #from step1_df, perform some data analysis action to produce step2_df
            #To see the data for yourself the only way is to use observe()
            observe("some_label", step2_df) #Always use observe() 
            #Decide to show it to user.
            fig=px.line(step2_df)
            #visualize fig object to user.  
            show(fig)
            #you can also directly display tabular or text data to end user.
            show(step2_df)
            ```
            Observation: 
            step2_df is displayed here
            Answer: Your final answer and comment for the question
            <</Template>>

            """

            extract_patterns = [
                ("Thought:", r"(Thought \d+):\s*(.*?)(?:\n|$)"),
                ("Action:", r"```python\n(.*?)```"),
                ("Answer:", r"([Aa]nswer:) (.*)"),
            ]
            extractor = ChatGPT_Handler(extract_patterns=extract_patterns)
        #"Settings" para mostrar u ocultar las configuraciones.
        st.button("Settings", on_click=toggleSettings)
        if st.session_state["show_settings"]:
            with st.form("AzureOpenAI"):
                st.title("Azure OpenAI Settings")
                
                st.text_input(
                    "GPT-4 deployment name",
                    key="txtGPT4",
                    help="Enter the GPT-4 deployment in Azure OpenAI. Defaults to above value if not specified",
                )
                st.text_input(
                    "Azure OpenAI Endpoint:",
                    key="txtEndpoint",
                    help="Enter the Azure Open AI Endpoint",
                    placeholder="https://<endpointname>.openai.azure.com/",
                )
                st.text_input(
                    "Azure OpenAI Key:",
                    type="password",
                    key="txtAPIKey",
                    help="Enter Azure OpenAI Key",
                )

                st.title("Snowflake Settings")
                st.text_input(
                    "Account Identifier:",
                    key="txtSNOWAccount",
                    help="Enter Snowflake Account Identifier. Do not enter with .snowflakecomputing.com",
                    placeholder="<orgname>-<accountname>",
                )
                st.text_input(
                    "User Name:", key="txtSNOWUser", help="Enter Snowflake Username"
                )
                st.text_input(
                    "Password:",
                    type="password",
                    key="txtSNOWPasswd",
                    help="Enter Snowflake Password",
                )
                st.text_input("Role:", key="txtSNOWRole", help="Enter Snowflake role")
                st.text_input(
                    "Database:", key="txtSNOWDatabase", help="Enter Snowflake Database"
                )
                st.text_input("Schema:", key="txtSNOWSchema", help="Enter Snowflake Schema")
                st.text_input(
                    "Warehouse:", key="txtSNOWWarehouse", help="Enter Snowflake Warehouse"
                )

                st.form_submit_button("Submit", on_click=saveOpenAI)

        show_code = st.checkbox("Show code", value=False)
        show_prompt = st.checkbox("Show prompt", value=False)
        question = st.text_area("Ask me a question")
        #Si se presiona el botón "Submit", se verifica que las configuraciones necesarias estén 
        #completas y se crea un objeto SQL_Query y un objeto AnalyzeGPT para interactuar con Snowflake y OpenAI GPT-4, respectivamente.
        if st.button("Submit"):
            if (
                st.session_state.apikey == ""
                or st.session_state.endpoint == ""
                or st.session_state.gpt4 == ""
            ):
                st.error("You need to specify Azure Open AI Deployment Settings!")
            elif (
                st.session_state.snowaccount == ""
                or st.session_state.snowuser == ""
                or st.session_state.snowpassword == ""
                or st.session_state.snowrole == ""
            ):
                st.error("You need to specify Snowflake Settings!")
            else:
                sql_query_tool = SQL_Query(
                    account_identifier=st.session_state.snowaccount,
                    db_user=st.session_state.snowuser,
                    db_password=st.session_state.snowpassword,
                    db_role=st.session_state.snowrole,
                    db_name=st.session_state.snowdatabase,
                    db_schema=st.session_state.snowschema,
                    db_warehouse=st.session_state.snowwarehouse
                )
                analyzer = AnalyzeGPT(
                    content_extractor=extractor,
                    sql_query_tool=sql_query_tool,
                    system_message=system_message,
                    few_shot_examples=few_shot_examples,
                    st=st,
                    gpt_deployment=st.session_state.gpt4,
                    api_type = api_type,
                    api_version = api_version,
                    api_key = api_key,
                    api_base = api_base,
                    max_response_tokens=max_response_tokens,
                    token_limit=token_limit,
                    temperature=temperature,
                    db_schema=st.session_state.snowschema
                )
                #Dependiendo de la opción seleccionada ("SQL Assistant" o "Data Analysis Assistant"), 
                #se llama a la función correspondiente para ejecutar la consulta o el análisis de datos.
                if index == 0:
                    analyzer.query_run(question, show_code, show_prompt, col1)
                elif index == 1:
                    analyzer.run(question, show_code, show_prompt, col1)
                else:
                    st.error("Not implemented yet!")
