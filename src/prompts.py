from langchain_core.prompts import BasePromptTemplate, PromptTemplate

examples = [
    {"input": "List all artists.", "query": "SELECT * FROM Artist;"},
    {
        "input": "Find all albums for the artist 'AC/DC'.",
        "query": "SELECT * FROM tabela_instrumentos WHERE ArtistId = (SELECT ArtistId FROM Artist WHERE Name = 'AC/DC');",
    }]


SCHEMA = """CREATE TABLE IF NOT EXISTS "orcamento" (
"autor_desc" TEXT,
  "emenda_cod" TEXT,
  "autorizado" REAL,
  "empenhado" REAL,
  "executado" REAL,
  "funcao_cod" INTEGER,
  "funcao_desc" TEXT,
  "subfuncao_cod" INTEGER,
  "subfuncao_desc" TEXT,
  "programa_cod" INTEGER,
  "programa_desc" TEXT,
  "acao_cod" TEXT,
  "acao_desc" TEXT,
  "localizador_cod" INTEGER,
  "gnd_cod" INTEGER,
  "gnd_desc" TEXT,
  "modalidade_cod" INTEGER,
  "modalidade_desc" TEXT
);
Here are the tools you have access:"""

FORMAT_INSTRUCTIONS = """
Use the following format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Simplify: Simplify the budgetary terms and concetps in a way that a common citizen would understand
Final Answer: the simplified final answer to the original input question"""

SQL_PREFIX = """You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the below tools. Only use the information returned by the below tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

After elaborating the answer, use the retriever tool to get the context of concepts of specific budgetary terms and simplify it to the user in a way that makes it uncomplicated
"""

SQL_SUFFIX = """Begin!

Question: {input}
Thought: I should look at the tables in the database to see what I can query.  Then I should query the schema of the most relevant tables. I Should ALWAYS format my
final answer in markdown, ALWAYS answer in portuguese!
{agent_scratchpad}"""

SQL_FUNCTIONS_SUFFIX = """I should look at the tables in the database to see what I can query.  Then I should query the schema of the most relevant tables."""

template = "\n\n".join(
                [
                    SQL_PREFIX,
                    SCHEMA,
                    "{tools}",
                    FORMAT_INSTRUCTIONS,
                    SQL_SUFFIX,
                ]
            )
prompt = PromptTemplate.from_template(template)

ulisses_prompt = f"""You are an agent designed to answer to the user questions related to brazil budget movement and facilitate understanding the complex terms.
for this purpose, you have access to a range of tools to communicate to a sql database, as well as to a vectorstore to retrieve context about specific terms.

Given an input question, create a syntactically correct sqlite query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 10 results.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the given tools. Only use the information returned by the tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

here is the schema of the db:

{SCHEMA}

After getting the result of the database, you MUST use the retriever_tool to access the Glossary of Budgetary Terms and find the description of the terms you have to
explain to the user. Once you have the context of the term, simplify it to the user in a way that anyone could easily understand

Example:

Answer to the user: 
1. **Mara Gabrielli** - R$ 308.459.293,07
2. **Celso Russomanno** - R$ 260.452.807,74
Esses valores refletem a soma dos repasses realizados através das emendas parlamentares.

Action: retriever_toool
Query: repasses

Final Simplified Answer: 
1. **Mara Gabrielli** - R$ 308.459.293,07
2. **Celso Russomanno** - R$ 260.452.807,74
Esses valores refletem a soma dos repasses realizados através das emendas parlamentares. 
"Repasses" referem-se a transferências de dinheiro que o governo faz de uma entidade para outra. 
Por exemplo, o governo federal pode transferir recursos para estados e municípios, que então usam esse dinheiro para financiar serviços como saúde, 
educação, segurança, etc. Em outras palavras, são como "envios de dinheiro" feitos pelo governo para garantir que diferentes áreas e regiões possam 
cuidar das necessidades da população.
 """