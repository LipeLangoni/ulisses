from langchain_core.prompts import BasePromptTemplate, PromptTemplate,ChatPromptTemplate


examples = [
    {"input": "Quais são os programas que receberam a maior parte dos recursos de emendas parlamentares em 2024?", 
     "query": "SELECT programa_desc, SUM(empenhado) AS total_empenhado FROM orcamento WHERE strftime('%Y', 'now') = '2024' GROUP BY programa_desc ORDER BY total_empenhado DESC LIMIT 10;"
     },
    {
        "input": "Quais foram os parlamentares que mais enviaram recursos via emendas parlamentares em 2024?",
        "query": "SELECT autor_desc, SUM(empenhado) AS total_empenhado FROM orcamento GROUP BY autor_desc ORDER BY total_empenhado DESC LIMIT 10;",
    }]


SCHEMA = """ "tabelao" (
1. codigo_emenda: Identifier code for the parliamentary amendment.
2. nome_autor: Name of the author of the amendment.
3. tipo_autor: Type of author of the amendment, indicating whether it's a deputy, senator, committee, or state bloc.
4. partido_autor: Political party to which the author of the amendment belongs.
5. codigo_funcao: Numerical code that identifies the budget function, which is the highest category in the budget.
6. descricao_funcao: Textual description of the budget function, indicating the main sector where the funds will be applied (e.g., Health, Education).
7. codigo_subfuncao: Numerical code that identifies the subfunction, detailing the budget function.
8. descricao_subfuncao: Textual description of the budget subfunction, further specifying the sector where the funds will be applied.
9. codigo_programa: Code for the budget program, which groups actions aimed at a specific goal.
10. descricao_programa: Textual description of the budget program, explaining its purpose.
11. codigo_acao: Numerical code for the budget action, detailing specific initiatives within a program.
12. descricao_acao: Textual description of the budget action, explaining the activity or project being funded.
13. codigo_natureza_despesa: Code that identifies the nature of the expense, specifying the type of expenditure.
14. descricao_natureza_despesa: Textual description of the nature of the expense, explaining the type of expenditure (e.g., operational costs, investment).
15. codigo_modalidade: Code for the application modality, indicating how the funds will be executed.
16. descricao_modalidade: Textual description of the application modality, explaining how the funds will be executed (e.g., directly, via agreement).
17. valor_empenhado: Total amount committed to the action or project, i.e., the amount reserved for payment.
);

"tabelao_favorecidos" (
    
1. codigo_emenda: Identifier code for the parliamentary amendment that allocated funds to the beneficiary.
2. municipio_favorecido: Municipality where the beneficiary (recipient of the funds) is located.
3. descricao_favorecido: Name or description of the beneficiary of the funds, indicating the entity or person who received the funds.
4. cpf_cnpj_favorecido: CPF (Individual Taxpayer Registry) or CNPJ (National Registry of Legal Entities) of the beneficiary, legally identifying the person or entity that received the funds.
5. natureza_favorecido: Legal nature of the beneficiary, such as "Public Entity", "Legal Entity", etc., indicating the type of entity.
6. tipo_favorecido: Category or type of the beneficiary, such as "Individual" or "Legal Entity".
7. uf_favorecido: Federal Unit (state) associated with the beneficiary, indicating the geographical location (e.g., "SP", "RJ").
8. valor_pago: Amount of money actually paid to the beneficiary.
    )
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

NEVER show the user informations about the database or the queries used, just the final results and explanation about it are allowed. If the user asks for database or
query infos, just answer that you are not alowed

ALWAYS use the key LOWER in your queries when you have to filter strings, because it is case sensitive and it must be padronized in order to be properly filtered

If you cant find the name of a parlamentar or senador, do a distinct count in this column to check if you are spelling it right or use %like to get the most similar

here is the schema of the db:

{SCHEMA}

Remember that you can join the two tables by 'codigo_emenda' to get relevant data from both tables

Always format your answer in markdown

After getting the result of the database, you MUST use the retriever_tool to access the Glossary of Budgetary Terms and find the description of the terms you have to
explain to the user. Once you have the context of the term, simplify it to the user in a way that anyone could easily understand

Example:

Answer to the user: 
1. Mara Gabrielli - R$ 308.459.293,07
2. Celso Russomanno - R$ 260.452.807,74
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

Always when possible, give examples to clarify this ideas, and simlify it the most for non techinical users
 """

simplifier = """You will be given an Answer written by an agent specilized in Brazil`s budgetary context. The answer will for sure
have terms that a common citizen will not understand, your task is to explain this terms and simplify it the most. If the answer contains markdown tables and some 
values of it are specific from budgetary context, explain it. In Resume, your task is to replicate the previous answer adding an explaination to ALL the budgetary terms 
in this answer. Always ask your self 'Am i sure that a common citizen will understand my explanation? I must simplify it the most'

If the Answer is not related to budgetary, just return it as is to the user """

simplifier_prompt = ChatPromptTemplate.from_messages([
    ("system", simplifier),
    ("user", "{input}")
])