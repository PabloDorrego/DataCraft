import streamlit as st
# Función para cargar la vista principal (home) de la aplicación
def load_view():
    # Crear columnas para las imágenes
    img1, img2, img3,img4, img5 = st.columns(5)
    
    # Mostrar la primera imagen en la primera columna
    # with img1:
    #     st.image("App/views/utils/logo-inetum.svg", width=300)
    
    # Título y encabezado principal
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.title(':red[DataCraft]')
    st.header("Asistentes para la segmentación de datos")
    
    # Descripción de la aplicación
    st.write("Con DataCraft podrás generar dominios y data marts con la ayuda de la inteligencia artificial generativa. Para ello solo necesitaremos que cuentes una descripción de tu empresa y las áreas de negocio o dominios. A partir de ahí, accederemos a los metadatos y se te presentará una propuesta de segmentación.")
    st.write("Además, podrás obtener información sobre los KPIs más relevantes para tu negocio y el data mart al que pertenecen.")
    # Separador
    st.divider()
    
    # Crear dos columnas para la información detallada sobre DomAIn y Data Marta
    col1, col2 = st.columns(2)
    
    # Sección de DomAIn
    with col1:
        st.header(":green[Domain]")
        st.write("Aplicación que permite generar dominios de datos de manera ágil y la generación de sentencias SQL para su creación en Snowflake.")
        st.write("Utiliza la inteligencia artificial generativa para segmentar los dominios de datos. Permite a los usuarios interactuar con el Chatbot para realizar modificaciones en los dominios y tablas, así como para obtener explicaciones sobre las propuestas presentadas. Además, ofrece la capacidad de generar sentencias SQL para respaldar la creación de dominios y tablas en la base de datos.")

    
    # Sección de Data Marta
    with col2:
        st.header(":green[Data Marts]")
        st.write("Sugiere distintos Data Marts basados en los metadatos extraídos, indicando el dominio al que deberían pertenecer y sugiriendo posibles KPIs asociados. La interfaz de la aplicación cambia para presentar un Chatbot exclusivamente dedicado a esta tarea, ofreciendo sugerencias basadas en la información de los metadatos.")
        st.header(":green[KPI]")
        st.write("Permite identificar el data mart ideal para un determinado kpi. A través de lenguaje natural, el usuario podrá obtener información sobre los KPIs más relevantes para su negocio y la sentencia SQL para obtenerlos.")
    st.divider()
    st.header(":red[Manual de usuario]")
    st.markdown("""
    <ul>
        <p>Para comenzar, deberás configurar las credenciales de acceso a Azure OpenAI y Snowflake. Para ello, completa los campos de la sección de configuración y haz clic en el botón 'Guardar configuración'.</p>
        <p>Una vez configuradas las credenciales, podrás acceder a las distintas secciones de la aplicación desde la barra de navegación superior.</p>
        <li>En la sección de Domain, deberas introducir una descripción de tu empresa y las áreas de negocio o dominios. A partir de ahí, accederemos a los metadatos y se te presentará una propuesta de segmentación.</li>
        <li>En la sección de Data Marts, deberas introducir una descripción de tu empresa y las áreas de negocio o dominios. A partir de ahí, accederemos a los metadatos y se te presentará una propuesta de segmentación.</li>
        <li>En la sección de KPI, solo deberás introducir el KPI en lenguaje natural que te interesa y se te presentará la información correspondiente sobre los KPI's.</li>
        <li>En la sección de GitHub, podrás acceder al repositorio de la aplicación en GitHub.</li>
    </ul>
    """,unsafe_allow_html = True)
    st.divider()
    st.header(":red[Bases de datos de ejemplo]")
    ej1,ej2=st.columns(2)
    with ej2:
        st.header(":green[Financial and economic]")
        st.write("**Descripción de la base de datos:** Esta base de datos incluye indicadores macroeconómicos, volúmenes de negociación y precios de acciones de Estados Unidos y ETF ejecutados en el Nasdaq, así como datos del sector bancario para proporcionar a los usuarios una visión del estado actual de la economía y la industria financiera. Los datos se actualizan diariamente y se remontan a 2010.")
        #enlace a la doc
        st.write("**Nombre de la base de datos en Snowflake:** FINANCIAL__ECONOMIC_ESSENTIALS")
        st.write("**Descripción de la empresa:** empresa líder en el campo del análisis financiero y economico. Con la misión de proporcionar información valiosa y análisis experto para respaldar sus decisiones estratégicas y operativas.")
        st.write("**Áreas de negocio:** análisis financiero, análisis de mercado, análisis de precios, localización.")
        st.markdown("[Documentación](https://docs.cybersyn.com/public-domain/economic-and-financial/financial-and-economic-essentials)")
    with ej1:
        st.header(":green[US Housing & Real Estate]")
        st.write("**Descripción de la base de datos:** esta base de datos ofrece una amplia gama de indicadores diarios, semanales, mensuales, trimestrales y anuales, incluyendo valores de mercado de viviendas, financiamiento hipotecario, ingresos, puntos de interés y permisos de construcción.")
        st.write("**Nombre de la base de datos en Snowflake:** US_HOUSING__REAL_ESTATE_ESSENTIALS")
        st.write("**Descripción de la empresa:**  empresa que se posiciona como una fuente central de datos sobre viviendas y bienes raíces que abarca todo Estados Unidos. Su producto ofrece una amplia gama de información relacionada con la evaluación y financiamiento de viviendas en todo el país.")
        st.write("**Áreas de negocio:** financiamiento de viviendas, estadísticas de ingresos, puntos de interés y negocios, permisos de construcción, datos inmobiliarios y de vivienda en general.")
        st.markdown("[Documentación](https://docs.cybersyn.com/public-domain/real-estate/us-housing-real-estate)")
    st.divider()
    # iniciar/reset session state
    # st.session_state.acc_input = None
    # st.session_state.user_input = None
    # st.session_state.pass_input = None
    # st.session_state.input3 = None
    # st.session_state.ao_key = None
    # st.session_state.ao_version = None
    # st.session_state.ao_endpoint = None
    # st.session_state.dep_name = None
    # st.header("Configuracion Azure OpenAI")

    # st.text_input("Azure api token: ", type="password",key='ao_key')
    # st.text_input("Azure api version:", "2023-10-01-preview",key='ao_version')
    # st.text_input("Azure endopoint:",type="password",key='ao_endpoint')
    # st.text_input("Azure deployment name:",key='dep_name')
    
    # st.header("Configuracion Snowflake")
    
    # st.text_input("Identificador cuenta de Snowflake",key='acc_input')
    # st.text_input("Nombre de usuario",key='user_input')
    # st.text_input("Contraseña", type='password',key='pass_input')
    # st.text_input("Base de datos:",key='input3')

    with st.form("config_form"):
        #Inicializar session state
        if 'ao_key' not in st.session_state:
            st.session_state['ao_key'] = ""
        if 'ao_version' not in st.session_state:
            st.session_state['ao_version'] = ""
        if "ao_endpoint" not in st.session_state:
            st.session_state['ao_endpoint'] = ""
        if 'dep_name' not in st.session_state:
            st.session_state['dep_name'] = ""
        if "acc_input" not in st.session_state:
            st.session_state['acc_input'] = ""
        if 'user_input' not in st.session_state:
            st.session_state['user_input'] = ""
        if "pass_input" not in st.session_state:
            st.session_state['pass_input'] = ""     
        if "input3" not in st.session_state:
            st.session_state['input3'] = ""                    
        st.header("Configuracion Azure OpenAI")

        ao_key=st.text_input("Azure api token: ", type="password",value="926966b68cec4b2a8daf602a911dccce")
        ao_version=st.text_input("Azure api version:", value="2023-10-01-preview")#1106-Preview
        ao_endpoint=st.text_input("Azure endopoint:",type="password",value="https://paodorrego.openai.azure.com/")
        dep_name=st.text_input("Azure deployment name:",value="datacraft-gpt4")
        
        st.header("Configuracion Snowflake")
        
        # acc_input=st.text_input("Identificador cuenta de Snowflake",value=st.session_state.acc_input)#JMQWFZT-DJ11978
        # user_input=st.text_input("Nombre de usuario",value=st.session_state.user_input)#PabloDorrego
        # pass_input=st.text_input("Contraseña", type='password',value=st.session_state.pass_input)
        # input3=st.text_input("Base de datos:",value=st.session_state.input3)#FINANCIAL__ECONOMIC_ESSENTIALS
        
        acc_input = st.text_input("Identificador cuenta de Snowflake", value="JMQWFZT-DJ11978")
        user_input = st.text_input("Nombre de usuario", value="PabloDorrego")
        pass_input = st.text_input("Contraseña", type='password')

        input3 = st.text_input("Base de datos:", "FINANCIAL__ECONOMIC_ESSENTIALS")
        # Every form must have a submit button.
        submitted = st.form_submit_button("Guardar configuración")
        if submitted:
            st.session_state.ao_key = ao_key
            st.session_state.ao_version = ao_version
            st.session_state.ao_endpoint = ao_endpoint
            st.session_state.dep_name = dep_name
            st.session_state.acc_input = acc_input
            st.session_state.user_input = user_input
            st.session_state.pass_input = pass_input
            st.session_state.input3 = input3
    #añadir elemento en blanco
    st.title(" ")



