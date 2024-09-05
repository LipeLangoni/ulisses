import sqlite3
import pandas as pd
conn = sqlite3.connect("orcamento.db")

df = pd.read_csv('src/tabelao.csv')
df2 = pd.read_csv('src/tabelao_favorecidos.csv')
df.to_sql("tabelao",conn,index=False, if_exists="replace")
df2.to_sql("tabelao_favorecidos",conn,index=False, if_exists="replace")