from langchain import PromptTemplate

_prompt_suffix = """Only use the following tables:
{table_info}

Question: {input}"""

_custom_prompt = """You are an PostgreSQL expert. Given an input question, first create a syntactically correct PostgreSQL query to run, then look at the results of the query and return the answer to the input question.
Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the TOP clause as per PostgreSQL. You can order the results to return the most informative data in the database.
Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in square brackets ([]) to denote them as delimited identifiers.
Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table. Use Russian language.

Use the following format:

Question: Question here
SQLQuery: SQL Query to run
SQLResult: Result of the SQLQuery
Answer: Final answer here
"""

# TODO: 24 и 25 строчки, кажется, не нужны. Проверить это и удалить, если не нужны. Если не нужны, убрать и упоминание MSU
# TODO: Возможно, стоит добавить пояснения для "Списание", "Перемещение_Приход", "Перемещение_Расход", "Поступление"
table_description = """
There is a company named MSU that works with many of counterparties. This is the table with payments of MSU.
If there is "компания" mentioned in the query it is meant MSU.

Some of the columns in the table:
"Тип документа" — possible values are "Списание", "Перемещение_Приход", "Перемещение_Расход", "Поступление"
"Банковский счет.МСУ вид банковского счета" — possible values are "ОБС", "Проектный", "УФК МО", "Департамент финансов Москва", "УФК Москва", "Расчетный"
"План/Факт" — possible values are "План", "Факт". Use "Факт" if there is not stated other in the query.
"Сумма" — actual transfer amount of money. Negative value means it was sent to counterparty. Positive value mean it was sent to MSU.
"Сумма договора" — contract amount.
"Период" — date of the payment. Working with that column use construction like LEFT(CONVERT(NVARCHAR(256), DATEADD(MONTH, _, GETDATE()), 120), 7) + '%'
"""

custom_prompt = PromptTemplate(
    input_variables=["input", "table_info", "top_k"],
    template=_custom_prompt  + table_description + _prompt_suffix,
)
