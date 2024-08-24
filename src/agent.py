from langchain.utilities import SQLDatabase
from langchain.llms import OpenAI
from langchain.agents import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from prompts import ulisses_prompt
from langchain.tools.retriever import create_retriever_tool
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver


class Agent:
    def __init__(self,db,llm):
        self.db = db
        self.agent_executor = create_sql_agent(
            llm=llm,
            toolkit=SQLDatabaseToolkit(db=self.db, llm=llm),
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            prompt=prompt,
            handle_parsing_errors=True
                                    )
    def invoke(self,input):
        return self.agent_executor.invoke(input)
    

class GraphAgent:
    def __init__(self,db,llm):
        embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.vectorstore = Chroma(
            collection_name="congresso",
            embedding_function=embeddings,
            persist_directory="./chroma_langchain_db",  # Where to save data locally, remove if not neccesary
                                    )
        self.retriever_tool = create_retriever_tool(
            self.vectorstore.as_retriever(),
            name="retriever_tool",
            description="""Use this tool to retrieve data from the vectorestore to explain to the user the congresso concepts""",

            )
        self.tools = SQLDatabaseToolkit(db=db, llm=llm).get_tools()
        self.tools.append(self.retriever_tool)
        self.agent_executor = create_react_agent(llm, tools=self.tools,messages_modifier=ulisses_prompt,checkpointer=MemorySaver())

    def invoke(self,input):
        return self.agent_executor.invoke({"messages": [("user", input)]},config={"configurable": {"thread_id": "1"}})
    
    def print_stream(self,stream):
        for s in stream:
            last_s = s
            message = s["messages"][-1]
            if isinstance(message, tuple):
                print(message)
            else:
                message.pretty_print()
        if last_s:
            last_message = last_s["messages"][-1]  # Get the last message in the last `s`
            return last_message.content
    
    def stream(self,input):
        return self.print_stream(self.agent_executor.stream({"messages": [("user", input)]},config={"configurable": {"thread_id": "1"}},stream_mode="values"))
    
    