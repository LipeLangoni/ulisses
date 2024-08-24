from langchain_core.prompts import BasePromptTemplate, PromptTemplate

examples = [
    {"input": "List all artists.", "query": "SELECT * FROM Artist;"},
    {
        "input": "Find all albums for the artist 'AC/DC'.",
        "query": "SELECT * FROM tabela_instrumentos WHERE ArtistId = (SELECT ArtistId FROM Artist WHERE Name = 'AC/DC');",
    }]


SCHEMA = """CREATE TABLE ordens_bancarias (
        ndeg_ob INTEGER, 
        data_ob TIMESTAMP, 
        no_instrumento INTEGER, 
        uf TEXT, 
        municipio TEXT, 
        tipo_de_repasse TEXT, 
        "situacao_(portal_fns)" TEXT, 
        valor_repasse REAL
)

/*
3 rows from ordens_bancarias table:
ndeg_ob data_ob no_instrumento  uf      municipio       tipo_de_repasse situacao_(portal_fns)   valor_repasse
20405   2024-07-05 00:00:00     12008067000121007       AP      CUTIAS  FAF     PROPOSTA PAGA   460262.0
20414   2024-07-05 00:00:00     12456167000123014       AP      VITORIA DO JARI FAF     PROPOSTA PAGA   641520.0
20651   2024-07-05 00:00:00     36000580575202400       BA      XIQUE-XIQUE     FAF     PROPOSTA PAGA   1747000.0
*/


CREATE TABLE tabela_instrumentos (
        ano INTEGER, 
        ndeg_emenda INTEGER, 
        partido TEXT, 
        parlamentar TEXT, 
        uf TEXT, 
        "cod._municipio_ibge" INTEGER, 
        municipio TEXT, 
        tipo_de_emenda TEXT, 
        grupo_de_despesa TEXT, 
        subfuncao INTEGER, 
        fonte INTEGER, 
        funcional TEXT, 
        data_inicio_proposta TEXT, 
        ndeg_instrumento INTEGER, 
        tipo_de_repasse TEXT, 
        tipo_de_instrumento TEXT, 
        "acao_orc." TEXT, 
        programa_estrategico TEXT, 
        componente TEXT, 
        beneficiario TEXT, 
        "nr._portaria" TEXT, 
        data_portaria TIMESTAMP, 
        "situacao_(portal_fns)" TEXT, 
        "situacao_(ds_proposta)" TEXT, 
        data_ultimo_pgto TEXT, 
        instrumento REAL, 
        empenhado REAL, 
        pago REAL
)

/*
3 rows from tabela_instrumentos table:
ano     ndeg_emenda     partido parlamentar     uf      cod._municipio_ibge     municipio       tipo_de_emenda  grupo_de_despesa        subfuncao       fonte   funcional       data_inicio_proposta      ndeg_instrumento        tipo_de_repasse tipo_de_instrumento     acao_orc.       programa_estrategico    componente      beneficiario    nr._portaria    data_portaria   situacao_(portal_fns)     situacao_(ds_proposta)  data_ultimo_pgto        instrumento     empenhado       pago
2024    43210001        PSD     CASTRO NETO     PI      220080  ANTONIO ALMEIDA INDIVIDUAL      CORRENTE        301     1001    1030151192E890022       2024-03-25 00:00:00     36000583614202400 FAF     INCREMENTO PAP  2E89    INCREMENTO TEMPORÁRIO AO CUSTEIO DOS SERVIÇOS DE ATENÇÃO PRIMÁRIA À SAÚDE - PAP INCREMENTO DO PISO DA ATENÇÃO PRIMÁRIA À SAÚDE - PAP    FUNDO MUNICIPAL DE SAUDE  3521/2024       2024-04-15 00:00:00     PROPOSTA PAGA   Proposta Paga   2024-05-14 00:00:00     151734.0        151734.0        151734.0
2024    90550006        NOVO    GILSON MARQUES  SC      420750  INDAIAL INDIVIDUAL      CORRENTE        302     1001    1030251182E900042       2024-04-04 00:00:00     36000596203202400FAF      INCREMENTO MAC  2E90    ATENÇÃO ESPECIALIZADA À SAÚDE   INCREMENTO TEMPORÁRIO DO TETO DA MÉDIA E ALTA COMPLEXIDADE - MAC        FUNDO MUNICIPAL DE SAUDE DE INDAIAL     3626/20242024-04-30 00:00:00      LIBERADO PAGAMENTO FNS  Proposta aprovada para Pagamento        -       300000.0        300000.0        0.0
2024    38220007        PT      MERLONG SOLANO  PI      220310  CRISTINO CASTRO INDIVIDUAL      CORRENTE        301     1001    1030151192E890022       2024-03-25 00:00:00     36000582736202400 FAF     INCREMENTO PAP  2E89    INCREMENTO TEMPORÁRIO AO CUSTEIO DOS SERVIÇOS DE ATENÇÃO PRIMÁRIA À SAÚDE - PAP INCREMENTO DO PISO DA ATENÇÃO PRIMÁRIA À SAÚDE - PAP    FUNDO MUNICIPAL DE SAUDE DE CRISTINO CASTRO - PI  3521/2024       2024-04-15 00:00:00     PROPOSTA PAGA   Proposta Paga   2024-05-23 00:00:00     2306000.0       2306000.0       2306000.0

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
Final Answer: the final answer to the original input question"""

SQL_PREFIX = """You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the below tools. Only use the information returned by the below tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

If the question does not seem related to the database, just return "I don't know" as the answer. Here are the schema of the db:
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

ulisses_prompt = """You are an agent designed to answer to the user questions related to brazil budget movement and facilitate understanding the complex terms.
for this purpose, you have access to a range of tools to communicate to a sql database, as well as to a vectorstore to retrieve context about specific terms.

Given an input question, create a syntactically correct sqlite query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 10 results.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the given tools. Only use the information returned by the tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

After getting the result of the database, you MUST use the retriever_tool to access the Glossary of Budgetary Terms and find the description of the terms you have to
explain to the user"""