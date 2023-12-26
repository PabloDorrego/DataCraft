import streamlit as st
# Función para cargar la vista principal (home) de la aplicación
def load_view():
    # Crear columnas para las imágenes
    img1, img2, img3,img4, img5 = st.columns(5)
    
    # Mostrar la primera imagen en la primera columna
    with img1:
        st.image("App/views/utils/logo-inetum.svg", width=300)
    
    # Título y encabezado principal
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
        st.write("Permite la generación de los data marts así como las consultas SQL relativas.")
        st.write("Se pone a disposición del usuario un chatbot que mostrará su propuesta en primer lugar.")
