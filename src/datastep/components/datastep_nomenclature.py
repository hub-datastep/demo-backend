import pathlib
import re

from infra.supabase import supabase
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.callbacks import get_openai_callback


group_template = """Отнеси отзыв к какой–либо группе. Обрати на содержание отзыва и эмоции автора.

Отзыв: 
{input}

Список групп:
{groups}

Используй формат:

Группа из списка:
"""

group_prompt = PromptTemplate(
    template=group_template,
    input_variables=["input", "groups", "description"]
)

llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-1106", request_timeout=10, max_retries=3)

group_chain = LLMChain(llm=llm, prompt=group_prompt)


def map_with_groups(query: str, tags: str) -> str:
    response = group_chain.run(input=query, groups=tags)
    return extract(response, "Группа из списка: (.+)")


def extract(response: str, regex: str):
    match = re.search(regex, response)
    try:
        return match.group(1)
    except:
        return response


def get_data_folder_path():
    return f"{pathlib.Path(__file__).parent.resolve()}"


def save_to_database(values: dict):
    return supabase.table("nomenclature_mapping").insert(values).execute()


def do_mapping(query: str, tags: list[str]) -> str:
    with get_openai_callback() as cb:
        response = map_with_groups(query, "\n".join(tags))

        # database_response = save_to_database({
        #     "input": query,
        #     "output": response,
        #     "source": job.get_meta().get("source", None),
        #     "status": job.get_status()
        # })
        #
        # job.meta["mapping_id"] = database_response.data[0]["id"]
        # job.save()

    # print(cb.total_cost)

    return response


if __name__ == "__main__":
    with open("/Users/bleschunov/PycharmProjects/msu-backend/src/datastep/components/tags.txt") as f:
        tags = f.readlines()
    print("FINAL_RESPONSE", do_mapping("Безобразное качество!Почти нет ядра,Прелые....,поэтому не знают как продать,огромная скидка...не берите!", tags))
