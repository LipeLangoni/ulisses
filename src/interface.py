import streamlit as st
import requests
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
import os
import re

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


for message in st.session_state.messages:
    st.chat_message(message["role"],avatar=message["avatar"]).write(message["content"])
       

# Chat input
if prompt := st.chat_input("Digite sua pergunta sobre emendas parlamentares"):

    st.chat_message("user").write(prompt)
    
    with st.spinner("Pensando..."):
        response = requests.post(url="http://localhost:8000/lumia",json={"input":prompt,"memory":extract_history(2)})
    
    st.session_state.messages.append({"role": "user", "content": prompt,'avatar':'🤖'})
    
    st.chat_message("assistant", avatar="src/lumia2.jpeg").write(convert_markdown_representation(response.content.decode('utf-8').replace('"','')))

    st.session_state.messages.append({"role": "assistant", "content": convert_markdown_representation(response.content.decode('utf-8').replace('"','')),'avatar':'src/lumia2.jpeg'})

st.write(f"<p style='padding-bottom: 50px;'></p>", unsafe_allow_html=True)
