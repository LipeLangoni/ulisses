from langchain.utilities import SQLDatabase
from langchain.llms import OpenAI
from langchain.agents import create_sql_agent
from src.tools import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from src.prompts import ulisses_prompt,simplifier_prompt
from langchain.tools.retriever import create_retriever_tool
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
from langfuse.callback import CallbackHandler
from langchain_chroma import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings

examples = [
    {"input": "Quem enviou recursos para Belém?", "output": """SELECT t.nome_autor, t.tipo_autor, t.partido_autor, SUM(DISTINCT tf.valor_pago) AS valor_total_pago
                                                            FROM tabelao t
                                                            JOIN tabelao_favorecidos tf
                                                            ON t.codigo_emenda = tf.codigo_emenda
                                                            WHERE tf.municipio_favorecido = 'belem'
                                                            GROUP BY t.nome_autor, t.tipo_autor, t.partido_autor
                                                            ORDER BY valor_total_pago DESC
                                                            LIMIT 10;"""},
    {"input": "Para que os recursos foram enviados para Belém?", "output": """SELECT t.descricao_funcao, SUM(DISTINCT tf.valor_pago) AS valor_total_pago
                                                                            FROM tabelao t 
                                                                            JOIN tabelao_favorecidos tf 
                                                                            ON t.codigo_emenda = tf.codigo_emenda 
                                                                            WHERE tf.municipio_favorecido = 'belem'
                                                                            ORDER BY valor_total_pago DESC;"""},
    {"input": "Para que a deputada Adriana Ventura enviou recursos para o município de São Paulo?", "output": """SELECT t.descricao_funcao, SUM(DISTINCT tf.valor_pago) AS valor_total_pago
                                                                                                                FROM tabelao t 
                                                                                                                JOIN tabelao_favorecidos tf 
                                                                                                                ON t.codigo_emenda = tf.codigo_emenda 
                                                                                                                WHERE t.nome_autor = 'adriana ventura' 
                                                                                                                AND tf.municipio_favorecido = 'sao paulo'
                                                                                                                ORDER BY valor_total_pago DESC;"""},
    {"input": "Quem enviou mais recursos para a saúde para Curitiba?", "output": """SELECT t.nome_autor, t.tipo_autor, t.partido_autor, SUM(DISTINCT tf.valor_pago) AS valor_total_pago
                                                                                    FROM tabelao t
                                                                                    JOIN tabelao_favorecidos tf
                                                                                    ON t.codigo_emenda = tf.codigo_emenda
                                                                                    WHERE tf.municipio_favorecido = 'curitiba'
                                                                                    AND t.descricao_funcao = 'saude'
                                                                                    GROUP BY t.nome_autor, t.tipo_autor, t.partido_autor
                                                                                    ORDER BY valor_total_pago DESC
                                                                                    LIMIT 10;"""}
]


to_vectorize = [" ".join(example.values()) for example in examples]



load_dotenv()

PUBLIC_KEY = os.getenv('PUBLIC_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
HOST = os.getenv('HOST')

langfuse_handler = CallbackHandler(
    public_key=PUBLIC_KEY,
    secret_key=SECRET_KEY,
    host=HOST
)
openai_api_key = os.getenv('OPENAI_API_KEY')

class GraphAgent:
    def __init__(self,db,llm):
        output_parser = StrOutputParser()
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key,model="text-embedding-3-small")
        few_shot_store = Chroma.from_texts(to_vectorize, embeddings, metadatas=examples)
        self.example_selector = SemanticSimilarityExampleSelector(
                                                            vectorstore=few_shot_store,
                                                            k=1,
                                                        )
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
        self.agent = create_react_agent(llm, tools=self.tools,messages_modifier=ulisses_prompt)
        self.simplifier =  simplifier_prompt | llm | output_parser

    def invoke(self,input):
        return self.agent.invoke({"messages": [("user", f"Use This Example to elaborate your query for this specific question{self.example_selector.select_examples({'input': input})}\n User Input:{input}")]},config={"configurable": {"thread_id": "1"}})
    
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
        return self.simplifier.invoke({"input":self.print_stream(self.agent.stream({"messages": [("user", f"Use This Example to elaborate your query for this specific question{self.example_selector.select_examples({'input': input})}\n User Input:{input}")]},config={"callbacks": [langfuse_handler]},stream_mode="values"))})
    
    