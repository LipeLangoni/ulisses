from langchain_community.llms import Ollama
from langchain import PromptTemplate
from langchain.chains import LLMChain

from langchain.agents import create_sql_agent
from langchain.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
import os
from agent import GraphAgent
from utils import parse_markdown_table, plot_data
from langchain.tools.retriever import create_retriever_tool
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

os.environ["OPENAI_API_KEY"] = ""
db = SQLDatabase.from_uri("sqlite:///emendas_parlamentares.db")

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
agent = GraphAgent(db,llm)

app = FastAPI()

@app.post("/ulisses")
def add_item(input):
    return agent.invoke(input)