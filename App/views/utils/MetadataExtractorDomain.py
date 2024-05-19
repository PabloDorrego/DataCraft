# Importar bibliotecas necesarias
from snowflake.snowpark import Session
import json
import streamlit as st

# Función para realizar la autenticación básica de Snowflake
def snowpark_basic_auth() -> Session:
    # Cargar las credenciales desde el archivo JSON
    with open('cred.json', 'r') as config_file:
        try:
            config = json.load(config_file)
        except json.JSONDecodeError:
            raise ValueError("Error al cargar el archivo JSON. Asegúrate de que el archivo no esté vacío y tenga un formato JSON válido.")

    # Extraer parámetros de conexión
    account = config['Snowflake']['account']
    user = config['Snowflake']['user']
    password = config['Snowflake']['password']

    connection_parameters = {
        "ACCOUNT": account,
        "USER": user,
        "PASSWORD": password
    }
    return Session.builder.configs(connection_parameters).create()

# Función para realizar la autenticación de Snowflake con parámetros específicos
def snowpark_auth(account, user, password) -> Session:
    connection_parameters = {
        "ACCOUNT": account,
        "USER": user,
        "PASSWORD": password
    }
    return Session.builder.configs(connection_parameters).create()

# Función para realizar la autenticación básica de Snowflake utilizando secretos de Streamlit
def snowpark_basic_auth_toml() -> Session:
    # Obtener parámetros de conexión desde secretos de Streamlit
    account = st.secrets["SNOWFLAKE_ACCOUNT"]
    user = st.secrets["SNOWFLAKE_USER"]
    password = st.secrets["SNOWFLAKE_PASSWORD"]

    connection_parameters = {
        "ACCOUNT": account,
        "USER": user,
        "PASSWORD": password
    }
    return Session.builder.configs(connection_parameters).create()

# Función para ejecutar una consulta y recuperar el resultado como un DataFrame
def execute_query_and_fetch_dataframe(session, db):
    # Establecer el rol y el almacén de Snowflake
    session.sql("use role accountadmin").collect()
    session.sql("use warehouse compute_wh").collect()

    # Consulta SQL para obtener metadatos de tablas y columnas
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
        AND TABLES.TABLE_SCHEMA != 'INFORMATION_SCHEMA'
        AND TABLES.TABLE_SCHEMA != 'DATA_MARTS'
    ORDER BY
        TABLES.TABLE_NAME, COLUMNS.COLUMN_NAME;
    """
    query = query.format(db, db)
    result = session.sql(query).collect()

    # Procesar el resultado y estructurarlo en un formato específico
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

# Función para dividir la lista en fragmentos más pequeños según el tamaño máximo especificado
def divide_list(result_json, max_size):
    json_str = json.dumps(result_json, ensure_ascii=False)

    # Verificar si el JSON es lo suficientemente pequeño
    if len(json_str) <= max_size:
        return [result_json]

    # Dividir el JSON en fragmentos más pequeños
    fragments = []
    current_fragment = []

    for item in result_json:
        current_fragment.append(item)
        current_size = len(json.dumps(current_fragment, ensure_ascii=False))

        if current_size > max_size:
            fragments.append(current_fragment[:-1])
            current_fragment = [item]

    # Agregar el último fragmento si es necesario
    if current_fragment:
        fragments.append(current_fragment)

    return fragments

# Función para guardar fragmentos en archivos JSON
def save_fragments_to_json(fragments, output_prefix="parte"):
    for idx, fragment in enumerate(fragments):
        output_file = f"{output_prefix}_{idx + 1}.json"
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(fragment, file, ensure_ascii=False, indent=2)
        print(f"Fragment {idx + 1} saved to {output_file}")

# Función para obtener metadatos para el prompt de OpenAI
def get_metadata(account, user, password, db):
    # Autenticación en Snowflake
    conn = snowpark_auth(account, user, password)

    # Generar prompt con metadatos de tablas y columnas
    GEN_SQL = """
Vas a actuar como un experto data architect de Snowflake llamado Yorkis.
Tu objetivo es aplicar inteligencia al proceso de segmentación por dominios en la capa Golden.
Responde solo a temas relacionados con los datos a nivel empresarial.
La respuesta esperada es un listado con los dominios recomendados por la IA, así como un listado de las tablas que deberían pertenecer a esos dominios.

Para ello debes ayudarte de una descripción de la empresa, sus áreas de negocio y los metadatos de las tablas.
Estos metadatos incluyen el nombre de la tabla, su descripción, el nombre de las columnas, su tipo y su descripción. Los metadataos tienen este formato:

Table: table1
Description: description1
Columns:
Column: column1
Description: column1 description



Es primordial que una tabla no puede estar en varios dominios.

A continuación te dejo los metadatos de las tablas:

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
