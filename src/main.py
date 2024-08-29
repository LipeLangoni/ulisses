from langchain_community.llms import Ollama
from langchain import PromptTemplate
from langchain.chains import LLMChain

from langchain.agents import create_sql_agent
from langchain.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
import os
from src.agent import GraphAgent
from langchain.tools.retriever import create_retriever_tool
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from fastapi import FastAPI, HTTPException,Request
from pydantic import BaseModel
from typing import List
import logging
from datetime import datetime

logging.basicConfig(
    filename="api_requests.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

db = SQLDatabase.from_uri("sqlite:///emendas.db")

open_api_key = "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"

llm = ChatOpenAI(openai_api_key=open_api_key,model="gpt-4o-mini", temperature=0)
agent = GraphAgent(db,llm)

app = FastAPI()

@app.post("/ulisses")
async def add_item(request: Request,input:dict):

    logging.info(f"Request URL: {request.url}")
    logging.info(f"Request Body: {input}")
    logging.info(f"Client IP: {request.client.host}")

    return agent.stream(input.get("input"))