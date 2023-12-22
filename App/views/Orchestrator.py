# Este script Python automatiza el proceso de creación de capas (Bronze, Silver, Golden), tareas, streams y procedures en Snowflake
# para la ingestión y transformación de datos desde archivos CSV almacenados en un stage interno de Snowflake.

# Importar las bibliotecas necesarias.from snowflake.snowpark import Session
import os
from snowflake.snowpark import Session
import streamlit as st
#Función para iniciar sesión en Snowflake mediante autenticación básica.
#Devuelve una instancia de Session para interactuar con Snowpark.


def load_view():
    with st.sidebar:
        st.title('Ver códio SQL:')
        select=st.radio('',options=['Nueva tarea','Reestablecer orden de ejecución','Alterar estado tasks','Crear data marts','Crear constraints'])
        if select=='Nueva tarea':
                st.header("Crear nueva task en capa silver")
                st.code('''
    //CIUDADES
    CREATE OR REPLACE TASK BRONZE_ZONE.CIUDADES_UPDATENULL
    WAREHOUSE = COMPUTE_WH
    AFTER BRONZE_ZONE.CIUDADES_BZTOSZ
    AS
    UPDATE SILVER_ZONE.CIUDADES
    SET
    CCAA = COALESCE(CCAA, ''),
    INVERSORES = COALESCE(INVERSORES, ''),
    STARTUPS = COALESCE(STARTUPS, ''),
    STARTUPS_SEDE_FUERA = COALESCE(STARTUPS_SEDE_FUERA, ''),
    REGION = COALESCE(REGION, ''),
    HABITANTES = COALESCE(HABITANTES, '0'),
    RONDAS = COALESCE(RONDAS, ''),
    EXITS = COALESCE(EXITS, ''),
    INVERSORES_CON_SEDE = COALESCE(INVERSORES_CON_SEDE, ''),
    CRECIMIENTO_INTERANUAL_2020 = REGEXP_REPLACE(
        COALESCE(CRECIMIENTO_INTERANUAL_2020, ''),
        '{specialValue=(NaN|Infinity)}',
        ''
    )
    WHERE 1=1;
                        ''',language='sql')
        if select=='Reestablecer orden de ejecución':
            st.header('Cambiar orden de ejecución de las tareas')
            st.code('''ALTER TASK BRONZE_ZONE.CIUDADES_SZTOGZ REMOVE AFTER BRONZE_ZONE.CIUDADES_BZTOSZ;
ALTER TASK BRONZE_ZONE.CIUDADES_SZTOGZ ADD AFTER BRONZE_ZONE.CIUDADES_UPDATENULL;''',language='sql')
        if select=='Alterar estado tasks':
            st.header('Activar, desactivar y suspender estado de las tasks')
            st.code('''//SUSPEND
ALTER TASK BRONZE_ZONE.CIUDADES_BZTOSZ SUSPEND;
ALTER TASK BRONZE_ZONE.CIUDADES_SZTOGZ SUSPEND;
ALTER TASK BRONZE_ZONE.CIUDADES_UPDATENULL SUSPEND;
//RESUME
ALTER TASK BRONZE_ZONE.CIUDADES_SZTOGZ RESUME;
ALTER TASK BRONZE_ZONE.CIUDADES_UPDATENULL RESUME;
ALTER TASK BRONZE_ZONE.CIUDADES_BZTOSZ RESUME;
//EXECUTE 
EXECUTE TASK BRONZE_ZONE.CIUDADES_BZTOSZ;
''',language='sql')
        if select=='Crear data marts':
            st.header('Crear data marts como vistas en la capa golden')
            st.code('''create or replace schema DATA_MART;
create or replace view DATA_MART.STARTUP_FACT as
select s.name,
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

create or replace view DATA_MART.EXITS_DIM as
select 
    z.tipo_exit,
    z.tipo_comprador,
    z.pais_comprador,
    z.anno,
    z.precio,
    z.ciudad_dash,
    z.record_id
from GOLDEN_ZONE.EXITS z;

create or replace view DATA_MART.INVERSORES_DIM as
select 
    i.name,
    i.tipo,
    i.pais,
    i.inversion,
    i.record_id
from GOLDEN_ZONE.INVERSORES i;

create or replace view DATA_MART.RONDAS_DIM as
select 
    r.tamanno_ronda,
    r.tipo_inversion,
    r.tipo_inversores,
    r.anno,
    r.customer_focus,
    r.id,
    r.total_captado_startup,
    r.ciudad_dash,
    r.record_id
from GOLDEN_ZONE.RONDAS r;''',language='sql')
        if select=='Crear constraints':
            st.header('Establecer relaciones entre las tablas')
            st.code('''ALTER TABLE GOLDEN_ZONE.CIUDADES ADD CONSTRAINT ciudades_pk PRIMARY KEY (RECORD_ID);
ALTER TABLE GOLDEN_ZONE.TAGS ADD CONSTRAINT tags_pk PRIMARY KEY (RECORD_ID);
ALTER TABLE GOLDEN_ZONE.EXITS ADD CONSTRAINT exits_pk PRIMARY KEY (RECORD_ID);
ALTER TABLE GOLDEN_ZONE.INVERSORES ADD CONSTRAINT inversores_pk PRIMARY KEY (RECORD_ID);
ALTER TABLE GOLDEN_ZONE.RONDAS ADD CONSTRAINT rondas_pk PRIMARY KEY (RECORD_ID);
ALTER TABLE GOLDEN_ZONE.STARTUPS ADD CONSTRAINT startups_pk PRIMARY KEY (RECORD_ID);


ALTER TABLE GOLDEN_ZONE.STARTUPS ADD CONSTRAINT inversores_fk FOREIGN KEY (INVERSORES) REFERENCES GOLDEN_ZONE.INVERSORES (RECORD_ID);
ALTER TABLE GOLDEN_ZONE.STARTUPS ADD CONSTRAINT ciudad_fk FOREIGN KEY (CIUDAD) REFERENCES GOLDEN_ZONE.CIUDADES (RECORD_ID);
ALTER TABLE GOLDEN_ZONE.STARTUPS ADD CONSTRAINT rondas_fk FOREIGN KEY (RONDAS) REFERENCES GOLDEN_ZONE.RONDAS (RECORD_ID);
ALTER TABLE GOLDEN_ZONE.STARTUPS ADD CONSTRAINT exits_fk FOREIGN KEY (EXITS) REFERENCES GOLDEN_ZONE.EXITS (RECORD_ID);
ALTER TABLE GOLDEN_ZONE.STARTUPS ADD CONSTRAINT tags_fk FOREIGN KEY (TAGS_STARTUP) REFERENCES GOLDEN_ZONE.TAGS (RECORD_ID);''',language='sql')

    def snowpark_basic_auth() -> Session:

        # Solicitar al usuario la información de la cuenta, usuario y contraseña de Snowflake.
        account=st.text_input("Account: ")
        user=st.text_input("Username: ")
        password=st.text_input("Password: ",type="password")
   
        # Configurar los parámetros de conexión con la información proporcionada por el usuario.
        connection_parameters = {
            "ACCOUNT":account,
            "USER":user,
            "PASSWORD": password
        }

        # Crear y devolver una sesión Snowpark con la configuración proporcionada.
        return Session.builder.configs(connection_parameters).create()

    # Función para generar la declaración SQL que crea un Stream en Snowflake para una tabla específica.

    def generate_stream_statement(table_name,db,sch):

        # Plantilla de la declaración CREATE STREAM en Snowflake.
        stream_template = "CREATE STREAM IF NOT EXISTS {}.{}.{}_stream ON TABLE {}.{}.{};"
        
        # Formatear la declaración con los parámetros proporcionados.    
        stream_statement= stream_template.format(db,sch,table_name,db,sch,table_name)
        
        # Devolver la declaración generada.    
        return stream_statement

    # Función para generar la declaración SQL de un procedimiento almacenado en JavaScript.
    # Este procedimiento almacorado realiza la inserción desde un stream a una tabla de destino.
    def generate_procedure_transport(stream_name, source_schema, source_table,db, target_schema,procedure_name):
        
        # Plantilla del procedimiento almacenado en JavaScript para realizar la inserción desde un stream.
        procedure_template = """
    CREATE OR REPLACE PROCEDURE {}.{}.{}()
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    EXECUTE AS CALLER
    AS
    $$
    // Obtiene las columnas disponibles en el stream
    var columnas_stream = [];
    var get_columns_query = `
    SELECT COLUMN_NAME
    FROM INFORMATION_SCHEMA.COLUMNS
    // AJUSTAR ESQUEMA Y TABLA
    WHERE TABLE_NAME = '{}'  
    AND TABLE_SCHEMA = '{}'
    ORDER BY ORDINAL_POSITION`;

    var statement = snowflake.createStatement({{sqlText: get_columns_query}});
    var result_set = statement.execute();
    while (result_set.next()) {{
    columnas_stream.push(result_set.getColumnValue(1));
    }}

    // Construye la consulta dinámicamente
    var sql_command = `
    INSERT INTO {}.{}.{}
    SELECT
        ${{columnas_stream.join(', ')}}
    FROM {}.{}.{}`;

    // Ejecuta la consulta
    var statement1 = snowflake.createStatement({{sqlText: sql_command}});
    statement1.execute();

    // Retorna un mensaje
    return 'Inserción exitosa desde el stream a la tabla de destino.';
    $$;
    """	

        # Formatear el procedimiento almacenado con los parámetros proporcionados.
        procedure_stmt_bronze = procedure_template.format(db,source_schema, procedure_name, source_table, source_schema, db, target_schema, source_table, db, source_schema, stream_name)
        
        # Devolver el procedimiento almacenado generado.    
        return procedure_stmt_bronze

    # Función para generar la declaración SQL de una tarea en Snowflake que se ejecuta basada en un stream.
    def generate_task_statement_bztosz(task_name,procedure_name,db,sch,stream_name):
        
        # Plantilla de la declaración CREATE TASK en Snowflake para la transferencia de BRONZE a SILVER.
        task_template = """
        CREATE OR REPLACE TASK {}.{}.{}_bztosz
        WAREHOUSE = {}
        SCHEDULE = '10 MINUTE'
        WHEN SYSTEM$STREAM_HAS_DATA('{}')
        AS CALL {}.{}.{}();
        """

        # Formatear la declaración de la tarea con los parámetros proporcionados.
        task_statement= task_template.format(db,sch,task_name,wh,stream_name,db,sch,procedure_name)
    
        # Devolver la declaración de la tarea generada.    
        return task_statement

    # Función para generar la declaración SQL de una tarea en Snowflake que se ejecuta después de otra tarea.
    def generate_task_statement_sztozg(table_name,procedure_name,db,source_schema,target_schema,task_name):
        
        # Plantilla de la declaración CREATE TASK en Snowflake para la transferencia de SILVER a GOLDEN.
        task_template = """
        CREATE OR REPLACE TASK {}.{}.{}_sztogz
        WAREHOUSE = {}
        AFTER {}.{}.{}
        AS CALL {}.{}.{}();
        """

        # Formatear la declaración de la tarea con los parámetros proporcionados.
        task_statement= task_template.format(db,source_schema,table_name,wh,db,source_schema,task_name,db,target_schema,procedure_name)
        
        # Devolver la declaración de la tarea generada.
        return task_statement

    # Función para generar la declaración SQL de una tabla en Snowflake con especificación de esquema y base de datos.
    def generate_ddl_statement_rest(column_names, data_types,table_name,db,sch):

        # Plantilla de la declaración CREATE TABLE en Snowflake con especificación de esquema y base de datos.
        ddl_template = "CREATE TABLE IF NOT EXISTS {}.{}.{} (\n{});"
        columns=[]

        # Crear las definiciones de las columnas con sus nombres y tipos de datos.
        for name, data_type in zip(column_names,data_types):
            colum_definition= f"    {name} {data_type}"
            columns.append(colum_definition)
        
        # Formatear la declaración CREATE TABLE con los parámetros proporcionados.    
        ddl_statement= ddl_template.format(db,sch,table_name, ",\n".join(columns))
        
        # Devolver la declaración CREATE TABLE generada.
        return ddl_statement

    # Función para generar la declaración SQL de una copia de datos en Snowflake desde un stage.
    def generate_copy_statement(sch_end,table_name,stage_name, csv_file_path, file_format):

        # Plantilla de la declaración COPY INTO en Snowflake.
        copy_command = f"""
        COPY INTO {sch_end}.{table_name}
        FROM @{stage_name}/{csv_file_path}
        FILE_FORMAT = (FORMAT_NAME = '{file_format}')
        ON_ERROR='CONTINUE';
        """

        # Devolver la declaración COPY INTO generada.
        return copy_command
    col1,col2,col3,col4,col5,col6,col7,col8,col9=st.columns(9)
    with col1:
        st.image("/home/site/wwwroot/App/views/utils/cuadrado-inetum.png")
    with col2:
        st.title(":red[Orchestrator]")

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
    st.header("Despliegue rápidamente su almacén de datos en Snowflake")
    st.write("""Como funciona

1- Proporcionar la información solicitada durante la ejecución para configurar la conexión con Snowflake y los detalles del proceso de ingestión.

2- El script inferirá automáticamente el esquema de las tablas a partir de los archivos CSV en el stage.

3- Creará capas (Bronze, Silver, Golden) en Snowflake con Streams, procedimientos almacenados y tareas programadas para la transferencia de datos entre capas.

4- Realizará la carga de datos desde los archivos CSV en el stage hacia la capa Bronze.""")
    # Iniciar sesión en Snowflake con autenticación básica.
    try: 
        session_with_pwd = snowpark_basic_auth()
    except:
        st.error("Rellene las credenciales de Snowflake")

    # Solicitar al usuario información sobre la base de datos, esquema y warehouse.
    database = st.text_input("Base de datos a utilizar: ")

    
    schema = st.text_input("Esquema de la primera capa (donde están los datos): ")
    

    wh = st.text_input("Warehouse utilizado: ")
    

    stage = st.text_input("Nombre del stage utilizado: ")
    
    on=st.toggle("SQL para la creación de file formats")
    ff_sql="""
 create or replace file format csv_schema
    type = csv 
    FILE_EXTENSION = 'csv'
    field_delimiter = ',' 
    record_delimiter= '\\n'
    field_optionally_enclosed_by = '"'
    empty_field_as_null = true
    parse_header=true;
create or replace file format csv_ff
    type = csv 
    FILE_EXTENSION = 'csv'
    field_delimiter = ',' 
    record_delimiter= '\\n'
    field_optionally_enclosed_by = '"'
    empty_field_as_null = true
    skip_header=1;
                 """
    if on:
        st.code(ff_sql,language='sql')
    schema_file = st.text_input("File format para la creación de tablas: ")
    schema_table = st.text_input("File format para la carga de datos en tablas: ")
    sch_end = st.text_input('Schema en el que cargar los datos por primera vez: ')
    if st.button("Connect"):
        session_with_pwd.sql("alter session set query_tag ='(v0) Start Snowpark automation'").collect()
        session_with_pwd.sql("use role accountadmin").collect()
        database_template = "use database {}"
        session_with_pwd.sql(database_template.format(database)).collect()
        schema_template = "use schema {}"
        session_with_pwd.sql(schema_template.format(schema)).collect()
        wh_template = "use warehouse {}"
        session_with_pwd.sql(wh_template.format(wh)).collect()
        stage_template = "list @{}"
        stg_files = session_with_pwd.sql(stage_template.format(stage)).collect()
        
        # Iteración sobre los archivos del stage y la generación de las sentencias SQL.
        for row in stg_files:
            # Obtener el valor del nombre del archivo y la ubicación del stage.
            row_value = row.as_dict()
            stg_file_path_value = row_value.get('name')

            # Dividir la ruta del archivo y extraer los nombres internos.
            file_path, file_name = os.path.split(stg_file_path_value)
            stg_location = "@" + file_path

            # Consulta SQL para inferir el esquema de la tabla desde el archivo CSV.
            infer_schema_sql = """ \
                SELECT * 
                FROM TABLE(
                    INFER_SCHEMA(
                    LOCATION=>'{}/',
                    files => '{}',
                    file_format=>'{}'
                    )
                )
            """.format(stg_location, file_name, schema_file)

            # Ejecutar la consulta SQL para inferir el esquema y obtener las columnas y tipos de datos.
            inferred_schema_rows = session_with_pwd.sql(infer_schema_sql).collect()
            col_name_lst = []
            col_data_type_lst = []

            # Iterar sobre las filas del esquema inferido y almacenar nombres y tipos de columnas.
            for row in inferred_schema_rows:
                row_value = row.as_dict()
                column_name = row_value.get('COLUMN_NAME')
                column_type = row_value.get('TYPE')
                col_name_lst.append(column_name)
                col_data_type_lst.append(column_type)

            # Obtener el nombre de la tabla a partir del nombre del archivo.
            table_name = file_name.split('.')[0]

            # Generar declaraciones SQL para la capa Bronze.
            create_ddl_stmt_bronze = generate_ddl_statement_rest(col_name_lst,col_data_type_lst,table_name.upper(),database.upper(),"BRONZE_ZONE")
            stream_stmt_bronze= generate_stream_statement(table_name.upper(),database.upper(),"BRONZE_ZONE")
            procedure_stmt_bztosz= generate_procedure_transport("{}_stream".format(table_name.upper()),"BRONZE_ZONE",table_name.upper(),database.upper(),"SILVER_ZONE","{}_BZTOSZ".format(table_name.upper()))
            task_stmt_bztosz= generate_task_statement_bztosz(table_name.upper(),"{}_BZTOSZ".format(table_name.upper()),database.upper(),"BRONZE_ZONE","{}_STREAM".format(table_name.upper()))
            
            # Generar declaraciones SQL para la capa Silver.
            create_ddl_stmt_silver = generate_ddl_statement_rest(col_name_lst,col_data_type_lst,table_name.upper(),database.upper(),"SILVER_ZONE")
            stream_stmt_silver= generate_stream_statement(table_name.upper(),database.upper(),"SILVER_ZONE")
            procedure_stmt_sztogz= generate_procedure_transport("{}_stream".format(table_name.upper()),"SILVER_ZONE",table_name.upper(),database.upper(),"GOLDEN_ZONE","{}_SZTOGZ".format(table_name.upper()))
            task_stmt_sztogz= generate_task_statement_sztozg(table_name.upper(),"{}_SZTOGZ".format(table_name.upper()),database.upper(),"BRONZE_ZONE","SILVER_ZONE","{}_BZTOSZ".format(table_name.upper()))
            
            # Generar declaración SQL para la capa Golden
            create_ddl_stmt_golden = generate_ddl_statement_rest(col_name_lst,col_data_type_lst,table_name.upper(),database.upper(),"GOLDEN_ZONE")

            #ACTIVATE TASKS
            #activate_task_template = "ALTER TASK {}.{}.{} RESUME;"
            #activate_task_sztogz= activate_task_template.format(database.upper(),"BRONZE_ZONE","{}_SZTOGZ".format(table_name.upper()))
            #activate_task_processing= activate_task_template.format(database.upper(),"BRONZE_ZONE","{}_UPDATENULL".format(table_name.upper()))
            #activate_task_bztosz= activate_task_template.format(database.upper(),"BRONZE_ZONE","{}_BZTOSZ".format(table_name.upper()))
            
            # Generar declaración SQL para copiar datos desde el stage a la capa Bronze.
            copy_stmt = generate_copy_statement(sch_end,table_name,stage,file_name,schema_table)        
        
        #EXECUTE TASK_BZTOSZ
            #execute_task_template = "EXECUTE TASK {}.{}.{}"
            #execute_task= execute_task_template.format(database.upper(),"BRONZE_ZONE","{}_BZTOSZ".format(table_name.upper()))

            #SEUPEND TASK
            #suspend_task_template = "ALTER TASK {}.{}.{} SUSPEND;"
            #suspend_task_bztosz=suspend_task_template.format(database.upper(),"BRONZE_ZONE","{}_BZTOSZ".format(table_name.upper()))
            #suspend_task_processing=suspend_task_template.format(database.upper(),"BRONZE_ZONE","{}_UPDATENULL".format(table_name.upper()))
            #suspend_task_sztogz=suspend_task_template.format(database.upper(),"BRONZE_ZONE","{}_SZTOGZ".format(table_name.upper()))

            # Ejecutar las declaraciones SQL en Snowflake.
            session_with_pwd.sql(create_ddl_stmt_bronze).collect()
            session_with_pwd.sql(stream_stmt_bronze).collect()
            session_with_pwd.sql(procedure_stmt_bztosz).collect()
            session_with_pwd.sql(task_stmt_bztosz).collect()
            session_with_pwd.sql(create_ddl_stmt_silver).collect()
            session_with_pwd.sql(stream_stmt_silver).collect()
            session_with_pwd.sql(procedure_stmt_sztogz).collect()
            session_with_pwd.sql(task_stmt_sztogz).collect()
            session_with_pwd.sql(create_ddl_stmt_golden).collect()
            #session_with_pwd.sql(activate_task_sztogz).collect()
            #session_with_pwd.sql(activate_task_processing).collect()
            #session_with_pwd.sql(activate_task_bztosz).collect()
            session_with_pwd.sql(copy_stmt).collect()
            #session_with_pwd.sql(execute_task).collect()
            #session_with_pwd.sql(suspend_task_bztosz).collect()
            #session_with_pwd.sql(suspend_task_processing).collect()
            #session_with_pwd.sql(suspend_task_sztogz).collect()

            
        session_with_pwd.sql("alter session set query_tag = '(v0) End Snowpark automation'").collect()
        left,mid,right=st.columns(3)
        with mid:
            st.header(":rainbow[Warehouse desplegado con éxito]")

        