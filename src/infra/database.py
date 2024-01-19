import os

from sqlmodel import create_engine, SQLModel, Session

from model import user_model
from scheme.mode_scheme import Mode
from scheme.prompt_scheme import Prompt
from scheme.tenant_scheme import Tenant
from scheme.user_scheme import UserCreate

db_url = os.getenv("DB_CONNECTION_STRING")

engine = create_engine(db_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def create_mock_data():
#     prompt_template = """You are a MS SQL expert. Given an input question, create a syntactically correct MS SQL query to run.
# Never query for all the columns from a specific table, only ask for a the few relevant columns given the question.
# Unless the user specifies in his question a specific number of examples he wishes to obtain, always limit your query to at most {limit} results using the TOP clause as per MS SQL.
# You must put TOP right after SELECT.
# Wrap each column name in square brackets ([]) to denote them as delimited identifiers.
# Use Russian language.
#
# Use LIKE operator for every text columns, for example LIKE "%название%".
# Name every column.
# You must use FORMAT function to display numbers in russian culture. You can put function into function, for example FORMAT(SUM(...)...).
# Current date is {current_date}
#
# Some of the columns in the table:
# "Тип документа" — income or debiting; possible values are "Списание", "Поступление"
# "План/Факт" — possible values are "План", "Факт". Use "Факт" if there is not stated other in the query.
# "Сумма" — actual transfer amount of money. Negative value means it was sent to counterparty. Positive value mean it was sent to МСУ.
# "Сумма договора" — contract amount.
# "Период" — date of the payment. Do not use FORMAT with this column.
# "Контрагент" — name of the counterpart/company/organization, this column can be used to detect company.
# "Группа статей ДДС" — purpose of the payment.
#
# Note that sometimes "Сумма" in the query means to calculate sum on the column "Сумма".
# Note that "фот" means filter WHERE "Группа статей ДДС"="Расходы на оплату труда"
# Note that "соц. страхование" means filter "WHERE c.[Группа статей ДДС] like '%соц%' OR c.[Группа статей ДДС] like '%страх%'
#
# Use only the following tables:
# {table_info}
#
# Question: {input}
# Return only SQL query ready for execution"""

    prompt_template = """You are a PostgreSQL expert. Given an input question, create a syntactically correct PostgreSQL query to run.
Never query for all the columns from a specific table, only ask for a the few relevant columns given the question.
Unless the user specifies in his question a specific number of examples he wishes to obtain, always limit your query to at most {limit} results using the LIMIT clause as per PostgreSQL.
Use Russian language.

Use LIKE operator for every text columns, for example LIKE "%название%".
Name every column.
You must use CAST(_ as money) function to display numbers. You can put function into function, for example CAST(SUM(...)...).
Current date is {current_date}

Some of the columns in the table:
"Тип документа" — income or debiting; possible values are "Списания", "Поступления"
"План/Факт" — possible values are "План", "Факт". Use "Факт" if there is not stated other in the query.
"Сумма" — actual transfer amount of money. Negative value means it was sent to counterparty. Positive value mean it was sent to us.
"Сумма договора" — contract amount.
"Период" — date of the payment. Do not use CAST with this column.
"Контрагент" — name of the counterpart/company/organization, this column can be used to detect company.
"Группа статей" — purpose of the payment.
 
Note that sometimes "Сумма" in the query means to calculate sum on the column "Сумма". 
Note that "фот" means filter WHERE "Группа статей"="Расходы на оплату труда"
Note that "соц. страхование" means filter "WHERE c.[Группа статей] like '%соц%' OR c.[Группа статей] like '%страх%'
Note that "заработко" or "чистая прибыль" is "Поступления" minus "Расходы"

Use only the following tables:
{table_info}

Question: {input}
Return only SQL query ready for execution"""

    def create_note(session: Session, scheme, obj: dict):
        note_db = scheme.parse_obj(obj)
        session.add(note_db)
        session.commit()
        return note_db

    with Session(engine) as session:
        modes = [
            create_note(session, Mode, {"name": "wiki"}),
            create_note(session, Mode, {"name": "databases"})
        ]
        tenant_db = create_note(session, Tenant, {
                "name": "datastep",
                "logo": "/path/to/logo",
                # "db_uri": "mssql+pyodbc://test:!1Testtest@mssql-129364-0.cloudclusters.net:15827/dwh_3?driver=ODBC+Driver+17+for+SQL+Server",
                "db_uri": "postgresql://qvzibsah:7wNHUBB3BMnY6QiFi0ggBejNd3SmlRf2@trumpet.db.elephantsql.com/qvzibsah",
                "modes": modes,
                "is_last": True
            }
        )
        prompt_db = create_note(session, Prompt, {
            "prompt": prompt_template,
            "is_active": True,
            "table": "платежи",
            "tenant_id": tenant_db.id
        })
        user_db = user_model.create_user(session, UserCreate(username="admin", password="admin", tenant_id=1))


def get_session() -> Session:
    with Session(engine) as session:
        yield session
