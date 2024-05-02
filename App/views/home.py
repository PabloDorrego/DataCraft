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
    st.title(':red[Snowflake GenAI]')
    st.header("Asistentes para la segmentación de datos")
    
    # Descripción de la aplicación
    st.write("Con Snowflake GenAI podrás generar dominios y data marts con la ayuda de la inteligencia artificial generativa. Para ello solo necesitaremos que cuentes una descripción de tu empresa y las áreas de negocio o dominios. A partir de ahí, accederemos a los metadatos y se te presentará una propuesta de segmentación.")
    
    # Separador
    st.markdown("------------------------------------------")
    
    # Crear dos columnas para la información detallada sobre DomAIn y Data Marta
    col1, col2 = st.columns(2)
    
    # Sección de DomAIn
    with col1:
        st.header(":green[DomAIn]")
        st.write("Aplicación que permite generar dominios de datos de manera ágil y la generación de sentencias SQL para su creación en Snowflake.")
        st.write("Mostrará en primera instancia un listado con los dominios recomendados, así como las correspondientes tablas que deberían pertenecer a esos dominios, ofreciendo además un chatbot con el que interactuar.")
    
    # Sección de Data Marta
    with col2:
        st.header(":green[Data Marta]")
        st.write("Permite la generación de los data marts así como las consultas SQL relativas y la propuesta de una serie de posibles kpis para dicho data mart.")
        st.header(":green[Data Marta Reverse]")
        st.write("Permite identificar el data mart ideal para un determinado kpi. Además te propone el código sql para generar el kpi.")
    st.markdown("------------------------------------------")
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



