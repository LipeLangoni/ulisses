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

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = GraphAgent(db,llm)

app = FastAPI()

@app.post("/ulisses")
async def add_item(input:dict):
    return agent.stream(input.get("input"))