import streamlit as st
import requests
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
import os
import re

pergunta1 = "Quais áreas receberam mais recursos via emendas parlamentares em 2024?"
pergunta2 = "Quais parlamentares enviaram mais recursos para Curitiba em 2024?"
pergunta3 = "Organize, em ordem decrescente, em uma tabela, os estados e o total de recursos recebidos por eles em 2024."

perguntas = [pergunta1,pergunta2,pergunta3]

def convert_markdown_representation(text):

    text = text.replace("\\n", "\n")
    
    text = text.replace("\\c", "").replace("\\~", "")
    
    text = re.sub(r"\∗\∗", "**", text)
    
    text = re.sub(r"(?<=\w)(\*\*)(?=\w)", r" \1", text)
    
    return text


def extract_history(window):
    return "\n\n".join([f"{message['role']}:{message['content']}\n" for message in st.session_state.messages[-window:]])


st.title("Lumi-a - Assistente de Pesquisa de Emendas Parlamentares")

# Add disclaimer
st.info("Disclaimer: a solução contém exclusivamente dados dos recursos destinados e empenhados via emendas parlamentares para o orçamento de 2024, abrangendo a funcional programática (função, subfunção, programa, ação e localizador), a modalidade e o grupo de natureza de despesa (GND). Atualização até 29/08/2024.")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "first_interaction" not in st.session_state:
    st.session_state.first_interaction = False


for message in st.session_state.messages:
    if message["role"] == "assistant":
        st.chat_message(message["role"],avatar=message["avatar"]).write(message["content"])
    else:
        st.chat_message(message["role"]).write(message["content"])
       
if not st.session_state.first_interaction:
    for pergunta in perguntas:
        if st.button(pergunta):
            st.chat_message("user").write(pergunta1)
        
            with st.spinner("Pensando..."):
                response = requests.post(url="http://localhost:8000/lumia",json={"input":pergunta,"memory":extract_history(2)})
            
            st.session_state.messages.append({"role": "user", "content": pergunta})
            
            st.chat_message("assistant", avatar="src/lumia2.jpeg").write(convert_markdown_representation(response.content.decode('utf-8').replace('"','')))

            st.session_state.messages.append({"role": "assistant", "content": convert_markdown_representation(response.content.decode('utf-8').replace('"','')),'avatar':'src/lumia2.jpeg'})
            st.session_state.first_interaction = True
            st.rerun()

# Chat input
if prompt := st.chat_input("Digite sua pergunta sobre emendas parlamentares"):

    st.session_state.first_interaction = True

    st.chat_message("user").write(prompt)
    
    with st.spinner("Pensando..."):
        response = requests.post(url="http://localhost:8000/lumia",json={"input":prompt,"memory":extract_history(2)})
    
    st.session_state.messages.append({"role": "user", "content": prompt,'avatar':'🤖'})
    
    st.chat_message("assistant", avatar="src/lumia2.jpeg").write(convert_markdown_representation(response.content.decode('utf-8').replace('"','')))

    st.session_state.messages.append({"role": "assistant", "content": convert_markdown_representation(response.content.decode('utf-8').replace('"','')),'avatar':'src/lumia2.jpeg'})
    st.rerun()
st.write(f"<p style='padding-bottom: 50px;'></p>", unsafe_allow_html=True)
