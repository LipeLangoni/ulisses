import streamlit as st
import requests
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from agent import GraphAgent
import os

db = SQLDatabase.from_uri("sqlite:///emendas.db")

llm = ChatOpenAI(openai_api_key=os.environ["OPENAI_API_KEY"], model="gpt-4o-mini", temperature=0)

agent = GraphAgent(db, llm)

st.title("Ulysses - Assistente de Pesquisa de Emendas Parlamentares")

# Add disclaimer
st.info("Disclaimer: a solução contém exclusivamente dados dos recursos destinados e empenhados via emendas parlamentares para o orçamento de 2024, abrangendo a funcional programática (função, subfunção, programa, ação e localizador), a modalidade e o grupo de natureza de despesa (GND).")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Digite sua pergunta sobre emendas parlamentares"):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.spinner("Pensando..."):
        response = agent.stream(prompt)
    
    with st.chat_message("assistant", avatar="avatar.jpg"):
        st.markdown(response, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": response})

st.write(f"<p style='padding-bottom: 50px;'></p>", unsafe_allow_html=True)
