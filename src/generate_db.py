import sqlite3
import pandas as pd
conn = sqlite3.connect("orcamento.db")

df = pd.read_csv('src/tabelao.csv')
df.to_sql("orcamento",conn,index=False, if_exists="replace")