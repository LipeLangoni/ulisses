from langchain.utilities import SQLDatabase
from langchain.llms import OpenAI
from langchain.agents import create_sql_agent
from src.tools import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from src.prompts import ulisses_prompt
from langchain.tools.retriever import create_retriever_tool
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

open_api_key = "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"

class GraphAgent:
    def __init__(self,db,llm):
        embeddings = OpenAIEmbeddings(openai_api_key=open_api_key,model="text-embedding-3-small")
        self.vectorstore = Chroma(
            collection_name="congresso",
            embedding_function=embeddings,
            persist_directory="./chroma_langchain_db", 
                                    )
        self.retriever_tool = create_retriever_tool(
            self.vectorstore.as_retriever(),
            name="retriever_tool",
            description="""Use this tool to retrieve data from the vectorestore to explain to the user the budgetary concepts. Simplify the concepts in a way that
            anyone could easily understand, including and mainly the common citizen""",

            )
        self.tools = SQLDatabaseToolkit(db=db, llm=llm).get_tools()
        self.tools.append(self.retriever_tool)
        self.agent = create_react_agent(llm, tools=self.tools,messages_modifier=ulisses_prompt,checkpointer=MemorySaver())

    def invoke(self,input):
        return self.agent.invoke({"messages": [("user", input)]},config={"configurable": {"thread_id": "1"}})
    
    def print_stream(self,stream):
        for s in stream:
            last_s = s
            message = s["messages"][-1]
            if isinstance(message, tuple):
                print(message)
            else:
                message.pretty_print()
        if last_s:
            last_message = last_s["messages"][-1]  
            return last_message.content
    
    def stream(self,input):
        return self.print_stream(self.agent.stream({"messages": [("user", input)]},config={"configurable": {"thread_id": "1"}},stream_mode="values"))
    
    