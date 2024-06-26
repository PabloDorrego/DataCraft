
import streamlit as st
import json
import openai
from typing import List
# Función para obtener el texto ingresado por el usuario
def get_text():

    input_text = st.text_input("You: ","", key="input")
    return input_text
# Función para obtener el área de negocio
def get_area():

    input_text = st.text_input("Areas de negocio: ","", key="area")
    return input_text
# Función para obtener la descripción de la empresa
def get_des():
    input_text = st.text_input("Descripción de la empresa: ","", key="des")
    return input_text 
# Función para obtener la respuesta generada por el modelo
def create_gpt_completion(ai_model: str, messages: List[dict]) -> dict:
    openai.api_key = st.secrets.api_credentials.api_key
    completion = openai.ChatCompletion.create(
        model=ai_model,
        messages=messages,
    )
    return completion
# Función para obtener el JSON con el listado de los dominios
def get_JSON():
	try:
		dominios = st.session_state.domains
	except:
		st.error("error json")
	return json.loads(dominios)
# Función para crear una tarjeta con las tablas de un dominio (para parsear el JSON)
def tables(alltables):
	r=""
	for table in alltables:
		r+= """<p class="card-text">%s</p>""" % str(table)
	return r
# Función para crear una tarjeta con las tablas de un dominio en HTML
def create_card(title, alltables):

	card="""
		<div class="m-1 p-1"style="padding: 2px 16px;">
			<div class="card m-2" style="width: 18rem;">
			  <div class="card-body bg-light">
			    <h3 class="card-title">%s</h3>
	""" % str(title)
	card+=tables(alltables)

	card+=""" 			  
				</div>
			</div>
		</div>
		"""
	return card
# Función para crear los dominios en la aplicación
def create_domains(dominios, container):
	st.markdown("""<h1 style="color:#018579; ">Dominios</h1>""", unsafe_allow_html= True)
	c = container.columns(2)
	i=0
	for dominio in dominios:
		d= create_card(dominio["nombre"], dominio["tablas"])
		c[i].markdown(d, unsafe_allow_html= True)
		i=(i+1)%2
# Función para generar el SQL a partir de los dominios seleccionados
def generarSQL(container):

	promt_sql= open('App/views/utils/promptsql.txt', 'r').read()

	st.session_state.messages.append({"role": "user", "content": promt_sql})
	cl=st.session_state.client.chat.completions.create(model=st.session_state["model"], messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages], stream=True)
	sql_response=""
	st.title("")
	with st.spinner('Generando SQL...'):
		for response in cl:
			if response.choices:
				sql_response += (response.choices[0].delta.content or "")
	st.session_state.messages.append({"role": "assistant", "content": sql_response})
	if "sql" not in st.session_state:
		st.session_state["sql"]=sql_response
	create_sql_statment(container)
# Función para mostrar el código SQL en la aplicación
def create_sql_statment(container):
	sql=st.session_state.sql
	container.header("Código SQL")
	container.write(sql)
# Función para hacer responsive el diseño del listado de dominios
def bootstrap():
	_bootstrap="""<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">"""
	st.markdown(_bootstrap, unsafe_allow_html= True)
	_css="""
	<style>
		.stButton>button {
			background-color: #f04641;
			color:white;
			border-radius: 8px;
			height: 4em;
			width: 12rem;
		}
	</style>"""
	st.markdown(_css, unsafe_allow_html= True)
# Función para validar el JSON
def validateJSON(txt):
	try:
		json.loads(txt)
	except:
		return False
	return True
# Función para finalizar el chat
def fin():
	st.session_state.finish=True
