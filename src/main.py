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
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
print(openai_api_key)
logging.basicConfig(
    filename="api_requests.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

db = SQLDatabase.from_uri("sqlite:///orcamento.db")

llm = ChatOpenAI(openai_api_key=openai_api_key,model="gpt-4o-mini-2024-07-18", temperature=0)
agent = GraphAgent(db,llm)

app = FastAPI()

@app.post("/lumia")
async def add_item(request: Request,input:dict):

    logging.info(f"Request URL: {request.url}")
    logging.info(f"Request Body: {input}")
    logging.info(f"Client IP: {request.client.host}")
    return agent.stream(f"chat history:{input.get('memory')} \n\n user new input: {input.get('input')}")