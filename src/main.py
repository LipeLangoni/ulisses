from fastapi import FastAPI, HTTPException, Request
from langchain.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
import os
from src.agent import GraphAgent
import logging
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

llm = ChatOpenAI(openai_api_key=openai_api_key,model="gpt-4o-mini", temperature=0)
agent = GraphAgent(db,llm)

app = FastAPI()

@app.post("/lumia")
async def add_item(request: Request,input:dict):

    logging.info(f"Request URL: {request.url}")
    logging.info(f"Request Body: {input}")
    logging.info(f"Client IP: {request.client.host}")
    return agent.stream(f"chat history:{input.get('memory')} \n\n user new input: {input.get('input')}")