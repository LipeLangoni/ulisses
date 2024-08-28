import streamlit as st
from langchain_community.llms import Ollama
from langchain import PromptTemplate
from langchain.chains import LLMChain

from langchain.agents import create_sql_agent
from langchain.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
import os
from agent import GraphAgent
from langchain.tools.retriever import create_retriever_tool
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import requests

st.title("Simple Chat App")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"],unsafe_allow_html=True)

if prompt := st.chat_input("Digitar"):

    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role":"user","content":prompt})

    response = requests.post(url="http://localhost:8000/ulisses",json={"input":prompt})

    with st.chat_message("assistant"):
        st.markdown(response.content.decode("utf-8").replace('"',""),unsafe_allow_html=True)

    st.session_state.messages.append({"role":"assistant","content":response.content.decode("utf-8").replace('"',"")})



# Scroll to the bottom of the chat
st.write(f"<p style='padding-bottom: 50px;'></p>", unsafe_allow_html=True)