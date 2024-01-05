
## Snowflake GenAI
El objetivo de este acelerador es el de aplicar inteligencia al proceso de segmentación por dominios en la capa Golden y la generación de data marts. 
Para ello creamos Snowflake GenAI, una aplicación basada en streamlit que permita a través de un chatbot (gpt-4) generar dominios de datos y data marts de manera ágil aplicando inteligencia artificial en el proceso de segmentación y generación de sentencias SQL para su creación en Snowflake. 
### Uso
- Ejecutar uno de los siguientes comandos para ejecutar la aplicación:
  - streamlit run Web/connection.py
  - python -m streamlit run Web/connection.py
  - O accede a la web: snowflakegenai.azurewebsites.net/?nav=home 
- Introducir claves del modelo LLM 
  - Azure OpenAI​ 
- Añadir descripción de la empresa​
- Añadir áreas de negocio​/dominios
El chatbot dará como respuesta, en primera instancia un listado con los dominios recomendados, así como las correspondientes tablas que deberían pertenecer a esos dominios. Para lo cual, esperará como input (prompt) una descripción de la empresa junto a sus áreas de negocios y los metadatos relativos a las tablas presentes en snowflake. 
Para usar DomAIn y Data Marta deberás tener acceso a la api de Azure OpenAI con el modelo GPT-4 idealmente.
### DomAIn
El chatbot dará como respuesta, en primera instancia un listado con los dominios recomendados, así como las correspondientes tablas que deberían pertenecer a esos dominios. Para lo cual, esperará como input (prompt) una descripción de la empresa junto a sus áreas de negocios y los metadatos relativos a las tablas presentes en snowflake.
### Data marta
Con este chatbot podrás obtener una respuesta con los data marts propuestos por la ia y hacer todo tipo de modificaciones además de poder pedirle las sentencias sql para agilizar la creación de los data marts en un entorno como Snowflake
  #### Data marta reverse
  Además como complemento a Data marta hemos añadido la funcionalidad de identificar el data mart idóneo para un determinado KPI, a parte de recomendar el data mart que debería ser usado, proporciona la sentencia sql para obtener dicho KPI
### Set up
También se añade este acelerador que pretende desplegar a partir de archivos almacenados en una area de stage una arquitectura Lakehouse en capas:
Creación DataWareHouse en Snowflake:  

- Raw_Zone: 

  - Primera capa para ingesta de datos crudos desde diversas fuentes. 

  - Sin procesar y de rápido almacenamiento. 

  - Permite la rápida adquisición de datos sin estructuración inicial. 

- Bronze_Zone: 

  - Segunda capa, almacena los datos en formato de tabla 

- Silver_Zone: 

  - Capa de transformación donde se estructuran y limpian los datos. 

  - Prepara los datos para un análisis más profundo. 

- Golden_Zone: 

  - Capa final con datos limpios y listos para su uso. 

  - Segmentación por dominios y creación de Data Marts
#### Uso del Script 

1- Ejecutar el script desde un entorno Python con las bibliotecas necesarias instaladas. 

2- Proporcionar la información solicitada durante la ejecución para configurar la conexión con Snowflake y los detalles del proceso de ingestión. 

3- El script inferirá automáticamente el esquema de las tablas a partir de los archivos CSV en el stage. 

4- Creará capas (Bronze, Silver, Golden) en Snowflake con Streams, procedimientos almacenados y tareas programadas para la transferencia de datos entre capas. 

5- Realizará la carga de datos desde los archivos CSV en el stage hacia la capa Bronze. 
### Analysis Assistant
Por último se añade un asistente para el análisis de datos almacenados en Snowflake mediante lenguaje natural.
-Asistente de redacción de consultas SQL: una aplicación sencilla que traduce preguntas comerciales al lenguaje de consultas SQL y luego las ejecuta y muestra los resultados.
-Asistente de análisis de datos: una aplicación más sofisticada para realizar análisis de datos avanzados, como análisis estadísticos y pronósticos. Aquí demostramos el uso de las técnicas de Cadena de Pensamiento y Reacción para realizar un procesamiento de varios pasos donde el siguiente paso de la cadena también depende de la observación/resultado del paso anterior.

