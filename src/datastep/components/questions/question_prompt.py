from langchain import PromptTemplate

question_prompt = """I have a database with such tables and columns:
{table_info}

Pay attention to use only the column names you can see in the tables and columns above.
Be careful to not use columns that do not exist.
Also, pay attention to which column is in which table.
Use Russian language.
Do not repeat questions.

Come up with {limit} new questions, the answer to which can be obtained using the information stored in these tables and columns.
If question contains not specific date replace it with recent dates or period, for example "specific period" you must replace with "last month" or "last year" or place here real recent date
Your answer must be a sequence of your questions. Each question should be on a new line.
"""


class QuestionPrompt:
    @classmethod
    def get_prompt(cls, table_description: str = "", limit: int = 3) -> PromptTemplate:
        prompt_template = PromptTemplate.from_template(
            question_prompt,
            partial_variables={
                "table_info": table_description,
                "limit": limit
            }
        )
        return prompt_template
