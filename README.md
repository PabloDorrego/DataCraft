
## DataCraft
El objetivo de este proyecto es el de aplicar inteligencia al proceso de segmentación por dominios en la capa Golden y la generación y consumo de data marts. 
Para ello se creo DataCraft, una aplicación basada en streamlit que permita a través de un chatbot (gpt-4) generar dominios de datos y data marts de manera ágil aplicando inteligencia artificial en el proceso de segmentación y generación de sentencias SQL para su creación en Snowflake. 
### Uso
- Versión de python soportada 3.11
- Instalar las librerías: pip install -r requirements.txt
- Ejecutar uno de los siguientes comandos para ejecutar la aplicación:
  - streamlit run App/main.py
  - python -m streamlit run App/main.py 
- Introducir claves del modelo LLM 
  - Azure OpenAI​ 
- Introducir las credenciales de su Data Warehouse de Snowflake
- Añadir descripción de la empresa​
- Añadir áreas de negocio​/dominios
El chatbot dará como respuesta, en primera instancia un listado con los dominios recomendados, así como las correspondientes tablas que deberían pertenecer a esos dominios. Para lo cual, esperará como input (prompt) una descripción de la empresa junto a sus áreas de negocios y los metadatos relativos a las tablas presentes en snowflake. 
Para usar DomAIn y Data Marta deberás tener acceso a la api de Azure OpenAI con el modelo GPT-4 idealmente.
### Domain
El chatbot dará como respuesta, en primera instancia un listado con los dominios recomendados, así como las correspondientes tablas que deberían pertenecer a esos dominios. Para lo cual, esperará como input (prompt) una descripción de la empresa junto a sus áreas de negocios y los metadatos relativos a las tablas presentes en snowflake.
### Data Marts
Con este chatbot podrás obtener una respuesta con los data marts propuestos por la ia y hacer todo tipo de modificaciones además de poder pedirle las sentencias sql para agilizar la creación de los data marts en un entorno como Snowflake
#### KPI identification
Además como complemento a Data marta hemos añadido la funcionalidad de identificar el data mart idóneo para un determinado KPI, a parte de recomendar el data mart que debería ser usado, proporciona la sentencia sql para obtener dicho KPI

