# Importar bibliotecas necesarias
from snowflake.snowpark import Session
import json
import streamlit as st

# Función para autenticar y obtener una sesión Snowflake básica
def snowpark_basic_auth() -> Session:
    # Leer configuración desde un archivo JSON
    with open('cred.json', 'r') as config_file:
        try:
            config = json.load(config_file)
        except json.JSONDecodeError:
            raise ValueError("Error al cargar el archivo JSON. Asegúrate de que el archivo no esté vacío y tenga un formato JSON válido.")

    account = config['Snowflake']['account']
    user = config['Snowflake']['user']
    password = config['Snowflake']['password']

    connection_parameters = {
        "ACCOUNT": account,
        "USER": user,
        "PASSWORD": password
    }
    return Session.builder.configs(connection_parameters).create()

# Función para autenticar y obtener una sesión Snowflake con parámetros específicos
def snowpark_auth(account, user, password) -> Session:
    connection_parameters = {
        "ACCOUNT": account,
        "USER": user,
        "PASSWORD": password
    }
    return Session.builder.configs(connection_parameters).create()

# Función para autenticar y obtener una sesión Snowflake utilizando secretos de Streamlit
def snowpark_basic_auth_toml() -> Session:
    account = st.secrets["SNOWFLAKE_ACCOUNT"]
    user = st.secrets["SNOWFLAKE_USER"]
    password = st.secrets["SNOWFLAKE_PASSWORD"]
    connection_parameters = {
        "ACCOUNT": account,
        "USER": user,
        "PASSWORD": password
    }
    return Session.builder.configs(connection_parameters).create()

# Función para ejecutar una consulta y obtener un DataFrame desde Snowflake
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
        AND TABLES.TABLE_SCHEMA != 'INFORMATION_SCHEMA'
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

        # Agregar información de la tabla y columna al resultado
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

# Función para dividir una lista de JSON en fragmentos más pequeños
def divide_list(result_json, max_size):
    json_str = json.dumps(result_json, ensure_ascii=False)

    # Verificar si el JSON ya es suficientemente pequeño
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

# Función para obtener información sobre los metadatos
def get_metadata(account,user,password,db):
    conn=snowpark_auth(account,user,password)
    GEN_SQL = """
Vas a actuar como un experta data architect de Snowflake llamada Marta.
Tu objetivo es aplicar inteligencia al proceso de creación de Data Marts.
La respuesta esperada es un listado con los Data Marts que recomiendas, así como un listado de las tablas de hechos y dimensiones que deberían pertenecer a esos Data Marts.

Aquí te dejo una serie de normas que debes seguir siempre:
IMPORTANTE: NO PUEDES INVENTARTE COLUMNAS. SI NO ESTAN EN LOS METADATOS NO LAS INCLUYAS.
1- Los Data Marts pueden estar compuestos por columnas de distintas tablas.
2- Los Data Marts deben contener una tabla de hechos y una o varias tablas de dimensiones.
3- No crees tablas redundantes dentro del mismo data mart.
4- Puedes seguir un esquema en estrella o en copo de nieve para crear los data marts.
5- Cuando te pida la SQL debe contener tanto la tabla de hechos como las tablas de dimensiones. Aqui te dejo un ejemplo por si te pido las sentencias SQL:
    create or replace view DATA_MART.STARTUP_FACT comment="decripcion" 
    as select s.name,
            s.customer_focus,
            s.total_inversion_captada,
            s.sector_dash,
            s.ciudad,
            s.inversores,
            s.rondas,
            s.exits,
            c.nombre_ciudad,
            c.pais,
            c.total_invertido_en_la_ciudad,
            a.tagname,
            a.type,
            s.record_id as startups_record_id,
            c.record_id as ciudades_recor_id,
            a.record_id as tags_record_id
    from GOLDEN_ZONE.STARTUPS s
    inner join GOLDEN_ZONE.CIUDADES c
        on s.ciudad = c.record_id
    inner join GOLDEN_ZONE.TAGS a
        on s.tags_startup = a.record_id;
Debes incluir siempre los comentarios.
El data mart se crea a partir de los datos de Golden_zone
Para ello debes ayudarte de una descripción de la empresa, los dominios de la empresa y los metadatos de las tablas y relaciones.
Los metadatos de las tablas incluyen el nombre de la tabla, su descripción, el nombre de las columnas, su tipo y su descripción. 
Los metadatos de las relaciones incluyen el nombre de la constraint, la tabla a la que pertenece y el tipo de constraint.

La respuesta esperada debe ser un listado con todos los datamarts posibles siguiendo siempre este esquema, sin inventarte ninguna columna:
"
Dominio :

    Data Mart :

        Nombre tabla de hechos: 
            Column 1 pk 
            Column 2 fk  
            Column 3 fk 

        Dim table
            Column 2 pk 
            Column   
        Dim table
            column 3 pk 
            column  
    Data Mart :

        Fact table:
            Column 1 

        Dim table

        Dim table

Dominio :
    ...
"
Además, si se te pide mostrar los kpis tienes que para cada data mart recomendar 3 insights o kpis que podrían usar los analistas de datos con ese data mart.
También debes proponer la fórmula matemática para generar esos kpis y explicar que hace el kpi.
Respuesta esperada:
"
Posibles insights/kpis

    (Nombre): uso.Formula

"
Es primordial que me lo des en ese formato.
Para recapitular te dejo los pasos que debes seguir, cumpliendo siempre las normas anteriores:
1- Explica que haces en 2-3 frases
2- Analizar los metadatos, descripcion y areas de la empresa
3- Crear todos los data marts con sus relaciones entre tablas, usando el formato anterior. No inventes nombres de las columnas
4- Preguntar si se desean hacer cambios, mostrar los kpis o se quieren las sentencias sql para su creación.

La respuesta esperada es un listado con los Data Marts que recomiendas, así como un listado de las tablas de hechos y dimensiones que deberían pertenecer a esos Data Marts.

A continuación te dejo los metadatos de las tablas:
{metadata}
Estas son las relaciones entre las tablas:
{relations}


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
    # Consulta adicional para obtener información sobre restricciones (constraints)
    contraints_sql="""
    select TABLE_NAME,
        CONSTRAINT_NAME,
        CONSTRAINT_TYPE
    from {}.INFORMATION_SCHEMA.TABLE_CONSTRAINTS;"""
    contraints_sql=contraints_sql.format(db)
    contraints = conn.sql(contraints_sql).collect()
    result_json = {}
    for row in contraints:
        table_name = row['TABLE_NAME']
        constraint_name=row['CONSTRAINT_NAME']
        constraint_type=row['CONSTRAINT_TYPE']

        result_json[constraint_name] = {
            'table': table_name,
            'type': constraint_type
        }

    prompt= GEN_SQL.format(metadata=Metadata_prompt,relations=result_json)

    #More metadata related to constraints
    return prompt
# Función para obtener información sobre dominios
def get_doms(account, user, password, db):
    session = snowpark_auth(account, user, password)
    session.sql("use role accountadmin").collect()
    session.sql("use warehouse compute_wh").collect()

    # Consulta para obtener información sobre los dominios
    query = """
    SELECT DISTINCT
        SCHEMA_NAME,
        COMMENT
    FROM {}.INFORMATION_SCHEMA.SCHEMATA
    WHERE SCHEMA_NAME <> 'INFORMATION_SCHEMA';
    """
    query = query.format(db)
    result = session.sql(query).collect()
    result_string = ""

    # Procesar y organizar los resultados en un formato específico
    for row in result:
        name = row['SCHEMA_NAME']
        comment = row['COMMENT']

        # Agregar información de la tabla y columna al result_string
        if name not in result_string:
            result_string += f"Table: {name}, Comment: {comment}\n"

    return result_string.strip()

# Bloque principal para ejecutar el script
if __name__ == '__main__':
    # Obtener información sobre dominios
    prompt = get_doms("TGKDGYU-UA22805", "SNOWPARK", "Snowpark1", "DEMO")
    print(prompt)
    #session_with_pwd=snowpark_basic_auth()

    #result_json = execute_query_and_fetch_dataframe(session_with_pwd)
    #print(result_json)
    #result_fragments = divide_list(result_json, 10000)
    #save_fragments_to_json(result_fragments)
    #print(json.dumps(result_fragments[1], ensure_ascii=False, indent=2))
    