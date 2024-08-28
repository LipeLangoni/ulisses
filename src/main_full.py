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

db = SQLDatabase.from_uri("sqlite:///emendas.db")

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
agent = GraphAgent(db,llm)
st.title("Simple Chat App")

if "messages" not in st.session_state:
    st.session_state.messages = []

prompt = st.chat_input("Say something")
if prompt:
    response = agent.invoke(prompt)
    st.session_state.messages.append(f"User: {prompt}")
    st.session_state.messages.append(f"Assistant: {response}")

if st.session_state.messages:
    for message in st.session_state.messages:
        st.write(message)

# Scroll to the bottom of the chat
st.write(f"<p style='padding-bottom: 50px;'></p>", unsafe_allow_html=True)