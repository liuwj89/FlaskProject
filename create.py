import psycopg2
from psycopg2 import sql

# 连接到默认数据库
# 请将your_username和your_password替换为你的数据库用户名和密码
conn = psycopg2.connect(
    dbname="postgres",
    user="your_username",
    password="your_password",
    host="localhost",
    port="5432"
)
conn.autocommit = True
cur = conn.cursor()

# 创建名为finalproject的数据库
cur.execute(sql.SQL("CREATE DATABASE finalproject"))

# 关闭连接
cur.close()
conn.close()

# 连接到finalproject数据库
conn = psycopg2.connect(
    dbname="finalproject",
    user="your_username",
    password="your_password",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# 读取并执行config.sql文件
with open('config.sql', 'r') as file:
    sql_commands = file.read()
cur.execute(sql_commands)

# 关闭连接
cur.close()
conn.close()