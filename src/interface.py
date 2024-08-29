import streamlit as st
import requests
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
import os

st.title("Ulysses - Assistente de Pesquisa de Emendas Parlamentares")

# Add disclaimer
st.info("Disclaimer: a solução contém exclusivamente dados dos recursos destinados e empenhados via emendas parlamentares para o orçamento de 2024, abrangendo a funcional programática (função, subfunção, programa, ação e localizador), a modalidade e o grupo de natureza de despesa (GND).")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])
       

# Chat input
if prompt := st.chat_input("Digite sua pergunta sobre emendas parlamentares"):

    st.chat_message("user").write(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.spinner("Pensando..."):
        response = requests.post(url="http://localhost:8000/ulisses",json={"input":prompt})
    
    st.chat_message("assistant", avatar="src/avatar.jpg").write(response.content.decode('utf-8').replace('"',''))

    st.session_state.messages.append({"role": "assistant", "content": response.content.decode('utf-8').replace('"','')})

st.write(f"<p style='padding-bottom: 50px;'></p>", unsafe_allow_html=True)
