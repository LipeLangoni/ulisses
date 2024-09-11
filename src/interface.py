import streamlit as st
import requests
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
import os
import re

pergunta1 = "Quais áreas receberam mais recursos via emendas parlamentares em 2024?"
pergunta2 = "Quais parlamentares enviaram mais recursos para Curitiba em 2024?"
pergunta3 = "Organize, em ordem decrescente, em uma tabela, os estados e o total de recursos recebidos por eles em 2024."

perguntas = [pergunta1, pergunta2, pergunta3]

def convert_markdown_representation(text):
    text = text.replace("\\n", "\n")
    text = text.replace("\\c", "").replace("\\~", "")
    text = re.sub(r"\∗\∗", "**", text)
    text = re.sub(r"(?<=\w)(\*\*)(?=\w)", r" \1", text)
    return text

def extract_history(window):
    return "\n\n".join([f"{message['role']}:{message['content']}\n" for message in st.session_state.messages[-window:]])

st.title("Lumi-A - Assistente de Pesquisa de Emendas Orçamentárias")

# Add disclaimer
st.info("Disclaimer: a solução contém exclusivamente dados dos recursos destinados e empenhados via emendas parlamentares para o orçamento de 2024, abrangendo a funcional programática (função, subfunção, programa, ação e localizador), a modalidade e o grupo de natureza de despesa (GND). Atualização até 29/08/2024.")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "first_interaction" not in st.session_state:
    st.session_state.first_interaction = False

if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

for message in st.session_state.messages:
    if message["role"] == "assistant":
        st.chat_message(message["role"],avatar=message["avatar"]).write(message["content"])
    else:
        st.chat_message(message["role"]).write(message["content"])
       
if not st.session_state.first_interaction:
    for pergunta in perguntas:
        if st.button(pergunta):
            st.chat_message("user").write(pergunta)
            st.session_state.is_processing = True
            st.session_state.current_prompt = pergunta
            st.rerun()

# Chat input
if prompt := st.chat_input("Digite sua pergunta sobre emendas orçamentárias", disabled=st.session_state.is_processing):
    st.session_state.is_processing = True
    st.session_state.current_prompt = prompt
    st.rerun()

if st.session_state.is_processing and 'current_prompt' in st.session_state:
    st.chat_message("user").write(st.session_state.current_prompt)
    
    with st.spinner("Pensando..."):
        response = requests.post(url="http://localhost:8000/lumia",json={"input":st.session_state.current_prompt,"memory":extract_history(2)})
    
    st.session_state.messages.append({"role": "user", "content": st.session_state.current_prompt})
    
    assistant_response = convert_markdown_representation(response.content.decode('utf-8').replace('"',''))
    st.chat_message("assistant", avatar="src/lumia2.jpeg").write(assistant_response)

    st.session_state.messages.append({"role": "assistant", "content": assistant_response, 'avatar':'src/lumia2.jpeg'})
    st.session_state.first_interaction = True
    st.session_state.is_processing = False
    del st.session_state.current_prompt
    st.rerun()

st.write(f"<p style='padding-bottom: 50px;'></p>", unsafe_allow_html=True)
